# Claude (Anthropic) Setup Guide

This guide explains how to configure and use Claude as the default AI provider for the Smart Backlog Assistant.

## Quick Setup

### 1. Configure Environment Variables

The system now uses Claude (Anthropic) as the default AI provider. Set up your `.env` file:

```bash
# Copy the example file
cp .env.example .env

# Edit the .env file with your API key
nano .env
```

Update your `.env` file:
```env
# AI API Keys
ANTHROPIC_API_KEY=your_actual_anthropic_api_key_here
OPENAI_API_KEY=your_openai_api_key_here  # Optional fallback

# Configuration
DEFAULT_AI_SERVICE=anthropic
MAX_RETRIES=3
TIMEOUT_SECONDS=30
LOG_LEVEL=INFO
```

### 2. Get Your Anthropic API Key

1. Visit [Anthropic Console](https://console.anthropic.com/)
2. Sign up or log in to your account
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key and paste it in your `.env` file

### 3. Install Dependencies

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env

# Set up the project with uv
./scripts/setup.sh

# Or manually install dependencies
uv sync
uv sync --extra dev  # For development
uv sync --extra test # For testing
```

## Usage Examples

### Original Framework with Claude

```bash
# Process meeting notes
uv run python src/main.py meeting-notes sample_data/complex_meeting_notes.md

# Analyze backlog
uv run python src/main.py backlog-analysis sample_data/large_backlog.json

# Generate sprint plan
uv run python src/main.py sprint-plan sample_data/large_backlog.json --capacity 40
```

### Enhanced Framework with Claude

```bash
# Interactive mode with rich CLI
uv run python src/enhanced_main.py --interactive

# Command line with caching
uv run python src/enhanced_main.py --framework original --cache-enabled meeting-notes sample_data/complex_meeting_notes.md

# Use pydantic-ai framework
uv run python src/enhanced_main.py --framework pydantic-ai backlog-analysis sample_data/large_backlog.json

# Development workflow
./scripts/dev.sh interactive
./scripts/dev.sh demo
./scripts/dev.sh config-test
```

### Pydantic-AI Framework with Claude

```bash
# Process meeting notes with multi-agent system
uv run python src/agents/pydantic_ai_main.py meeting-notes sample_data/complex_meeting_notes.md

# Comprehensive backlog analysis
uv run python src/agents/pydantic_ai_main.py backlog-analysis sample_data/large_backlog.json

# Generate sprint plan with AI agents
uv run python src/agents/pydantic_ai_main.py sprint-plan sample_data/large_backlog.json
```

## Configuration Options

### AI Service Selection

You can override the default AI service:

```bash
# Use OpenAI instead of Claude
DEFAULT_AI_SERVICE=openai uv run python src/main.py meeting-notes input.md

# Use Hugging Face models
DEFAULT_AI_SERVICE=huggingface uv run python src/main.py analyze-backlog backlog.json
```

### Model Selection

The system automatically selects the best available model:

- **Claude**: `claude-3-5-sonnet-20241022` (default)
- **OpenAI**: `gpt-4` (fallback)

### Fallback Behavior

The system provides intelligent fallback:

1. **Primary**: Uses Claude (Anthropic) if configured
2. **Fallback**: Uses OpenAI if Claude fails
3. **Last Resort**: Uses Hugging Face local models

## Testing Your Setup

Run the configuration test:

```bash
python3 test_claude_config.py
```

Expected output:
```
🚀 Claude (Anthropic) Configuration Test
==================================================
✅ DEFAULT_AI_SERVICE: anthropic
✅ ANTHROPIC_API_KEY: ***configured***
✅ Anthropic client: Available
✅ Document Analyst agent: anthropic:claude-3-5-sonnet-20241022
🎉 Claude configuration is working correctly!
```

## Demo and Examples

### Run Enhanced Features Demo

```bash
# Test all enhanced features with Claude
python3 src/simple_demo.py
```

### Process Sample Data

```bash
# Complex meeting notes processing
python3 src/agents/pydantic_ai_main.py meeting-notes sample_data/complex_meeting_notes.md

# Large backlog analysis
python3 src/agents/pydantic_ai_main.py backlog-analysis sample_data/large_backlog.json
```

## Troubleshooting

### Common Issues

1. **API Key Not Found**
   ```
   Error: ANTHROPIC_API_KEY not found
   ```
   **Solution**: Ensure your `.env` file contains the correct API key

2. **Import Errors**
   ```
   ModuleNotFoundError: No module named 'anthropic'
   ```
   **Solution**: Install dependencies: `pip install -r requirements.txt`

3. **Rate Limiting**
   ```
   Error: Rate limit exceeded
   ```
   **Solution**: The system includes automatic retry with exponential backoff

### Debug Mode

Enable debug logging:

```bash
export LOG_LEVEL=DEBUG
python3 src/enhanced_main.py --interactive
```

### Verify Configuration

Check your configuration:

```python
import os
from dotenv import load_dotenv

load_dotenv()
print(f"Default AI Service: {os.getenv('DEFAULT_AI_SERVICE')}")
print(f"Anthropic Key: {'✓' if os.getenv('ANTHROPIC_API_KEY') else '✗'}")
```

## Performance and Cost Optimization

### Caching

Enable intelligent caching to reduce API calls:

```bash
python3 src/enhanced_main.py --cache-enabled meeting-notes sample_data/complex_meeting_notes.md
```

### Batch Processing

Process multiple files efficiently:

```bash
# Process all markdown files in a directory
for file in sample_data/*.md; do
    python3 src/agents/pydantic_ai_main.py meeting-notes "$file"
done
```

## Advanced Usage

### Custom Model Configuration

Override model selection in your code:

```python
from agents.document_analyst import document_analyst

# The agent automatically uses Claude based on .env configuration
result = await document_analyst.run("Analyze this document...")
```

### Multi-Agent Workflows

Use the coordinator for complex workflows:

```python
from agents.coordinator import coordinator

# Execute comprehensive analysis
result = await coordinator.run(
    "Execute comprehensive analysis workflow",
    context={"input_file": "sample_data/complex_meeting_notes.md"}
)
```

## Integration with CI/CD

### GitHub Actions

```yaml
- name: Test with Claude
  env:
    ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
    DEFAULT_AI_SERVICE: anthropic
  run: |
    python3 test_claude_config.py
    python3 src/simple_demo.py
```

### Docker

```bash
# Build with Claude configuration
docker build -t smart-backlog-claude .

# Run with environment variables
docker run -e ANTHROPIC_API_KEY=your_key -e DEFAULT_AI_SERVICE=anthropic smart-backlog-claude
```

## Next Steps

1. **Set up your Anthropic API key** in the `.env` file
2. **Run the configuration test** to verify setup
3. **Try the interactive mode**: `python3 src/enhanced_main.py --interactive`
4. **Process sample data** to see Claude in action
5. **Explore the pydantic-ai framework** for advanced multi-agent workflows

For more detailed usage instructions, see `RUN_COMMANDS.md`.
