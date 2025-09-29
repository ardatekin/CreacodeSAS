import os
import subprocess
import time
from gtts import gTTS

# ----------------------
# Configuration
# ----------------------
SCRIPT_NAME = "say_numbers"

# Languages and numbers
NUMBERS = [str(n) for n in list(range(0, 100)) + list(range(100, 1001, 100))]

PROMPTS = {
    "english": ("en", NUMBERS),
    "german": ("de", NUMBERS),
    "french": ("fr", NUMBERS),
    "italian": ("it", NUMBERS),
    "turkish": ("tr", NUMBERS),
    "spanish": ("es", NUMBERS),
    "russian": ("ru", NUMBERS),
}

# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Full path to G.729 encoder
G729_ENCODER = os.path.join(os.path.dirname(BASE_DIR), "va_g729a_encoder.exe")


def ensure_dirs(lang_dir):
    """Create PCM, G711A, G711U, G729A directories."""
    for sub in ["PCM", "G711A", "G711U", "G729A"]:
        os.makedirs(os.path.join(lang_dir, sub), exist_ok=True)


def tts_with_retry(text, lang, mp3_file, retries=3, delay=2):
    """Generate TTS with retry logic in case of SSL/network errors."""
    for attempt in range(1, retries + 1):
        try:
            tts = gTTS(text=text, lang=lang, slow=False)
            tts.save(mp3_file)
            return True
        except Exception as e:
            print(f"   ⚠️ TTS failed (attempt {attempt}/{retries}): {e}")
            if attempt < retries:
                time.sleep(delay)
    return False


def generate_prompt(lang, code, numbers):
    """Generate all number prompts for a given language."""
    print(f"\n🔊 Generating {lang.title()} {SCRIPT_NAME} prompts...")

    lang_dir = os.path.join(BASE_DIR, lang)
    ensure_dirs(lang_dir)

    total = len(numbers)
    for idx, num in enumerate(numbers, start=1):
        filename = f"Say_{num}"
        tmp_mp3 = os.path.join(BASE_DIR, f"{filename}.mp3")
        pcm_wav = os.path.join(lang_dir, "PCM", filename + ".wav")
        pcm_final = os.path.join(lang_dir, "PCM", filename)
        g711u_wav = os.path.join(lang_dir, "G711U", filename + ".wav")
        g711u_final = os.path.join(lang_dir, "G711U", filename)
        g711a_wav = os.path.join(lang_dir, "G711A", filename + ".wav")
        g711a_final = os.path.join(lang_dir, "G711A", filename)
        g729_final = os.path.join(lang_dir, "G729A", filename)

        print(f"➡️ Generating {filename} ({idx}/{total}) in {lang}...")

        # 1. TTS MP3
        if not tts_with_retry(num, code, tmp_mp3):
            print(f"   ❌ Skipping {filename}, TTS failed after retries")
            continue

        # 2. MP3 → PCM
        os.system(f'ffmpeg -y -i "{tmp_mp3}" -ar 8000 -ac 1 -codec:a pcm_s16le "{pcm_wav}" >nul 2>&1')
        if os.path.exists(pcm_wav):
            os.replace(pcm_wav, pcm_final)

        # 3. PCM → G711 µ-law
        os.system(f'ffmpeg -y -i "{pcm_final}" -ar 8000 -ac 1 -codec:a pcm_mulaw "{g711u_wav}" >nul 2>&1')
        if os.path.exists(g711u_wav):
            os.replace(g711u_wav, g711u_final)

        # 4. PCM → G711 A-law
        os.system(f'ffmpeg -y -i "{pcm_final}" -ar 8000 -ac 1 -codec:a pcm_alaw "{g711a_wav}" >nul 2>&1')
        if os.path.exists(g711a_wav):
            os.replace(g711a_wav, g711a_final)

        # 5. PCM → G729A
        subprocess.run([G729_ENCODER, pcm_final, g729_final], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # Cleanup
        if os.path.exists(tmp_mp3):
            os.remove(tmp_mp3)

    print(f"🏁 {lang.title()} {SCRIPT_NAME} prompt generation complete")


def print_tree():
    """Print the resulting directory tree."""
    print("\n📂 Directory structure:")
    for root, dirs, files in os.walk(BASE_DIR):
        level = root.replace(BASE_DIR, "").count(os.sep)
        indent = " " * 4 * level
        print(f"{indent}{os.path.basename(root)}/")
        subindent = " " * 4 * (level + 1)
        for f in files:
            print(f"{subindent}{f}")


if __name__ == "__main__":
    for lang, (code, numbers) in PROMPTS.items():
        generate_prompt(lang, code, numbers)
    print_tree()
