"""Pytest configuration and fixtures for comprehensive test coverage."""

import json
import os
import sys
import tempfile
from datetime import date, datetime
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

# Add src to Python path
project_root = os.path.dirname(os.path.dirname(__file__))
src_path = os.path.join(project_root, "src")
sys.path.insert(0, src_path)

# Import without "src." prefix since src is already in sys.path
from models.ai_models import AgentRole, AIRequest, AIResponse, AIService
from models.backlog_models import (
    AcceptanceCriterion,
    BacklogItem,
    BacklogProject,
    UserStory,
)
from models.base_models import (
    BusinessImpact,
    Category,
    EffortEstimate,
    Priority,
    Status,
    TechnicalComplexity,
)


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield tmp_dir


@pytest.fixture
def sample_text_file(temp_dir):
    """Create a sample text file for testing."""
    file_path = os.path.join(temp_dir, "sample.txt")
    with open(file_path, "w") as f:
        f.write(
            "This is a sample text file with requirements.\nUser should be able to login.\nSystem must validate inputs."
        )
    return file_path


@pytest.fixture
def sample_meeting_notes(temp_dir):
    """Create sample meeting notes for testing."""
    content = """
    # Sprint Planning Meeting
    
    ## Attendees
    - John Doe
    - Jane Smith
    
    ## Action Items
    - Implement user authentication
    - Fix login bug
    
    ## Requirements
    - System must support OAuth
    - Response time under 200ms
    """
    file_path = os.path.join(temp_dir, "meeting_notes.txt")
    with open(file_path, "w") as f:
        f.write(content)
    return file_path


@pytest.fixture
def sample_backlog_json(temp_dir):
    """Create sample backlog JSON for testing."""
    backlog_data = {
        "items": [
            {
                "id": "ITEM-001",
                "title": "User Authentication",
                "description": "Implement user login system",
                "priority": "high",
                "status": "todo",
                "story_points": 5,
                "tags": ["backend", "security"],
            },
            {
                "id": "ITEM-002",
                "title": "Dashboard UI",
                "description": "Create user dashboard",
                "priority": "medium",
                "status": "in_progress",
                "story_points": 8,
                "tags": ["frontend", "ui"],
            },
        ]
    }
    file_path = os.path.join(temp_dir, "backlog.json")
    with open(file_path, "w") as f:
        json.dump(backlog_data, f)
    return file_path


@pytest.fixture
def sample_backlog_item():
    """Create a sample BacklogItem for testing."""
    return BacklogItem(
        title="Sample Backlog Item",
        description="This is a sample backlog item for testing purposes",
        priority=Priority.HIGH,
        status=Status.TODO,
        category=Category.FEATURE,
        story_points=5,
        tags=["test", "sample"],
        assignee="test.user@example.com",
    )


@pytest.fixture
def sample_user_story():
    """Create a sample UserStory for testing."""
    criteria = [
        AcceptanceCriterion(
            id="AC-001", description="User can login with valid credentials"
        ),
        AcceptanceCriterion(
            id="AC-002", description="System shows error for invalid credentials"
        ),
    ]

    return UserStory(
        title="User Login Story",
        user_type="registered user",
        functionality="login to the system",
        benefit="I can access my personal dashboard",
        acceptance_criteria=criteria,
        priority=Priority.HIGH,
        estimated_effort=EffortEstimate.MEDIUM,
        story_points=5,
        tags=["authentication", "login"],
    )


@pytest.fixture
def sample_ai_response():
    """Create a sample AIResponse for testing."""
    return AIResponse(
        content="Sample AI response content",
        service_used=AIService.OPENAI,
        agent_role=AgentRole.BUSINESS_ANALYST,
        success=True,
        processing_time=1.5,
        tokens_used=150,
        confidence_score=0.85,
    )


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client for testing."""
    mock_client = Mock()
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = "Mock AI response"
    mock_response.usage.total_tokens = 100
    mock_client.chat.completions.create.return_value = mock_response
    return mock_client


@pytest.fixture
def mock_anthropic_client():
    """Mock Anthropic client for testing."""
    mock_client = Mock()
    mock_response = Mock()
    mock_response.content = [Mock()]
    mock_response.content[0].text = "Mock Anthropic response"
    mock_client.messages.create.return_value = mock_response
    return mock_client


@pytest.fixture
def mock_env_vars():
    """Mock environment variables for testing."""
    env_vars = {
        "OPENAI_API_KEY": "test_openai_key",
        "ANTHROPIC_API_KEY": "test_anthropic_key",
        "HUGGINGFACE_API_KEY": "test_hf_key",
        "LOG_LEVEL": "DEBUG",
        "MAX_RETRIES": "3",
        "TIMEOUT_SECONDS": "30",
    }

    with patch.dict(os.environ, env_vars):
        yield env_vars


@pytest.fixture
def sample_backlog_project():
    """Create a sample BacklogProject for testing."""
    # Use valid Fibonacci sequence values for story points
    fibonacci_points = [1, 2, 3, 5, 8]
    items = [
        BacklogItem(
            title=f"Item {i}",
            description=f"Description for item {i}",
            priority=Priority.HIGH if i % 2 == 0 else Priority.MEDIUM,
            status=Status.TODO,
            story_points=fibonacci_points[i],
        )
        for i in range(5)
    ]

    return BacklogProject(
        name="Test Project",
        description="A test project for unit testing",
        version="1.0.0",
        items=items,
        team_members=["dev1@example.com", "dev2@example.com"],
    )


@pytest.fixture
def mock_logger():
    """Mock logger for testing."""
    return Mock()


@pytest.fixture
def mock_file_operations():
    """Mock file operations for testing."""
    with patch("builtins.open", create=True) as mock_open:
        mock_open.return_value.__enter__.return_value.read.return_value = (
            "Mock file content"
        )
        yield mock_open


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Set up test environment automatically for all tests."""
    # Ensure logs directory exists
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    # Set test environment variables
    test_env = {
        "LOG_LEVEL": "ERROR",  # Reduce log noise in tests
        "MAX_RETRIES": "1",  # Faster test execution
        "TIMEOUT_SECONDS": "5",  # Shorter timeouts for tests
    }

    with patch.dict(os.environ, test_env):
        yield


class MockAIProcessor:
    """Mock AI processor for testing without API calls."""

    def __init__(self):
        self.call_count = 0

    def extract_requirements(self, content):
        self.call_count += 1
        return AIResponse(
            content="Mock extracted requirements",
            service_used=AIService.OPENAI,
            agent_role=AgentRole.BUSINESS_ANALYST,
            success=True,
            processing_time=0.5,
        )

    def generate_user_stories(self, requirements):
        self.call_count += 1
        return AIResponse(
            content="Mock generated user stories",
            service_used=AIService.OPENAI,
            agent_role=AgentRole.PRODUCT_OWNER,
            success=True,
            processing_time=0.7,
        )

    def assess_priority(self, item_description):
        self.call_count += 1
        return AIResponse(
            content="Mock priority assessment",
            service_used=AIService.OPENAI,
            agent_role=AgentRole.ENGINEERING_MANAGER,
            success=True,
            processing_time=0.3,
        )


@pytest.fixture
def mock_ai_processor():
    """Provide mock AI processor for testing."""
    return MockAIProcessor()


# Test markers for different test categories
pytest.mark.unit = pytest.mark.unit
pytest.mark.integration = pytest.mark.integration
pytest.mark.slow = pytest.mark.slow
pytest.mark.ai_dependent = pytest.mark.ai_dependent
