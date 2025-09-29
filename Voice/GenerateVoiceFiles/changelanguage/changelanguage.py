import os
import subprocess
from gtts import gTTS

# ----------------------
# Configuration
# ----------------------
PROMPTS = [
    ("de", "Drücken Sie die Eins für Deutsch."),        # German
    ("fr", "Appuyez sur deux pour le français."),       # French
    ("it", "Premere tre per italiano."),                # Italian
    ("es", "Presione cuatro para español."),            # Spanish
    ("ru", "Нажмите пять для русского."),               # Russian
    ("tr", "Türkçe için altıya basın."),                # Turkish
    ("en", "Please wait to continue in English."),      # English
]

# Languages we want to mirror directories for
LANGUAGES = ["english", "german", "french", "italian", "spanish", "russian", "turkish"]

# Script folder
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# G.729 encoder path (1 level up)
G729_ENCODER = os.path.join(os.path.dirname(BASE_DIR), "va_g729a_encoder.exe")


def concat_mp3s(mp3_files, out_file):
    list_file = os.path.join(BASE_DIR, "file_list.txt")
    with open(list_file, "w", encoding="utf-8") as f:
        for mp3 in mp3_files:
            f.write(f"file '{mp3}'\n")

    os.system(f'ffmpeg -y -f concat -safe 0 -i "{list_file}" -c copy "{out_file}"')
    os.remove(list_file)


def generate_changelanguage():
    print("\n🔊 Generating multilanguage changelanguage prompt...")

    mp3_segments = []
    # Generate individual segments
    for idx, (lang, text) in enumerate(PROMPTS, start=1):
        seg_file = os.path.join(BASE_DIR, f"seg_{idx}.mp3")
        tts = gTTS(text=text, lang=lang, slow=False)
        tts.save(seg_file)
        mp3_segments.append(seg_file)
        print(f"✅ Segment {idx} created: [{lang}] {text}")

    # Concatenate into one MP3
    combined_mp3 = os.path.join(BASE_DIR, "changelanguage_tmp.mp3")
    concat_mp3s(mp3_segments, combined_mp3)
    print(f"✅ Combined MP3 created: {combined_mp3}")

    # Remove segment MP3s
    for seg in mp3_segments:
        if os.path.exists(seg):
            os.remove(seg)

    # Reference PCM file (temporary in base dir)
    ref_pcm = os.path.join(BASE_DIR, "changelanguage_ref.wav")
    os.system(f'ffmpeg -y -i "{combined_mp3}" -ar 8000 -ac 1 -codec:a pcm_s16le "{ref_pcm}"')
    print(f"✅ Reference PCM generated: {ref_pcm}")

    # Now copy into each language folder
    for lang in LANGUAGES:
        lang_dir = os.path.join(BASE_DIR, lang)
        for sub in ["PCM", "G711A", "G711U", "G729A"]:
            os.makedirs(os.path.join(lang_dir, sub), exist_ok=True)

        pcm_file = os.path.join(lang_dir, "PCM", "changelanguage.wav")
        g711u_file = os.path.join(lang_dir, "G711U", "changelanguage.wav")
        g711a_file = os.path.join(lang_dir, "G711A", "changelanguage.wav")
        g729_file = os.path.join(lang_dir, "G729A", "changelanguage.wav")

        # Copy PCM reference
        os.system(f'ffmpeg -y -i "{ref_pcm}" -ar 8000 -ac 1 -codec:a pcm_s16le "{pcm_file}"')
        print(f"✅ {lang}: PCM ready")

        # Export G.711 µ-law
        os.system(f'ffmpeg -y -i "{pcm_file}" -ar 8000 -ac 1 -codec:a pcm_mulaw "{g711u_file}"')
        print(f"✅ {lang}: G711U ready")

        # Export G.711 A-law
        os.system(f'ffmpeg -y -i "{pcm_file}" -ar 8000 -ac 1 -codec:a pcm_alaw "{g711a_file}"')
        print(f"✅ {lang}: G711A ready")

        # Export G.729A
        cmd = [G729_ENCODER, pcm_file, g729_file]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0 and os.path.exists(g729_file):
            print(f"✅ {lang}: G729A ready")
        else:
            print(f"❌ {lang}: G729A failed (code {result.returncode})")

    # Cleanup
    if os.path.exists(combined_mp3):
        os.remove(combined_mp3)
    if os.path.exists(ref_pcm):
        os.remove(ref_pcm)

    print("🏁 Changelanguage prompt generation complete")

    # Print directory tree
    print("\n📂 Directory structure:")
    for root, dirs, files in os.walk(BASE_DIR):
        level = root.replace(BASE_DIR, "").count(os.sep)
        indent = " " * 4 * level
        print(f"{indent}{os.path.basename(root)}/")
        subindent = " " * 4 * (level + 1)
        for f in files:
            print(f"{subindent}{f}")


if __name__ == "__main__":
    generate_changelanguage()
