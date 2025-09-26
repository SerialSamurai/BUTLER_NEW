"""
Enhanced Ollama API for BUTLER with Document Access
Allows BUTLER to answer questions about uploaded documents
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json
import logging
import os
import PyPDF2
from pathlib import Path
import re

app = Flask(__name__)
CORS(app)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('BUTLER_OLLAMA_DOCS')

OLLAMA_URL = "http://localhost:11434"
MODEL = "llama3.2:latest"
UPLOAD_FOLDER = "uploads"

# Cache for document contents
DOCUMENT_CACHE = {}

def extract_pdf_text(filepath):
    """Extract text from PDF file"""
    try:
        with open(filepath, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text() + "\n"
            return text
    except Exception as e:
        logger.error(f"Error extracting PDF {filepath}: {e}")
        return ""

def load_documents():
    """Load all documents from uploads folder into memory"""
    global DOCUMENT_CACHE

    upload_path = Path(UPLOAD_FOLDER)
    if not upload_path.exists():
        logger.warning(f"Upload folder {UPLOAD_FOLDER} does not exist")
        return

    for file_path in upload_path.glob("*.pdf"):
        if file_path.name not in DOCUMENT_CACHE:
            logger.info(f"Loading document: {file_path.name}")
            text = extract_pdf_text(file_path)
            if text:
                DOCUMENT_CACHE[file_path.name] = {
                    'content': text[:10000],  # Limit to first 10k chars for context
                    'full_path': str(file_path),
                    'name': file_path.name
                }

    logger.info(f"Loaded {len(DOCUMENT_CACHE)} documents")

def search_documents(query):
    """Search through cached documents for relevant content"""
    query_lower = query.lower()
    relevant_docs = []

    keywords = query_lower.split()

    for doc_name, doc_info in DOCUMENT_CACHE.items():
        content_lower = doc_info['content'].lower()
        relevance_score = 0

        # Check how many keywords match
        for keyword in keywords:
            if keyword in content_lower:
                relevance_score += content_lower.count(keyword)

        if relevance_score > 0:
            # Extract relevant snippet around the first keyword
            first_keyword = next((kw for kw in keywords if kw in content_lower), None)
            if first_keyword:
                index = content_lower.find(first_keyword)
                start = max(0, index - 200)
                end = min(len(content_lower), index + 500)
                snippet = doc_info['content'][start:end]

                relevant_docs.append({
                    'name': doc_name,
                    'score': relevance_score,
                    'snippet': snippet
                })

    # Sort by relevance
    relevant_docs.sort(key=lambda x: x['score'], reverse=True)
    return relevant_docs[:3]  # Return top 3 most relevant

# System prompts for different contexts
SYSTEM_PROMPTS = {
    "general": """You are BUTLER, an AI assistant for the Texas Association of Counties.
    You help with county operations, permits, fines, taxes, and general administrative tasks.
    You have access to several official documents including:
    - 2023 Bylaws
    - County Clerk Manual 2023 Edition
    - TCCA Code of Ethics 2017
    - TCCA Education Committee 2025 Policies and Procedures

    When answering questions, reference these documents when relevant.
    Be helpful, specific, and provide actionable information for Texas county residents and officials.""",

    "admin": """You are BUTLER, an advanced AI system administrator assistant.
    You have full access to all system documentation and can provide detailed technical information.
    Reference the uploaded documents when discussing policies and procedures.""",

    "document": """You are BUTLER, specialized in analyzing Texas county documentation.
    You have access to official county documents and should provide accurate information based on them.
    Always cite the specific document when providing information."""
}

@app.route('/api/status', methods=['GET'])
def status():
    """Check if Ollama is running and documents are loaded"""
    try:
        response = requests.get(f"{OLLAMA_URL}/api/tags")
        models = response.json()

        return jsonify({
            "status": "online",
            "ollama": "connected",
            "model": MODEL,
            "available_models": [m['name'] for m in models.get('models', [])],
            "documents_loaded": len(DOCUMENT_CACHE),
            "documents": list(DOCUMENT_CACHE.keys())
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    """Process chat messages with document context"""
    try:
        data = request.json
        user_message = data.get('message', '')
        context_type = data.get('context_type', 'general')

        # Search for relevant documents
        relevant_docs = search_documents(user_message)

        # Build context from documents
        doc_context = ""
        if relevant_docs:
            doc_context = "\n\nRelevant information from county documents:\n"
            for doc in relevant_docs:
                doc_context += f"\n[From {doc['name']}]:\n{doc['snippet']}\n"

        # Get appropriate system prompt
        system_prompt = SYSTEM_PROMPTS.get(context_type, SYSTEM_PROMPTS['general'])

        # Build the full prompt with document context
        full_prompt = f"""{system_prompt}

{doc_context}

User: {user_message}

BUTLER:"""

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
                    "num_predict": 500
                }
            },
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            ai_response = result.get('response', 'No response generated')

            # Add document references if found
            if relevant_docs:
                ai_response += "\n\n📄 Sources: " + ", ".join([doc['name'] for doc in relevant_docs])

            logger.info(f"Query: {user_message[:50]}... Found {len(relevant_docs)} relevant docs")

            return jsonify({
                "success": True,
                "response": ai_response,
                "model": MODEL,
                "context": context_type,
                "documents_used": [doc['name'] for doc in relevant_docs]
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

@app.route('/api/search_docs', methods=['POST'])
def search_docs():
    """Search through documents for specific information"""
    try:
        data = request.json
        query = data.get('query', '')

        results = search_documents(query)

        return jsonify({
            "success": True,
            "query": query,
            "results": results,
            "total_documents": len(DOCUMENT_CACHE)
        })

    except Exception as e:
        logger.error(f"Search error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/list_documents', methods=['GET'])
def list_documents():
    """List all available documents"""
    try:
        docs = []
        for name, info in DOCUMENT_CACHE.items():
            docs.append({
                "name": name,
                "size": len(info['content']),
                "preview": info['content'][:200] + "..."
            })

        return jsonify({
            "success": True,
            "documents": docs,
            "total": len(docs)
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/reload_documents', methods=['POST'])
def reload_documents():
    """Reload documents from upload folder"""
    try:
        global DOCUMENT_CACHE
        DOCUMENT_CACHE = {}
        load_documents()

        return jsonify({
            "success": True,
            "message": f"Reloaded {len(DOCUMENT_CACHE)} documents",
            "documents": list(DOCUMENT_CACHE.keys())
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/')
def index():
    """Serve a simple test interface"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>BUTLER Ollama + Documents Test</title>
        <style>
            body { font-family: Arial; max-width: 900px; margin: 50px auto; padding: 20px; }
            .container { display: grid; grid-template-columns: 1fr 300px; gap: 20px; }
            input { width: 100%; padding: 10px; font-size: 16px; }
            button { padding: 10px 20px; font-size: 16px; background: #1a73e8; color: white; border: none; cursor: pointer; border-radius: 4px; }
            #response { margin-top: 20px; padding: 15px; background: #f0f0f0; border-radius: 5px; min-height: 100px; }
            .status { padding: 10px; margin-bottom: 20px; background: #e8f5e9; border-radius: 5px; }
            .docs-panel { background: #f8f9fa; padding: 15px; border-radius: 5px; }
            .doc-item { padding: 5px 0; color: #5f6368; font-size: 14px; }
        </style>
    </head>
    <body>
        <h1>BUTLER - Document-Aware Assistant</h1>
        <div class="status" id="status">Checking connection...</div>

        <div class="container">
            <div>
                <h3>Ask about county documents:</h3>
                <p style="color: #5f6368; font-size: 14px;">
                    Try asking about: bylaws, code of ethics, county clerk procedures, education policies, etc.
                </p>
                <input type="text" id="message" placeholder="Ask about Texas county policies..." autofocus>
                <button onclick="sendMessage()" style="margin-top: 10px;">Ask BUTLER</button>

                <div id="response"></div>
            </div>

            <div class="docs-panel">
                <h4>Available Documents:</h4>
                <div id="docsList"></div>
            </div>
        </div>

        <script>
            // Check status on load
            fetch('/api/status')
                .then(r => r.json())
                .then(data => {
                    document.getElementById('status').innerHTML =
                        `Status: ${data.status} | Ollama: ${data.ollama} | Documents: ${data.documents_loaded}`;

                    // Show documents
                    if (data.documents) {
                        let docsHtml = '';
                        data.documents.forEach(doc => {
                            docsHtml += `<div class="doc-item">📄 ${doc}</div>`;
                        });
                        document.getElementById('docsList').innerHTML = docsHtml;
                    }
                });

            function sendMessage() {
                const msg = document.getElementById('message').value;
                if (!msg) return;

                document.getElementById('response').innerHTML = 'Searching documents and thinking...';

                fetch('/api/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({message: msg, context_type: 'document'})
                })
                .then(r => r.json())
                .then(data => {
                    let response = `<strong>BUTLER:</strong><br>${data.response}`;
                    if (data.documents_used && data.documents_used.length > 0) {
                        response += `<br><br><em>Referenced: ${data.documents_used.join(', ')}</em>`;
                    }
                    document.getElementById('response').innerHTML = response;
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
    print("BUTLER Document-Aware Ollama API")
    print("="*60)

    # Load documents on startup
    print("Loading documents from uploads folder...")
    load_documents()

    print("="*60)
    print(f"Ollama URL: {OLLAMA_URL}")
    print(f"Model: {MODEL}")
    print(f"Documents loaded: {len(DOCUMENT_CACHE)}")
    if DOCUMENT_CACHE:
        print("\nAvailable documents:")
        for doc in DOCUMENT_CACHE.keys():
            print(f"  - {doc}")
    print("="*60)
    print("Starting server on http://localhost:5019")
    print("Test interface: http://localhost:5019")
    print("API endpoints:")
    print("  GET  /api/status - Check status and loaded documents")
    print("  POST /api/chat - Chat with document context")
    print("  POST /api/search_docs - Search documents")
    print("  GET  /api/list_documents - List all documents")
    print("  POST /api/reload_documents - Reload documents")
    print("="*60)

    app.run(host='0.0.0.0', port=5019, debug=False)