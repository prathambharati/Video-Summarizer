## 🧠 Video Summarizer App (Whisper + BLIP + GPT)

This is a **Streamlit-based web application** that generates **concise, story-like summaries** of videos by combining **audio transcription** and **visual captioning**. It uses OpenAI's Whisper for audio, Salesforce BLIP for image captioning, and GPT-3.5 for final summarization.

### 🚀 Features
- 📥 Upload and preview videos directly in the browser.
- 🖼️ Extracts key frames and generates contextual captions using **BLIP**.
- 🎧 Transcribes spoken audio using **Whisper ASR**.
- 🧠 Generates insightful summaries using **GPT-3.5**, with a focus on audio content.
- ⚡ Powered by **FFmpeg** (auto-downloaded if not available) for efficient video handling.

### 💡 Use Cases
- Summarize **educational lectures**, **YouTube Shorts**, or **seminars**.
- Quickly understand long videos without watching them in full.
- Capture **notable quotes** and **main themes** from spoken content.

### 🛠️ Tech Stack
- **Python**, **Streamlit**
- [OpenAI Whisper](https://github.com/openai/whisper)
- [Salesforce BLIP](https://huggingface.co/Salesforce/blip-image-captioning-base)
- **OpenAI GPT-3.5** for natural language summarization
- **FFmpeg** via `imageio-ffmpeg` for extracting frames


```

