# Smart Backlog Assistant - Development and Testing Makefile

.PHONY: help install test test-cov test-fast lint format type-check clean docker-build docker-test docker-run

# Default target
help:
	@echo "Smart Backlog Assistant - Available Commands:"
	@echo ""
	@echo "Development:"
	@echo "  install     - Install dependencies"
	@echo "  test        - Run all tests"
	@echo "  test-cov    - Run tests with coverage report"
	@echo "  test-fast   - Run tests without slow tests"
	@echo "  lint        - Run code linting"
	@echo "  format      - Format code with black and isort"
	@echo "  type-check  - Run type checking with mypy"
	@echo ""
	@echo "Docker:"
	@echo "  docker-build - Build Docker image"
	@echo "  docker-test  - Run tests in Docker"
	@echo "  docker-run   - Run application in Docker"
	@echo ""
	@echo "Utilities:"
	@echo "  clean       - Clean up generated files"

# Development setup
install:
	pip install -r requirements.txt
	pip install flake8 black isort mypy

# Testing
test:
	pytest -v

test-cov:
	pytest --cov=src --cov-report=html --cov-report=term-missing --cov-fail-under=80

test-fast:
	pytest -v -m "not slow"

# Code quality
lint:
	flake8 src tests --max-line-length=100 --ignore=E203,W503
	black --check src tests
	isort --check-only src tests

format:
	black src tests
	isort src tests

type-check:
	mypy src --ignore-missing-imports --no-strict-optional

# Docker operations
docker-build:
	docker build -t smart-backlog-assistant .

docker-test:
	docker run --rm \
		-v $(PWD)/tests:/app/tests \
		-e PYTHONPATH=/app/src \
		smart-backlog-assistant \
		pytest tests/ --cov=src --cov-fail-under=80

docker-run:
	docker-compose up -d

# Cleanup
clean:
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf coverage.xml
	rm -rf .pytest_cache/
	rm -rf __pycache__/
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf logs/*.log

# Demo commands
demo-meeting-notes:
	python src/main.py meeting-notes sample_data/complex_meeting_notes.md -o output/meeting_analysis.json

demo-backlog-analysis:
	python src/main.py analyze-backlog sample_data/large_backlog.json -o output/backlog_analysis.json

demo-sprint-plan:
	python src/main.py sprint-plan sample_data/large_backlog.json --capacity 40 -o output/sprint_plan.json

demo-requirements:
	python src/main.py requirements sample_data/requirements_document.md -o output/requirements_analysis.json
