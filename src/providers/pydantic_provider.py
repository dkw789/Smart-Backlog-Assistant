"""PydanticAI provider module for structured AI services."""

import json
import logging
from typing import Any, Dict, Optional, Type

from .base_provider import AIProvider

try:
    from pydantic import BaseModel
    from pydantic_ai import Agent

    PYDANTIC_AI_AVAILABLE = True
except ImportError:
    PYDANTIC_AI_AVAILABLE = False


class PydanticAIProvider(AIProvider):
    """Provider for PydanticAI services."""

    def __init__(self, model: str = "openai:gpt-3.5-turbo"):
        self.logger = logging.getLogger(__name__)
        self.model = model
        self.agents = {}
        self._available = PYDANTIC_AI_AVAILABLE

    def is_available(self) -> bool:
        """Check if PydanticAI is available."""
        return self._available

    def get_config(self) -> Dict[str, Any]:
        """Get PydanticAI provider configuration."""
        return {
            "provider": "pydantic_ai",
            "model": self.model,
            "available": self.is_available(),
            "agents_count": len(self.agents),
        }

    def create_agent(
        self, name: str, system_prompt: str, result_type: Optional[Type] = None
    ) -> Any:
        """Create a PydanticAI agent."""
        if not self.is_available():
            return MockPydanticAgent(name, system_prompt)

        try:
            agent = Agent(
                model=self.model,
                system_prompt=system_prompt,
                result_type=result_type or str,
            )
            self.agents[name] = agent
            return agent
        except Exception as e:
            self.logger.error(f"Failed to create PydanticAI agent: {e}")
            return MockPydanticAgent(name, system_prompt)

    def get_agent(self, name: str) -> Optional[Any]:
        """Get an existing agent by name."""
        return self.agents.get(name)

    def generate_completion(
        self, prompt: str, agent_name: Optional[str] = None, **kwargs
    ) -> str:
        """Generate a completion using PydanticAI."""
        if not self.is_available():
            return f"Mock PydanticAI response to: {prompt[:50]}..."

        try:
            if agent_name and agent_name in self.agents:
                agent = self.agents[agent_name]
                result = agent.run_sync(prompt)
                return str(result.data)
            else:
                # Create a temporary agent
                temp_agent = Agent(model=self.model, result_type=str)
                result = temp_agent.run_sync(prompt)
                return str(result.data)
        except Exception as e:
            self.logger.error(f"PydanticAI completion failed: {e}")
            raise

    def generate_structured_response(
        self,
        prompt: str,
        schema: Optional[Dict] = None,
        agent_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate a structured response using PydanticAI."""
        if not self.is_available():
            return {
                "analysis": "Mock structured response",
                "confidence": 0.8,
                "source": "pydantic_ai_mock",
            }

        try:
            if agent_name and agent_name in self.agents:
                agent = self.agents[agent_name]
                result = agent.run_sync(prompt)

                # Convert result to dict if it's a Pydantic model
                if hasattr(result.data, "model_dump"):
                    return result.data.model_dump()
                elif isinstance(result.data, dict):
                    return result.data
                else:
                    return {"result": str(result.data)}
            else:
                # Create temporary structured agent
                if schema and PYDANTIC_AI_AVAILABLE:
                    from pydantic import create_model

                    # Create dynamic Pydantic model from schema
                    fields = {}
                    for key, value in schema.items():
                        if isinstance(value, dict) and "type" in value:
                            field_type = str if value["type"] == "string" else Any
                        else:
                            field_type = Any
                        fields[key] = (field_type, ...)

                    DynamicModel = create_model("DynamicResponse", **fields)
                    agent = Agent(model=self.model, result_type=DynamicModel)
                    result = agent.run_sync(prompt)
                    return result.data.model_dump()
                else:
                    # Fallback to string response
                    agent = Agent(model=self.model, result_type=str)
                    result = agent.run_sync(prompt)
                    try:
                        return json.loads(result.data)
                    except json.JSONDecodeError:
                        return {"result": result.data}
        except Exception as e:
            self.logger.error(f"PydanticAI structured response failed: {e}")
            raise


class MockPydanticAgent:
    """Mock PydanticAI agent for testing."""

    def __init__(self, name: str, system_prompt: str):
        self.name = name
        self.system_prompt = system_prompt
        self.call_count = 0

    def run_sync(self, prompt: str) -> "MockResult":
        """Mock synchronous run."""
        self.call_count += 1
        return MockResult(f"Mock response from {self.name}: {prompt[:30]}...")


class MockResult:
    """Mock result object."""

    def __init__(self, data: Any):
        self.data = data


class MockPydanticProvider(AIProvider):
    """Mock PydanticAI provider for testing."""

    def __init__(self):
        self.agents = {}
        self.responses = {}

    def is_available(self) -> bool:
        """Mock provider is always available."""
        return True

    def get_config(self) -> Dict[str, Any]:
        """Get mock provider configuration."""
        return {
            "provider": "mock_pydantic_ai",
            "available": True,
            "agents_count": len(self.agents),
        }

    def create_agent(
        self, name: str, system_prompt: str, result_type: Optional[Type] = None
    ) -> MockPydanticAgent:
        """Create a mock agent."""
        agent = MockPydanticAgent(name, system_prompt)
        self.agents[name] = agent
        return agent

    def get_agent(self, name: str) -> Optional[MockPydanticAgent]:
        """Get a mock agent."""
        return self.agents.get(name)

    def generate_completion(
        self, prompt: str, agent_name: Optional[str] = None, **kwargs
    ) -> str:
        """Generate a mock completion."""
        return self.responses.get(
            "completion", f"Mock completion for: {prompt[:50]}..."
        )

    def generate_structured_response(
        self,
        prompt: str,
        schema: Optional[Dict] = None,
        agent_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate a mock structured response."""
        default_response = {
            "analysis": "Mock analysis",
            "priority": "medium",
            "confidence": 0.8,
            "agent": agent_name or "default",
        }
        return self.responses.get("structured", default_response)

    def set_mock_response(self, response_type: str, response: Any) -> None:
        """Set mock response for testing."""
        self.responses[response_type] = response
