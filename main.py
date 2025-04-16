# main.py
import torch
import whisper
from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import cv2
import numpy as np
from openai import OpenAI
from fastapi import FastAPI, File, UploadFile
import tempfile

# Initialize FastAPI app
app = FastAPI()

# Load models once
device = "cuda" if torch.cuda.is_available() else "cpu"
blip_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
blip_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base").to(device)
whisper_model = whisper.load_model("base")
client = OpenAI(api_key="your-open-api-key")#Enter your open api key here

# Core functions
def extract_frames(video_path, num_frames=5):
    cap = cv2.VideoCapture(video_path)
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    idxs = np.linspace(0, total - 1, num_frames, dtype=int)
    frames = []
    for idx in idxs:
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ret, frame = cap.read()
        if ret:
            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frames.append(Image.fromarray(img))
    cap.release()
    return frames

def generate_captions(frames):
    captions = []
    for img in frames:
        inputs = blip_processor(images=img, return_tensors="pt").to(device)
        output = blip_model.generate(**inputs)
        caption = blip_processor.decode(output[0], skip_special_tokens=True)
        captions.append(caption)
    return captions

def transcribe(video_path):
    return whisper_model.transcribe(video_path)['text']

def summarize(audio_text, visual_captions):
    prompt = f"""
You are an assistant summarizing educational videos. Focus on extracting key topics and notable quotes.

🎧 Audio Transcript:
{audio_text}

🖼️ Visual Captions:
{visual_captions}

Generate a concise summary.
"""
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip()

# API endpoint
@app.post("/summarize/")
async def summarize_video(file: UploadFile = File(...), num_frames: int = 5):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
        tmp.write(await file.read())
        video_path = tmp.name

    frames = extract_frames(video_path, num_frames)
    captions = generate_captions(frames)
    transcript = transcribe(video_path)
    final_summary = summarize(transcript, "\n".join(captions))

    return {
        "transcript": transcript,
        "captions": captions,
        "summary": final_summary
    }
