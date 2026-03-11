"""AI processing module for the Smart Backlog Assistant."""

import os
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import anthropic
import openai
from dotenv import load_dotenv

from src.utils.exception_handler import (
    ConfigurationError,
    handle_exceptions,
    validate_api_key,
)
from src.utils.logger_service import get_logger

load_dotenv()


@dataclass
class AIResponse:
    """Structured response from AI processing."""

    content: str
    service_used: str
    processing_time: float
    success: bool
    error_message: Optional[str] = None


class AIProcessor:
    """Handles AI processing using multiple services with fallback."""

    def __init__(self):
        from src.config import config

        self.openai_client = None
        self.anthropic_client = None
        self.qwen_client = None
        self.max_retries = config.max_retries
        self.timeout = config.timeout_seconds
        self.logger = get_logger(__name__)

        self._initialize_clients()

    @handle_exceptions("AI Client Initialization", reraise=False)
    def _initialize_clients(self) -> None:
        """Initialize AI service clients."""
        from src.config import config

        # OpenAI
        openai_key = config.openai_api_key
        if openai_key:
            try:
                validate_api_key(openai_key, "OpenAI")
                openai.api_key = openai_key
                self.openai_client = openai
                self.logger.info("OpenAI client initialized successfully")
            except Exception as e:
                self.logger.warning(f"Failed to initialize OpenAI client: {e}")

        # Anthropic
        anthropic_key = config.anthropic_api_key
        if anthropic_key:
            try:
                validate_api_key(anthropic_key, "Anthropic")
                self.anthropic_client = anthropic.Anthropic(api_key=anthropic_key)
                self.logger.info("Anthropic client initialized successfully")
            except Exception as e:
                self.logger.warning(f"Failed to initialize Anthropic client: {e}")

        # Qwen (using OpenAI-compatible API)
        qwen_key = config.openai_api_key  # Qwen uses OpenAI-compatible API
        qwen_base_url = os.getenv("QWEN_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
        if qwen_key:
            try:
                validate_api_key(qwen_key, "Qwen")
                self.qwen_client = openai.OpenAI(
                    api_key=qwen_key,
                    base_url=qwen_base_url
                )
                self.logger.info("Qwen client initialized successfully")
            except Exception as e:
                self.logger.warning(f"Failed to initialize Qwen client: {e}")

        # Check if at least one service is available
        if not any([self.openai_client, self.anthropic_client, self.qwen_client]):
            raise ConfigurationError(
                "No AI services available. Please configure at least one API key.",
                "NO_AI_SERVICES",
                context={"available_services": []},
            )

    def extract_requirements(self, content: str) -> AIResponse:
        """Extract engineering requirements from content."""
        prompt = f"""
        Role: Senior Business Analyst
        Task: Extract engineering requirements from the following content
        
        Content:
        {content}
        
        Please extract and structure the key engineering requirements in the following format:
        1. **Requirement Title**: Brief description
           - Priority: High/Medium/Low
           - Type: Feature/Bug/Enhancement/Technical Debt
           - Dependencies: Any dependencies mentioned
           - Acceptance Criteria: Key criteria for completion
        
        Focus on actionable engineering tasks and avoid duplicates.
        """

        return self._process_with_fallback(prompt, "requirement_extraction")

    def generate_user_stories(self, requirements: str) -> AIResponse:
        """Generate user stories from requirements."""
        prompt = f"""
        Role: Product Owner
        Task: Convert the following technical requirements into well-formatted user stories
        
        Requirements:
        {requirements}
        
        For each requirement, create a user story in this format:
        
        **Story Title**: [Descriptive title]
        **User Story**: As a [user type], I want [functionality] so that [benefit]
        **Acceptance Criteria**:
        - [ ] Criterion 1
        - [ ] Criterion 2
        - [ ] Criterion 3
        **Priority**: High/Medium/Low
        **Estimated Effort**: Small/Medium/Large
        **Tags**: [relevant tags]
        
        Ensure each story is:
        - Specific and actionable
        - Testable with clear acceptance criteria
        - Focused on user value
        - Appropriately sized for development
        """

        return self._process_with_fallback(prompt, "user_story_generation")

    def assess_priority(self, item_description: str) -> AIResponse:
        """Assess priority and categorization for a backlog item."""
        prompt = f"""
        Role: Engineering Manager
        Task: Assess priority and categorization for the following backlog item
        
        Item Description:
        {item_description}
        
        Please provide:
        1. **Priority Level**: Critical/High/Medium/Low
        2. **Category**: Feature/Bug/Enhancement/Technical Debt/Research
        3. **Effort Estimate**: Small (1-2 days)/Medium (3-5 days)/Large (1-2 weeks)/XL (2+ weeks)
        4. **Business Impact**: High/Medium/Low
        5. **Technical Complexity**: High/Medium/Low
        6. **Dependencies**: List any dependencies or blockers
        7. **Reasoning**: Brief explanation for the priority assessment
        
        Consider factors like:
        - Business value and user impact
        - Technical complexity and risk
        - Dependencies and blockers
        - Resource availability
        - Strategic alignment
        """

        return self._process_with_fallback(prompt, "priority_assessment")

    def analyze_backlog_items(self, backlog_data: List[Dict[str, Any]]) -> AIResponse:
        """Analyze existing backlog items for improvements."""
        backlog_summary = self._summarize_backlog(backlog_data)

        prompt = f"""
        Role: Agile Coach
        Task: Analyze the following backlog items and provide improvement recommendations
        
        Current Backlog:
        {backlog_summary}
        
        Please provide:
        1. **Overall Assessment**: Summary of backlog health
        2. **Missing Information**: What's missing from current items
        3. **Priority Recommendations**: Suggested priority adjustments
        4. **Grouping Suggestions**: How items could be grouped or split
        5. **Next Steps**: Recommended actions for backlog improvement
        
        Focus on:
        - Clarity and completeness of descriptions
        - Appropriate sizing and prioritization
        - Dependencies and sequencing
        - Missing acceptance criteria
        - Opportunities for consolidation or splitting
        """

        return self._process_with_fallback(prompt, "backlog_analysis")

    def _summarize_backlog(self, backlog_data: List[Dict[str, Any]]) -> str:
        """Create a summary of backlog items for analysis."""
        summary = "Backlog Items:\n"
        for i, item in enumerate(backlog_data[:20], 1):  # Limit to first 20 items
            title = item.get("title", "Untitled")
            description = item.get("description", "No description")[:100]
            priority = item.get("priority", "Not set")
            status = item.get("status", "Not set")

            summary += f"{i}. **{title}**\n"
            summary += f"   Description: {description}...\n"
            summary += f"   Priority: {priority}, Status: {status}\n\n"

        if len(backlog_data) > 20:
            summary += f"... and {len(backlog_data) - 20} more items\n"

        return summary

    def _process_with_fallback(self, prompt: str, operation_type: str) -> AIResponse:
        """Process prompt with fallback between AI services."""
        start_time = time.time()

        # Get preferred service from config
        from src.config import config

        default_service = config.default_ai_service.lower()
        services_tried = set()

        # Try default service first
        if default_service == "anthropic" and self.anthropic_client:
            try:
                response = self._call_anthropic(prompt)
                if response:
                    return AIResponse(
                        content=response,
                        service_used="anthropic",
                        processing_time=time.time() - start_time,
                        success=True,
                    )
            except Exception as e:
                self.logger.warning(f"Anthropic failed for {operation_type}: {e}")
            services_tried.add("anthropic")
        elif default_service == "openai" and self.openai_client:
            try:
                response = self._call_openai(prompt)
                if response:
                    return AIResponse(
                        content=response,
                        service_used="openai",
                        processing_time=time.time() - start_time,
                        success=True,
                    )
            except Exception as e:
                self.logger.warning(f"OpenAI failed for {operation_type}: {e}")
            services_tried.add("openai")
        elif default_service == "qwen" and self.qwen_client:
            try:
                response = self._call_qwen(prompt)
                if response:
                    return AIResponse(
                        content=response,
                        service_used="qwen",
                        processing_time=time.time() - start_time,
                        success=True,
                    )
            except Exception as e:
                self.logger.warning(f"Qwen failed for {operation_type}: {e}")
            services_tried.add("qwen")

        # Try remaining services as fallback
        if "anthropic" not in services_tried and self.anthropic_client:
            try:
                response = self._call_anthropic(prompt)
                if response:
                    return AIResponse(
                        content=response,
                        service_used="anthropic",
                        processing_time=time.time() - start_time,
                        success=True,
                    )
            except Exception as e:
                self.logger.warning(f"Anthropic failed for {operation_type}: {e}")
            services_tried.add("anthropic")

        if "openai" not in services_tried and self.openai_client:
            try:
                response = self._call_openai(prompt)
                if response:
                    return AIResponse(
                        content=response,
                        service_used="openai",
                        processing_time=time.time() - start_time,
                        success=True,
                    )
            except Exception as e:
                self.logger.warning(f"OpenAI failed for {operation_type}: {e}")
            services_tried.add("openai")

        if "qwen" not in services_tried and self.qwen_client:
            try:
                response = self._call_qwen(prompt)
                if response:
                    return AIResponse(
                        content=response,
                        service_used="qwen",
                        processing_time=time.time() - start_time,
                        success=True,
                    )
            except Exception as e:
                self.logger.warning(f"Qwen failed for {operation_type}: {e}")
            services_tried.add("qwen")

        # All services failed
        return AIResponse(
            content="",
            service_used="none",
            processing_time=time.time() - start_time,
            success=False,
            error_message="All AI services failed",
        )

    def _call_openai(self, prompt: str) -> Optional[str]:
        """Call OpenAI API."""
        from src.config import config
        
        response = self.openai_client.chat.completions.create(
            model=config.openai_model,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert software engineering assistant.",
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=config.max_tokens,
            temperature=config.temperature,
        )
        return response.choices[0].message.content

    def _call_anthropic(self, prompt: str) -> Optional[str]:
        """Call Anthropic API."""
        from src.config import config
        
        response = self.anthropic_client.messages.create(
            model=config.anthropic_model,
            max_tokens=config.max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text

    def _call_qwen(self, prompt: str) -> Optional[str]:
        """Call Qwen API using OpenAI-compatible interface."""
        from src.config import config
        
        response = self.qwen_client.chat.completions.create(
            model=config.qwen_model,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert software engineering assistant.",
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=config.max_tokens,
            temperature=config.temperature,
        )
        return response.choices[0].message.content
