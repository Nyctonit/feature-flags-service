# Feature Flags / A/B Testing Microservice MVP

A minimal, production-ready Feature Flags service built with FastAPI and SQLAlchemy. Perfect for A/B testing, gradual rollouts, and feature toggles.

## 🚀 Features

- ✅ **Create/Update Feature Flags** with on/off status and rollout percentages
- ✅ **User-specific Flag Evaluation** using consistent hash-based assignment
- ✅ **REST API** with automatic OpenAPI documentation
- ✅ **SQLite Database** (easily switchable to PostgreSQL)
- ✅ **Rollout Logic** - gradually roll out features to percentage of users
- ✅ **Health Checks** for deployment monitoring
- ✅ **Deployment Ready** for Railway, Render, Heroku, Docker
- ✅ **Production Optimized** with proper error handling and validation

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Client App    │────│  Feature Flags   │────│   SQLite DB     │
│                 │    │   Service API    │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                       ┌──────────────┐
                       │  Hash-based  │
                       │  Rollout     │
                       │  Logic       │
                       └──────────────┘
```

## 🔧 Quick Start

### Local Development

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd feature-flags-service

# 2. Set up Python environment
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

🎉 **Service is now running at:**
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

### Quick Test

```bash
# Health check
curl http://localhost:8000/health

# Create a feature flag
curl -X POST "http://localhost:8000/flags" \
  -H "Content-Type: application/json" \
  -d '{
    "flag_name": "new_feature",
    "status": true,
    "rollout_percentage": 50.0,
    "description": "New feature for 50% of users"
  }'

# Check flag for a user
curl "http://localhost:8000/users/user123/flags/new_feature"
```

## 📊 API Endpoints

### Feature Flag Management
- `POST /flags` - Create a feature flag
- `GET /flags` - List all feature flags
- `GET /flags/{flag_name}` - Get specific flag
- `PUT /flags/{flag_name}` - Update flag
- `DELETE /flags/{flag_name}` - Delete flag

### User Flag Evaluation
- `GET /users/{user_id}/flags` - Get all flags for user
- `GET /users/{user_id}/flags/{flag_name}` - Get specific flag for user

### System
- `GET /health` - Health check endpoint

## 🎯 Usage Examples

### Creating Feature Flags

```bash
# Basic flag (all users when enabled)
curl -X POST "http://localhost:8000/flags" \
  -H "Content-Type: application/json" \
  -d '{
    "flag_name": "dark_mode",
    "status": true,
    "description": "Enable dark mode UI"
  }'

# Gradual rollout flag
curl -X POST "http://localhost:8000/flags" \
  -H "Content-Type: application/json" \
  -d '{
    "flag_name": "beta_search",
    "status": true,
    "rollout_percentage": 25.0,
    "description": "New search algorithm - 25% rollout"
  }'

# Disabled flag
curl -X POST "http://localhost:8000/flags" \
  -H "Content-Type: application/json" \
  -d '{
    "flag_name": "experimental_ai",
    "status": false,
    "description": "AI features (currently disabled)"
  }'
```

### Evaluating Flags for Users

```bash
# Get all flags for a user
curl "http://localhost:8000/users/alice123/flags"

# Get specific flag for user
curl "http://localhost:8000/users/alice123/flags/beta_search"

# Test different users for rollout
for user in user1 user2 user3 user4 user5; do
  echo "User $user:"
  curl -s "http://localhost:8000/users/$user/flags/beta_search" | jq .enabled
done
```

### Updating Flags

```bash
# Enable a flag
curl -X PUT "http://localhost:8000/flags/experimental_ai" \
  -H "Content-Type: application/json" \
  -d '{"status": true}'

# Increase rollout percentage
curl -X PUT "http://localhost:8000/flags/beta_search" \
  -H "Content-Type: application/json" \
  -d '{"rollout_percentage": 50.0}'
```

## 🧠 Rollout Logic Explained

The service uses **deterministic hash-based assignment** to ensure:

1. **Consistency**: Same user always gets same result for a flag
2. **Distribution**: Users are evenly distributed across the rollout percentage
3. **Independence**: Different flags can have different results for same user

### How it works:

```python
# For user "alice123" and flag "beta_search"
hash = SHA256("alice123:beta_search")
user_percentage = (hash % 100)  # 0-99

if user_percentage < rollout_percentage:
    flag_enabled = True
else:
    flag_enabled = False
```

**Example with 25% rollout:**
- User "alice123" gets hash value 15 → **Enabled** (15 < 25)
- User "bob456" gets hash value 67 → **Disabled** (67 > 25)
- Results remain consistent across all requests

## 🚀 Deployment

### Railway (Recommended)

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

### Render

1. Connect your GitHub repo to [Render](https://render.com)
2. The `render.yaml` file handles the configuration automatically

### Docker

```bash
# Build and run
docker build -t feature-flags-service .
docker run -p 8000:8000 feature-flags-service
```

📖 **See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions**

## 🛠️ Development

### Project Structure

```
feature-flags-service/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── database.py             # Database configuration
│   ├── models.py               # SQLAlchemy models
│   ├── schemas.py              # Pydantic schemas
│   └── feature_flag_service.py # Business logic
├── tests/                      # Test files (future)
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Docker configuration
├── railway.json               # Railway deployment config
├── render.yaml                # Render deployment config
├── Procfile                   # Heroku deployment config
├── API_EXAMPLES.md           # Detailed API examples
├── DEPLOYMENT.md             # Deployment guide
└── README.md                 # This file
```

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests (when implemented)
pytest tests/
```

### Code Quality

The codebase follows Python best practices:
- Type hints throughout
- Comprehensive docstrings
- Error handling with proper HTTP status codes
- Input validation with Pydantic
- Database session management
- Security considerations

## ⚡ Performance Features

- **Efficient Database Indexes** on commonly queried fields
- **Connection Pooling** ready for production databases
- **Minimal Dependencies** for fast startup
- **Health Checks** for deployment platforms
- **Optimized Docker Image** with multi-stage builds

## 📈 Scaling & Improvements

### Immediate Improvements (Easy)
- Add Redis caching for frequently accessed flags
- Implement API key authentication
- Add request rate limiting
- Set up structured logging

### Advanced Features (Medium)
- User segmentation (by country, plan, etc.)
- Flag scheduling (auto-enable/disable at time)
- A/B test result tracking and analytics
- Admin dashboard UI
- Webhook notifications on flag changes

### Enterprise Features (Hard)
- Multi-tenancy support
- Advanced targeting rules
- Integration with data warehouses
- Real-time flag updates via WebSocket
- Advanced analytics and reporting

📖 **See [IMPROVEMENTS.md](IMPROVEMENTS.md) for detailed enhancement suggestions**

## 🔒 Security Considerations

- ✅ Input validation on all endpoints
- ✅ SQL injection prevention via SQLAlchemy
- ✅ CORS configuration
- ⚠️ **TODO**: Add API authentication
- ⚠️ **TODO**: Rate limiting for production

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- 📖 **Documentation**: See `API_EXAMPLES.md` and `DEPLOYMENT.md`
- 🐛 **Issues**: Create an issue on GitHub
- 💡 **Feature Requests**: Create an issue with the "enhancement" label

---

**Built with ❤️ using FastAPI, SQLAlchemy, and Python 3.11**