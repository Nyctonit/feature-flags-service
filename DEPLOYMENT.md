# Deployment Guide

This document provides step-by-step instructions for deploying the Feature Flags service to Railway, Render, or other platforms.

## Local Development Setup

### Prerequisites
- Python 3.11+
- pip

### Setup Steps
```bash
# 1. Clone or download the project
git clone <your-repo-url>
cd feature-flags-service

# 2. Create virtual environment (recommended)
python -m venv venv

# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the application
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 5. Test the service
curl http://localhost:8000/health
```

The service will be available at:
- API: `http://localhost:8000`
- Interactive docs: `http://localhost:8000/docs`
- Alternative docs: `http://localhost:8000/redoc`

## Railway Deployment

### Method 1: Using Railway CLI (Recommended)

1. **Install Railway CLI**
   ```bash
   npm install -g @railway/cli
   ```

2. **Login to Railway**
   ```bash
   railway login
   ```

3. **Initialize Railway project**
   ```bash
   railway init
   ```

4. **Deploy**
   ```bash
   railway up
   ```

5. **Set environment variables (optional)**
   ```bash
   railway variables set DATABASE_URL=sqlite:///./feature_flags.db
   ```

### Method 2: Using GitHub Integration

1. Push your code to GitHub
2. Go to [Railway](https://railway.app)
3. Click "Deploy from GitHub repo"
4. Select your repository
5. Railway will automatically detect the Python app and deploy

### Railway Configuration

The `railway.json` file is already configured with:
- **Start command**: `gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT`
- **Health check**: `/health` endpoint
- **Auto-restart**: On failure with 3 max retries

## Render Deployment

### Method 1: Using Render Dashboard

1. Go to [Render](https://render.com)
2. Click "New" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app.main:app -w 2 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT`
   - **Plan**: Free

### Method 2: Using render.yaml (Infrastructure as Code)

1. The `render.yaml` file is already configured
2. Go to Render → "New" → "Blueprint"
3. Connect your repository
4. Render will automatically use the configuration

### Render Configuration

The `render.yaml` includes:
- Python 3.11.5 runtime
- SQLite database (for free tier)
- Health check endpoint
- Auto-deploy on git push

## Docker Deployment

### Local Docker
```bash
# Build image
docker build -t feature-flags-service .

# Run container
docker run -p 8000:8000 feature-flags-service
```

### Docker Compose
```yaml
# docker-compose.yml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite:///./feature_flags.db
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

Run with: `docker-compose up`

## Other Deployment Platforms

### Heroku
1. Create `Procfile`:
   ```
   web: gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
   ```

2. Deploy:
   ```bash
   heroku create your-app-name
   git push heroku main
   ```

### Fly.io
1. Install flyctl and run:
   ```bash
   fly launch
   fly deploy
   ```

### DigitalOcean App Platform
1. Use the GitHub integration
2. Configure build command: `pip install -r requirements.txt`
3. Configure run command: `gunicorn app.main:app -w 2 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8080`

## Environment Variables

### Required
- `PORT`: Port number (automatically set by most platforms)

### Optional
- `DATABASE_URL`: Database connection string (defaults to SQLite)
- `DEBUG`: Set to "true" for debug mode (not recommended in production)

### Setting Environment Variables

**Railway:**
```bash
railway variables set KEY=value
```

**Render:**
Set in the dashboard under "Environment Variables"

**Docker:**
```bash
docker run -e DATABASE_URL=sqlite:///./db.sqlite3 -p 8000:8000 feature-flags-service
```

## Database Considerations

### SQLite (Default - Free Tier)
- Good for MVP and small scale
- Data persists in container filesystem
- Single-file database
- **Limitation**: Data lost on container restart in some platforms

### PostgreSQL (Production Recommended)
```bash
# Set DATABASE_URL to PostgreSQL connection string
DATABASE_URL="postgresql://user:password@host:5432/database"
```

### Migration Script
Create `migrate.py` for database migrations:
```python
from app.database import create_tables
if __name__ == "__main__":
    create_tables()
    print("Database tables created successfully!")
```

## Monitoring and Health Checks

### Health Check Endpoint
- **URL**: `GET /health`
- **Response**: JSON with status, timestamp, and version
- **Use**: Configure platform health checks to this endpoint

### Logs
- **Railway**: `railway logs`
- **Render**: Available in dashboard
- **Docker**: `docker logs <container-id>`

## Scaling Considerations

### Free Tier Limitations
- **Railway**: 500 hours/month, sleeps after 30 minutes
- **Render**: 750 hours/month, sleeps after 15 minutes

### Production Scaling
1. **Increase worker count**: Modify `-w` parameter in start command
2. **Add database connection pooling**: For PostgreSQL
3. **Add caching**: Redis for frequently accessed flags
4. **Add monitoring**: Application performance monitoring (APM)

## Troubleshooting

### Common Issues

1. **App won't start**
   - Check logs for import errors
   - Verify all dependencies in requirements.txt
   - Ensure Python version compatibility

2. **Database errors**
   - Check DATABASE_URL format
   - Ensure database permissions
   - Verify network connectivity

3. **Memory limits**
   - Reduce worker count for free tiers
   - Optimize database queries
   - Consider SQLite for lower memory usage

4. **Timeouts**
   - Increase health check timeout
   - Optimize endpoint response times
   - Check database connection pooling

### Debug Commands
```bash
# Test locally first
uvicorn app.main:app --reload

# Check health endpoint
curl https://your-app.railway.app/health

# Test flag creation
curl -X POST https://your-app.railway.app/flags \
  -H "Content-Type: application/json" \
  -d '{"flag_name": "test", "status": true}'
```

## Security Notes

### Production Checklist
- [ ] Set proper CORS origins (not "*")
- [ ] Use environment variables for sensitive data
- [ ] Enable HTTPS (usually handled by platform)
- [ ] Consider API authentication for admin endpoints
- [ ] Regular security updates for dependencies

### Database Security
- [ ] Use PostgreSQL for production
- [ ] Enable SSL for database connections
- [ ] Regular backups
- [ ] Access control and user permissions