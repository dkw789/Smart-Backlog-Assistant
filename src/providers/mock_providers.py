"""Mock providers for testing the enhanced modules with dependency injection."""

from typing import Any, Dict, List
from dataclasses import dataclass
from src.processors.ai_processor import AIResponse


@dataclass
class MockAIResponse:
    """Mock AI response for testing."""
    content: str
    service_used: str = "mock"
    processing_time: float = 0.1
    success: bool = True
    error_message: str = None


class MockAIProvider:
    """Mock AI provider for testing."""
    
    def __init__(self, responses: Dict[str, str] = None):
        self.responses = responses or {
            "assess_priority": "Priority: High\nCategory: Feature\nBusiness Impact: High\nTechnical Complexity: Medium\nReasoning: Critical user-facing feature",
            "generate_user_stories": "**Story 1**: As a user, I want to login so that I can access my account\n**Acceptance Criteria**:\n- [ ] User can enter credentials\n- [ ] System validates credentials",
            "analyze_backlog_items": "Overall health score: 85%\nRecommendations:\n- Add more detailed acceptance criteria\n- Balance priority distribution"
        }
        self.call_count = 0
    
    def assess_priority(self, item_description: str) -> AIResponse:
        """Mock priority assessment."""
        self.call_count += 1
        return AIResponse(
            content=self.responses.get("assess_priority", "Mock priority assessment"),
            service_used="mock",
            processing_time=0.1,
            success=True
        )
    
    def generate_user_stories(self, requirements: str) -> AIResponse:
        """Mock user story generation."""
        self.call_count += 1
        return AIResponse(
            content=self.responses.get("generate_user_stories", "Mock user stories"),
            service_used="mock", 
            processing_time=0.1,
            success=True
        )
    
    def analyze_backlog_items(self, backlog_data: List[Dict[str, Any]]) -> AIResponse:
        """Mock backlog analysis."""
        self.call_count += 1
        return AIResponse(
            content=self.responses.get("analyze_backlog_items", "Mock backlog analysis"),
            service_used="mock",
            processing_time=0.1,
            success=True
        )


class MockConsoleProvider:
    """Mock console provider for testing."""
    
    def __init__(self):
        self.printed_messages = []
        self.input_responses = []
        self.input_index = 0
    
    def print(self, *args, **kwargs):
        """Mock print function."""
        message = " ".join(str(arg) for arg in args)
        self.printed_messages.append(message)
    
    def input(self, prompt: str = "") -> str:
        """Mock input function."""
        if self.input_index < len(self.input_responses):
            response = self.input_responses[self.input_index]
            self.input_index += 1
            return response
        return "mock_input"
    
    def set_input_responses(self, responses: List[str]):
        """Set predefined input responses."""
        self.input_responses = responses
        self.input_index = 0


class MockFailingAIProvider:
    """Mock AI provider that simulates failures for testing error handling."""
    
    def __init__(self, failure_rate: float = 1.0):
        self.failure_rate = failure_rate
        self.call_count = 0
    
    def assess_priority(self, item_description: str) -> AIResponse:
        """Mock failing priority assessment."""
        self.call_count += 1
        return AIResponse(
            content="",
            service_used="mock_failing",
            processing_time=0.1,
            success=False,
            error_message="Mock AI service failure"
        )
    
    def generate_user_stories(self, requirements: str) -> AIResponse:
        """Mock failing user story generation."""
        self.call_count += 1
        return AIResponse(
            content="",
            service_used="mock_failing",
            processing_time=0.1,
            success=False,
            error_message="Mock AI service failure"
        )
    
    def analyze_backlog_items(self, backlog_data: List[Dict[str, Any]]) -> AIResponse:
        """Mock failing backlog analysis."""
        self.call_count += 1
        return AIResponse(
            content="",
            service_used="mock_failing",
            processing_time=0.1,
            success=False,
            error_message="Mock AI service failure"
        )
