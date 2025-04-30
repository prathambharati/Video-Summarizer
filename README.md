---
title: Summary
emoji: 📚
colorFrom: green
colorTo: blue
sdk: streamlit
sdk_version: 1.44.1
app_file: app.py
pinned: false
short_description: video summarizer
---

Check out the configuration reference at https://huggingface.co/docs/hub/spaces-config-reference

# 🎬 AI Video Summarizer

This project contains two key components for summarizing educational videos using AI:

1. `video.py` – A Streamlit-based frontend app for interactive summarization.
2. `main.py` – A FastAPI backend service that enables API-based summarization.

Both tools use **OpenAI Whisper** for transcription and **GPT-3.5** for summarization, with `video.py` adding extra visual context using **BLIP image captioning**.

---

## 📄 `video.py` – Streamlit UI (Frontend)

`video.py` is an interactive web app built with **Streamlit** that allows users to upload a video and receive a comprehensive summary powered by Whisper, BLIP, and GPT.

### 🔹 Features

- ✅ **Automatic FFmpeg setup** (downloads on first run if not present)
- 📥 Upload video files (`.mp4`, `.mov`, `.avi`)
- 📸 Extracts **key frames** from video using OpenCV
- 🖼️ Uses **BLIP** (Hugging Face) to generate image captions from selected frames
- 🎧 Uses **Whisper** to transcribe spoken content
- 🧠 Uses **OpenAI GPT-3.5** to generate an intelligent, audio-focused summary
- 🖥️ Displays:
  - Visual captions
  - Raw audio transcript
  - Final GPT-generated summary

🛠 How to Run

bash
streamlit run video.py 

### main.py – FastAPI API (Backend)

main.py is a FastAPI-based REST API that provides programmatic access to video summarization. Ideal for integrating into other apps, automations, or deployments like Hugging Face Spaces or Docker.

### 🔹 Features
📤 Accepts video files via POST /summarize/

✅ Automatically saves and validates uploaded video

⚙️ Runs FFmpeg to fix missing moov atom issues (with fallback re-encoding)

🎧 Transcribes audio using OpenAI Whisper

🧠 Summarizes transcription using OpenAI GPT-3.5

📄 Returns both transcript and summary in JSON format
