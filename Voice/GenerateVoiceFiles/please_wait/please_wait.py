import os
import subprocess
from gtts import gTTS

# ----------------------
# Configuration
# ----------------------
SCRIPT_NAME = "please_wait"

PROMPTS = {
    "english": ("en", "Please wait."),
    "german": ("de", "Bitte warten Sie."),
    "french": ("fr", "Veuillez patienter."),
    "italian": ("it", "Attendere prego."),
    "turkish": ("tr", "Lütfen bekleyin."),
    "spanish": ("es", "Por favor espere."),
    "russian": ("ru", "Пожалуйста, подождите."),
}

# Base directory of this script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Full path to G.729 encoder (one level up from scripts)
G729_ENCODER = os.path.join(os.path.dirname(BASE_DIR), "va_g729a_encoder.exe")


def ensure_dirs(lang_dir):
    """Create codec subfolders (PCM, G711A, G711U, G729A) under each language directory."""
    for sub in ["PCM", "G711A", "G711U", "G729A"]:
        os.makedirs(os.path.join(lang_dir, sub), exist_ok=True)


def generate_prompt(lang, code, text):
    """Generate TTS and convert into PCM, G711A, G711U, G729A formats."""
    print(f"\n🔊 Generating {lang.title()} {SCRIPT_NAME} prompt...")

    lang_dir = os.path.join(BASE_DIR, lang)
    ensure_dirs(lang_dir)

    # Temporary MP3 in script folder
    mp3_file = os.path.join(BASE_DIR, f"{lang}_tmp.mp3")

    # PCM output file
    pcm_file = os.path.join(lang_dir, "PCM", f"{SCRIPT_NAME}.wav")

    # Generate TTS with gTTS
    tts = gTTS(text=text, lang=code, slow=False)
    tts.save(mp3_file)
    print(f"✅ TTS MP3 generated for {lang}: {text}")

    # Convert MP3 → PCM (8kHz mono)
    os.system(f'ffmpeg -y -i "{mp3_file}" -ar 8000 -ac 1 -codec:a pcm_s16le "{pcm_file}"')
    print(f"✅ PCM WAV generated: {pcm_file}")

    # Convert PCM → G711 µ-law
    g711u_file = os.path.join(lang_dir, "G711U", f"{SCRIPT_NAME}.wav")
    os.system(f'ffmpeg -y -i "{pcm_file}" -ar 8000 -ac 1 -codec:a pcm_mulaw "{g711u_file}"')
    print(f"✅ G711U generated: {g711u_file}")

    # Convert PCM → G711 A-law
    g711a_file = os.path.join(lang_dir, "G711A", f"{SCRIPT_NAME}.wav")
    os.system(f'ffmpeg -y -i "{pcm_file}" -ar 8000 -ac 1 -codec:a pcm_alaw "{g711a_file}"')
    print(f"✅ G711A generated: {g711a_file}")

    # Convert PCM → G729A (using external encoder)
    g729_out = os.path.join(lang_dir, "G729A", f"{SCRIPT_NAME}.wav")
    cmd = [G729_ENCODER, pcm_file, g729_out]
    print(f"⚙️ Running encoder command: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0 and os.path.exists(g729_out):
        print(f"✅ G729A generated: {g729_out}")
    else:
        print(f"❌ G729A not created for {lang}, exit code {result.returncode}")

    # Cleanup temp MP3
    if os.path.exists(mp3_file):
        os.remove(mp3_file)
        print("🧹 Temp MP3 cleaned up")

    print(f"🏁 {lang.title()} {SCRIPT_NAME} prompt generation complete")


def print_tree():
    """Print directory structure for verification."""
    print("\n📂 Directory structure:")
    for root, dirs, files in os.walk(BASE_DIR):
        level = root.replace(BASE_DIR, "").count(os.sep)
        indent = " " * 4 * level
        print(f"{indent}{os.path.basename(root)}/")
        subindent = " " * 4 * (level + 1)
        for f in files:
            print(f"{subindent}{f}")


if __name__ == "__main__":
    for lang, (code, text) in PROMPTS.items():
        generate_prompt(lang, code, text)
    print_tree()
