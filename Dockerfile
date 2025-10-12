# ==============================
# Dockerfile for Hugging Face Spaces Deployment
# FastAPI backend (port 8000) + Streamlit frontend (port 7860)
# ==============================

# Base Python image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy all project files
COPY . /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose ports: 8000 (FastAPI) and 7860 (Streamlit)
EXPOSE 8000
EXPOSE 7860

# Start both backend (FastAPI) and frontend (Streamlit)
CMD bash -c "uvicorn backend.main:app --host 0.0.0.0 --port 8000 & streamlit run app.py --server.port 7860 --server.address 0.0.0.0"
