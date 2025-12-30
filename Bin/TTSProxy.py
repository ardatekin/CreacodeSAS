# ---------------------------------------------------------------------------
# Creacode SIP Application Server – Text-to-Speech (TTS) Proxy
#
# File       : TTSProxy.py
# Project    : CreacodeSAS
# Author     : Arda Tekin
#
# Overview:
# This module implements a standalone Text-to-Speech proxy service used by
# the Creacode SIP Application Server. Its primary purpose is to offload
# speech synthesis responsibilities from the core IVR engine and provide
# a clean, network-based TTS interface.
#
# Deployment & Runtime:
# - Deployed under C:\CreacodeSAS\Bin
# - Runs as a long-lived background process
# - Installed and managed as a Windows Service via NSSM
#   (service name: CreacodeSAS-TTSProxy)
# - Uses system-wide GOOGLE_APPLICATION_CREDENTIALS for cloud authentication
#
# Interfaces:
# - HTTP endpoint for TTS requests from the IVR layer
# - HTTP health endpoint for service monitoring
# - Listens on TCP port 8090
#
# Request / Response:
# - Receives text payloads (and optional language/voice parameters) over HTTP
# - Produces telephony-friendly audio output for IVR playback
#
# TTS Processing:
# - Integrates with Google Cloud Text-to-Speech
# - Generates 8 kHz LINEAR16 PCM output suitable for telephony pipelines
# - Designed to be robust against provider/API errors (returns clear HTTP
#   error responses rather than crashing the service)
#
# Operational Notes:
# - Designed to be restarted independently from the IVR core
# - Failures in this service do not crash the main CreacodeSAS process
#
# License    : See LICENSE.txt
# ---------------------------------------------------------------------------

#!/usr/bin/env python3
import logging

from fastapi import FastAPI, Response, HTTPException
from pydantic import BaseModel

import google.auth
from google.api_core import exceptions as gexc
from google.cloud import texttospeech

# ----------------------------------------------------------------------
# Logging
# ----------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("ivr-tts-proxy")

app = FastAPI(title="IVR TTS Proxy", version="1.0")

# ----------------------------------------------------------------------
# Log which ADC credentials/project we are using at startup
# ----------------------------------------------------------------------
try:
    _creds, _project = google.auth.default()
    logger.info("ADC project=%s, creds=%s", _project, type(_creds).__name__)
except Exception as e:
    logger.error("ADC lookup failed: %s", e)

# ----------------------------------------------------------------------
# Request model
# ----------------------------------------------------------------------
class TTSRequest(BaseModel):
    text: str
    lang: str = "en-US"


# ----------------------------------------------------------------------
# Health check
# ----------------------------------------------------------------------
@app.get("/health")
def health():
    return {"status": "ok"}


# ----------------------------------------------------------------------
# TTS endpoint
# ----------------------------------------------------------------------
@app.post("/tts")
def tts(req: TTSRequest):
    text = (req.text or "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="Empty text")

    logger.info("TTS request received, lang='%s', text='%s'", req.lang, text)

    try:
        client = texttospeech.TextToSpeechClient()

        synthesis_input = texttospeech.SynthesisInput(text=text)

        voice = texttospeech.VoiceSelectionParams(
            language_code=req.lang,
            ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL,
        )

        # We request 8 kHz LINEAR16 for telephony playback pipeline.
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.LINEAR16,
            sample_rate_hertz=8000,
        )

        resp = client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config,
        )

        pcm_data = resp.audio_content or b""
        logger.info("TTS generated %d bytes of PCM16 audio", len(pcm_data))

        if not pcm_data:
            raise HTTPException(status_code=502, detail="Google TTS returned empty audio")

        return Response(
            content=pcm_data,
            media_type="application/octet-stream",
        )

    except gexc.PermissionDenied as e:
        # Typical cases: API disabled, missing IAM permission, billing issues
        logger.exception("Google TTS PermissionDenied: %s", e)
        raise HTTPException(status_code=403, detail=str(e))

    except gexc.FailedPrecondition as e:
        logger.exception("Google TTS FailedPrecondition: %s", e)
        raise HTTPException(status_code=412, detail=str(e))

    except gexc.ServiceUnavailable as e:
        logger.exception("Google TTS ServiceUnavailable: %s", e)
        raise HTTPException(status_code=503, detail=str(e))

    except gexc.GoogleAPICallError as e:
        # Catch-all for Google API errors
        logger.exception("Google TTS GoogleAPICallError: %s", e)
        raise HTTPException(status_code=502, detail=str(e))

    except Exception as e:
        # Catch-all for unexpected bugs
        logger.exception("Unexpected error in /tts: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8090,
        reload=False,
    )
