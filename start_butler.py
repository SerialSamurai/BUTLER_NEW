#!/usr/bin/env python3
"""
BUTLER Startup Script
Checks Ollama connection and starts the BUTLER API server
"""

import os
import sys
import asyncio
import subprocess
import time
import logging
from ollama_integration import OllamaIntegration
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('BUTLER_STARTUP')

def print_banner():
    """Print BUTLER startup banner"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   ██████╗ ██╗   ██╗████████╗██╗     ███████╗██████╗        ║
║   ██╔══██╗██║   ██║╚══██╔══╝██║     ██╔════╝██╔══██╗       ║
║   ██████╔╝██║   ██║   ██║   ██║     █████╗  ██████╔╝       ║
║   ██╔══██╗██║   ██║   ██║   ██║     ██╔══╝  ██╔══██╗       ║
║   ██████╔╝╚██████╔╝   ██║   ███████╗███████╗██║  ██║       ║
║   ╚═════╝  ╚═════╝    ╚═╝   ╚══════╝╚══════╝╚═╝  ╚═╝       ║
║                                                              ║
║   Behavioral Understanding & Tactical Law Enforcement       ║
║                      Resource System                        ║
║                                                              ║
║                    Dallas County Edition                     ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

async def check_ollama_connection():
    """Check if Ollama is running and model is available"""
    ollama = OllamaIntegration()

    print("\n🔍 Checking Ollama connection...")
    print(f"   URL: {ollama.base_url}")
    print(f"   Model: {ollama.model}")

    try:
        # Initialize Ollama connection
        connected = await ollama.initialize()
        if not connected:
            return False

        # Check model availability
        print("\n📦 Checking model availability...")
        model_available = await ollama.check_model_availability()

        if not model_available:
            print(f"\n⚠️  Model '{ollama.model}' not found.")
            print("\n   Would you like to pull the model? (This may take several minutes)")
            response = input("   Pull model? (y/n): ").strip().lower()

            if response == 'y':
                print(f"\n📥 Pulling model '{ollama.model}'...")
                print("   This may take several minutes depending on your connection...")
                success = await ollama.pull_model()
                if success:
                    print(f"✅ Model '{ollama.model}' successfully pulled!")
                    return True
                else:
                    print(f"❌ Failed to pull model '{ollama.model}'")
                    return False
            else:
                print("\n❌ Model not available. Please pull the model manually:")
                print(f"   Run: ollama pull {ollama.model}")
                return False

        print(f"✅ Model '{ollama.model}' is available!")

        # Test model with a simple query
        print("\n🧪 Testing model response...")
        response = await ollama.generate_response(
            "Hello, this is a test message. Respond briefly.",
            "You are BUTLER, an AI assistant. Respond in one sentence."
        )

        if response.content:
            print("✅ Model responded successfully!")
            print(f"   Response: {response.content[:100]}...")
            return True
        else:
            print("❌ Model did not respond")
            return False

    except Exception as e:
        print(f"\n❌ Error connecting to Ollama: {e}")
        print("\n   Please ensure Ollama is running:")
        print("   1. Install Ollama from https://ollama.ai")
        print("   2. Start Ollama service")
        print(f"   3. Pull the model: ollama pull {ollama.model}")
        return False
    finally:
        await ollama.cleanup()

def start_api_server():
    """Start the BUTLER API server"""
    print("\n🚀 Starting BUTLER API Server...")
    print("   URL: http://localhost:5017")
    print("   Demo UI: http://localhost:5017")
    print("\n   Press Ctrl+C to stop the server")

    try:
        # Start the Flask API server
        subprocess.run([sys.executable, "api_server.py"])
    except KeyboardInterrupt:
        print("\n\n👋 BUTLER shutting down gracefully...")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error starting API server: {e}")
        sys.exit(1)

async def main():
    """Main startup sequence"""
    print_banner()

    # Check Python version
    if sys.version_info < (3, 7):
        print("❌ BUTLER requires Python 3.7 or higher")
        sys.exit(1)

    print("\n📋 System Check")
    print("   ✅ Python version:", sys.version.split()[0])

    # Check Ollama connection
    ollama_ready = await check_ollama_connection()

    if not ollama_ready:
        print("\n⚠️  BUTLER can run in demo mode without Ollama")
        print("   The system will use pre-configured responses instead of AI")
        response = input("\n   Continue in demo mode? (y/n): ").strip().lower()

        if response != 'y':
            print("\n👋 Exiting BUTLER setup")
            sys.exit(0)

    print("\n" + "=" * 60)
    print("✅ All systems ready!")
    print("=" * 60)

    # Start the API server
    start_api_server()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 BUTLER shutdown complete")
        sys.exit(0)