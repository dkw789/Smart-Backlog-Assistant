"""Main application using pydantic-ai framework architecture."""

import argparse
import json
import sys
from datetime import datetime
from typing import Any, Dict, Optional

from src.agents.context_models import CoordinatorContext
from src.agents.coordinator import coordinator
from src.utils.exception_handler import handle_exceptions
from src.utils.logger_service import get_logger


class PydanticAIBacklogAssistant:
    """Smart Backlog Assistant using pydantic-ai framework."""

    def __init__(self):
        self.logger = get_logger(__name__)
        self.session_id = f"session_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

    @handle_exceptions("Process Meeting Notes", return_error_response=True)
    def process_meeting_notes(
        self, file_path: str, output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process meeting notes using pydantic-ai agents."""
        try:
            # Create coordinator context
            context = CoordinatorContext(
                session_id=self.session_id, coordination_strategy="document_focused"
            )

            # Execute document analysis workflow
            result = coordinator.run_sync(
                f"Execute comprehensive document analysis for meeting notes at {file_path}",
                deps=context,
            )

            # Process and structure the result
            processed_result = {
                "operation": "meeting_notes_processing",
                "source_file": file_path,
                "session_id": self.session_id,
                "timestamp": datetime.utcnow().isoformat(),
                "agent_framework": "pydantic-ai",
                "result": str(result),
                "success": True,
            }

            # Save output if path provided
            if output_path:
                with open(output_path, "w") as f:
                    json.dump(processed_result, f, indent=2)
                self.logger.info(f"Results saved to {output_path}")

            return processed_result

        except Exception as e:
            self.logger.error(f"Meeting notes processing failed: {str(e)}")
            return {
                "operation": "meeting_notes_processing",
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }

    @handle_exceptions("Analyze Backlog", return_error_response=True)
    def analyze_backlog(
        self, backlog_path: str, output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """Analyze backlog using pydantic-ai agents."""
        try:
            # Load backlog data
            with open(backlog_path) as f:
                backlog_data = json.load(f)

            # Extract items
            if isinstance(backlog_data, dict) and "items" in backlog_data:
                items = backlog_data["items"]
            elif isinstance(backlog_data, list):
                items = backlog_data
            else:
                raise ValueError("Invalid backlog format")

            # Create coordinator context
            context = CoordinatorContext(
                session_id=self.session_id, coordination_strategy="backlog_focused"
            )

            # Execute comprehensive analysis workflow
            input_data = {"backlog_items": items}
            result = coordinator.run_sync(
                f"Execute comprehensive backlog analysis for {len(items)} items",
                deps=context,
            )

            # Process and structure the result
            processed_result = {
                "operation": "backlog_analysis",
                "source_file": backlog_path,
                "session_id": self.session_id,
                "timestamp": datetime.utcnow().isoformat(),
                "agent_framework": "pydantic-ai",
                "items_analyzed": len(items),
                "result": str(result),
                "success": True,
            }

            # Save output if path provided
            if output_path:
                with open(output_path, "w") as f:
                    json.dump(processed_result, f, indent=2)
                self.logger.info(f"Analysis saved to {output_path}")

            return processed_result

        except Exception as e:
            self.logger.error(f"Backlog analysis failed: {str(e)}")
            return {
                "operation": "backlog_analysis",
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }

    @handle_exceptions("Generate Sprint Plan", return_error_response=True)
    def generate_sprint_plan(
        self, backlog_path: str, capacity: int, output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate sprint plan using pydantic-ai agents."""
        try:
            # Load backlog data
            with open(backlog_path) as f:
                backlog_data = json.load(f)

            # Extract items
            if isinstance(backlog_data, dict) and "items" in backlog_data:
                items = backlog_data["items"]
            elif isinstance(backlog_data, list):
                items = backlog_data
            else:
                raise ValueError("Invalid backlog format")

            # Create coordinator context
            context = CoordinatorContext(
                session_id=self.session_id, coordination_strategy="sprint_planning"
            )

            # Execute priority assessment and sprint planning
            input_data = {"backlog_items": items, "sprint_capacity": capacity}
            result = coordinator.run_sync(
                f"Execute sprint planning workflow for {len(items)} items with capacity {capacity}",
                deps=context,
            )

            # Process and structure the result
            processed_result = {
                "operation": "sprint_planning",
                "source_file": backlog_path,
                "session_id": self.session_id,
                "timestamp": datetime.utcnow().isoformat(),
                "agent_framework": "pydantic-ai",
                "sprint_capacity": capacity,
                "items_considered": len(items),
                "result": str(result),
                "success": True,
            }

            # Save output if path provided
            if output_path:
                with open(output_path, "w") as f:
                    json.dump(processed_result, f, indent=2)
                self.logger.info(f"Sprint plan saved to {output_path}")

            return processed_result

        except Exception as e:
            self.logger.error(f"Sprint planning failed: {str(e)}")
            return {
                "operation": "sprint_planning",
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }

    @handle_exceptions("Process Requirements", return_error_response=True)
    def process_requirements_document(
        self, file_path: str, output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process requirements document using pydantic-ai agents."""
        try:
            # Create coordinator context
            context = CoordinatorContext(
                session_id=self.session_id, coordination_strategy="requirements_focused"
            )

            # Execute comprehensive requirements processing
            input_data = {"file_path": file_path, "requirements_text": ""}
            result = coordinator.run_sync(
                f"Execute comprehensive requirements analysis for {file_path}",
                deps=context,
            )

            # Process and structure the result
            processed_result = {
                "operation": "requirements_processing",
                "source_file": file_path,
                "session_id": self.session_id,
                "timestamp": datetime.utcnow().isoformat(),
                "agent_framework": "pydantic-ai",
                "result": str(result),
                "success": True,
            }

            # Save output if path provided
            if output_path:
                with open(output_path, "w") as f:
                    json.dump(processed_result, f, indent=2)
                self.logger.info(f"Requirements analysis saved to {output_path}")

            return processed_result

        except Exception as e:
            self.logger.error(f"Requirements processing failed: {str(e)}")
            return {
                "operation": "requirements_processing",
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }


def main():
    """Main CLI function for pydantic-ai Smart Backlog Assistant."""
    parser = argparse.ArgumentParser(
        description="Smart Backlog Assistant (Pydantic-AI Framework)"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Meeting notes command
    meeting_parser = subparsers.add_parser(
        "meeting-notes", help="Process meeting notes"
    )
    meeting_parser.add_argument("input_file", help="Path to meeting notes file")
    meeting_parser.add_argument("-o", "--output", help="Output file path")

    # Analyze backlog command
    analyze_parser = subparsers.add_parser(
        "analyze-backlog", help="Analyze backlog health"
    )
    analyze_parser.add_argument("backlog_file", help="Path to backlog JSON file")
    analyze_parser.add_argument("-o", "--output", help="Output file path")

    # Sprint plan command
    sprint_parser = subparsers.add_parser("sprint-plan", help="Generate sprint plan")
    sprint_parser.add_argument("backlog_file", help="Path to backlog JSON file")
    sprint_parser.add_argument(
        "--capacity", type=int, required=True, help="Sprint capacity in story points"
    )
    sprint_parser.add_argument("-o", "--output", help="Output file path")

    # Requirements command
    req_parser = subparsers.add_parser(
        "requirements", help="Process requirements document"
    )
    req_parser.add_argument("input_file", help="Path to requirements document")
    req_parser.add_argument("-o", "--output", help="Output file path")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Initialize assistant
    assistant = PydanticAIBacklogAssistant()

    try:
        if args.command == "meeting-notes":
            print("🔄 Processing meeting notes with pydantic-ai agents...")
            result = assistant.process_meeting_notes(args.input_file, args.output)

            if result.get("success"):
                print("✅ Meeting notes processed successfully!")
                print(f"📊 Session ID: {result.get('session_id')}")
                if args.output:
                    print(f"💾 Results saved to: {args.output}")
            else:
                print(f"❌ Error: {result.get('error')}")
                sys.exit(1)

        elif args.command == "analyze-backlog":
            print("🔄 Analyzing backlog with pydantic-ai agents...")
            result = assistant.analyze_backlog(args.backlog_file, args.output)

            if result.get("success"):
                print("✅ Backlog analysis completed!")
                print(f"📊 Items analyzed: {result.get('items_analyzed')}")
                print(f"🔍 Session ID: {result.get('session_id')}")
                if args.output:
                    print(f"💾 Analysis saved to: {args.output}")
            else:
                print(f"❌ Error: {result.get('error')}")
                sys.exit(1)

        elif args.command == "sprint-plan":
            print("🔄 Generating sprint plan with pydantic-ai agents...")
            result = assistant.generate_sprint_plan(
                args.backlog_file, args.capacity, args.output
            )

            if result.get("success"):
                print("✅ Sprint plan generated successfully!")
                print(f"📊 Capacity: {result.get('sprint_capacity')} story points")
                print(f"🔍 Items considered: {result.get('items_considered')}")
                print(f"🆔 Session ID: {result.get('session_id')}")
                if args.output:
                    print(f"💾 Sprint plan saved to: {args.output}")
            else:
                print(f"❌ Error: {result.get('error')}")
                sys.exit(1)

        elif args.command == "requirements":
            print("🔄 Processing requirements document with pydantic-ai agents...")
            result = assistant.process_requirements_document(
                args.input_file, args.output
            )

            if result.get("success"):
                print("✅ Requirements processed successfully!")
                print(f"🔍 Session ID: {result.get('session_id')}")
                if args.output:
                    print(f"💾 Analysis saved to: {args.output}")
            else:
                print(f"❌ Error: {result.get('error')}")
                sys.exit(1)

    except KeyboardInterrupt:
        print("\n⚠️ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
