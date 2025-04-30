# Use the official Python image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies (includes ffmpeg and git)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Create a writable cache directory for Whisper
RUN mkdir -p /app/cache && chmod -R 777 /app/cache

# Set environment variables
ENV XDG_CACHE_HOME=/app/cache
ENV PORT=7860

# Copy app files
COPY . .

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Expose the app port (Hugging Face expects 7860)
EXPOSE 7860

# Run the app with Uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
