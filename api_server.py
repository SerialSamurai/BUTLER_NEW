"""
BUTLER API Server
REST API endpoints for BUTLER system with Ollama integration
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import asyncio
import logging
from datetime import datetime
import json
import os
from dotenv import load_dotenv
from butler_core import ButlerCore, SecurityLevel, User
from ollama_integration import OllamaIntegration
from government_integrations import ListServProcessor
from intelligence_engine import CrimePatternAnalyzer

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for demo

# Initialize BUTLER system
butler = ButlerCore()
ollama = OllamaIntegration()

# File upload configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc', 'txt'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('BUTLER_API')

# Demo user for testing (in production, this would use real authentication)
DEMO_USER = {
    "user_id": "demo.user@dallascounty.gov",
    "department": "Administration",
    "role": "analyst",
    "clearance_level": SecurityLevel.CONFIDENTIAL
}

@app.route('/')
def serve_demo():
    """Serve the TAOC dual-mode platform HTML page"""
    try:
        with open('butler-dual.html', 'r', encoding='utf-8') as f:
            content = f.read()
        return content, 200, {'Content-Type': 'text/html; charset=utf-8'}
    except FileNotFoundError:
        return "butler-dual.html not found", 404
    except Exception as e:
        return f"Error: {str(e)}", 500

@app.route('/TAOC.png')
def serve_taoc_png():
    """Serve TAOC logo PNG"""
    return send_from_directory('.', 'TAOC.png')

@app.route('/TAOC.webp')
def serve_taoc_webp():
    """Serve TAOC logo WebP"""
    return send_from_directory('.', 'TAOC.webp')

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get system status"""
    try:
        # Add demo user if not exists
        if DEMO_USER["user_id"] not in butler.active_users:
            butler.active_users[DEMO_USER["user_id"]] = User(
                user_id=DEMO_USER["user_id"],
                department=DEMO_USER["department"],
                role=DEMO_USER["role"],
                clearance_level=DEMO_USER["clearance_level"],
                active_directory_id="DALLAS\\demo.user"
            )

        status = butler.get_system_status()
        return jsonify({
            "success": True,
            "status": status,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Status error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    """Process chat messages with Ollama"""
    try:
        data = request.json
        message = data.get('message', '')
        context_type = data.get('context_type', 'general')
        user_id = data.get('user_id', DEMO_USER["user_id"])

        # Ensure user is authenticated
        if user_id not in butler.active_users:
            butler.active_users[user_id] = User(
                user_id=user_id,
                department=DEMO_USER["department"],
                role=DEMO_USER["role"],
                clearance_level=SecurityLevel.CONFIDENTIAL,
                active_directory_id=f"DALLAS\\{user_id.split('@')[0]}"
            )

        # Process query through BUTLER with Ollama
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        response = loop.run_until_complete(butler.process_query(user_id, message, context_type))

        # Log interaction
        butler.log_action(
            user_id, "chat_interaction", "api",
            SecurityLevel.INTERNAL,
            {"message_length": len(message)}
        )

        return jsonify({
            "success": True,
            "response": response,
            "timestamp": datetime.now().isoformat(),
            "model": ollama.model
        })

    except Exception as e:
        logger.error(f"Chat error: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "response": "I apologize, but I'm having trouble processing your request. Please ensure Ollama is running locally."
        }), 500

@app.route('/api/analyze_email', methods=['POST'])
def analyze_email():
    """Analyze email content using Ollama"""
    try:
        data = request.json
        email_content = data.get('content', '')
        email_metadata = {
            'from': data.get('from', 'Unknown'),
            'subject': data.get('subject', 'No Subject'),
            'timestamp': data.get('timestamp', datetime.now().isoformat())
        }

        # Analyze with Ollama
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        analysis = loop.run_until_complete(ollama.analyze_email(email_content, email_metadata))

        return jsonify({
            "success": True,
            "analysis": analysis,
            "timestamp": datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"Email analysis error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/listserv/summary', methods=['GET'])
def get_listserv_summary():
    """Get summary of ListServ activity"""
    try:
        # Initialize ListServ processor
        listserv = ListServProcessor(butler)

        # Get summary for demo
        summary = {
            "total_emails": 42,
            "urgent_items": 3,
            "pending_actions": 7,
            "categories": {
                "emergency_alerts": 2,
                "foia_requests": 5,
                "citizen_complaints": 8,
                "vendor_inquiries": 12,
                "policy_updates": 15
            },
            "recent_activity": [
                {
                    "from": "emergency.mgmt@dallascounty.org",
                    "subject": "Weather Alert - Severe Thunderstorm",
                    "priority": "high",
                    "time": "5 minutes ago"
                },
                {
                    "from": "facilities@dallascounty.org",
                    "subject": "Maintenance Schedule Update",
                    "priority": "normal",
                    "time": "15 minutes ago"
                }
            ]
        }

        return jsonify({
            "success": True,
            "summary": summary,
            "timestamp": datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"ListServ summary error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/intelligence/alerts', methods=['GET'])
def get_intelligence_alerts():
    """Get current intelligence alerts"""
    try:
        # Initialize crime pattern analyzer
        analyzer = CrimePatternAnalyzer(butler)

        # Demo alerts
        alerts = [
            {
                "id": "ALERT-001",
                "type": "pattern_recognition",
                "level": "high",
                "title": "Unusual Activity Pattern Detected",
                "description": "Multiple related incidents in North District",
                "confidence": 0.87,
                "timestamp": datetime.now().isoformat()
            },
            {
                "id": "ALERT-002",
                "type": "resource_optimization",
                "level": "medium",
                "title": "Resource Allocation Suggestion",
                "description": "Recommend additional patrols in East Sector",
                "confidence": 0.92,
                "timestamp": datetime.now().isoformat()
            }
        ]

        return jsonify({
            "success": True,
            "alerts": alerts,
            "total": len(alerts),
            "timestamp": datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"Intelligence alerts error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/upload_document', methods=['POST'])
def upload_document():
    """Upload and process document for RAG"""
    try:
        # Check if file is in request
        if 'file' not in request.files:
            return jsonify({"success": False, "error": "No file provided"}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({"success": False, "error": "No file selected"}), 400

        if not allowed_file(file.filename):
            return jsonify({"success": False, "error": "File type not allowed"}), 400

        # Save file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Get metadata
        department = request.form.get('department', 'general')
        doc_type = request.form.get('doc_type', 'document')

        # Process with RAG (simplified for demo)
        doc_info = {
            "id": timestamp,
            "filename": filename,
            "filepath": filepath,
            "department": department,
            "doc_type": doc_type,
            "size": os.path.getsize(filepath),
            "upload_time": datetime.now().isoformat(),
            "status": "processed"
        }

        logger.info(f"Document uploaded: {filename}")

        return jsonify({
            "success": True,
            "document": doc_info,
            "message": f"Document '{filename}' uploaded and processed successfully"
        })

    except Exception as e:
        logger.error(f"Upload error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/query_documents', methods=['POST'])
def query_documents():
    """Query uploaded documents using RAG"""
    try:
        data = request.json
        query = data.get('query', '')
        department = data.get('department', None)

        # Simulate RAG search (in production, this would use the RAG system)
        results = [
            {
                "document": "Court_Procedures_Manual.pdf",
                "relevance": 0.92,
                "excerpt": "For filing a court summons in Dallas County, follow these steps: 1) Complete form CV-100...",
                "department": "court"
            },
            {
                "document": "FOIA_Guidelines_2024.pdf",
                "relevance": 0.87,
                "excerpt": "Public records requests must be submitted within 10 business days...",
                "department": "administration"
            }
        ]

        return jsonify({
            "success": True,
            "query": query,
            "results": results,
            "count": len(results)
        })

    except Exception as e:
        logger.error(f"Query error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/generate_document', methods=['POST'])
def generate_document():
    """Generate document from template"""
    try:
        data = request.json
        template_type = data.get('template', 'court_summons')
        variables = data.get('variables', {})

        # Generate using template (simplified)
        templates = {
            "court_summons": """COURT SUMMONS

Case No: {case_number}
Defendant: {defendant}
Date: {date}

You are hereby commanded to appear before the Court...""",
            "public_notice": """PUBLIC NOTICE

{title}
Date: {date}

Notice is hereby given that {details}..."""
        }

        template = templates.get(template_type, "Template not found")

        # Fill in variables
        for key, value in variables.items():
            template = template.replace(f"{{{key}}}", str(value))

        return jsonify({
            "success": True,
            "document": template,
            "template_type": template_type
        })

    except Exception as e:
        logger.error(f"Generation error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/check_ollama', methods=['GET'])
def check_ollama():
    """Check Ollama connection and model availability"""
    try:
        # Initialize Ollama session if needed
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        if not ollama.session:
            loop.run_until_complete(ollama.initialize())

        # Check model availability
        model_available = loop.run_until_complete(ollama.check_model_availability())

        return jsonify({
            "success": True,
            "connected": bool(ollama.session),
            "model": ollama.model,
            "model_available": model_available,
            "base_url": ollama.base_url
        })

    except Exception as e:
        logger.error(f"Ollama check error: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Please ensure Ollama is running locally on port 11434"
        }), 500


if __name__ == '__main__':
    # Get configuration from environment
    API_HOST = os.getenv('API_HOST', '0.0.0.0')
    API_PORT = int(os.getenv('API_PORT', '5017'))
    API_DEBUG = os.getenv('API_DEBUG', 'true').lower() == 'true'

    print("=" * 60)
    print("BUTLER API Server Starting")
    print("=" * 60)
    print(f"Ollama URL: {ollama.base_url}")
    print(f"Ollama Model: {ollama.model}")
    print("=" * 60)
    print("API Endpoints:")
    print("  GET  /api/status - System status")
    print("  POST /api/chat - Chat with BUTLER")
    print("  POST /api/analyze_email - Analyze email content")
    print("  GET  /api/listserv/summary - ListServ activity summary")
    print("  GET  /api/intelligence/alerts - Current alerts")
    print("  POST /api/upload_document - Upload document for RAG")
    print("  POST /api/query_documents - Query RAG documents")
    print("  POST /api/generate_document - Generate from template")
    print("  GET  /api/check_ollama - Check Ollama connection")
    print("=" * 60)
    print(f"Demo UI: http://localhost:{API_PORT}")
    print(f"Enhanced: http://localhost:{API_PORT}/")
    print(f"Basic: http://localhost:{API_PORT}/basic")
    print("=" * 60)

    # Run the Flask app
    # Note: Debug mode disabled due to Python 3.13 compatibility issue
    app.run(debug=False, host=API_HOST, port=API_PORT)