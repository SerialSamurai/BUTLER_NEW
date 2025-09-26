"""
Simple Ollama API for BUTLER - Direct integration without complex async issues
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json
import logging

app = Flask(__name__)
CORS(app)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('BUTLER_OLLAMA')

OLLAMA_URL = "http://localhost:11434"
MODEL = "llama3.2:latest"

# System prompts for different contexts
SYSTEM_PROMPTS = {
    "general": """You are BUTLER, an AI assistant for the Texas Association of Counties.
    You help with county operations, permits, fines, taxes, and general administrative tasks.
    Be helpful, specific, and provide actionable information for Texas county residents and officials.""",

    "admin": """You are BUTLER, an advanced AI system administrator assistant.
    You have access to neural network configurations, API integrations, and system monitoring.
    Provide technical, detailed responses about system operations and configurations.""",

    "legal": """You are BUTLER, specializing in Texas county legal matters.
    Provide information about fines, permits, court procedures, and county regulations.
    Always remind users to verify information with official sources.""",

    "tax": """You are BUTLER, focusing on Texas county tax and property matters.
    Help with property tax information, assessments, payment procedures, and deadlines."""
}

@app.route('/api/status', methods=['GET'])
def status():
    """Check if Ollama is running"""
    try:
        response = requests.get(f"{OLLAMA_URL}/api/tags")
        models = response.json()
        return jsonify({
            "status": "online",
            "ollama": "connected",
            "model": MODEL,
            "available_models": [m['name'] for m in models.get('models', [])]
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    """Process chat messages with Ollama"""
    try:
        data = request.json
        user_message = data.get('message', '')
        context_type = data.get('context_type', 'general')

        # Get appropriate system prompt
        system_prompt = SYSTEM_PROMPTS.get(context_type, SYSTEM_PROMPTS['general'])

        # Build the full prompt
        full_prompt = f"{system_prompt}\n\nUser: {user_message}\n\nBUTLER:"

        # Query Ollama
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": MODEL,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                }
            },
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            ai_response = result.get('response', 'No response generated')

            logger.info(f"Query: {user_message[:50]}... Response: {ai_response[:50]}...")

            return jsonify({
                "success": True,
                "response": ai_response,
                "model": MODEL,
                "context": context_type
            })
        else:
            return jsonify({
                "success": False,
                "response": "Error communicating with Ollama",
                "error": response.text
            }), 500

    except requests.exceptions.Timeout:
        return jsonify({
            "success": False,
            "response": "Request timed out. Please try again."
        }), 504
    except Exception as e:
        logger.error(f"Chat error: {e}")
        return jsonify({
            "success": False,
            "response": f"Error: {str(e)}"
        }), 500

@app.route('/api/analyze', methods=['POST'])
def analyze():
    """Analyze specific content (emails, documents, etc.)"""
    try:
        data = request.json
        content = data.get('content', '')
        analysis_type = data.get('type', 'general')

        prompts = {
            "email": f"Analyze this email and provide: category, priority, summary, and suggested action:\n\n{content}",
            "document": f"Analyze this document and provide: type, key points, and compliance status:\n\n{content}",
            "fine": f"Analyze this fine/citation and provide: amount, due date, payment options, and consequences:\n\n{content}"
        }

        prompt = prompts.get(analysis_type, f"Analyze the following:\n\n{content}")

        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": MODEL,
                "prompt": f"You are BUTLER, a government AI assistant. {prompt}",
                "stream": False
            },
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            return jsonify({
                "success": True,
                "analysis": result.get('response', 'No analysis generated'),
                "type": analysis_type
            })
        else:
            return jsonify({
                "success": False,
                "error": "Analysis failed"
            }), 500

    except Exception as e:
        logger.error(f"Analysis error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/complete', methods=['POST'])
def complete():
    """Auto-complete functionality for forms and searches"""
    try:
        data = request.json
        partial_text = data.get('text', '')
        context = data.get('context', 'general')

        prompt = f"""Complete this text for a Texas county government context:
        Context: {context}
        Partial text: {partial_text}

        Provide a natural completion:"""

        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.5,
                    "max_tokens": 50
                }
            },
            timeout=10
        )

        if response.status_code == 200:
            result = response.json()
            completion = result.get('response', '').strip()
            return jsonify({
                "success": True,
                "completion": partial_text + " " + completion,
                "suggestion": completion
            })
        else:
            return jsonify({
                "success": False,
                "completion": partial_text
            }), 500

    except Exception as e:
        return jsonify({
            "success": False,
            "completion": partial_text,
            "error": str(e)
        }), 500

@app.route('/')
def index():
    """Serve a simple test interface"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>BUTLER Ollama Test</title>
        <style>
            body { font-family: Arial; max-width: 800px; margin: 50px auto; padding: 20px; }
            input { width: 70%; padding: 10px; font-size: 16px; }
            button { padding: 10px 20px; font-size: 16px; background: #4CAF50; color: white; border: none; cursor: pointer; }
            #response { margin-top: 20px; padding: 15px; background: #f0f0f0; border-radius: 5px; min-height: 100px; }
            .status { padding: 10px; margin-bottom: 20px; background: #e8f5e9; border-radius: 5px; }
        </style>
    </head>
    <body>
        <h1>BUTLER - Ollama Integration Test</h1>
        <div class="status" id="status">Checking connection...</div>

        <div>
            <input type="text" id="message" placeholder="Ask BUTLER anything..." autofocus>
            <button onclick="sendMessage()">Send</button>
        </div>

        <div id="response"></div>

        <script>
            // Check status on load
            fetch('/api/status')
                .then(r => r.json())
                .then(data => {
                    document.getElementById('status').innerHTML =
                        `Status: ${data.status} | Ollama: ${data.ollama} | Model: ${data.model}`;
                });

            function sendMessage() {
                const msg = document.getElementById('message').value;
                if (!msg) return;

                document.getElementById('response').innerHTML = 'Thinking...';

                fetch('/api/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({message: msg, context_type: 'general'})
                })
                .then(r => r.json())
                .then(data => {
                    document.getElementById('response').innerHTML =
                        `<strong>BUTLER:</strong><br>${data.response}`;
                })
                .catch(err => {
                    document.getElementById('response').innerHTML =
                        `Error: ${err.message}`;
                });
            }

            // Enter key support
            document.getElementById('message').addEventListener('keypress', (e) => {
                if (e.key === 'Enter') sendMessage();
            });
        </script>
    </body>
    </html>
    '''

if __name__ == '__main__':
    print("="*60)
    print("BUTLER Simple Ollama API")
    print("="*60)
    print(f"Ollama URL: {OLLAMA_URL}")
    print(f"Model: {MODEL}")
    print("="*60)
    print("Starting server on http://localhost:5018")
    print("Test interface: http://localhost:5018")
    print("API endpoints:")
    print("  GET  /api/status - Check Ollama connection")
    print("  POST /api/chat - Chat with BUTLER")
    print("  POST /api/analyze - Analyze content")
    print("  POST /api/complete - Auto-complete text")
    print("="*60)

    app.run(host='0.0.0.0', port=5018, debug=False)