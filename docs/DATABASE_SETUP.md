# Database Setup Guide

This guide explains how to configure and use the database layer in Smart Backlog Assistant.

## Overview

The Smart Backlog Assistant now includes an enterprise-grade database layer built with SQLAlchemy, supporting both SQLite (development) and PostgreSQL (production).

## Database Models

The system includes the following entities:

- **Projects**: Top-level containers for backlog items
- **BacklogItems**: Individual tasks/features with priority, status, and categorization
- **UserStories**: Generated user stories linked to backlog items
- **PriorityAssessments**: AI-generated priority evaluations
- **ProcessingJobs**: Track async processing operations
- **CacheEntries**: Persistent caching for performance

## Quick Setup

### SQLite (Development - Default)

No additional setup required. The system automatically creates a SQLite database:

```bash
# Database file will be created automatically
./smart_backlog_assistant.db
```

### PostgreSQL (Production)

1. **Install PostgreSQL dependencies:**
   ```bash
   pip install psycopg2-binary
   ```

2. **Set database URL in .env:**
   ```bash
   DATABASE_URL=postgresql://username:password@localhost:5432/smart_backlog_assistant
   ```

3. **Create the database:**
   ```sql
   CREATE DATABASE smart_backlog_assistant;
   ```

## Configuration

### Environment Variables

Add to your `.env` file:

```bash
# Database Configuration
DATABASE_URL=sqlite:///./smart_backlog_assistant.db  # Default
# DATABASE_URL=postgresql://user:pass@localhost:5432/dbname  # PostgreSQL

# Database Settings
DEBUG_MODE=false  # Set to true for SQL query logging
```

### Programmatic Configuration

```python
from src.database.models import DatabaseManager

# Custom database URL
db_manager = DatabaseManager("postgresql://user:pass@localhost:5432/mydb")

# Create tables
db_manager.create_tables()
```

## Usage Examples

### Using Repository Pattern

```python
from src.database.repository import get_repository_manager
from src.database.models import Priority, ItemStatus, ItemCategory

# Create a new project and backlog items
with get_repository_manager() as repo:
    # Create project
    project = repo.projects.create_project(
        name="My Project",
        description="Project description"
    )
    
    # Create backlog item
    item = repo.backlog_items.create_backlog_item(
        title="Implement user authentication",
        description="Add login/logout functionality",
        project_id=project.id,
        priority=Priority.HIGH,
        status=ItemStatus.TODO,
        category=ItemCategory.FEATURE
    )
    
    # Create user story
    story = repo.user_stories.create_user_story(
        title="User Login Story",
        user_type="user",
        functionality="login to the system",
        benefit="access protected features",
        project_id=project.id,
        backlog_item_id=item.id
    )
    
    # Get health metrics
    metrics = repo.backlog_items.get_backlog_health_metrics(project.id)
    print(f"Project health: {metrics}")
```

### Direct Database Access

```python
from src.database.models import db_manager, Project, BacklogItem

# Get a database session
session = db_manager.get_session()

try:
    # Query projects
    projects = session.query(Project).all()
    
    # Query backlog items with filters
    high_priority_items = session.query(BacklogItem).filter(
        BacklogItem.priority == Priority.HIGH
    ).all()
    
    session.commit()
finally:
    session.close()
```

## Database Schema

### Projects Table
- `id` (UUID): Primary key
- `name` (String): Project name
- `description` (Text): Project description
- `created_at`, `updated_at` (DateTime): Timestamps

### BacklogItems Table
- `id` (UUID): Primary key
- `title` (String): Item title
- `description` (Text): Item description
- `priority` (Enum): CRITICAL, HIGH, MEDIUM, LOW
- `status` (Enum): TODO, IN_PROGRESS, DONE, BLOCKED
- `category` (Enum): FEATURE, BUG, ENHANCEMENT, TECHNICAL_DEBT, RESEARCH, MAINTENANCE
- `story_points` (Integer): Effort estimation
- `business_value`, `technical_complexity` (Integer): Scoring
- `tags` (JSON): List of tags
- `extra_data` (JSON): Additional flexible data
- `project_id` (UUID): Foreign key to projects

### UserStories Table
- `id` (UUID): Primary key
- `title` (String): Story title
- `user_type` (String): Type of user
- `functionality` (Text): What functionality
- `benefit` (Text): What benefit
- `acceptance_criteria` (JSON): List of criteria
- `priority` (Enum): Story priority
- `estimated_effort` (String): Effort estimate
- `tags` (JSON): Story tags
- `generated_by_ai` (Boolean): AI-generated flag
- `ai_service_used` (String): Which AI service
- `project_id`, `backlog_item_id` (UUID): Foreign keys

## Performance Considerations

### Indexing
The system automatically creates indexes on:
- Foreign key relationships
- Frequently queried fields (priority, status, category)
- Timestamp fields for sorting

### Connection Pooling
For production PostgreSQL deployments:

```python
from sqlalchemy import create_engine

engine = create_engine(
    "postgresql://user:pass@localhost:5432/db",
    pool_size=20,
    max_overflow=0,
    pool_pre_ping=True
)
```

### Caching
The system includes database-backed caching:

```python
with get_repository_manager() as repo:
    # Set cache entry
    repo.cache.set_cache(
        "my_key", 
        {"data": "value"}, 
        tags=["tag1", "tag2"]
    )
    
    # Get cache entry
    entry = repo.cache.get_cache("my_key")
    
    # Invalidate by tags
    repo.cache.invalidate_by_tags(["tag1"])
```

## Migration and Maintenance

### Creating Tables
```python
from src.database.models import db_manager

# Create all tables
db_manager.create_tables()
```

### Backup (SQLite)
```bash
# Backup SQLite database
cp smart_backlog_assistant.db backup_$(date +%Y%m%d).db
```

### Backup (PostgreSQL)
```bash
# Backup PostgreSQL database
pg_dump smart_backlog_assistant > backup_$(date +%Y%m%d).sql
```

## Troubleshooting

### Common Issues

1. **"No module named 'psycopg2'"**
   ```bash
   pip install psycopg2-binary
   ```

2. **"Permission denied" on SQLite**
   ```bash
   # Ensure write permissions in project directory
   chmod 755 .
   ```

3. **PostgreSQL connection issues**
   ```bash
   # Check PostgreSQL is running
   pg_ctl status
   
   # Check connection
   psql -h localhost -U username -d smart_backlog_assistant
   ```

### Debug Mode
Enable SQL query logging:

```python
# In .env file
DEBUG_MODE=true
```

This will show all SQL queries in the console for debugging.

## Integration with Async Processing

The database layer works seamlessly with the async processing system:

```python
from src.main_unified import UnifiedSmartBacklogAssistant

# Create assistant with database integration
assistant = UnifiedSmartBacklogAssistant(use_async=True)

# Process with automatic database storage
result = await assistant.analyze_backlog_async("backlog.json")
```

The system automatically:
- Stores processing results in the database
- Tracks job status and performance metrics
- Caches AI responses for efficiency
- Maintains relationships between entities
