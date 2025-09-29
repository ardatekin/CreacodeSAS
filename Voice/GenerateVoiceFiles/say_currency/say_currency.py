import os
import subprocess
from gtts import gTTS

# ----------------------
# Configuration
# ----------------------
SCRIPT_NAME = "say_currency"

CURRENCIES = {
    "english": ("en", {
        "dollars": "dollars",
        "cents": "cents",
    }),
    "german": ("de", {
        "euros": "Euro",
        "cents": "Cent",
    }),
    "french": ("fr", {
        "euros": "euros",
        "cents": "centimes",
    }),
    "italian": ("it", {
        "euros": "euro",
        "cents": "centesimi",
    }),
    "turkish": ("tr", {
        "lira": "lira",
        "kurus": "kuruş",
    }),
    "spanish": ("es", {
        "euros": "euros",
        "cents": "céntimos",
    }),
    "russian": ("ru", {
        "rubles": "рублей",
        "kopeks": "копеек",
    }),
}

# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# G.729 encoder path
G729_ENCODER = os.path.join(os.path.dirname(BASE_DIR), "va_g729a_encoder.exe")


def ensure_dirs(lang_dir):
    """Create PCM, G711A, G711U, G729A subfolders."""
    for sub in ["PCM", "G711A", "G711U", "G729A"]:
        os.makedirs(os.path.join(lang_dir, sub), exist_ok=True)


def generate_prompt(lang, code, label, text):
    """Generate one currency prompt file in all codecs."""
    print(f"\n🔊 Generating {lang.title()} {label}.wav ...")


    lang_dir = os.path.join(BASE_DIR, lang)
    ensure_dirs(lang_dir)

    filename = f"{label}.wav"

    # Temp MP3
    mp3_file = os.path.join(BASE_DIR, f"{lang}_{label}_tmp.mp3")

    # PCM
    pcm_file = os.path.join(lang_dir, "PCM", filename)

    # TTS
    tts = gTTS(text=text, lang=code, slow=False)
    tts.save(mp3_file)
    print(f"✅ TTS MP3 generated for {label}: {text}")

    # MP3 → PCM
    os.system(f'ffmpeg -y -i "{mp3_file}" -ar 8000 -ac 1 -codec:a pcm_s16le "{pcm_file}"')
    print(f"✅ PCM generated: {pcm_file}")

    # PCM → G711U
    g711u_file = os.path.join(lang_dir, "G711U", filename)
    os.system(f'ffmpeg -y -i "{pcm_file}" -ar 8000 -ac 1 -codec:a pcm_mulaw "{g711u_file}"')

    # PCM → G711A
    g711a_file = os.path.join(lang_dir, "G711A", filename)
    os.system(f'ffmpeg -y -i "{pcm_file}" -ar 8000 -ac 1 -codec:a pcm_alaw "{g711a_file}"')

    # PCM → G729A
    g729_file = os.path.join(lang_dir, "G729A", filename)
    cmd = [G729_ENCODER, pcm_file, g729_file]
    subprocess.run(cmd)

    # Cleanup
    if os.path.exists(mp3_file):
        os.remove(mp3_file)


def print_tree():
    """Print resulting directory structure."""
    print("\n📂 Directory structure:")
    for root, dirs, files in os.walk(BASE_DIR):
        level = root.replace(BASE_DIR, "").count(os.sep)
        indent = " " * 4 * level
        print(f"{indent}{os.path.basename(root)}/")
        subindent = " " * 4 * (level + 1)
        for f in files:
            print(f"{subindent}{f}")


if __name__ == "__main__":
    for lang, (code, labels) in CURRENCIES.items():
        for label, text in labels.items():
            generate_prompt(lang, code, label, text)
    print_tree()
