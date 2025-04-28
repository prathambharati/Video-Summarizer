import os
import shutil
import tempfile
import subprocess
import logging
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from openai import OpenAI
import whisper

# === Detect Environment ===
def is_huggingface():
    return os.path.exists("/.dockerenv") and os.environ.get("HF_SPACE_ID") is not None

# Set FFmpeg path and Whisper cache directory based on environment
if is_huggingface():
    ffmpeg_cmd = "ffmpeg"
    os.environ["XDG_CACHE_HOME"] = "/tmp/.cache"
else:
    ffmpeg_cmd = r"C:\ffmpeg-2025-03-31-git-35c091f4b7-full_build\bin\ffmpeg.exe"
    os.environ["XDG_CACHE_HOME"] = "C:\\tmp\\.cache"

# === Logging ===
logging.basicConfig(level=logging.INFO)

# === Load environment variables ===
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    logging.error("OPENAI_API_KEY is missing in the environment!")
    raise RuntimeError("OPENAI_API_KEY not set in environment.")

# === Init clients ===
client = OpenAI(api_key=OPENAI_API_KEY)
whisper_model = whisper.load_model("base")
app = FastAPI()

# === File Saving ===
def save_upload_file_tmp(upload_file: UploadFile) -> str:
    try:
        tmp_dir = tempfile.mkdtemp()
        raw_path = os.path.join(tmp_dir, "raw.mp4")

        logging.info(f"Received file: {upload_file.filename}")
        logging.info(f"Content type: {upload_file.content_type}")

        upload_file.file.seek(0, os.SEEK_END)
        size = upload_file.file.tell()
        logging.info(f"Incoming file size (pre-save): {size} bytes")
        upload_file.file.seek(0)

        with open(raw_path, "wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)

        saved_size = os.path.getsize(raw_path)
        logging.info(f"Saved file at: {raw_path}, size: {saved_size} bytes")

        if not os.path.exists(raw_path) or saved_size == 0:
            raise RuntimeError("Saved file is empty")

        return raw_path
    except Exception as e:
        raise RuntimeError(f"Failed to save upload file: {e}")

# === FFmpeg Fix ===
def fix_moov_atom(input_path: str, output_path: str):
    try:
        cmd = [
            ffmpeg_cmd,
            "-y",
            "-i", input_path,
            "-c", "copy",
            "-movflags", "+faststart",
            output_path
        ]
        logging.info(f"Running FFmpeg command: {' '.join(cmd)}")
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        logging.info(result.stdout.decode("utf-8"))
    except subprocess.CalledProcessError as e:
        logging.error(f"FFmpeg error: {e.stderr.decode('utf-8')}")
        raise RuntimeError(f"FFmpeg failed: {e.stderr.decode('utf-8')}")

# === GPT Summary ===
def generate_summary(transcript: str) -> str:
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{
                "role": "system", 
                "content": "You are a helpful assistant that summarizes video transcripts."
            },
            {
                "role": "user", 
                "content": f"Summarize this transcript:\n{transcript}"
            }], temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error during GPT summarization:\n{str(e)}"

# === FastAPI Endpoint ===
@app.post("/summarize/")
async def summarize_video(file: UploadFile = File(...)):
    try:
        raw_path = save_upload_file_tmp(file)
        if not os.path.exists(raw_path) or os.path.getsize(raw_path) == 0:
            raise HTTPException(status_code=400, detail="Uploaded file is empty or invalid")

        fixed_path = os.path.join(os.path.dirname(raw_path), "fixed.mp4")
        fix_moov_atom(raw_path, fixed_path)

        logging.info("Transcription started.")
        result = whisper_model.transcribe(fixed_path)
        transcript = result["text"]
        logging.info("Transcription completed.")

        summary = generate_summary(transcript)

        return JSONResponse(content={"transcript": transcript, "summary": summary})

    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        logging.error(f"Error in /summarize/: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})
