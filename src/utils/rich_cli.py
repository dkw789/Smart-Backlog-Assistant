"""Rich CLI interface with progress tracking and interactive features."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from rich import box
from abc import ABC, abstractmethod
from typing import Protocol, Optional
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn, TaskID, BarColumn
from rich.prompt import Prompt
from rich.table import Table
from rich.text import Text
from rich.tree import Tree

from src.utils.logger_service import get_logger


class RichProgressTracker:
    """Rich progress tracker for multi-step operations."""

    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()
        self.progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=self.console,
        )
        self.tasks: Dict[str, TaskID] = {}
        self.logger = get_logger(__name__)

    def start_task(self, task_id: str, description: str, total: int = 100) -> TaskID:
        """Start a new progress task."""
        if not self.progress.live.is_started:
            self.progress.start()

        task = self.progress.add_task(description, total=total)
        self.tasks[task_id] = task
        return task

    def update_task(
        self, task_id: str, advance: int = 1, description: Optional[str] = None
    ):
        """Update task progress."""
        if task_id in self.tasks:
            kwargs = {"advance": advance}
            if description:
                kwargs["description"] = description
            self.progress.update(self.tasks[task_id], **kwargs)

    def complete_task(self, task_id: str, description: Optional[str] = None):
        """Complete a task."""
        if task_id in self.tasks:
            if description:
                self.progress.update(self.tasks[task_id], description=description)
            self.progress.update(self.tasks[task_id], completed=True)

    def stop(self):
        """Stop progress tracking."""
        if self.progress.live.is_started:
            self.progress.stop()


class InteractiveWorkflowRunner:
    """Interactive workflow runner with rich UI."""

    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()
        self.progress_tracker = RichProgressTracker(self.console)
        self.logger = get_logger(__name__)

    def run_workflow(
        self, workflow_name: str, steps: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Run interactive workflow with progress tracking."""
        self.console.print(
            Panel(
                f"[bold blue]Starting Workflow: {workflow_name}[/bold blue]",
                box=box.ROUNDED,
            )
        )

        results = {
            "workflow_name": workflow_name,
            "started_at": datetime.utcnow().isoformat(),
            "steps_completed": [],
            "results": {},
            "success": True,
        }

        # Start main progress task
        main_task = self.progress_tracker.start_task(
            "main", f"Executing {workflow_name}", len(steps)
        )

        try:
            for i, step in enumerate(steps):
                step_name = step.get("name", f"Step {i+1}")
                step_description = step.get("description", "Processing...")
                step_function = step.get("function")
                step_args = step.get("args", [])
                step_kwargs = step.get("kwargs", {})

                # Start step task
                step_task = self.progress_tracker.start_task(
                    f"step_{i}", f"{step_name}: {step_description}", 100
                )

                self.console.print(
                    f"\n[yellow]► {step_name}[/yellow]: {step_description}"
                )

                try:
                    # Execute step
                    if step_function:
                        step_result = step_function(*step_args, **step_kwargs)
                        results["results"][step_name] = step_result

                    # Complete step
                    self.progress_tracker.complete_task(
                        f"step_{i}", f"✅ {step_name} completed"
                    )
                    results["steps_completed"].append(step_name)

                    # Update main progress
                    self.progress_tracker.update_task("main", advance=1)

                except Exception as e:
                    self.console.print(f"[red]✗ {step_name} failed: {str(e)}[/red]")
                    results["success"] = False
                    results["error"] = str(e)
                    break

            # Complete workflow
            if results["success"]:
                self.progress_tracker.complete_task(
                    "main", "🎉 Workflow completed successfully"
                )
                self.console.print(
                    Panel(
                        "[bold green]Workflow completed successfully![/bold green]",
                        box=box.ROUNDED,
                    )
                )

        finally:
            self.progress_tracker.stop()
            results["completed_at"] = datetime.utcnow().isoformat()

        return results

    def show_results_summary(self, results: Dict[str, Any]):
        """Show workflow results summary."""
        table = Table(title="Workflow Results Summary", box=box.ROUNDED)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Workflow", results.get("workflow_name", "Unknown"))
        table.add_row("Status", "✅ Success" if results.get("success") else "❌ Failed")
        table.add_row("Steps Completed", str(len(results.get("steps_completed", []))))
        table.add_row("Started At", results.get("started_at", "Unknown"))
        table.add_row("Completed At", results.get("completed_at", "Unknown"))

        if not results.get("success") and results.get("error"):
            table.add_row("Error", results["error"])

        self.console.print(table)


class ConsoleProviderProtocol(Protocol):
    """Protocol for console providers."""
    
    def print(self, *args, **kwargs) -> None:
        """Print to console."""
        ...
    
    def input(self, prompt: str = "") -> str:
        """Get input from console."""
        ...


class RichCLIInterface:
    """Rich CLI interface for the Smart Backlog Assistant with provider injection."""

    def __init__(self, console_provider: Optional[ConsoleProviderProtocol] = None):
        self.console = console_provider or Console()
        self.workflow_runner = InteractiveWorkflowRunner(self.console)
        self.logger = get_logger(__name__)
        self.logger.info(f"RichCLIInterface initialized with console provider: {type(self.console).__name__}")

    def show_welcome(self):
        """Show welcome message."""
        welcome_text = Text()
        welcome_text.append("🚀 Smart Backlog Assistant", style="bold blue")
        welcome_text.append(
            "\nPowered by Pydantic-AI Multi-Agent Framework", style="italic"
        )

        panel = Panel(welcome_text, title="Welcome", box=box.DOUBLE, padding=(1, 2))

        self.console.print(panel)

    def show_menu(self) -> str:
        """Show interactive menu and get user choice."""
        self.console.print("\n[bold cyan]Available Operations:[/bold cyan]")

        options = [
            ("meeting-notes", "📝 Process Meeting Notes"),
            ("analyze-backlog", "📊 Analyze Backlog Health"),
            ("sprint-plan", "🏃 Generate Sprint Plan"),
            ("requirements", "📋 Process Requirements Document"),
            ("interactive", "🎯 Interactive Workflow Builder"),
            ("status", "📈 Show System Status"),
            ("quit", "❌ Exit"),
        ]

        table = Table(box=box.SIMPLE)
        table.add_column("Option", style="yellow")
        table.add_column("Description", style="white")

        for option, description in options:
            table.add_row(option, description)

        self.console.print(table)

        return Prompt.ask(
            "\n[bold]Choose an operation[/bold]",
            choices=[opt[0] for opt in options],
            default="interactive",
        )

    def get_file_input(self, prompt: str, file_types: List[str] = None) -> str:
        """Get file input with validation."""
        while True:
            file_path = Prompt.ask(prompt)

            if not file_path:
                self.console.print("[red]File path cannot be empty[/red]")
                continue

            # Basic validation
            from pathlib import Path

            path = Path(file_path)

            if not path.exists():
                self.console.print(f"[red]File not found: {file_path}[/red]")
                if not Confirm.ask("Continue anyway?"):
                    continue

            if file_types and path.suffix.lower() not in file_types:
                self.console.print(
                    f"[yellow]Warning: Expected file types: {', '.join(file_types)}[/yellow]"
                )
                if not Confirm.ask("Continue anyway?"):
                    continue

            return file_path

    def show_processing_status(self, operation: str, details: Dict[str, Any]):
        """Show processing status with rich formatting."""
        status_table = Table(title=f"{operation} Status", box=box.ROUNDED)
        status_table.add_column("Component", style="cyan")
        status_table.add_column("Status", style="green")
        status_table.add_column("Details", style="white")

        for key, value in details.items():
            if isinstance(value, bool):
                status = "✅ Active" if value else "❌ Inactive"
            elif isinstance(value, (int, float)):
                status = f"📊 {value}"
            else:
                status = str(value)[:50] + "..." if len(str(value)) > 50 else str(value)

            status_table.add_row(key.replace("_", " ").title(), status, "")

        self.console.print(status_table)

    def show_results_tree(self, results: Dict[str, Any], title: str = "Results"):
        """Show results in a tree format."""
        tree = Tree(f"[bold blue]{title}[/bold blue]")

        def add_to_tree(node, data, parent_key=""):
            if isinstance(data, dict):
                for key, value in data.items():
                    if isinstance(value, (dict, list)):
                        branch = node.add(f"[yellow]{key}[/yellow]")
                        add_to_tree(branch, value, key)
                    else:
                        display_value = (
                            str(value)[:100] + "..."
                            if len(str(value)) > 100
                            else str(value)
                        )
                        node.add(f"[cyan]{key}[/cyan]: {display_value}")
            elif isinstance(data, list):
                for i, item in enumerate(data[:10]):  # Limit to first 10 items
                    if isinstance(item, (dict, list)):
                        branch = node.add(f"[yellow]Item {i+1}[/yellow]")
                        add_to_tree(branch, item, f"item_{i}")
                    else:
                        display_value = (
                            str(item)[:100] + "..."
                            if len(str(item)) > 100
                            else str(item)
                        )
                        node.add(f"[white]{display_value}[/white]")

                if len(data) > 10:
                    node.add(f"[dim]... and {len(data) - 10} more items[/dim]")

        add_to_tree(tree, results)
        self.console.print(tree)

    def confirm_operation(self, operation: str, details: Dict[str, Any]) -> bool:
        """Confirm operation with user."""
        self.console.print(f"\n[bold yellow]Confirm {operation}:[/bold yellow]")

        for key, value in details.items():
            self.console.print(
                f"  • {key.replace('_', ' ').title()}: [cyan]{value}[/cyan]"
            )

        return Confirm.ask("\nProceed with this operation?", default=True)

    def show_error(self, error: str, details: Optional[Dict[str, Any]] = None):
        """Show error with rich formatting."""
        error_panel = Panel(
            f"[bold red]Error:[/bold red] {error}",
            title="❌ Operation Failed",
            box=box.ROUNDED,
            border_style="red",
        )

        self.console.print(error_panel)

        if details:
            self.console.print("\n[dim]Error Details:[/dim]")
            for key, value in details.items():
                self.console.print(f"  • {key}: {value}")

    def show_success(self, message: str, details: Optional[Dict[str, Any]] = None):
        """Show success message with rich formatting."""
        success_panel = Panel(
            f"[bold green]Success:[/bold green] {message}",
            title="✅ Operation Completed",
            box=box.ROUNDED,
            border_style="green",
        )

        self.console.print(success_panel)

        if details:
            self.show_results_tree(details, "Operation Results")


# Global rich CLI instance
rich_cli = RichCLIInterface()
