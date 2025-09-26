# BUTLER System Deployment Guide

## Overview
BUTLER is an AI-powered assistant for the Texas Association of Counties that provides intelligent document-aware responses using Ollama LLM.

## System Components

### Core Files
- `butler-final.html` - Main web interface (User/Admin dual mode)
- `ollama_with_docs.py` - Document-aware API server (Port 5019)
- `simple_ollama_api.py` - Basic Ollama integration (Port 5018)
- `uploads/` - Directory containing county PDF documents

### Documents Included
- 2023 BYLAWS.pdf
- County Clerk Manual 2023 Edition
- TCCA Code of Ethics 2017
- TCCA Education Committee 2025 Policies

## Prerequisites

1. **Python 3.8+**
2. **Ollama** installed and running locally
3. **Llama 3.2 model** pulled in Ollama

## Installation Methods

### Method 1: Direct Installation (Recommended for Development)

1. **Clone/Copy the project folder** to your laptop

2. **Install Ollama**:
   ```bash
   # Windows (using WSL2 or native)
   curl -fsSL https://ollama.ai/install.sh | sh

   # macOS
   brew install ollama

   # Linux
   curl -fsSL https://ollama.ai/install.sh | sh
   ```

3. **Pull the Llama model**:
   ```bash
   ollama pull llama3.2:latest
   ```

4. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Start Ollama service**:
   ```bash
   ollama serve
   ```

6. **Run BUTLER API** (in a new terminal):
   ```bash
   python ollama_with_docs.py
   ```

7. **Open the interface**:
   - Open `butler-final.html` in a web browser
   - Or navigate to http://localhost:5019

### Method 2: Using Docker (Recommended for Production)

1. **Install Docker and Docker Compose**

2. **Build and run with Docker Compose**:
   ```bash
   docker-compose up -d
   ```

3. **Access BUTLER**:
   - Web Interface: http://localhost
   - API: http://localhost:5019

4. **Stop services**:
   ```bash
   docker-compose down
   ```

### Method 3: Using the Startup Script

1. **Windows** - Run `start-butler.bat`:
   ```batch
   @echo off
   echo Starting BUTLER System...
   start /B ollama serve
   timeout /t 5
   start /B python ollama_with_docs.py
   timeout /t 3
   start http://localhost:5019
   ```

2. **macOS/Linux** - Run `start-butler.sh`:
   ```bash
   #!/bin/bash
   echo "Starting BUTLER System..."
   ollama serve &
   sleep 5
   python ollama_with_docs.py &
   sleep 3
   open http://localhost:5019
   ```

## Configuration

### API Ports
- **5019**: Document-aware Ollama API (primary)
- **5018**: Simple Ollama API (backup)
- **11434**: Ollama service

### Environment Variables
Create a `.env` file if needed:
```
OLLAMA_URL=http://localhost:11434
MODEL=llama3.2:latest
API_PORT=5019
```

## Usage

### User Mode
1. Type questions about county procedures, bylaws, ethics
2. BUTLER searches documents and provides sourced answers
3. Click "Quick Help" for suggested queries

### Admin Mode
1. Toggle switch in upper right corner
2. Access system metrics and configuration
3. Monitor API connections and document status

## Troubleshooting

### Issue: "Ollama not connected"
**Solution**:
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Restart Ollama
ollama serve
```

### Issue: "Documents not loading"
**Solution**:
- Ensure PDF files are in the `uploads/` folder
- Check PyPDF2 is installed: `pip install PyPDF2`
- Restart the API server

### Issue: "Port already in use"
**Solution**:
```bash
# Find and kill process on port 5019
# Windows:
netstat -ano | findstr :5019
taskkill /PID <PID> /F

# Linux/Mac:
lsof -i :5019
kill -9 <PID>
```

## File Structure
```
BUTLER_NEW-main/
├── butler-final.html          # Main interface
├── ollama_with_docs.py       # Document-aware API
├── simple_ollama_api.py      # Basic API (backup)
├── requirements.txt          # Python dependencies
├── Dockerfile               # Container setup
├── docker-compose.yml       # Multi-container setup
├── uploads/                 # PDF documents
│   ├── 2023 BYLAWS.pdf
│   ├── county-clerk-manual-2023-edition.pdf
│   └── ...
├── TAOC.png                # Logo
└── TAOC.webp              # Logo (WebP format)
```

## Security Notes

- Default configuration is for local/development use
- For production, implement:
  - HTTPS/TLS encryption
  - Authentication middleware
  - Rate limiting
  - Input validation
  - Secure document storage

## Support

For issues or questions:
- Check the logs in the terminal
- Verify Ollama is running: `ollama list`
- Ensure all dependencies are installed
- Check firewall settings for ports 5019, 11434

## Quick Start Commands

```bash
# One-line setup (after installing prerequisites)
pip install -r requirements.txt && ollama pull llama3.2:latest && python ollama_with_docs.py

# Docker one-liner
docker-compose up -d && open http://localhost
```

## Backup and Migration

To migrate to another system:
1. Copy entire project folder
2. Include the `uploads/` directory with PDFs
3. Follow installation steps on new system
4. Verify Ollama model is available

---
**Version**: 1.0
**Last Updated**: January 2024
**System**: BUTLER - Texas Association of Counties AI Assistant