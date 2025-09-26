# BUTLER System Docker Container
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY *.py ./
COPY butler-final.html ./
COPY TAOC.png ./
COPY TAOC.webp ./

# Create uploads directory
RUN mkdir -p uploads

# Copy upload documents if they exist
COPY uploads/* uploads/ 2>/dev/null || :

# Environment variables
ENV FLASK_APP=ollama_with_docs.py
ENV PYTHONUNBUFFERED=1

# Expose ports
EXPOSE 5019

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5019/api/status || exit 1

# Start the application
CMD ["python", "ollama_with_docs.py"]