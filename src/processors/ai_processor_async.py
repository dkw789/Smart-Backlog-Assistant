"""Async AI processing module for the Smart Backlog Assistant."""

import asyncio
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union

import aiohttp
import anthropic
import openai
from dotenv import load_dotenv

from src.config import config
from src.utils.exception_handler import (
    AIProcessingError,
    ConfigurationError,
    create_ai_error,
    handle_exceptions,
    validate_api_key,
)
from src.utils.logger_service import get_logger, log_ai_request, log_performance

load_dotenv()


@dataclass
class AIResponse:
    """Structured response from AI processing."""

    content: str
    service_used: str
    processing_time: float
    success: bool
    error_message: Optional[str] = None


class AsyncAIProcessor:
    """Handles async AI processing using multiple services with fallback."""

    def __init__(self):
        self.openai_client = None
        self.anthropic_client = None
        self.max_retries = config.max_retries
        self.timeout = config.timeout_seconds
        self.logger = get_logger(__name__)
        self.session: Optional[aiohttp.ClientSession] = None

        self._initialize_clients()

    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.timeout)
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()

    @handle_exceptions("AI Client Initialization", reraise=False)
    def _initialize_clients(self) -> None:
        """Initialize AI service clients."""
        # OpenAI
        openai_key = config.openai_api_key
        if openai_key:
            try:
                validate_api_key(openai_key, "OpenAI")
                self.openai_client = openai.AsyncOpenAI(api_key=openai_key)
                self.logger.info("Async OpenAI client initialized successfully")
            except Exception as e:
                self.logger.warning(f"Failed to initialize async OpenAI client: {e}")

        # Anthropic
        anthropic_key = config.anthropic_api_key
        if anthropic_key:
            try:
                validate_api_key(anthropic_key, "Anthropic")
                self.anthropic_client = anthropic.AsyncAnthropic(api_key=anthropic_key)
                self.logger.info("Async Anthropic client initialized successfully")
            except Exception as e:
                self.logger.warning(f"Failed to initialize async Anthropic client: {e}")

        # Check if at least one service is available
        if not any([self.openai_client, self.anthropic_client]):
            raise ConfigurationError(
                "No AI services available. Please configure at least one API key.",
                "NO_AI_SERVICES",
                context={"available_services": []},
            )

    async def extract_requirements(self, content: str) -> AIResponse:
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

        return await self._process_with_fallback(prompt, "requirement_extraction")

    async def generate_user_stories(self, requirements: str) -> AIResponse:
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

        return await self._process_with_fallback(prompt, "user_story_generation")

    async def assess_priority(self, item_description: str) -> AIResponse:
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

        return await self._process_with_fallback(prompt, "priority_assessment")

    async def analyze_backlog_items(self, backlog_data: List[Dict[str, Any]]) -> AIResponse:
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

        return await self._process_with_fallback(prompt, "backlog_analysis")

    async def process_multiple_items_concurrently(
        self, items: List[Dict[str, Any]], operation: str
    ) -> List[AIResponse]:
        """Process multiple items concurrently for better performance."""
        tasks = []
        
        for item in items:
            if operation == "extract_requirements":
                task = self.extract_requirements(item.get("content", ""))
            elif operation == "assess_priority":
                task = self.assess_priority(item.get("description", ""))
            elif operation == "generate_user_stories":
                task = self.generate_user_stories(item.get("requirements", ""))
            else:
                continue
            tasks.append(task)

        # Process with controlled concurrency to avoid rate limits
        semaphore = asyncio.Semaphore(3)  # Max 3 concurrent requests
        
        async def bounded_task(task):
            async with semaphore:
                return await task

        bounded_tasks = [bounded_task(task) for task in tasks]
        results = await asyncio.gather(*bounded_tasks, return_exceptions=True)

        # Convert exceptions to failed AIResponse objects
        processed_results = []
        for result in results:
            if isinstance(result, Exception):
                processed_results.append(
                    AIResponse(
                        content="",
                        service_used="none",
                        processing_time=0.0,
                        success=False,
                        error_message=str(result),
                    )
                )
            else:
                processed_results.append(result)

        return processed_results

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

    async def _process_with_fallback(self, prompt: str, operation_type: str) -> AIResponse:
        """Process prompt with fallback between AI services."""
        start_time = time.time()

        # Get preferred service from config
        default_service = config.default_ai_service.lower()
        services_tried = set()

        # Try default service first
        if default_service == "anthropic" and self.anthropic_client:
            try:
                response = await self._call_anthropic_async(prompt)
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
                response = await self._call_openai_async(prompt)
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

        # Try remaining services as fallback
        if "anthropic" not in services_tried and self.anthropic_client:
            try:
                response = await self._call_anthropic_async(prompt)
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
                response = await self._call_openai_async(prompt)
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

        # All services failed
        return AIResponse(
            content="",
            service_used="none",
            processing_time=time.time() - start_time,
            success=False,
            error_message="All AI services failed",
        )

    async def _call_openai_async(self, prompt: str) -> Optional[str]:
        """Call OpenAI API asynchronously."""
        response = await self.openai_client.chat.completions.create(
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

    async def _call_anthropic_async(self, prompt: str) -> Optional[str]:
        """Call Anthropic API asynchronously."""
        response = await self.anthropic_client.messages.create(
            model=config.anthropic_model,
            max_tokens=config.max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text
