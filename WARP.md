# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Development Commands

### Starting the Application
```bash
# Development server with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production server (multi-worker)
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Environment Setup
```bash
# Set up virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

### Testing
```bash
# Install test dependencies (tests not yet implemented)
pip install pytest pytest-asyncio httpx

# Run tests when implemented
pytest tests/
```

### Quick API Testing
```bash
# Health check
curl http://localhost:8000/health

# Create a test flag
curl -X POST "http://localhost:8000/flags" -H "Content-Type: application/json" -d '{"flag_name": "test_feature", "status": true, "rollout_percentage": 50.0}'

# Test user evaluation
curl "http://localhost:8000/users/testuser123/flags/test_feature"
```

## Architecture Overview

This is a **Feature Flags/A/B Testing microservice** built with FastAPI and SQLAlchemy. The core architecture uses a deterministic hash-based rollout system that ensures consistent user experiences.

### Key Components

**`app/main.py`** - FastAPI application with all REST endpoints
- Feature flag CRUD operations (`/flags/*`)
- User-specific flag evaluation (`/users/{user_id}/flags/*`)
- Health check endpoint (`/health`)

**`app/feature_flag_service.py`** - Core business logic
- Implements deterministic hash-based user assignment using SHA-256
- Formula: `hash(user_id + ":" + flag_name) % 100 <= rollout_percentage`
- Ensures same user always gets same result for a flag across requests

**`app/models.py`** - Database schema (SQLAlchemy ORM)
- Single `FeatureFlag` table with optimized indexes
- Supports rollout percentages (0-100) and on/off status
- Timestamps for audit trail

**`app/database.py`** - Database configuration
- SQLite by default, easily switchable to PostgreSQL via `DATABASE_URL`
- Session management with proper cleanup

**`app/schemas.py`** - Pydantic models for request/response validation
- Strict validation of rollout percentages (0-100)
- Separate schemas for create, update, and response operations

### Hash-Based Rollout Logic

The service uses **deterministic hashing** to assign users to feature flags:

1. Combines `user_id:flag_name` into a string
2. Generates SHA-256 hash and takes first 8 hex characters
3. Converts to percentage (0-100)
4. Compares against flag's `rollout_percentage`

This ensures:
- **Consistency**: Same user always gets same result
- **Distribution**: Even distribution across rollout percentage
- **Independence**: Different flags can have different results for same user

### Database Design

Single table approach optimized for read-heavy workloads:
- `flag_name` - Unique string identifier
- `status` - Boolean on/off switch
- `rollout_percentage` - Float 0-100 for gradual rollouts
- Compound indexes on frequently queried combinations

## Development Patterns

### Adding New Endpoints
1. Define Pydantic schema in `schemas.py`
2. Add endpoint function in `main.py` with proper error handling
3. Use dependency injection for database sessions: `db: Session = Depends(get_database_session)`
4. Follow existing patterns for HTTP status codes and error responses

### Database Migrations
Currently using `Base.metadata.create_all()` for table creation. For production:
1. Install Alembic: `pip install alembic`
2. Initialize: `alembic init migrations`
3. Generate migrations: `alembic revision --autogenerate -m "description"`
4. Apply: `alembic upgrade head`

### Business Logic Extension
New evaluation logic should go in `FeatureFlagService` class:
- Keep hash-based consistency for rollout features
- Add new static methods for different evaluation strategies
- Maintain separation between API logic (main.py) and business logic (service)

## Deployment Configuration

The service includes deployment configs for multiple platforms:
- **Railway**: `railway.json` with health checks and auto-restart
- **Render**: `render.yaml` with Python 3.11 runtime
- **Docker**: Multi-stage `Dockerfile` with non-root user
- **Heroku**: `Procfile` with gunicorn configuration

### Environment Variables
- `DATABASE_URL`: Database connection (defaults to SQLite)
- `PORT`: Server port (auto-set by most platforms)

### Database Switching
To switch from SQLite to PostgreSQL:
```bash
# Set environment variable
export DATABASE_URL="postgresql://user:password@host:port/dbname"
# Or set in deployment platform environment variables
```

The database configuration will automatically adapt based on the URL scheme.