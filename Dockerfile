#  Official lightweight Python 🐍 image
FROM python:3.11-slim

# 🧰 Install required system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    tesseract-ocr \
    libgl1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 📁 Set the working directory
WORKDIR /app

# 🔁 Copy only requirements first for efficient caching
COPY requirements.txt /app/

# ⚙️ Install Python dependencies
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# 📦 Copy the entire project
COPY . /app

# 🌐 Expose the FastAPI port
EXPOSE 10000

# 🚀 Run the FastAPI app using uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
