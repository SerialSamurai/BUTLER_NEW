"""
BUTLER Ollama Integration Module
Connects BUTLER to local Ollama instance for AI intelligence
"""

import aiohttp
import asyncio
import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import os

@dataclass
class OllamaResponse:
    content: str
    model: str
    total_duration: Optional[int] = None
    load_duration: Optional[int] = None
    prompt_eval_count: Optional[int] = None
    eval_count: Optional[int] = None

class OllamaIntegration:
    """
    Integrates BUTLER with local Ollama instance running Llama 3.2
    Provides intelligent responses and analysis capabilities
    """

    def __init__(self, base_url: str = None, model: str = None):
        self.base_url = base_url or os.getenv('OLLAMA_URL', 'http://localhost:11434')
        self.model = model or os.getenv('OLLAMA_MODEL', 'llama3.2:latest')
        self.logger = logging.getLogger('BUTLER.Ollama')
        self.session = None
        self.context_window = []
        self.max_context_messages = 10

    async def initialize(self):
        """Initialize connection to Ollama"""
        try:
            self.session = aiohttp.ClientSession()
            # Test connection
            async with self.session.get(f'{self.base_url}/api/version') as response:
                if response.status == 200:
                    version = await response.json()
                    self.logger.info(f"Connected to Ollama version: {version.get('version', 'unknown')}")
                    return True
        except Exception as e:
            self.logger.error(f"Failed to connect to Ollama: {e}")
            return False

    async def generate_response(self, prompt: str, system_prompt: str = None,
                               context: List[Dict] = None, stream: bool = False) -> OllamaResponse:
        """
        Generate response from Ollama

        Args:
            prompt: User prompt
            system_prompt: System instructions for the model
            context: Previous conversation context
            stream: Whether to stream the response
        """
        if not self.session:
            await self.initialize()

        # Build the full prompt with system instructions
        full_prompt = self._build_prompt(prompt, system_prompt, context)

        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": stream,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9,
                "top_k": 40,
                "num_predict": 2048
            }
        }

        try:
            async with self.session.post(
                f'{self.base_url}/api/generate',
                json=payload,
                timeout=aiohttp.ClientTimeout(total=120)
            ) as response:
                if stream:
                    return await self._handle_streaming_response(response)
                else:
                    result = await response.json()
                    return OllamaResponse(
                        content=result.get('response', ''),
                        model=result.get('model', self.model),
                        total_duration=result.get('total_duration'),
                        load_duration=result.get('load_duration'),
                        prompt_eval_count=result.get('prompt_eval_count'),
                        eval_count=result.get('eval_count')
                    )
        except asyncio.TimeoutError:
            self.logger.error("Ollama request timed out")
            return OllamaResponse(
                content="I apologize, but the request timed out. Please try again.",
                model=self.model
            )
        except Exception as e:
            self.logger.error(f"Error generating response: {e}")
            return OllamaResponse(
                content=f"Error generating response: {str(e)}",
                model=self.model
            )

    async def analyze_email(self, email_content: str, email_metadata: Dict) -> Dict[str, Any]:
        """
        Analyze email content using Ollama for categorization and priority
        """
        system_prompt = """You are BUTLER, an AI assistant for Dallas County government operations.
        Analyze the following email and provide:
        1. Category (one of: emergency, foia_request, citizen_complaint, vendor_inquiry, permit_request, court_notification, budget_related, it_maintenance, general)
        2. Priority (critical, high, medium, low)
        3. Suggested actions
        4. Key entities mentioned
        5. Summary

        Respond in JSON format."""

        prompt = f"""
        Email From: {email_metadata.get('from', 'Unknown')}
        Subject: {email_metadata.get('subject', 'No Subject')}
        Content: {email_content}

        Analyze this email and provide categorization and recommendations.
        """

        response = await self.generate_response(prompt, system_prompt)

        # Parse response as JSON or extract information
        try:
            # Attempt to parse JSON from response
            content = response.content
            # Find JSON in the response
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass

        # Fallback structure if JSON parsing fails
        return {
            "category": "general",
            "priority": "medium",
            "actions": ["Review and process manually"],
            "entities": [],
            "summary": response.content[:200] if response.content else "Unable to analyze"
        }

    async def get_contextual_response(self, message: str, conversation_type: str = "general") -> str:
        """
        Get contextual response based on conversation type
        """
        system_prompts = {
            "general": """You are BUTLER, an AI assistant for Dallas County government operations.
            You help with email management, operational tasks, and provide intelligent insights.
            Be professional, concise, and helpful.""",

            "emergency": """You are BUTLER responding to an emergency situation.
            Provide clear, immediate, actionable guidance.
            Focus on safety and proper emergency protocols.""",

            "technical": """You are BUTLER providing technical assistance.
            Give clear technical explanations and step-by-step solutions.""",

            "administrative": """You are BUTLER assisting with administrative tasks.
            Provide efficient solutions for government operations and procedures."""
        }

        system_prompt = system_prompts.get(conversation_type, system_prompts["general"])

        # Add context awareness
        if self.context_window:
            context_str = "\n".join([f"{msg['role']}: {msg['content']}"
                                    for msg in self.context_window[-5:]])
            prompt = f"Previous context:\n{context_str}\n\nCurrent message: {message}"
        else:
            prompt = message

        response = await self.generate_response(prompt, system_prompt)

        # Update context window
        self.context_window.append({"role": "user", "content": message})
        self.context_window.append({"role": "assistant", "content": response.content})

        # Trim context window if too long
        if len(self.context_window) > self.max_context_messages * 2:
            self.context_window = self.context_window[-self.max_context_messages * 2:]

        return response.content

    def _build_prompt(self, prompt: str, system_prompt: str = None,
                     context: List[Dict] = None) -> str:
        """Build full prompt with system instructions and context"""
        full_prompt = ""

        if system_prompt:
            full_prompt += f"System: {system_prompt}\n\n"

        if context:
            for msg in context[-5:]:  # Last 5 messages for context
                role = msg.get('role', 'user')
                content = msg.get('content', '')
                full_prompt += f"{role.capitalize()}: {content}\n"
            full_prompt += "\n"

        full_prompt += f"User: {prompt}\nAssistant:"

        return full_prompt

    async def _handle_streaming_response(self, response):
        """Handle streaming response from Ollama"""
        full_response = ""
        async for line in response.content:
            if line:
                try:
                    data = json.loads(line)
                    if 'response' in data:
                        full_response += data['response']
                except json.JSONDecodeError:
                    continue

        return OllamaResponse(content=full_response, model=self.model)

    async def check_model_availability(self) -> bool:
        """Check if the specified model is available in Ollama"""
        try:
            async with self.session.get(f'{self.base_url}/api/tags') as response:
                if response.status == 200:
                    data = await response.json()
                    models = data.get('models', [])
                    available_models = [m.get('name', '') for m in models]

                    if self.model in available_models or any(self.model.split(':')[0] in m for m in available_models):
                        self.logger.info(f"Model {self.model} is available")
                        return True
                    else:
                        self.logger.warning(f"Model {self.model} not found. Available models: {available_models}")
                        return False
        except Exception as e:
            self.logger.error(f"Error checking model availability: {e}")
            return False

    async def pull_model(self, model_name: str = None) -> bool:
        """Pull a model from Ollama registry"""
        model = model_name or self.model
        try:
            payload = {"name": model, "stream": False}
            async with self.session.post(
                f'{self.base_url}/api/pull',
                json=payload,
                timeout=aiohttp.ClientTimeout(total=3600)  # 1 hour timeout for model download
            ) as response:
                if response.status == 200:
                    self.logger.info(f"Successfully pulled model: {model}")
                    return True
                else:
                    self.logger.error(f"Failed to pull model: {response.status}")
                    return False
        except Exception as e:
            self.logger.error(f"Error pulling model: {e}")
            return False

    async def cleanup(self):
        """Cleanup resources"""
        if self.session:
            await self.session.close()

    def clear_context(self):
        """Clear conversation context"""
        self.context_window = []
        self.logger.info("Context window cleared")