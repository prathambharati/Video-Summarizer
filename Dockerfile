# Use the official Python image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create a cache directory for Whisper
RUN mkdir -p /app/cache && chmod -R 777 /app/cache

# Set the cache directory environment variable
ENV WHISPER_CACHE_DIR=/app/cache

# Copy app files
COPY . .

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Hugging Face expects apps to run on port 7860
ENV PORT 7860

# Expose the app port
EXPOSE 7860

# Run the API with Uvicorn on port 7860
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
