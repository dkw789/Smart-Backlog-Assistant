"""Unified main application combining sync and async capabilities."""

import argparse
import asyncio
import logging
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from src.config import config
from src.generators.priority_engine import PriorityEngine
from src.generators.user_story_generator import UserStoryGenerator
from src.processors.ai_processor import AIProcessor
from src.processors.ai_processor_async import AsyncAIProcessor
from src.processors.backlog_analyzer import BacklogAnalyzer
from src.processors.document_processor import DocumentProcessor
from src.utils.caching_system import ai_response_cache, default_cache
from src.utils.enhanced_error_handler import resilient_service_manager, CircuitBreakerConfig
from src.utils.file_handler import FileHandler
from src.utils.logger_service import get_logger
from src.utils.rich_cli import RichCLIInterface
from src.utils.validators import InputValidator


class UnifiedSmartBacklogAssistant:
    """Unified Smart Backlog Assistant with both sync and async capabilities."""

    def __init__(
        self, 
        use_async: bool = True, 
        enable_caching: bool = True,
        use_rich_cli: bool = True
    ):
        self.use_async = use_async
        self.enable_caching = enable_caching
        self.use_rich_cli = use_rich_cli
        
        self.setup_logging()
        self.logger = get_logger(__name__)
        
        # Initialize components
        self.document_processor = DocumentProcessor()
        self.backlog_analyzer = BacklogAnalyzer()
        self.story_generator = UserStoryGenerator()
        self.priority_engine = PriorityEngine()
        self.file_handler = FileHandler()
        
        # Initialize AI processor (sync or async)
        if use_async:
            self.ai_processor = None  # Will be initialized in async context
            self.async_ai_processor = None  # Will be created when needed
        else:
            self.ai_processor = AIProcessor()
            self.async_ai_processor = None
        
        # Initialize CLI if requested
        if use_rich_cli:
            self.cli = RichCLIInterface()
        else:
            self.cli = None
        
        # Register services for resilience
        self._register_services()
        
        self.logger.info(
            f"Unified assistant initialized (async: {use_async}, "
            f"caching: {enable_caching}, rich_cli: {use_rich_cli})"
        )

    def setup_logging(self) -> None:
        """Setup logging configuration."""
        log_level = config.log_level.upper()
        logging.basicConfig(
            level=getattr(logging, log_level),
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler(config.log_file),
            ],
        )

    def _register_services(self) -> None:
        """Register services with circuit breakers."""
        # AI services with different thresholds
        ai_config = CircuitBreakerConfig(
            failure_threshold=3, recovery_timeout=120.0, success_threshold=2
        )

        resilient_service_manager.register_service("openai", ai_config)
        resilient_service_manager.register_service("anthropic", ai_config)
        resilient_service_manager.register_service("document_processing", ai_config)

    async def process_meeting_notes_async(
        self, file_path: str, output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process meeting notes asynchronously."""
        self.logger.info(f"Processing meeting notes from: {file_path}")

        try:
            # Process document (sync operation)
            processed_doc = self.document_processor.process_document(file_path)

            if not processed_doc.processing_success:
                raise ValueError(
                    f"Failed to process document: {processed_doc.error_message}"
                )

            # Extract requirements using async AI
            async with AsyncAIProcessor() as async_ai:
                ai_response = await async_ai.extract_requirements(processed_doc.content)

                if not ai_response.success:
                    raise ValueError(f"AI processing failed: {ai_response.error_message}")

                # Generate user stories asynchronously
                user_stories_response = await async_ai.generate_user_stories(
                    ai_response.content
                )

            # Create output structure
            output = {
                "source_file": file_path,
                "processing_timestamp": processed_doc.metadata,
                "extracted_requirements": ai_response.content,
                "user_stories_raw": user_stories_response.content if user_stories_response.success else "",
                "ai_service_used": ai_response.service_used,
                "processing_time": ai_response.processing_time,
                "async_processing": True,
            }

            # Save output if path provided
            if output_path:
                self.file_handler.write_json_file(output_path, output)
                self.logger.info(f"Output saved to: {output_path}")

            return output

        except Exception as e:
            self.logger.error(f"Error processing meeting notes: {str(e)}")
            raise

    def process_meeting_notes_sync(
        self, file_path: str, output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process meeting notes synchronously."""
        self.logger.info(f"Processing meeting notes from: {file_path}")

        try:
            # Process document
            processed_doc = self.document_processor.process_document(file_path)

            if not processed_doc.processing_success:
                raise ValueError(
                    f"Failed to process document: {processed_doc.error_message}"
                )

            # Extract requirements using AI
            ai_response = self.ai_processor.extract_requirements(processed_doc.content)

            if not ai_response.success:
                raise ValueError(f"AI processing failed: {ai_response.error_message}")

            # Generate user stories
            user_stories = self.story_generator.generate_stories_from_requirements(
                ai_response.content
            )

            # Create output structure
            output = {
                "source_file": file_path,
                "processing_timestamp": processed_doc.metadata,
                "extracted_requirements": ai_response.content,
                "user_stories": [
                    self._user_story_to_dict(story) for story in user_stories
                ],
                "ai_service_used": ai_response.service_used,
                "processing_time": ai_response.processing_time,
                "async_processing": False,
            }

            # Save output if path provided
            if output_path:
                self.file_handler.write_json_file(output_path, output)
                self.logger.info(f"Output saved to: {output_path}")

            return output

        except Exception as e:
            self.logger.error(f"Error processing meeting notes: {str(e)}")
            raise

    async def analyze_backlog_async(
        self, backlog_file: str, output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """Analyze existing backlog asynchronously."""
        self.logger.info(f"Analyzing backlog from: {backlog_file}")

        try:
            # Read backlog data (sync operation)
            items = self._load_backlog_data(backlog_file)

            # Analyze backlog structure (sync operation)
            analysis = self.backlog_analyzer.analyze_backlog_data(items)

            # Get AI recommendations and priority assessments concurrently
            async with AsyncAIProcessor() as async_ai:
                # Process multiple items concurrently
                ai_analysis_task = async_ai.analyze_backlog_items(items)
                priority_tasks = async_ai.process_multiple_items_concurrently(
                    [{"description": item.get("description", "")} for item in items],
                    "assess_priority"
                )

                # Wait for both to complete
                ai_analysis, priority_responses = await asyncio.gather(
                    ai_analysis_task, priority_tasks
                )

            # Create comprehensive output
            output = {
                "source_file": backlog_file,
                "analysis_summary": {
                    "total_items": analysis.total_items,
                    "health_score": analysis.health_score,
                    "items_by_priority": analysis.items_by_priority,
                    "items_by_status": analysis.items_by_status,
                },
                "missing_information": analysis.missing_information,
                "recommendations": analysis.recommendations,
                "ai_insights": (
                    ai_analysis.content if ai_analysis.success else "AI analysis unavailable"
                ),
                "priority_assessments": [
                    {
                        "item_index": i,
                        "success": resp.success,
                        "assessment": resp.content if resp.success else resp.error_message,
                        "processing_time": resp.processing_time,
                    }
                    for i, resp in enumerate(priority_responses)
                ],
                "enhanced_items": self.backlog_analyzer.enhance_backlog_items(items),
                "async_processing": True,
                "concurrent_processing_count": len(priority_responses),
            }

            # Save output if path provided
            if output_path:
                self.file_handler.write_json_file(output_path, output)
                self.logger.info(f"Analysis saved to: {output_path}")

            return output

        except Exception as e:
            self.logger.error(f"Error analyzing backlog: {str(e)}")
            raise

    def _load_backlog_data(self, backlog_file: str) -> List[Dict[str, Any]]:
        """Load backlog data from file."""
        if self.file_handler.get_file_type(backlog_file) == "json":
            backlog_data = self.file_handler.read_json_file(backlog_file)
            if isinstance(backlog_data, dict) and "items" in backlog_data:
                return backlog_data["items"]
            elif isinstance(backlog_data, list):
                return backlog_data
            else:
                return [backlog_data]
        else:
            # Try to extract from text content
            content = self.file_handler.read_file_content(backlog_file)
            return self.backlog_analyzer.extract_backlog_from_json(content)

    def _user_story_to_dict(self, story) -> Dict[str, Any]:
        """Convert UserStory object to dictionary."""
        return {
            "title": story.title,
            "user_type": story.user_type,
            "functionality": story.functionality,
            "benefit": story.benefit,
            "acceptance_criteria": [
                ac.model_dump() if hasattr(ac, "model_dump") else ac
                for ac in story.acceptance_criteria
            ],
            "priority": story.priority,
            "estimated_effort": story.estimated_effort,
            "tags": story.tags,
            "original_requirement": story.original_requirement,
        }

    async def run_interactive_mode_async(self):
        """Run interactive mode with async processing."""
        if not self.cli:
            raise ValueError("Rich CLI not initialized. Set use_rich_cli=True")

        self.cli.show_welcome()

        while True:
            try:
                choice = self.cli.show_menu()

                if choice == "quit":
                    self.cli.console.print("[yellow]👋 Goodbye![/yellow]")
                    break
                elif choice == "meeting-notes":
                    await self._interactive_meeting_notes_async()
                elif choice == "analyze-backlog":
                    await self._interactive_backlog_analysis_async()
                elif choice == "status":
                    self._show_system_status()

            except KeyboardInterrupt:
                self.cli.console.print("\n[yellow]Operation cancelled by user[/yellow]")
                continue
            except Exception as e:
                self.cli.show_error(f"Unexpected error: {str(e)}")
                self.logger.error(f"Interactive mode error: {str(e)}", exc_info=True)

    async def _interactive_meeting_notes_async(self):
        """Interactive meeting notes processing with async."""
        file_path = self.cli.get_file_input(
            "📝 Enter path to meeting notes file:", [".txt", ".md", ".pdf", ".docx"]
        )

        output_path = self.cli.console.input("💾 Output file path (optional): ").strip()
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"output/meeting_notes_async_{timestamp}.json"

        # Confirm operation
        details = {
            "input_file": file_path,
            "output_file": output_path,
            "processing_mode": "Async (faster)",
            "caching_enabled": self.enable_caching,
        }

        if not self.cli.confirm_operation("Meeting Notes Processing", details):
            return

        # Process with progress tracking
        try:
            steps = [
                {
                    "name": "Document Analysis",
                    "description": "Extracting content and structure",
                    "function": lambda: self._process_with_caching_async(
                        "meeting_notes",
                        lambda: self.process_meeting_notes_async(file_path, output_path),
                        file_path,
                    ),
                }
            ]

            # Since we can't easily make the workflow runner async, we'll process directly
            self.cli.console.print("\n[yellow]► Processing meeting notes...[/yellow]")
            
            start_time = datetime.now()
            result = await self.process_meeting_notes_async(file_path, output_path)
            end_time = datetime.now()
            
            processing_time = (end_time - start_time).total_seconds()
            
            self.cli.show_success(
                f"Meeting notes processed in {processing_time:.2f}s!", 
                {
                    "requirements_extracted": len(result.get("extracted_requirements", "")),
                    "ai_service": result.get("ai_service_used", "unknown"),
                    "output_file": output_path,
                }
            )

        except Exception as e:
            self.cli.show_error(f"Processing failed: {str(e)}")
            self.logger.error(f"Meeting notes processing error: {str(e)}", exc_info=True)

    async def _interactive_backlog_analysis_async(self):
        """Interactive backlog analysis with async."""
        file_path = self.cli.get_file_input(
            "📊 Enter path to backlog JSON file:", [".json"]
        )

        output_path = self.cli.console.input("💾 Output file path (optional): ").strip()
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"output/backlog_analysis_async_{timestamp}.json"

        # Confirm operation
        details = {
            "input_file": file_path,
            "output_file": output_path,
            "processing_mode": "Async with concurrent AI calls",
            "analysis_type": "Comprehensive health analysis",
        }

        if not self.cli.confirm_operation("Backlog Analysis", details):
            return

        # Process with progress tracking
        try:
            self.cli.console.print("\n[yellow]► Processing backlog analysis...[/yellow]")
            
            start_time = datetime.now()
            result = await self.analyze_backlog_async(file_path, output_path)
            end_time = datetime.now()
            
            processing_time = (end_time - start_time).total_seconds()
            
            self.cli.show_success(
                f"Backlog analysis completed in {processing_time:.2f}s!", 
                {
                    "total_items": result["analysis_summary"]["total_items"],
                    "health_score": f"{result['analysis_summary']['health_score']:.1f}%",
                    "concurrent_assessments": result.get("concurrent_processing_count", 0),
                    "output_file": output_path,
                }
            )

        except Exception as e:
            self.cli.show_error(f"Analysis failed: {str(e)}")
            self.logger.error(f"Backlog analysis error: {str(e)}", exc_info=True)

    def run_interactive_mode_sync(self):
        """Run interactive mode with sync processing."""
        if not self.cli:
            raise ValueError("Rich CLI not initialized. Set use_rich_cli=True")

        self.cli.show_welcome()

        while True:
            try:
                choice = self.cli.show_menu()

                if choice == "quit":
                    self.cli.console.print("[yellow]👋 Goodbye![/yellow]")
                    break
                elif choice == "meeting-notes":
                    self._interactive_meeting_notes_sync()
                elif choice == "analyze-backlog":
                    self._interactive_backlog_analysis_sync()
                elif choice == "status":
                    self._show_system_status()

            except KeyboardInterrupt:
                self.cli.console.print("\n[yellow]Operation cancelled by user[/yellow]")
                continue
            except Exception as e:
                self.cli.show_error(f"Unexpected error: {str(e)}")
                self.logger.error(f"Interactive mode error: {str(e)}", exc_info=True)

    def _interactive_meeting_notes_sync(self):
        """Interactive meeting notes processing with sync."""
        file_path = self.cli.get_file_input(
            "📝 Enter path to meeting notes file:", [".txt", ".md", ".pdf", ".docx"]
        )

        output_path = self.cli.console.input("💾 Output file path (optional): ").strip()
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"output/meeting_notes_sync_{timestamp}.json"

        # Confirm operation
        details = {
            "input_file": file_path,
            "output_file": output_path,
            "processing_mode": "Sync (standard)",
            "caching_enabled": self.enable_caching,
        }

        if not self.cli.confirm_operation("Meeting Notes Processing", details):
            return

        # Process with progress tracking
        try:
            self.cli.console.print("\n[yellow]► Processing meeting notes...[/yellow]")
            
            start_time = datetime.now()
            result = self.process_meeting_notes_sync(file_path, output_path)
            end_time = datetime.now()
            
            processing_time = (end_time - start_time).total_seconds()
            
            self.cli.show_success(
                f"Meeting notes processed in {processing_time:.2f}s!", 
                {
                    "requirements_extracted": len(result.get("extracted_requirements", "")),
                    "ai_service": result.get("ai_service_used", "unknown"),
                    "output_file": output_path,
                }
            )

        except Exception as e:
            self.cli.show_error(f"Processing failed: {str(e)}")
            self.logger.error(f"Meeting notes processing error: {str(e)}", exc_info=True)

    def _interactive_backlog_analysis_sync(self):
        """Interactive backlog analysis with sync."""
        file_path = self.cli.get_file_input(
            "📊 Enter path to backlog JSON file:", [".json"]
        )

        output_path = self.cli.console.input("💾 Output file path (optional): ").strip()
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"output/backlog_analysis_sync_{timestamp}.json"

        # Confirm operation
        details = {
            "input_file": file_path,
            "output_file": output_path,
            "processing_mode": "Sync (sequential processing)",
            "analysis_type": "Comprehensive health analysis",
        }

        if not self.cli.confirm_operation("Backlog Analysis", details):
            return

        # Process with progress tracking
        try:
            self.cli.console.print("\n[yellow]► Processing backlog analysis...[/yellow]")
            
            start_time = datetime.now()
            result = self.analyze_backlog_sync(file_path, output_path)
            end_time = datetime.now()
            
            processing_time = (end_time - start_time).total_seconds()
            
            self.cli.show_success(
                f"Backlog analysis completed in {processing_time:.2f}s!", 
                {
                    "total_items": result["analysis_summary"]["total_items"],
                    "health_score": f"{result['analysis_summary']['health_score']:.1f}%",
                    "processing_mode": "Sequential",
                    "output_file": output_path,
                }
            )

        except Exception as e:
            self.cli.show_error(f"Analysis failed: {str(e)}")
            self.logger.error(f"Backlog analysis error: {str(e)}", exc_info=True)

    def _show_system_status(self):
        """Show comprehensive system status."""
        if not self.cli:
            return
            
        self.cli.console.print("\n[bold blue]📈 System Status[/bold blue]")

        # Service status
        service_status = resilient_service_manager.get_service_status()
        self.cli.show_processing_status("Circuit Breaker Status", service_status)

        # Cache statistics
        if self.enable_caching:
            cache_stats = default_cache.get_stats()
            ai_cache_stats = ai_response_cache.cache.get_stats()

            cache_info = {
                "default_cache_hit_rate": f"{cache_stats['hit_rate_percent']}%",
                "default_cache_size": cache_stats["cache_size"],
                "ai_cache_hit_rate": f"{ai_cache_stats['hit_rate_percent']}%",
                "ai_cache_size": ai_cache_stats["cache_size"],
                "total_cache_hits": cache_stats["hits"] + ai_cache_stats["hits"],
            }

            self.cli.show_processing_status("Cache Statistics", cache_info)

        # System info
        system_info = {
            "processing_mode": "Async" if self.use_async else "Sync",
            "caching_enabled": self.enable_caching,
            "rich_cli_enabled": self.use_rich_cli,
            "python_version": sys.version.split()[0],
            "config_validation": config.validate_ai_services(),
        }

        self.cli.show_processing_status("System Information", system_info)

    async def _process_with_caching_async(
        self, operation_type: str, func_async, cache_key_suffix: str = "", input_data: str = ""
    ):
        """Process async operation with intelligent caching."""
        if not self.enable_caching:
            return await func_async()

        # Create stable cache key based on input data instead of function object
        import hashlib
        input_hash = hashlib.sha256(f"{operation_type}_{cache_key_suffix}_{input_data}".encode()).hexdigest()[:16]
        cache_key = f"{operation_type}_{input_hash}"

        # Try to get from cache
        cached_result = default_cache.get(cache_key)
        if cached_result:
            self.logger.info(f"Using cached result for {operation_type}")
            return cached_result

        # Execute async and cache
        result = await func_async()
        default_cache.set(cache_key, result, ttl=config.cache_ttl_seconds, tags=[operation_type])

        return result

    async def generate_sprint_plan_async(self, backlog_file: str, capacity: int = 40, output_path: Optional[str] = None) -> Dict[str, Any]:
        """Generate sprint plan asynchronously."""
        return await self._process_with_caching_async(
            "sprint_plan",
            lambda: self._generate_sprint_plan_impl_async(backlog_file, capacity, output_path),
            f"sprint_{backlog_file}_{capacity}",
            backlog_file
        )

    def generate_sprint_plan_sync(self, backlog_file: str, capacity: int = 40, output_path: Optional[str] = None) -> Dict[str, Any]:
        """Generate sprint plan synchronously."""
        return self._generate_sprint_plan_impl_sync(backlog_file, capacity, output_path)

    async def _generate_sprint_plan_impl_async(self, backlog_file: str, capacity: int, output_path: Optional[str] = None) -> Dict[str, Any]:
        """Async sprint plan implementation."""
        # Load and analyze backlog
        backlog_data = self._load_backlog_data(backlog_file)
        analysis = self.backlog_analyzer.analyze_backlog_data(backlog_data)
        
        # Generate sprint plan using priority engine
        sprint_items = self.priority_engine.recommend_sprint_items(backlog_data, capacity)
        
        # Convert non-serializable objects to dictionaries for JSON serialization
        def serialize_item(item):
            def serialize_obj(obj):
                # Handle enums specifically
                if hasattr(obj, 'value') and hasattr(obj, 'name'):
                    return obj.value
                elif hasattr(obj, "__dict__"):
                    return obj.__dict__
                elif isinstance(obj, dict):
                    return {k: serialize_obj(v) for k, v in obj.items()}
                elif isinstance(obj, (list, tuple)):
                    return [serialize_obj(item) for item in obj]
                else:
                    return str(obj)  # Fallback to string representation
            
            item_dict = item.copy()
            for key, value in item_dict.items():
                item_dict[key] = serialize_obj(value)
            return item_dict
        
        sprint_items_serializable = [serialize_item(item) for item in sprint_items]
        
        result = {
            "sprint_items": sprint_items_serializable,
            "capacity": capacity,
            "total_points": sum(item.get("story_points", 0) for item in sprint_items),
            "backlog_analysis": analysis,
            "generated_at": datetime.utcnow().isoformat()
        }
        
        # Save output if specified
        if output_path:
            self.file_handler.write_json_file(output_path, result)
            
        return result

    def _generate_sprint_plan_impl_sync(self, backlog_file: str, capacity: int, output_path: Optional[str] = None) -> Dict[str, Any]:
        """Sync sprint plan implementation."""
        # Load and analyze backlog
        backlog_data = self._load_backlog_data(backlog_file)
        analysis = self.backlog_analyzer.analyze_backlog_data(backlog_data)
        
        # Generate sprint plan using priority engine
        sprint_items = self.priority_engine.recommend_sprint_items(backlog_data, capacity)
        
        # Convert non-serializable objects to dictionaries for JSON serialization
        def serialize_item(item):
            def serialize_obj(obj):
                # Handle enums specifically
                if hasattr(obj, 'value') and hasattr(obj, 'name'):
                    return obj.value
                elif hasattr(obj, "__dict__"):
                    return obj.__dict__
                elif isinstance(obj, dict):
                    return {k: serialize_obj(v) for k, v in obj.items()}
                elif isinstance(obj, (list, tuple)):
                    return [serialize_obj(item) for item in obj]
                else:
                    return str(obj)  # Fallback to string representation
            
            item_dict = item.copy()
            for key, value in item_dict.items():
                item_dict[key] = serialize_obj(value)
            return item_dict
        
        sprint_items_serializable = [serialize_item(item) for item in sprint_items]
        
        result = {
            "sprint_items": sprint_items_serializable,
            "capacity": capacity,
            "total_points": sum(item.get("story_points", 0) for item in sprint_items),
            "backlog_analysis": analysis,
            "generated_at": datetime.utcnow().isoformat()
        }
        
        # Save output if specified
        if output_path:
            self.file_handler.write_json_file(output_path, result)
            
        return result

    async def process_requirements_async(self, requirements_file: str, output_path: Optional[str] = None) -> Dict[str, Any]:
        """Process requirements document asynchronously."""
        return await self._process_with_caching_async(
            "requirements",
            lambda: self._process_requirements_impl_async(requirements_file, output_path),
            f"requirements_{requirements_file}",
            requirements_file
        )

    def process_requirements_sync(self, requirements_file: str, output_path: Optional[str] = None) -> Dict[str, Any]:
        """Process requirements document synchronously."""
        return self._process_requirements_impl_sync(requirements_file, output_path)

    async def _process_requirements_impl_async(self, requirements_file: str, output_path: Optional[str] = None) -> Dict[str, Any]:
        """Async requirements processing implementation."""
        # Read requirements file
        with open(requirements_file, 'r', encoding='utf-8') as f:
            requirements_content = f.read()
        
        # Process using async AI processor
        async with AsyncAIProcessor() as async_ai:
            # Extract requirements using AI
            requirements = await async_ai.extract_requirements(requirements_content)
            
            # Generate user stories from requirements
            user_stories = await async_ai.generate_user_stories(requirements.content)
        
        result = {
            "requirements": requirements.content,
            "user_stories": user_stories.content,
            "source_file": requirements_file,
            "processed_at": datetime.utcnow().isoformat(),
            "summary": {
                "total_requirements": len(requirements.content) if isinstance(requirements.content, list) else 1,
                "total_user_stories": len(user_stories.content) if isinstance(user_stories.content, list) else 1
            }
        }
        
        # Save output if specified
        if output_path:
            self.file_handler.write_json_file(output_path, result)
            
        return result

    def _process_requirements_impl_sync(self, requirements_file: str, output_path: Optional[str] = None) -> Dict[str, Any]:
        """Sync requirements processing implementation."""
        # Read requirements file
        with open(requirements_file, 'r', encoding='utf-8') as f:
            requirements_content = f.read()
        
        # Extract requirements using AI
        requirements = self.ai_processor.extract_requirements(requirements_content)
        
        # Generate user stories from requirements
        user_stories = self.user_story_generator.generate_user_stories(requirements.content)
        
        result = {
            "requirements": requirements.content,
            "user_stories": user_stories.content,
            "source_file": requirements_file,
            "processed_at": datetime.utcnow().isoformat(),
            "summary": {
                "total_requirements": len(requirements.content) if isinstance(requirements.content, list) else 1,
                "total_user_stories": len(user_stories.content) if isinstance(user_stories.content, list) else 1
            }
        }
        
        # Save output if specified
        if output_path:
            self.file_handler.write_json_file(output_path, result)
            
        return result


async def main_async():
    """Async main function."""
    parser = argparse.ArgumentParser(description="Unified Smart Backlog Assistant")
    parser.add_argument(
        "command",
        nargs="?",
        choices=["meeting-notes", "analyze-backlog", "sprint-plan", "requirements", "interactive"],
        default="interactive",
        help="Command to execute",
    )
    parser.add_argument("input_file", nargs="?", help="Input file path")
    parser.add_argument("-o", "--output", help="Output file path")
    parser.add_argument("--sync", action="store_true", help="Use synchronous processing")
    parser.add_argument("--no-cache", action="store_true", help="Disable caching")
    parser.add_argument("--no-cli", action="store_true", help="Disable rich CLI")
    parser.add_argument("--capacity", type=int, default=40, help="Sprint capacity for sprint-plan command")

    args = parser.parse_args()

    assistant = UnifiedSmartBacklogAssistant(
        use_async=not args.sync,
        enable_caching=not args.no_cache,
        use_rich_cli=not args.no_cli
    )

    try:
        if args.command == "interactive":
            if assistant.use_async:
                await assistant.run_interactive_mode_async()
            else:
                assistant.run_interactive_mode_sync()
                
        elif args.command == "meeting-notes":
            if not args.input_file:
                print("Error: input_file required for meeting-notes command")
                return
                
            if assistant.use_async:
                result = await assistant.process_meeting_notes_async(args.input_file, args.output)
            else:
                result = assistant.process_meeting_notes_sync(args.input_file, args.output)
                
            print(f"✅ Processed meeting notes. Output saved to: {args.output or 'console'}")
            
        elif args.command == "analyze-backlog":
            if not args.input_file:
                print("Error: input_file required for analyze-backlog command")
                return
                
            if assistant.use_async:
                result = await assistant.analyze_backlog_async(args.input_file, args.output)
                print(f"✅ Analyzed backlog. Health score: {result['analysis_summary']['health_score']:.1f}/100")
            else:
                result = assistant.analyze_backlog_sync(args.input_file, args.output)
                print(f"✅ Analyzed backlog. Health score: {result['analysis_summary']['health_score']:.1f}/100")
                
        elif args.command == "sprint-plan":
            if not args.input_file:
                print("Error: input_file required for sprint-plan command")
                return
                
            # Extract capacity from args or use default
            capacity = getattr(args, 'capacity', 40)
            
            if assistant.use_async:
                result = await assistant.generate_sprint_plan_async(args.input_file, capacity, args.output)
                print(f"✅ Generated sprint plan with {len(result['sprint_items'])} items")
            else:
                result = assistant.generate_sprint_plan_sync(args.input_file, capacity, args.output)
                print(f"✅ Generated sprint plan with {len(result['sprint_items'])} items")
                
        elif args.command == "requirements":
            if not args.input_file:
                print("Error: input_file required for requirements command")
                return
                
            if assistant.use_async:
                result = await assistant.process_requirements_async(args.input_file, args.output)
                print(f"✅ Processed requirements document. Generated {len(result['user_stories'])} user stories")
            else:
                result = assistant.process_requirements_sync(args.input_file, args.output)
                print(f"✅ Processed requirements document. Generated {len(result['user_stories'])} user stories")

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return 1

    return 0


def main():
    """Synchronous main entry point."""
    return asyncio.run(main_async())


if __name__ == "__main__":
    exit(main())
