# backend/services/ruru/Dockerfile

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy necessary files
COPY main.py /app/main.py
COPY requirements.txt /app/requirements.txt

# Install requirements
RUN pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 8004

# Start FastAPI server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8004"]