import os
import subprocess
from gtts import gTTS

# ----------------------
# Prompts in all languages
# ----------------------
PROMPTS = {
    "english": ("en", "Invalid or incomplete entry."),
    "german": ("de", "Ungültige oder unvollständige Eingabe."),
    "french": ("fr", "Entrée invalide ou incomplète."),
    "italian": ("it", "Inserimento non valido o incompleto."),
    "turkish": ("tr", "Eksik veya hatalı giriş yaptınız."),
    "spanish": ("es", "Entrada no válida o incompleta."),
    "russian": ("ru", "Неверный или неполный ввод."),
}

# Base directory of this script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Full path to G.729 encoder (1 level up from this script)
G729_ENCODER = os.path.join(os.path.dirname(BASE_DIR), "va_g729a_encoder.exe")


def ensure_dirs(lang_dir):
    for sub in ["PCM", "G711A", "G711U", "G729A"]:
        os.makedirs(os.path.join(lang_dir, sub), exist_ok=True)


def generate_prompt(lang, code, text):
    print(f"\n🔊 Generating {lang.title()} invalid_entry prompt...")

    lang_dir = os.path.join(BASE_DIR, lang)
    ensure_dirs(lang_dir)

    # Temp MP3 in script folder
    mp3_file = os.path.join(BASE_DIR, f"{lang}_tmp.mp3")

    # PCM output
    pcm_file = os.path.join(lang_dir, "PCM", "invalid_entry.wav")

    # Generate TTS
    tts = gTTS(text=text, lang=code, slow=False)
    tts.save(mp3_file)
    print(f"✅ TTS MP3 generated for {lang}: {text}")

    # Convert MP3 → PCM
    os.system(f'ffmpeg -y -i "{mp3_file}" -ar 8000 -ac 1 -codec:a pcm_s16le "{pcm_file}"')
    print(f"✅ PCM WAV generated: {pcm_file}")

    # Export G.711 µ-law
    g711u_file = os.path.join(lang_dir, "G711U", "invalid_entry.wav")
    os.system(f'ffmpeg -y -i "{pcm_file}" -ar 8000 -ac 1 -codec:a pcm_mulaw "{g711u_file}"')
    print(f"✅ G711U generated: {g711u_file}")

    # Export G.711 A-law
    g711a_file = os.path.join(lang_dir, "G711A", "invalid_entry.wav")
    os.system(f'ffmpeg -y -i "{pcm_file}" -ar 8000 -ac 1 -codec:a pcm_alaw "{g711a_file}"')
    print(f"✅ G711A generated: {g711a_file}")

    # Export G.729A
    g729_out = os.path.join(lang_dir, "G729A", "invalid_entry.wav")
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

    print(f"🏁 {lang.title()} invalid_entry prompt generation complete")


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
