# Smart Backlog Assistant - Usage Guide

## Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <repository-url>
cd smart-backlog-assistant

# Install dependencies
pip install -e ".[test,dev]"

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys
```

### 2. Configuration

Add your AI service API keys to the `.env` file:

```bash
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
HUGGINGFACE_API_KEY=your_huggingface_api_key_here
```

### 3. Basic Usage

```bash
# Process meeting notes
python src/main_unified.py meeting-notes sample_data/meeting_notes.txt -o output/meeting_analysis.json

# Analyze existing backlog
python src/main_unified.py analyze-backlog sample_data/backlog.json -o output/backlog_analysis.json

# Generate sprint plan
python src/main_unified.py sprint-plan sample_data/backlog.json --capacity 40 -o output/sprint_plan.json

# Process requirements document
python src/main_unified.py requirements sample_data/requirements_document.md -o output/requirements_analysis.json
```

## Detailed Usage Examples

### Processing Meeting Notes

The Smart Backlog Assistant can extract actionable items from meeting notes and convert them into structured user stories.

**Input**: Text file with meeting notes
```
# Sprint Planning Meeting
## Action Items
- Implement user authentication
- Fix login bug
- Create mobile dashboard
```

**Command**:
```bash
python src/main_unified.py meeting-notes meeting_notes.txt -o output.json
```

**Output**: Structured JSON with:
- Extracted requirements
- Generated user stories with acceptance criteria
- Priority assessments
- Processing metadata

### Analyzing Existing Backlog

Analyze your current backlog for completeness, priority distribution, and improvement opportunities.

**Input**: JSON file with backlog items
```json
{
  "items": [
    {
      "title": "User Authentication",
      "description": "Implement login system",
      "priority": "high",
      "status": "todo"
    }
  ]
}
```

**Command**:
```bash
python src/main_unified.py analyze-backlog backlog.json -o analysis.json
```

**Output**: Comprehensive analysis including:
- Health score (0-100)
- Priority and status distribution
- Missing information identification
- Enhancement recommendations
- AI-powered insights

### Generating Sprint Plans

Create optimized sprint plans based on priority, capacity, and dependencies.

**Command**:
```bash
python src/main_unified.py sprint-plan backlog.json --capacity 40 -o sprint.json
```

**Output**: Sprint plan with:
- Selected items fitting within capacity
- Effort point calculations
- Priority-based ordering
- Generated user stories for selected items

### Processing Requirements Documents

Extract and structure requirements from PDF or Markdown documents.

**Input**: Requirements document (PDF, DOCX, or Markdown)

**Command**:
```bash
python src/main_unified.py requirements requirements.pdf -o requirements_analysis.json
```

**Output**: Structured analysis with:
- Extracted requirements
- Generated user stories
- Priority assessments
- Categorization

## Advanced Usage

### Programmatic API

You can also use the Smart Backlog Assistant programmatically:

```python
from src.main import SmartBacklogAssistant

assistant = SmartBacklogAssistant()

# Process meeting notes
result = assistant.process_meeting_notes('meeting_notes.txt')
print(f"Generated {len(result['user_stories'])} user stories")

# Analyze backlog
analysis = assistant.analyze_backlog('backlog.json')
print(f"Backlog health score: {analysis['analysis_summary']['health_score']}")

# Generate sprint plan
sprint = assistant.generate_sprint_plan('backlog.json', capacity=40)
print(f"Sprint plan: {sprint['selected_items_count']} items")
```

### Custom Configuration

You can customize the AI processing behavior by modifying environment variables:

```bash
# Set default AI service
DEFAULT_AI_SERVICE=openai

# Configure retry behavior
MAX_RETRIES=3
TIMEOUT_SECONDS=30

# Set logging level
LOG_LEVEL=INFO
```

## Input Formats

### Supported File Types

- **Text Files**: `.txt`, `.md` (meeting notes, requirements)
- **PDF Files**: `.pdf` (requirements documents)
- **Word Documents**: `.docx` (requirements documents)
- **JSON Files**: `.json` (backlog data)

### Meeting Notes Format

For best results, structure your meeting notes with clear sections:

```markdown
# Meeting Title

## Attendees
- Person 1
- Person 2

## Action Items
- Task 1
- Task 2

## Requirements
- Requirement 1
- Requirement 2

## Decisions
- Decision 1
- Decision 2
```

### Backlog JSON Format

Structure your backlog JSON files as follows:

```json
{
  "items": [
    {
      "title": "Item Title",
      "description": "Detailed description",
      "priority": "high|medium|low",
      "status": "todo|in_progress|done|blocked",
      "story_points": 5,
      "tags": ["tag1", "tag2"],
      "acceptance_criteria": ["criteria1", "criteria2"],
      "assignee": "email@company.com",
      "dependencies": ["ITEM-001"]
    }
  ]
}
```

## Output Formats

### User Stories

Generated user stories follow this structure:

```json
{
  "title": "Story Title",
  "user_type": "user",
  "functionality": "what the user wants to do",
  "benefit": "why they want to do it",
  "acceptance_criteria": [
    "Criterion 1",
    "Criterion 2"
  ],
  "priority": "high",
  "estimated_effort": "medium",
  "tags": ["frontend", "api"]
}
```

### Priority Assessments

Priority assessments include:

```json
{
  "priority": "high",
  "category": "feature",
  "business_impact": "high",
  "technical_complexity": "medium",
  "effort_estimate": "large",
  "dependencies": ["dependency1"],
  "reasoning": "Explanation for priority",
  "confidence_score": 0.85
}
```

## Best Practices

### 1. Input Quality
- Provide detailed descriptions in backlog items
- Use consistent terminology across documents
- Include context and business rationale

### 2. AI Service Configuration
- Set up multiple AI services for redundancy
- Monitor API usage and costs
- Use appropriate service for task complexity

### 3. Output Validation
- Review generated user stories for accuracy
- Validate priority assessments against business needs
- Adjust recommendations based on team context

### 4. Iterative Improvement
- Use the tool regularly to maintain backlog health
- Incorporate feedback into future inputs
- Track improvements in backlog quality over time

## Troubleshooting

### Common Issues

**1. API Key Errors**
```
Error: OpenAI API key not found
```
Solution: Ensure API keys are set in `.env` file

**2. File Processing Errors**
```
Error: Failed to process document
```
Solution: Check file format and permissions

**3. Empty Results**
```
Generated 0 user stories
```
Solution: Improve input quality and structure

### Logging

Enable detailed logging for troubleshooting:

```bash
export LOG_LEVEL=DEBUG
python src/main_unified.py meeting-notes input.txt
```

Check the log file: `backlog_assistant.log`

### Performance Optimization

- Use smaller input files for faster processing
- Configure appropriate timeout values
- Monitor AI service response times
- Consider batch processing for large datasets

## Integration Examples

### CI/CD Pipeline

```yaml
# .github/workflows/backlog-analysis.yml
name: Backlog Analysis
on:
  schedule:
    - cron: '0 9 * * 1'  # Weekly on Monday

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Analyze Backlog
        run: |
          python src/main_unified.py analyze-backlog backlog.json -o analysis.json
          # Upload results or create PR with recommendations
```

### Slack Integration

```python
# slack_bot.py
import slack_sdk
from src.main import SmartBacklogAssistant

def analyze_backlog_command(channel, file_path):
    assistant = SmartBacklogAssistant()
    result = assistant.analyze_backlog(file_path)
    
    message = f"📊 Backlog Health Score: {result['analysis_summary']['health_score']}/100\n"
    message += f"📝 Recommendations: {len(result['recommendations'])}"
    
    slack_client.chat_postMessage(channel=channel, text=message)
```

## Support and Contributing

For issues, feature requests, or contributions, please refer to the project repository documentation.
