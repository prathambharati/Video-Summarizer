import os
import platform
import subprocess
import urllib.request
import zipfile
import shutil
import tempfile
import streamlit as st
st.set_page_config(page_title="Video Summarizer", layout="wide")
import torch
import openai
from openai import OpenAI
from PIL import Image
from torchvision import transforms
from transformers import BlipProcessor, BlipForConditionalGeneration
import whisper
import imageio_ffmpeg
import cv2
import numpy as np

api_key = "Enter your open ai api key"
client = OpenAI(api_key=api_key)


# 📥 Ensure FFmpeg
def ensure_ffmpeg():
    ffmpeg_dir = os.path.join(os.getcwd(), "ffmpeg")
    ffmpeg_bin = os.path.join(ffmpeg_dir, "bin", "ffmpeg.exe")
    if not os.path.isfile(ffmpeg_bin):
        print("📥 FFmpeg not found. Downloading...")
        ffmpeg_url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
        zip_path = os.path.join(os.getcwd(), "ffmpeg.zip")
        urllib.request.urlretrieve(ffmpeg_url, zip_path)
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall("ffmpeg_temp")
        for folder in os.listdir("ffmpeg_temp"):
            if folder.startswith("ffmpeg"):
                shutil.move(os.path.join("ffmpeg_temp", folder), ffmpeg_dir)
                break
        os.remove(zip_path)
        shutil.rmtree("ffmpeg_temp", ignore_errors=True)
    os.environ["PATH"] = os.path.join(ffmpeg_dir, "bin") + os.pathsep + os.environ["PATH"]
    print("✅ FFmpeg is ready!")

ensure_ffmpeg()

# 🔧 Setup
device = "cuda" if torch.cuda.is_available() else "cpu"

# 🚀 Load models (cached)
@st.cache_resource
def load_blip():
    processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
    model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base").to(device)
    return processor, model

@st.cache_resource
def load_whisper():
    return whisper.load_model("base")

blip_processor, blip_model = load_blip()
whisper_model = load_whisper()

# 📸 Extract key frames
def extract_frames(video_path, num_frames=5):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return []

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_indices = np.linspace(0, total_frames - 1, num_frames, dtype=int)
    selected_frames = []

    for idx in frame_indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ret, frame = cap.read()
        if ret:
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            selected_frames.append(Image.fromarray(image))

    cap.release()
    return selected_frames

# 🖼️ Generate BLIP captions
def generate_blip_captions(frames):
    captions = []
    for img in frames:
        inputs = blip_processor(images=img, return_tensors="pt").to(device)
        output = blip_model.generate(**inputs)
        caption = blip_processor.decode(output[0], skip_special_tokens=True)
        captions.append(caption)
    return captions

# 🎧 Whisper transcription
def transcribe_audio(video_path):
    result = whisper_model.transcribe(video_path)
    return result['text']

# 📊 Video metadata
def get_video_metadata(video_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return None, None, None
    duration = cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()
    return duration, width, height

# 🧠 GPT Summary
def generate_openai_summary(audio_summary, visual_summary):
    prompt = f"""
You are an assistant summarizing educational videos. Focus on extracting **key topics** and **notable quotes** from the spoken audio. Use visual information only for extra context, not as the primary source.

🎧 Audio Transcript:
{audio_summary}

🖼️ Visual Captions (for light context only):
{visual_summary}

Generate a concise, vivid, and informative summary of the video's content. Include any important statements or quotes that were spoken.
"""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that summarizes educational videos."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip()

# 🎬 Streamlit UI
def main():
    st.title("🎬 Video Summarizer (Whisper + BLIP + GPT)")

    uploaded_video = st.file_uploader("Upload a video", type=["mp4", "mov", "avi"])

    if uploaded_video:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
            tmp.write(uploaded_video.read())
            video_path = tmp.name

        st.video(video_path)

        # 📊 Show metadata
        duration, width, height = get_video_metadata(video_path)
        if duration:
            st.markdown(f"**📊 Video Duration**: {duration:.2f}s  \n"
                        f"**📐 Resolution**: {width} x {height}")

        # 🔢 Frame selection
        num_frames = st.slider("Select number of key frames to extract", 3, 10, 5)

        with st.spinner("📸 Extracting key frames..."):
            frames = extract_frames(video_path, num_frames)
            if not frames:
                st.error("❌ Could not extract frames from video.")
                return

            visual_summary = "\n".join(generate_blip_captions(frames))
            st.subheader("🖼️ Visual Captions")
            st.text(visual_summary)

        with st.spinner("🎧 Transcribing audio..."):
            audio_summary = transcribe_audio(video_path)
            st.subheader("🎧 Audio Transcript (Preview)")
            preview = audio_summary[:1000] + "..." if len(audio_summary) > 1000 else audio_summary
            st.text(preview)

            if st.checkbox("Show full transcript"):
                st.text(audio_summary)

        with st.spinner("🧠 Generating GPT Summary..."):
            final_summary = generate_openai_summary(audio_summary, visual_summary)
            st.markdown("### 📝 Final Summary")
            st.markdown(final_summary)

if __name__ == "__main__":
    main()
