"""Demo version of the Smart Backlog Assistant that works without API keys."""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from src.utils.caching_system import default_cache
from src.utils.logger_service import get_logger
from src.utils.rich_cli import RichCLIInterface


class DemoSmartBacklogAssistant:
    """Demo version of Smart Backlog Assistant without API dependencies."""

    def __init__(self):
        self.logger = get_logger(__name__)
        self.cli = RichCLIInterface()
        self.logger.info("Demo assistant initialized (no API keys required)")

    def run_interactive_mode(self):
        """Run interactive demo mode."""
        self.cli.show_welcome()

        while True:
            try:
                choice = self.cli.show_menu()

                if choice == "quit":
                    self.cli.console.print("[yellow]👋 Goodbye![/yellow]")
                    break
                elif choice == "status":
                    self._show_system_status()
                elif choice == "meeting-notes":
                    self._demo_meeting_notes()
                elif choice == "analyze-backlog":
                    self._demo_backlog_analysis()
                elif choice == "sprint-plan":
                    self._demo_sprint_planning()
                elif choice == "requirements":
                    self._demo_requirements_processing()
                elif choice == "interactive":
                    self._demo_workflow_builder()

            except KeyboardInterrupt:
                self.cli.console.print("\n[yellow]Operation cancelled by user[/yellow]")
                continue
            except Exception as e:
                self.cli.show_error(f"Demo error: {str(e)}")
                self.logger.error(f"Demo mode error: {str(e)}", exc_info=True)

    def _demo_meeting_notes(self):
        """Demo meeting notes processing."""
        self.cli.console.print(
            "\n[bold blue]📝 Meeting Notes Processing Demo[/bold blue]"
        )

        # Show available sample files
        sample_files = [
            "sample_data/complex_meeting_notes.md",
            "sample_data/simple_meeting.txt",
        ]

        self.cli.console.print("\n[cyan]Available sample files:[/cyan]")
        for i, file in enumerate(sample_files, 1):
            exists = "✅" if Path(file).exists() else "❌"
            self.cli.console.print(f"  {i}. {file} {exists}")

        file_choice = self.cli.console.input(
            "\nEnter file number or custom path: "
        ).strip()

        try:
            if file_choice.isdigit() and 1 <= int(file_choice) <= len(sample_files):
                file_path = sample_files[int(file_choice) - 1]
            else:
                file_path = file_choice

            # Demo processing steps
            steps = [
                {
                    "name": "Document Loading",
                    "description": f"Loading {file_path}",
                    "function": lambda: self._mock_document_loading(file_path),
                },
                {
                    "name": "Content Extraction",
                    "description": "Extracting text and structure",
                    "function": lambda: self._mock_content_extraction(),
                },
                {
                    "name": "Requirements Analysis",
                    "description": "Analyzing requirements and action items",
                    "function": lambda: self._mock_requirements_analysis(),
                },
                {
                    "name": "Story Generation",
                    "description": "Generating user stories",
                    "function": lambda: self._mock_story_generation(),
                },
            ]

            results = self.cli.workflow_runner.run_workflow(
                "Meeting Notes Processing", steps
            )

            if results["success"]:
                demo_result = {
                    "source_file": file_path,
                    "extracted_requirements": [
                        "User authentication system needed",
                        "Dashboard performance optimization required",
                        "Bug fixes for login issues",
                    ],
                    "generated_stories": [
                        {
                            "title": "User Authentication",
                            "narrative": "As a user, I want to login securely so that I can access my dashboard",
                            "acceptance_criteria": [
                                "Valid credentials accepted",
                                "Invalid credentials rejected",
                            ],
                        },
                        {
                            "title": "Dashboard Performance",
                            "narrative": "As a user, I want fast dashboard loading so that I can work efficiently",
                            "acceptance_criteria": [
                                "Page loads under 2 seconds",
                                "Responsive on mobile",
                            ],
                        },
                    ],
                    "processing_time": "2.3 seconds",
                    "framework": "Demo Mode",
                }

                self.cli.show_success(
                    "Meeting notes processed successfully!", demo_result
                )

                # Save demo output
                output_path = f"demo_output/meeting_notes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                os.makedirs("demo_output", exist_ok=True)
                with open(output_path, "w") as f:
                    json.dump(demo_result, f, indent=2)
                self.cli.console.print(
                    f"[green]Demo results saved to: {output_path}[/green]"
                )

        except Exception as e:
            self.cli.show_error(f"Demo processing failed: {str(e)}")

    def _demo_backlog_analysis(self):
        """Demo backlog analysis."""
        self.cli.console.print("\n[bold blue]📊 Backlog Analysis Demo[/bold blue]")

        # Mock backlog data
        demo_backlog = [
            {
                "title": "User Login",
                "priority": "high",
                "status": "todo",
                "story_points": 5,
            },
            {
                "title": "Dashboard UI",
                "priority": "medium",
                "status": "in_progress",
                "story_points": 8,
            },
            {
                "title": "Bug Fix",
                "priority": "high",
                "status": "todo",
                "story_points": 3,
            },
            {
                "title": "Performance",
                "priority": "low",
                "status": "todo",
                "story_points": 13,
            },
        ]

        steps = [
            {
                "name": "Backlog Loading",
                "description": "Loading backlog data",
                "function": lambda: {"items_loaded": len(demo_backlog)},
            },
            {
                "name": "Health Analysis",
                "description": "Analyzing backlog health metrics",
                "function": lambda: self._mock_health_analysis(),
            },
            {
                "name": "Recommendations",
                "description": "Generating improvement recommendations",
                "function": lambda: self._mock_recommendations(),
            },
        ]

        results = self.cli.workflow_runner.run_workflow("Backlog Analysis", steps)

        if results["success"]:
            demo_result = {
                "total_items": len(demo_backlog),
                "health_score": 72.5,
                "priority_distribution": {"high": 2, "medium": 1, "low": 1},
                "status_distribution": {"todo": 3, "in_progress": 1, "done": 0},
                "recommendations": [
                    "Add acceptance criteria to 75% of items",
                    "Break down large items (>8 points)",
                    "Balance priority distribution",
                    "Complete in-progress items before starting new ones",
                ],
                "framework": "Demo Mode",
            }

            self.cli.show_success("Backlog analysis completed!", demo_result)

    def _demo_sprint_planning(self):
        """Demo sprint planning."""
        self.cli.console.print("\n[bold blue]🏃 Sprint Planning Demo[/bold blue]")

        capacity = self.cli.console.input(
            "Sprint capacity (story points, default 40): "
        ).strip()
        capacity = int(capacity) if capacity.isdigit() else 40

        steps = [
            {
                "name": "Priority Assessment",
                "description": "Assessing item priorities",
                "function": lambda: {"items_assessed": 15},
            },
            {
                "name": "Capacity Planning",
                "description": f"Planning for {capacity} story points",
                "function": lambda: self._mock_sprint_planning(capacity),
            },
        ]

        results = self.cli.workflow_runner.run_workflow("Sprint Planning", steps)

        if results["success"]:
            selected_items = [
                {"title": "User Login", "story_points": 5, "priority": "high"},
                {"title": "Bug Fix", "story_points": 3, "priority": "high"},
                {"title": "Dashboard UI", "story_points": 8, "priority": "medium"},
            ]
            total_points = sum(item["story_points"] for item in selected_items)

            demo_result = {
                "sprint_capacity": capacity,
                "selected_items": selected_items,
                "total_effort_planned": total_points,
                "capacity_utilization": f"{(total_points/capacity*100):.1f}%",
                "framework": "Demo Mode",
            }

            self.cli.show_success("Sprint plan generated!", demo_result)

    def _demo_requirements_processing(self):
        """Demo requirements processing."""
        self.cli.console.print(
            "\n[bold blue]📋 Requirements Processing Demo[/bold blue]"
        )

        steps = [
            {
                "name": "Document Analysis",
                "description": "Analyzing requirements document",
                "function": lambda: {"sections_found": 5},
            },
            {
                "name": "Story Generation",
                "description": "Converting requirements to user stories",
                "function": lambda: {"stories_generated": 8},
            },
        ]

        results = self.cli.workflow_runner.run_workflow(
            "Requirements Processing", steps
        )

        if results["success"]:
            demo_result = {
                "requirements_extracted": 12,
                "user_stories_generated": 8,
                "acceptance_criteria_created": 24,
                "framework": "Demo Mode",
            }

            self.cli.show_success("Requirements processed!", demo_result)

    def _demo_workflow_builder(self):
        """Demo workflow builder."""
        self.cli.console.print(
            "\n[bold blue]🎯 Interactive Workflow Builder Demo[/bold blue]"
        )
        self.cli.console.print(
            "This would allow you to chain multiple operations together."
        )
        self.cli.console.print("In the full version, you can combine:")
        self.cli.console.print("  • Meeting notes processing")
        self.cli.console.print("  • Backlog analysis")
        self.cli.console.print("  • Sprint planning")
        self.cli.console.print("  • Requirements processing")
        self.cli.console.print(
            "\n[yellow]Demo: Workflow builder functionality shown[/yellow]"
        )

    def _show_system_status(self):
        """Show demo system status."""
        self.cli.console.print("\n[bold blue]📈 System Status (Demo Mode)[/bold blue]")

        system_info = {
            "mode": "Demo (No API keys required)",
            "framework": "Rich CLI + Caching System",
            "cache_enabled": True,
            "python_version": sys.version.split()[0],
            "dependencies_installed": "✅ Rich, Click, Caching",
            "api_keys_required": "❌ Not needed for demo",
        }

        self.cli.show_processing_status("Demo System Information", system_info)

        # Show cache stats
        cache_stats = default_cache.get_stats()
        cache_info = {
            "cache_hits": cache_stats["hits"],
            "cache_misses": cache_stats["misses"],
            "hit_rate": f"{cache_stats['hit_rate_percent']}%",
            "cache_size": cache_stats["cache_size"],
        }

        self.cli.show_processing_status("Cache Statistics", cache_info)

    def _mock_document_loading(self, file_path: str) -> Dict[str, Any]:
        """Mock document loading."""
        import time

        time.sleep(0.5)  # Simulate processing time
        return {"status": "loaded", "file": file_path, "size": "2.3 KB"}

    def _mock_content_extraction(self) -> Dict[str, Any]:
        """Mock content extraction."""
        import time

        time.sleep(0.8)
        return {"sections": 4, "action_items": 6, "participants": 3}

    def _mock_requirements_analysis(self) -> Dict[str, Any]:
        """Mock requirements analysis."""
        import time

        time.sleep(1.0)
        return {"requirements": 5, "priorities": "assigned", "categories": 3}

    def _mock_story_generation(self) -> Dict[str, Any]:
        """Mock story generation."""
        import time

        time.sleep(0.7)
        return {"stories": 3, "acceptance_criteria": 9, "quality_score": 85}

    def _mock_health_analysis(self) -> Dict[str, Any]:
        """Mock health analysis."""
        import time

        time.sleep(1.2)
        return {"health_score": 72.5, "issues_found": 3, "strengths": 5}

    def _mock_recommendations(self) -> Dict[str, Any]:
        """Mock recommendations generation."""
        import time

        time.sleep(0.6)
        return {"recommendations": 4, "priority_actions": 2, "timeline": "2 weeks"}

    def _mock_sprint_planning(self, capacity: int) -> Dict[str, Any]:
        """Mock sprint planning."""
        import time

        time.sleep(0.9)
        return {"capacity": capacity, "items_selected": 3, "utilization": "80%"}


def main():
    """Demo main function."""
    parser = argparse.ArgumentParser(
        description="Smart Backlog Assistant - Demo Mode (No API Keys Required)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Demo Examples:
  %(prog)s --interactive          # Start interactive demo mode
  %(prog)s --status              # Show system status
  %(prog)s --help                # Show this help message

Note: This is a demo version that doesn't require API keys.
For the full version with AI capabilities, set up your API keys:
  export OPENAI_API_KEY="your_key_here"
  export ANTHROPIC_API_KEY="your_key_here"
        """,
    )

    parser.add_argument(
        "--interactive",
        action="store_true",
        default=True,
        help="Start interactive demo mode (default)",
    )

    parser.add_argument("--status", action="store_true", help="Show system status")

    args = parser.parse_args()

    # Initialize demo assistant
    assistant = DemoSmartBacklogAssistant()

    try:
        if args.status:
            assistant._show_system_status()
        else:
            # Interactive mode (default)
            assistant.run_interactive_mode()

    except KeyboardInterrupt:
        assistant.cli.console.print("\n[yellow]👋 Demo cancelled by user[/yellow]")
        sys.exit(0)
    except Exception as e:
        assistant.cli.show_error(f"Demo error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
