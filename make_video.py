import os
import requests
from moviepy.editor import *
from datetime import datetime
from pydub import AudioSegment
import pytz

# === CONFIG ===
ELEVEN_API_KEY = os.getenv("ELEVEN_API_KEY")  # TTS nâng cấp
VOICE_ID = "EXAVITQu4vr4xnSDxMaL"  # Giọng mẫu (có thể thay)

BG_MUSIC_PATH = "assets/bg_music.mp3"
BG_IMAGE_PATH = "assets/background.jpg"
FPS = 24
WIDTH, HEIGHT = 1280, 720


def get_today_txt_file():
    vn_today = datetime.now(pytz.timezone("Asia/Ho_Chi_Minh")).strftime("%Y%m%d")
    return f"daily_summary_{vn_today}.txt"


def read_text_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read().strip().split("\n\n")


def tts_elevenlabs(text, out_path):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    headers = {
        "xi-api-key": ELEVEN_API_KEY,
        "Content-Type": "application/json"
    }
    body = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.4,
            "similarity_boost": 0.75
        }
    }
    r = requests.post(url, headers=headers, json=body)
    if r.status_code == 200:
        with open(out_path, "wb") as f:
            f.write(r.content)
        return out_path
    else:
        raise Exception("TTS API failed: " + r.text)


def mix_with_bg_music(voice_path, output_path):
    voice = AudioSegment.from_file(voice_path)
    music = AudioSegment.from_file(BG_MUSIC_PATH).apply_gain(-20)
    music = music[:len(voice)]  # cắt cùng độ dài

    final = voice.overlay(music)
    final.export(output_path, format="mp3")


def create_slide(text, audio_path):
    txt_clip = TextClip(text, fontsize=40, color='white', size=(WIDTH - 100, HEIGHT - 100), method='caption')
    txt_clip = txt_clip.set_position('center').set_duration(AudioFileClip(audio_path).duration)

    # ảnh nền minh hoạ
    bg = ImageClip(BG_IMAGE_PATH).set_duration(txt_clip.duration).resize((WIDTH, HEIGHT))

    return CompositeVideoClip([bg, txt_clip]).set_audio(AudioFileClip(audio_path))


def make_video_from_txt():
    txt_file = get_today_txt_file()
    if not os.path.exists(txt_file):
        print("⚠️ Không tìm thấy file .txt!")
        return

    print("🎬 Đang tạo video từ:", txt_file)
    sections = read_text_file(txt_file)

    clips = []
    for idx, section in enumerate(sections):
        if not section.strip():
            continue

        print(f"🔈 Đoạn {idx+1} → tạo voice và nhạc nền")

        raw_audio = f"voice_{idx}.mp3"
        final_audio = f"voice_final_{idx}.mp3"

        # Dùng ElevenLabs để tạo giọng đọc cao cấp
        tts_elevenlabs(section, raw_audio)

        # Mix nhạc nền nhẹ vào giọng đọc
        mix_with_bg_music(raw_audio, final_audio)

        print(f"🎞 Đoạn {idx+1} → tạo slide video")
        clip = create_slide(section, final_audio)
        clips.append(clip)

    final = concatenate_videoclips(clips, method="compose")
    out_file = f"video_{datetime.now().strftime('%Y%m%d_%H%M')}.mp4"
    final.write_videofile(out_file, fps=FPS)

    print(f"✅ Video đã tạo: {out_file}")


if __name__ == "__main__":
    make_video_from_txt()
