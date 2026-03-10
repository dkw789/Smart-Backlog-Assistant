"""Rich CLI provider module for UI services."""

import logging
from typing import Any, Dict, List, Optional

from .base_provider import UIProvider

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.progress import Progress, TaskID
    from rich.status import Status
    from rich.table import Table

    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


class RichUIProvider(UIProvider):
    """Provider for Rich CLI services."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.console = None
        self.progress = None

        if RICH_AVAILABLE:
            try:
                self.console = Console()
            except Exception as e:
                self.logger.error(f"Failed to initialize Rich console: {e}")

    def is_available(self) -> bool:
        """Check if Rich is available and configured."""
        return RICH_AVAILABLE and self.console is not None

    def get_config(self) -> Dict[str, Any]:
        """Get Rich provider configuration."""
        return {
            "provider": "rich",
            "available": self.is_available(),
            "features": (
                ["console", "progress", "tables", "panels"]
                if self.is_available()
                else []
            ),
        }

    def print_message(self, message: str, style: Optional[str] = None) -> None:
        """Print a message with optional styling."""
        if not self.is_available():
            print(message)  # Fallback to standard print
            return

        try:
            if style:
                self.console.print(message, style=style)
            else:
                self.console.print(message)
        except Exception as e:
            self.logger.error(f"Rich print failed: {e}")
            print(message)  # Fallback

    def create_progress_tracker(self) -> "RichProgressTracker":
        """Create a Rich progress tracker instance."""
        if not self.is_available():
            return MockProgressTracker()

        return RichProgressTracker(self.console)

    def format_table(self, data: List[List[str]], title: Optional[str] = None) -> Any:
        """Format data as a Rich table."""
        if not self.is_available():
            return self._format_simple_table(data, title)

        try:
            if not data:
                return Table(title=title or "Empty Table")

            table = Table(title=title)

            # Add columns from first row (headers)
            if data:
                for header in data[0]:
                    table.add_column(header)

                # Add rows
                for row in data[1:]:
                    table.add_row(*row)

            return table
        except Exception as e:
            self.logger.error(f"Rich table formatting failed: {e}")
            return self._format_simple_table(data, title)

    def create_panel(
        self,
        content: str,
        title: Optional[str] = None,
        border_style: Optional[str] = None,
    ) -> Any:
        """Create a Rich panel."""
        if not self.is_available():
            return f"[{title}]\n{content}" if title else content

        try:
            return Panel(content, title=title, border_style=border_style)
        except Exception as e:
            self.logger.error(f"Rich panel creation failed: {e}")
            return f"[{title}]\n{content}" if title else content

    def display_status(self, message: str, spinner: Optional[str] = None) -> Any:
        """Display a status message with spinner."""
        if not self.is_available():
            print(f"Status: {message}")
            return None

        try:
            return Status(message, spinner=spinner)
        except Exception as e:
            self.logger.error(f"Rich status display failed: {e}")
            print(f"Status: {message}")
            return None

    def _format_simple_table(
        self, data: List[List[str]], title: Optional[str] = None
    ) -> str:
        """Fallback simple table formatting."""
        if not data:
            return title or "Empty Table"

        result = []
        if title:
            result.append(title)
            result.append("-" * len(title))

        for row in data:
            result.append(" | ".join(row))

        return "\n".join(result)


class RichProgressTracker:
    """Rich-based progress tracker."""

    def __init__(self, console: Console):
        self.console = console
        self.progress = None
        self.tasks = {}

    def start(self) -> None:
        """Start the progress tracker."""
        if RICH_AVAILABLE:
            self.progress = Progress()
            self.progress.start()

    def stop(self) -> None:
        """Stop the progress tracker."""
        if self.progress:
            self.progress.stop()
            self.progress = None

    def add_task(self, description: str, total: int = 100) -> str:
        """Add a new task to track."""
        if not self.progress:
            return f"task_{len(self.tasks)}"

        task_id = self.progress.add_task(description, total=total)
        task_key = f"task_{task_id}"
        self.tasks[task_key] = task_id
        return task_key

    def update(
        self, task_key: str, advance: int = 0, completed: Optional[int] = None
    ) -> None:
        """Update task progress."""
        if not self.progress or task_key not in self.tasks:
            return

        task_id = self.tasks[task_key]
        if completed is not None:
            self.progress.update(task_id, completed=completed)
        else:
            self.progress.advance(task_id, advance)

    def complete(self, task_key: str) -> None:
        """Mark task as complete."""
        if not self.progress or task_key not in self.tasks:
            return

        task_id = self.tasks[task_key]
        self.progress.update(task_id, completed=100)


class MockUIProvider(UIProvider):
    """Mock UI provider for testing."""

    def __init__(self):
        self.messages = []
        self.tables = []
        self.panels = []

    def is_available(self) -> bool:
        """Mock provider is always available."""
        return True

    def get_config(self) -> Dict[str, Any]:
        """Get mock provider configuration."""
        return {
            "provider": "mock",
            "available": True,
            "messages_count": len(self.messages),
        }

    def print_message(self, message: str, style: Optional[str] = None) -> None:
        """Mock print message."""
        self.messages.append({"message": message, "style": style})

    def create_progress_tracker(self) -> "MockProgressTracker":
        """Create a mock progress tracker."""
        return MockProgressTracker()

    def format_table(self, data: List[List[str]], title: Optional[str] = None) -> str:
        """Mock table formatting."""
        table_info = {"data": data, "title": title}
        self.tables.append(table_info)
        return f"Mock table: {title}" if title else "Mock table"


class MockProgressTracker:
    """Mock progress tracker for testing."""

    def __init__(self):
        self.tasks = {}
        self.started = False

    def start(self) -> None:
        """Mock start."""
        self.started = True

    def stop(self) -> None:
        """Mock stop."""
        self.started = False

    def add_task(self, description: str, total: int = 100) -> str:
        """Mock add task."""
        task_key = f"mock_task_{len(self.tasks)}"
        self.tasks[task_key] = {
            "description": description,
            "total": total,
            "completed": 0,
        }
        return task_key

    def update(
        self, task_key: str, advance: int = 0, completed: Optional[int] = None
    ) -> None:
        """Mock update."""
        if task_key in self.tasks:
            if completed is not None:
                self.tasks[task_key]["completed"] = completed
            else:
                self.tasks[task_key]["completed"] += advance

    def complete(self, task_key: str) -> None:
        """Mock complete."""
        if task_key in self.tasks:
            self.tasks[task_key]["completed"] = self.tasks[task_key]["total"]
