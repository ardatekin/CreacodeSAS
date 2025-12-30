# ---------------------------------------------------------------------------
# Creacode SIP Application Server – Speech-to-Text (STT) Proxy
#
# File       : STTProxy.py
# Project    : CreacodeSAS
# Author     : Arda Tekin
#
# Overview:
# This module implements a standalone Speech-to-Text proxy service used by
# the Creacode SIP Application Server. Its primary purpose is to offload
# speech recognition responsibilities from the core IVR engine and provide
# a clean, network-based STT interface.
#
# Deployment & Runtime:
# - Deployed under C:\CreacodeSAS\Bin
# - Runs as a long-lived background process
# - Installed and managed as a Windows Service via NSSM
#   (service name: CreacodeSAS-STTProxy)
# - Uses system-wide GOOGLE_APPLICATION_CREDENTIALS for cloud authentication
#
# Interfaces:
# - WebSocket interface for real-time audio streaming from the IVR layer
# - HTTP health endpoint for service monitoring
# - Listens on TCP port 8089
#
# Audio Handling:
# - Receives telephony-grade audio frames over WebSocket
# - Supports multiple codecs as signaled by the IVR:
#     * G711 μ-law (8 kHz)
#     * G711 A-law / PCM (8 kHz, linear)
#     * G729A (accepted but not processed for STT)
# - Audio frames are buffered until end-of-stream (EOS) is received
#
# STT Processing:
# - Integrates with Google Cloud Speech-to-Text
# - Selects recognition configuration based on codec and language
# - Performs synchronous recognition in a background executor to avoid
#   blocking the async event loop
#
# Operational Notes:
# - Designed to be restarted independently from the IVR core
# - Failures in this service do not crash the main CreacodeSAS process
#
# License    : See LICENSE.txt
# ---------------------------------------------------------------------------

#!/usr/bin/env python3
import asyncio
import json
import logging
import os
from typing import Tuple

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import uvicorn
from google.cloud import speech
import wave

# ----------------------------------------------------------------------
# Logging
# ----------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger("ivr-stt-proxy")

app = FastAPI(title="IVR STT Proxy", version="1.0")


# ----------------------------------------------------------------------
# Health check
# ----------------------------------------------------------------------
@app.get("/health")
async def health():
    return {"status": "ok"}


# ----------------------------------------------------------------------
# Google STT helper (batch recognize, G.711 8 kHz)
# ----------------------------------------------------------------------
async def recognize_google_g711(
    audio_bytes: bytes,
    codec: str = "G711U",
    language_code: str = "en-US",
) -> Tuple[str, float]:
    """
    Run synchronous Google Speech-to-Text recognition on G.711 8 kHz audio.

    codec: "G711U" (μ-law) or "G711A" (A-law).

    Returns (transcript, confidence).
    """
    if not audio_bytes:
        return "", 0.0

    codec_norm = (codec or "G711U").strip().upper()

    if codec_norm == "G711U":
        encoding = speech.RecognitionConfig.AudioEncoding.MULAW
    elif codec_norm == "G711A":
        # encoding = speech.RecognitionConfig.AudioEncoding.ALAW  <-- Not supported by google-cloud-speech.v1
        # G711A audio was ALREADY converted to LINEAR16 and being sent to this script by IVR
        encoding = speech.RecognitionConfig.AudioEncoding.LINEAR16
    else:
        raise ValueError(
            f"Unsupported codec for Google STT: {codec_norm}. "
            "Only G711U/G711A are supported."
        )

    loop = asyncio.get_running_loop()

    def _call():
        client = speech.SpeechClient()

        lang_norm = (language_code or "").strip().lower()
        codec_norm_local = (codec or "G711U").strip().upper()

        # Conservative allowlist: expand as you confirm in your environment.
        PHONE_CALL_LANG_ALLOWLIST = {
            "en-us",
            "en-gb",
            # add more after confirming: "fr-fr", "de-de", etc.
        }
                
        if codec_norm_local == "G711A":
            # LINEAR16. Use phone_call only if language is known to support it.
            if lang_norm in PHONE_CALL_LANG_ALLOWLIST:
                config = speech.RecognitionConfig(
                    encoding=encoding,
                    sample_rate_hertz=8000,
                    language_code=language_code,
                    enable_automatic_punctuation=True,
                    model="phone_call",
                    use_enhanced=True,
                )
            else:
                config = speech.RecognitionConfig(
                    encoding=encoding,
                    sample_rate_hertz=8000,
                    language_code=language_code,
                    enable_automatic_punctuation=True,
                )

        elif codec_norm_local == "G711U":
            # MULAW baseline config
            config = speech.RecognitionConfig(
                encoding=encoding,
                sample_rate_hertz=8000,
                language_code=language_code,
                enable_automatic_punctuation=True,
            )

        else:
            # Should never happen because G729A is skipped earlier
            raise ValueError(f"Unexpected codec {codec_norm}")


        audio = speech.RecognitionAudio(content=audio_bytes)

        response = client.recognize(config=config, audio=audio)

        best_transcript = ""
        best_conf = 0.0

        for result in response.results:
            if not result.alternatives:
                continue
            alt = result.alternatives[0]
            if alt.confidence >= best_conf:
                best_conf = alt.confidence
                best_transcript = alt.transcript

        return best_transcript, best_conf

    return await loop.run_in_executor(None, _call)


# ----------------------------------------------------------------------
# WebSocket endpoint: phone -> IVR -> WS -> Google STT -> IVR
# ----------------------------------------------------------------------
@app.websocket("/stt-stream")
async def stt_stream(ws: WebSocket):
    """
    IVR connects here and sends:
      - binary frames: G.711 / G.729A 8 kHz audio (20 ms → 160 bytes for G.711)
            * IVR uses codec codes: G711U, G711A, G729A
      - a text frame "LANG=xx-XX" (optional) to override language per call
      - a text frame "CODEC=G711U|G711A|G729A" to set codec
      - a text frame "EOS" when it has finished sending audio.

    STT behavior:
      - G711U → Google MULAW
      - G711A → Google ALAW
      - G729A → accepted but STT is currently not supported; we just
                skip recognition and return an empty final result.
    """
    await ws.accept()
    logger.info("STT stream connected")

    total_bytes = 0
    audio_buffer = bytearray()

    # Default language from environment; can be overridden per call via LANG=xx
    language_code = os.getenv("IVR_STT_LANG", "en-US")

    # Default codec from environment; IVR uses G711U/G711A/G729A
    codec_name = os.getenv("IVR_STT_CODEC", "G711U").strip().upper()

    logger.info("Initial language_code=%s", language_code)
    logger.info("Initial codec_name=%s", codec_name)

    def normalize_codec_name(raw: str) -> str:
        """
        Map IVR codec names to internal identifiers used for STT.

        Accepted (for STT):
          - G711U, G.711U  -> G711U (μ-law)
          - G711A, G.711A  -> G711A (A-law)

        NOTE:
          - G729A is handled separately (no STT yet, skipped).
          - PCMU / PCMA / others are NOT accepted at all.
        """
        if not raw:
            return "G711U"

        v = raw.strip().upper()

        # G.711 μ-law
        if v in ("G711U", "G.711U"):
            return "G711U"

        # G.711 A-law
        if v in ("G711A", "G.711A"):
            return "G711A"

        # Everything else is unsupported on STT side
        raise ValueError(
            f"Unsupported codec: {v}. Only G711U and G711A are supported for STT; "
            "G729A is accepted but currently skipped."
        )

    try:
        while True:
            msg = await ws.receive()

            # 1) Binary audio frame
            if "bytes" in msg and msg["bytes"] is not None:
                data = msg["bytes"]
                if data:
                    audio_buffer.extend(data)
                    total_bytes += len(data)
                    logger.info(
                        "Received %d bytes of audio (total=%d)",
                        len(data),
                        total_bytes,
                    )
                continue

            # 2) Text control frame (e.g., "EOS", "LANG=tr-TR", "CODEC=G711U")
            if "text" in msg and msg["text"] is not None:
                text = msg["text"]
                logger.info("Received text message from IVR: %s", text)

                stripped = text.strip()
                up = stripped.upper()

                # Language override: LANG=tr-TR, LANG=en-US, etc.
                if up.startswith("LANG="):
                    lang_value = stripped[5:]  # after 'LANG='
                    if lang_value:
                        language_code = lang_value
                        logger.info("Language overridden by client: %s", language_code)
                    continue

                # Codec override: CODEC=G711U / G711A / G729A / G.711U / G.729A ...
                if up.startswith("CODEC="):
                    codec_value = stripped[6:]  # after 'CODEC='
                    v = codec_value.strip().upper()

                    # G729A: accepted by IVR but STT not supported yet.
                    # We remember it and will "skip" STT at EOS.
                    if v in ("G729A", "G.729A"):
                        codec_name = "G729A"
                        logger.info(
                            "Codec overridden by client (G729A - STT will be skipped)"
                        )
                        continue

                    # For STT, we only accept G711U / G711A via normalize_codec_name
                    try:
                        new_codec = normalize_codec_name(codec_value)
                        codec_name = new_codec
                        logger.info("Codec overridden by client: %s", codec_name)
                    except ValueError as ce:
                        logger.error("Codec override error: %s", ce)
                        err = {"error": str(ce)}
                        await ws.send_text(json.dumps(err, separators=(",", ":")))
                        return

                    continue

                # End of stream: run (or skip) STT
                if up == "EOS":
                    logger.info(
                        "EOS received (total_bytes=%d, language=%s, codec=%s)",
                        total_bytes,
                        language_code,
                        codec_name,
                    )
                    
                    # DEBUG: dump audio to WAV for inspection (G711A example below)
                    #if codec_name == "G711A":
                    #    with wave.open("debug_g711a_linear16.wav", "wb") as wf:
                    #        wf.setnchannels(1)
                    #        wf.setsampwidth(2)   # 16-bit
                    #        wf.setframerate(8000)
                    #        wf.writeframes(bytes(audio_buffer))

                    # If codec is G729A, STT is not supported yet.
                    # We just skip recognition and return an empty final result.
                    if codec_name == "G729A":
                        logger.info("Skipping STT because codec=G729A (not supported yet)")
                        resp = {
                            "transcript": "",
                            "is_final": True,
                            "confidence": 0.0,
                        }
                        await ws.send_text(json.dumps(resp, separators=(",", ":")))
                        return

                    # For STT, we only accept G711U/G711A via normalize_codec_name
                    try:
                        normalized_codec = normalize_codec_name(codec_name)
                    except ValueError as ce:
                        logger.error("Codec validation error at EOS: %s", ce)
                        err = {"error": str(ce)}
                        await ws.send_text(json.dumps(err, separators=(",", ":")))
                        return

                    try:
                        transcript, conf = await recognize_google_g711(
                            bytes(audio_buffer),
                            codec=normalized_codec,
                            language_code=language_code,
                        )
                        logger.info(
                            "Google STT result: '%s' (confidence=%.3f)",
                            transcript,
                            conf,
                        )

                        resp = {
                            "transcript": transcript,
                            "is_final": True,
                            "confidence": float(conf),
                        }
                        await ws.send_text(json.dumps(resp, separators=(",", ":")))
                    except Exception as e:
                        logger.exception("Error during Google STT: %s", e)
                        err = {"error": str(e)}
                        await ws.send_text(json.dumps(err, separators=(",", ":")))

                    # After sending final result, we can exit handler
                    return

                # Any other text message: just log and continue
                continue

            # 3) Unexpected message
            logger.warning("Unknown WS message: %s", msg)

    except WebSocketDisconnect:
        logger.info(
            "STT stream disconnected by client. Total audio bytes = %d",
            total_bytes,
        )

    except RuntimeError as e:
        logger.info(
            "WS runtime close: %s (total bytes=%d)",
            str(e),
            total_bytes,
        )

    except Exception as e:
        logger.exception("Unexpected error in stt_stream: %s", e)
        try:
            err = {"error": str(e)}
            await ws.send_text(json.dumps(err, separators=(",", ":")))
        except Exception:
            # Ignore if already disconnected
            pass


# ----------------------------------------------------------------------
# Start server
# ----------------------------------------------------------------------
if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8089,
        reload=False,
        ws_per_message_deflate=False,
    )
