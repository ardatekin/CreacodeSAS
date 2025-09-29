import os
import subprocess
from gtts import gTTS

# ----------------------
# Configuration
# ----------------------
PROMPTS = {
    "english": ("en", "Welcome to Creacode."),
    "german": ("de", "Willkommen bei Creacode."),
    "french": ("fr", "Bienvenue chez Creacode."),
    "italian": ("it", "Benvenuti su Creacode."),
    "turkish": ("tr", "Creacode'a hoş geldiniz."),
    "spanish": ("es", "Bienvenido a Creacode."),
    "russian": ("ru", "Добро пожаловать в Creacode."),
}

# Base directory of this script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# G.729 encoder is one level up from script directory
G729_ENCODER = os.path.join(os.path.dirname(BASE_DIR), "va_g729a_encoder.exe")

def ensure_dirs(lang_dir):
    for sub in ["PCM", "G711A", "G711U", "G729A"]:
        os.makedirs(os.path.join(lang_dir, sub), exist_ok=True)

def generate_prompt(lang, code, text):
    print(f"\n🔊 Generating {lang.title()} prompt...")

    lang_dir = os.path.join(BASE_DIR, lang)
    ensure_dirs(lang_dir)

    # Temp MP3 in script folder
    mp3_file = os.path.join(BASE_DIR, f"{lang}_tmp.mp3")

    # PCM output (always .wav)
    pcm_file = os.path.join(lang_dir, "PCM", "welcome.wav")

    # Generate TTS
    tts = gTTS(text=text, lang=code, slow=False)
    tts.save(mp3_file)
    print(f"✅ TTS MP3 generated: {text}")

    # Convert MP3 → PCM
    os.system(f'ffmpeg -y -i "{mp3_file}" -ar 8000 -ac 1 -codec:a pcm_s16le "{pcm_file}"')
    print(f"✅ PCM WAV generated: {pcm_file}")

    # Export to G.711 µ-law
    g711u_file = os.path.join(lang_dir, "G711U", "welcome.wav")
    os.system(f'ffmpeg -y -i "{pcm_file}" -ar 8000 -ac 1 -codec:a pcm_mulaw "{g711u_file}"')
    print(f"✅ G711U generated: {g711u_file}")

    # Export to G.711 A-law
    g711a_file = os.path.join(lang_dir, "G711A", "welcome.wav")
    os.system(f'ffmpeg -y -i "{pcm_file}" -ar 8000 -ac 1 -codec:a pcm_alaw "{g711a_file}"')
    print(f"✅ G711A generated: {g711a_file}")

    # Export to G.729a (named welcome.wav for consistency)
    g729_out = os.path.join(lang_dir, "G729A", "welcome.wav")
    cmd = [G729_ENCODER, pcm_file, g729_out]
    print(f"⚙️ Running encoder command:\n{' '.join(cmd)}")

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.stdout: print("➡️ Encoder stdout:", result.stdout.strip())
    if result.stderr: print("➡️ Encoder stderr:", result.stderr.strip())

    if result.returncode == 0 and os.path.exists(g729_out):
        print(f"✅ G729A generated: {g729_out}")
    else:
        print(f"❌ G729A not created, exit code {result.returncode}")

    # Cleanup temp MP3
    if os.path.exists(mp3_file):
        os.remove(mp3_file)
        print("🧹 Temp MP3 cleaned up")

    print(f"🏁 {lang.title()} prompt generation complete")


def print_tree():
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
