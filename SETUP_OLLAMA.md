# BUTLER with Ollama Integration Setup Guide

## 🚀 Quick Start

BUTLER is now configured to use Ollama with Llama 3.2 as its intelligence engine. Follow these steps to get started:

## Prerequisites

1. **Python 3.7+** installed
2. **Ollama** installed and running locally
3. **Llama 3.2** model available in Ollama

## Step 1: Install Ollama

### Windows
1. Download Ollama from [https://ollama.ai](https://ollama.ai)
2. Run the installer
3. Ollama will start automatically

### macOS/Linux
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

## Step 2: Pull Llama 3.2 Model

Open a terminal/command prompt and run:
```bash
ollama pull llama3.2:latest
```

This will download the Llama 3.2 model (about 2GB).

## Step 3: Verify Ollama is Running

```bash
ollama list
```

You should see `llama3.2:latest` in the list.

## Step 4: Install Python Dependencies

Navigate to the BUTLER directory and run:
```bash
pip install -r requirements.txt
```

## Step 5: Configure Environment (Optional)

Copy the example environment file:
```bash
cp .env.example .env
```

Edit `.env` if you need to change any settings (default settings should work).

## Step 6: Start BUTLER

Run the startup script:
```bash
python start_butler.py
```

This script will:
1. Check Ollama connection
2. Verify the model is available
3. Test the model response
4. Start the BUTLER API server

## Step 7: Access BUTLER

Open your browser and navigate to:
```
http://localhost:5017
```

## 🎯 Testing the Integration

Once BUTLER is running, try these commands in the chat interface:

1. **System Status**: "Check system status"
2. **Email Analysis**: "What's the latest on the weather alert?"
3. **General Query**: "How can you help me with county operations?"

## 📝 Architecture

```
┌─────────────────┐
│   Browser UI    │
│  (butler-demo)  │
└────────┬────────┘
         │ HTTP
         ▼
┌─────────────────┐
│   Flask API     │
│  (api_server)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  BUTLER Core    │
│ (butler_core)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│     Ollama      │
│   Integration   │
└────────┬────────┘
         │ HTTP
         ▼
┌─────────────────┐
│  Ollama Server  │
│  (localhost)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Llama 3.2      │
│     Model       │
└─────────────────┘
```

## 🔧 Troubleshooting

### Ollama Not Connected
- Ensure Ollama is running: `ollama serve`
- Check if it's accessible: `curl http://localhost:11434/api/version`

### Model Not Found
- Pull the model: `ollama pull llama3.2:latest`
- List available models: `ollama list`

### API Server Issues
- Check if port 5017 is available
- Review logs in `butler_audit.log`
- If port 5017 is taken, edit `api_server.py` to use another port (5000-5020 range)

### Slow Responses
- Llama 3.2 requires decent hardware (8GB+ RAM recommended)
- Consider using a smaller model if needed: `ollama pull llama2:7b`

## 🛡️ Security Notes

- BUTLER is designed for **air-gapped** operation
- Ollama runs **locally** - no internet connection required
- All data stays on your machine
- Suitable for government/sensitive operations

## 📚 Advanced Configuration

### Using Different Models

Edit `.env` or `ollama_integration.py`:
```python
OLLAMA_MODEL=llama2:13b  # For more capable responses
OLLAMA_MODEL=mistral:7b  # For faster responses
```

### Adjusting Response Parameters

In `ollama_integration.py`, modify the options:
```python
"options": {
    "temperature": 0.7,  # Creativity (0.0-1.0)
    "top_p": 0.9,       # Nucleus sampling
    "num_predict": 2048  # Max tokens
}
```

## 🚨 Demo Mode

If Ollama is not available, BUTLER can run in demo mode with pre-configured responses. This is useful for testing the UI without AI capabilities.

## 📞 Support

For issues or questions:
1. Check the logs in `butler_audit.log`
2. Verify Ollama status: `ollama list`
3. Ensure all dependencies are installed: `pip install -r requirements.txt`

---

**Note**: BUTLER with Ollama provides true AI capabilities while maintaining complete data sovereignty - perfect for government operations requiring intelligent automation without cloud dependencies.