import os
import subprocess
from gtts import gTTS

# ----------------------
# Prompts in all languages
# ----------------------
PROMPTS = {
    "english": ("en", "Please enter your card’s expiration date as month and year, using four digits."),
    "german": ("de", "Bitte geben Sie das Ablaufdatum Ihrer Karte als Monat und Jahr in vier Ziffern ein."),
    "french": ("fr", "Veuillez entrer la date d'expiration de votre carte en mois et année, en utilisant quatre chiffres."),
    "italian": ("it", "Inserisci la data di scadenza della tua carta come mese e anno, usando quattro cifre."),
    "turkish": ("tr", "Lütfen kredi kartınızın son kullanma tarihini ay ve yıl olarak, dört hane şeklinde giriniz."),
    "spanish": ("es", "Por favor, introduzca la fecha de vencimiento de su tarjeta como mes y año, usando cuatro dígitos."),
    "russian": ("ru", "Пожалуйста, введите срок действия вашей карты месяц и год, используя четыре цифры."),
}

# Base directory of this script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Full path to G.729 encoder (1 level up from this script)
G729_ENCODER = os.path.join(os.path.dirname(BASE_DIR), "va_g729a_encoder.exe")


def ensure_dirs(lang_dir):
    for sub in ["PCM", "G711A", "G711U", "G729A"]:
        os.makedirs(os.path.join(lang_dir, sub), exist_ok=True)


def generate_prompt(lang, code, text):
    print(f"\n🔊 Generating {lang.title()} enter_cc_expire_date prompt...")

    lang_dir = os.path.join(BASE_DIR, lang)
    ensure_dirs(lang_dir)

    # Temp MP3 in script folder
    mp3_file = os.path.join(BASE_DIR, f"{lang}_tmp.mp3")

    # PCM output
    pcm_file = os.path.join(lang_dir, "PCM", "enter_cc_expire_date.wav")

    # Generate TTS
    tts = gTTS(text=text, lang=code, slow=False)
    tts.save(mp3_file)
    print(f"✅ TTS MP3 generated for {lang}: {text}")

    # Convert MP3 → PCM
    os.system(f'ffmpeg -y -i "{mp3_file}" -ar 8000 -ac 1 -codec:a pcm_s16le "{pcm_file}"')
    print(f"✅ PCM WAV generated: {pcm_file}")

    # Export G.711 µ-law
    g711u_file = os.path.join(lang_dir, "G711U", "enter_cc_expire_date.wav")
    os.system(f'ffmpeg -y -i "{pcm_file}" -ar 8000 -ac 1 -codec:a pcm_mulaw "{g711u_file}"')
    print(f"✅ G711U generated: {g711u_file}")

    # Export G.711 A-law
    g711a_file = os.path.join(lang_dir, "G711A", "enter_cc_expire_date.wav")
    os.system(f'ffmpeg -y -i "{pcm_file}" -ar 8000 -ac 1 -codec:a pcm_alaw "{g711a_file}"')
    print(f"✅ G711A generated: {g711a_file}")

    # Export G.729A
    g729_out = os.path.join(lang_dir, "G729A", "enter_cc_expire_date.wav")
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

    print(f"🏁 {lang.title()} enter_cc_expire_date prompt generation complete")


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
