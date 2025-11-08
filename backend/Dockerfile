# Use official lightweight Python image
FROM python:3.13-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    LC_ALL=mi_NZ.UTF-8 \
    LANG=mi_NZ.UTF-8

# Install system packages needed by Pillow, OCR & PostgreSQL
RUN apt-get update && apt-get install -y \
    build-essential \
    libjpeg-dev \
    zlib1g-dev \
    libpng-dev \
    libfreetype6-dev \
    tesseract-ocr \
    locales \
    && locale-gen mi_NZ.UTF-8 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy backend files
COPY backend/requirements.txt .

# Install dependencies with upgraded pip, setuptools, wheel
RUN pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt

# Copy the rest of your code
COPY backend .

# Expose FastAPI port
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the app with auto-reload disabled for production
CMD ["uvicorn", "core.main:app", "--host", "0.0.0.0", "--port", "8000"]
