# Use the official Python image as a base
FROM python:3.10-slim

# Set working directory inside the container
WORKDIR /app

# Install system dependencies required by the app
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy only the requirements file first to optimize caching during image builds
COPY requirements.txt .

# Upgrade pip and install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy the rest of the application files into the container
COPY . .

# Expose the app's port (default FastAPI port is 8000)
EXPOSE 8000

# Command to run the FastAPI app using Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
