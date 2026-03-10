"""OpenAI provider module for AI services."""

import json
import logging
from typing import Any, Dict, Optional

from .base_provider import AIProvider

try:
    import openai

    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class OpenAIProvider(AIProvider):
    """Provider for OpenAI services."""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo"):
        self.logger = logging.getLogger(__name__)
        self.model = model
        self.client = None

        if OPENAI_AVAILABLE and api_key:
            try:
                self.client = openai.OpenAI(api_key=api_key)
            except Exception as e:
                self.logger.error(f"Failed to initialize OpenAI client: {e}")

    def is_available(self) -> bool:
        """Check if OpenAI is available and configured."""
        return OPENAI_AVAILABLE and self.client is not None

    def get_config(self) -> Dict[str, Any]:
        """Get OpenAI provider configuration."""
        return {
            "provider": "openai",
            "model": self.model,
            "available": self.is_available(),
        }

    def generate_completion(self, prompt: str, **kwargs) -> str:
        """Generate a completion from OpenAI."""
        if not self.is_available():
            raise RuntimeError("OpenAI provider is not available")

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                **kwargs,
            )
            return response.choices[0].message.content
        except Exception as e:
            self.logger.error(f"OpenAI completion failed: {e}")
            raise

    def generate_structured_response(
        self, prompt: str, schema: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Generate a structured response from OpenAI."""
        if not self.is_available():
            raise RuntimeError("OpenAI provider is not available")

        try:
            # Add JSON format instruction to prompt
            structured_prompt = f"{prompt}\n\nPlease respond with valid JSON."
            if schema:
                structured_prompt += f" Use this schema: {json.dumps(schema)}"

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": structured_prompt}],
            )

            content = response.choices[0].message.content
            return json.loads(content)
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse JSON response: {e}")
            return {"error": "Invalid JSON response", "raw_content": content}
        except Exception as e:
            self.logger.error(f"OpenAI structured response failed: {e}")
            raise


class MockAIProvider(AIProvider):
    """Mock AI provider for testing."""

    def __init__(self, responses: Optional[Dict[str, Any]] = None):
        self.responses = responses or {}
        self.call_count = 0

    def is_available(self) -> bool:
        """Mock provider is always available."""
        return True

    def get_config(self) -> Dict[str, Any]:
        """Get mock provider configuration."""
        return {"provider": "mock", "available": True, "call_count": self.call_count}

    def generate_completion(self, prompt: str, **kwargs) -> str:
        """Generate a mock completion."""
        self.call_count += 1
        return self.responses.get("completion", f"Mock response to: {prompt[:50]}...")

    def generate_structured_response(
        self, prompt: str, schema: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Generate a mock structured response."""
        self.call_count += 1
        default_response = {
            "analysis": "Mock analysis",
            "priority": "medium",
            "confidence": 0.8,
        }
        return self.responses.get("structured", default_response)
