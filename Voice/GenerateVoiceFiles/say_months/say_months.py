import os
import subprocess
from gtts import gTTS

# ----------------------
# Configuration
# ----------------------
SCRIPT_NAME = "say_months"

MONTHS = [
    ("january", {
        "english": ("en", "January"),
        "german": ("de", "Januar"),
        "french": ("fr", "janvier"),
        "italian": ("it", "gennaio"),
        "turkish": ("tr", "Ocak"),
        "spanish": ("es", "enero"),
        "russian": ("ru", "январь"),
    }),
    ("february", {
        "english": ("en", "February"),
        "german": ("de", "Februar"),
        "french": ("fr", "février"),
        "italian": ("it", "febbraio"),
        "turkish": ("tr", "Şubat"),
        "spanish": ("es", "febrero"),
        "russian": ("ru", "февраль"),
    }),
    ("march", {
        "english": ("en", "March"),
        "german": ("de", "März"),
        "french": ("fr", "mars"),
        "italian": ("it", "marzo"),
        "turkish": ("tr", "Mart"),
        "spanish": ("es", "marzo"),
        "russian": ("ru", "март"),
    }),
    ("april", {
        "english": ("en", "April"),
        "german": ("de", "April"),
        "french": ("fr", "avril"),
        "italian": ("it", "aprile"),
        "turkish": ("tr", "Nisan"),
        "spanish": ("es", "abril"),
        "russian": ("ru", "апрель"),
    }),
    ("may", {
        "english": ("en", "May"),
        "german": ("de", "Mai"),
        "french": ("fr", "mai"),
        "italian": ("it", "maggio"),
        "turkish": ("tr", "Mayıs"),
        "spanish": ("es", "mayo"),
        "russian": ("ru", "май"),
    }),
    ("june", {
        "english": ("en", "June"),
        "german": ("de", "Juni"),
        "french": ("fr", "juin"),
        "italian": ("it", "giugno"),
        "turkish": ("tr", "Haziran"),
        "spanish": ("es", "junio"),
        "russian": ("ru", "июнь"),
    }),
    ("july", {
        "english": ("en", "July"),
        "german": ("de", "Juli"),
        "french": ("fr", "juillet"),
        "italian": ("it", "luglio"),
        "turkish": ("tr", "Temmuz"),
        "spanish": ("es", "julio"),
        "russian": ("ru", "июль"),
    }),
    ("august", {
        "english": ("en", "August"),
        "german": ("de", "August"),
        "french": ("fr", "août"),
        "italian": ("it", "agosto"),
        "turkish": ("tr", "Ağustos"),
        "spanish": ("es", "agosto"),
        "russian": ("ru", "август"),
    }),
    ("september", {
        "english": ("en", "September"),
        "german": ("de", "September"),
        "french": ("fr", "septembre"),
        "italian": ("it", "settembre"),
        "turkish": ("tr", "Eylül"),
        "spanish": ("es", "septiembre"),
        "russian": ("ru", "сентябрь"),
    }),
    ("october", {
        "english": ("en", "October"),
        "german": ("de", "Oktober"),
        "french": ("fr", "octobre"),
        "italian": ("it", "ottobre"),
        "turkish": ("tr", "Ekim"),
        "spanish": ("es", "octubre"),
        "russian": ("ru", "октябрь"),
    }),
    ("november", {
        "english": ("en", "November"),
        "german": ("de", "November"),
        "french": ("fr", "novembre"),
        "italian": ("it", "novembre"),
        "turkish": ("tr", "Kasım"),
        "spanish": ("es", "noviembre"),
        "russian": ("ru", "ноябрь"),
    }),
    ("december", {
        "english": ("en", "December"),
        "german": ("de", "Dezember"),
        "french": ("fr", "décembre"),
        "italian": ("it", "dicembre"),
        "turkish": ("tr", "Aralık"),
        "spanish": ("es", "diciembre"),
        "russian": ("ru", "декабрь"),
    }),
]

# Base directory of this script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Full path to G.729 encoder (one level up from scripts)
G729_ENCODER = os.path.join(os.path.dirname(BASE_DIR), "va_g729a_encoder.exe")


def ensure_dirs(lang_dir):
    for sub in ["PCM", "G711A", "G711U", "G729A"]:
        os.makedirs(os.path.join(lang_dir, sub), exist_ok=True)


def generate_prompt(lang, code, text, filename):
    print(f"\n🔊 Generating {lang.title()} month prompt: {filename}")

    lang_dir = os.path.join(BASE_DIR, lang)
    ensure_dirs(lang_dir)

    mp3_file = os.path.join(BASE_DIR, f"{lang}_{filename}_tmp.mp3")
    pcm_file = os.path.join(lang_dir, "PCM", f"{filename}.wav")

    tts = gTTS(text=text, lang=code, slow=False)
    tts.save(mp3_file)
    print(f"✅ TTS MP3 generated for {lang}: {text}")

    os.system(f'ffmpeg -y -i "{mp3_file}" -ar 8000 -ac 1 -codec:a pcm_s16le "{pcm_file}"')
    print(f"✅ PCM WAV generated: {pcm_file}")

    g711u_file = os.path.join(lang_dir, "G711U", f"{filename}.wav")
    os.system(f'ffmpeg -y -i "{pcm_file}" -ar 8000 -ac 1 -codec:a pcm_mulaw "{g711u_file}"')
    print(f"✅ G711U generated: {g711u_file}")

    g711a_file = os.path.join(lang_dir, "G711A", f"{filename}.wav")
    os.system(f'ffmpeg -y -i "{pcm_file}" -ar 8000 -ac 1 -codec:a pcm_alaw "{g711a_file}"')
    print(f"✅ G711A generated: {g711a_file}")

    g729_out = os.path.join(lang_dir, "G729A", f"{filename}.wav")
    cmd = [G729_ENCODER, pcm_file, g729_out]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0 and os.path.exists(g729_out):
        print(f"✅ G729A generated: {g729_out}")
    else:
        print(f"❌ G729A not created for {lang}, exit code {result.returncode}")

    if os.path.exists(mp3_file):
        os.remove(mp3_file)
        print("🧹 Temp MP3 cleaned up")

    print(f"🏁 {lang.title()} month {filename} generation complete")


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
    for filename, langs in MONTHS:
        for lang, (code, text) in langs.items():
            generate_prompt(lang, code, text, filename)
    print_tree()
