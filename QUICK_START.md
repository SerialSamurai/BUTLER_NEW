# BUTLER Quick Start Guide

## Fastest Setup (5 minutes)

### Prerequisites
1. Install Python 3.8+: https://python.org
2. Install Ollama: https://ollama.ai

### Windows Quick Start
```batch
# 1. Install dependencies
pip install Flask Flask-CORS requests PyPDF2

# 2. Start Ollama (in new terminal)
ollama serve

# 3. Pull the AI model (one-time, may take 5-10 minutes)
ollama pull llama3.2:latest

# 4. Run BUTLER
python ollama_with_docs.py

# 5. Open browser to http://localhost:5019
```

**OR just double-click `start-butler.bat`**

### macOS/Linux Quick Start
```bash
# 1. Install dependencies
pip3 install Flask Flask-CORS requests PyPDF2

# 2. Start Ollama (in new terminal)
ollama serve

# 3. Pull the AI model (one-time)
ollama pull llama3.2:latest

# 4. Run BUTLER
python3 ollama_with_docs.py

# 5. Open browser to http://localhost:5019
```

**OR run `./start-butler.sh`**

## Essential Files Only

If you want minimal setup, you only need:
- `ollama_with_docs.py` - The API server
- `butler-final.html` - The web interface
- `uploads/` folder with PDF documents
- `TAOC.png` - Logo file

## Test It's Working

1. Open http://localhost:5019 in your browser
2. Type: "What are the bylaws about board meetings?"
3. You should get a response citing the uploaded documents

## Troubleshooting

**"Connection refused" error:**
- Make sure Ollama is running: `ollama serve`

**"Model not found" error:**
- Pull the model: `ollama pull llama3.2:latest`

**"No documents loaded" message:**
- Check the `uploads/` folder has PDF files

## For Demo/Presentation

Best questions to showcase BUTLER:
- "What does the code of ethics say about conflicts of interest?"
- "What are the education requirements for county clerks?"
- "How are board meetings conducted according to the bylaws?"
- "What are the procedures for handling public records requests?"

---
**That's it! BUTLER should be running in under 5 minutes.**