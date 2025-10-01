# Feature Flags Service API Examples

This document provides example requests for all API endpoints using both `curl` and `HTTPie`.

## Prerequisites

Start the service locally:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`
- Interactive API docs: `http://localhost:8000/docs`
- Alternative docs: `http://localhost:8000/redoc`

## Health Check

### curl
```bash
curl -X GET "http://localhost:8000/health"
```

### HTTPie
```bash
http GET localhost:8000/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-10T14:17:00.123456Z",
  "version": "1.0.0"
}
```

## Feature Flag Management

### 1. Create a Feature Flag

#### curl
```bash
# Basic flag (enabled for all users)
curl -X POST "http://localhost:8000/flags" \
  -H "Content-Type: application/json" \
  -d '{
    "flag_name": "new_dashboard",
    "status": true,
    "description": "Enable new dashboard UI"
  }'

# Flag with rollout percentage
curl -X POST "http://localhost:8000/flags" \
  -H "Content-Type: application/json" \
  -d '{
    "flag_name": "beta_feature",
    "status": true,
    "rollout_percentage": 25.0,
    "description": "Beta feature for 25% of users"
  }'

# Disabled flag
curl -X POST "http://localhost:8000/flags" \
  -H "Content-Type: application/json" \
  -d '{
    "flag_name": "experimental_ai",
    "status": false,
    "rollout_percentage": 5.0,
    "description": "Experimental AI features (currently disabled)"
  }'
```

#### HTTPie
```bash
# Basic flag (enabled for all users)
http POST localhost:8000/flags \
  flag_name="new_dashboard" \
  status:=true \
  description="Enable new dashboard UI"

# Flag with rollout percentage
http POST localhost:8000/flags \
  flag_name="beta_feature" \
  status:=true \
  rollout_percentage:=25.0 \
  description="Beta feature for 25% of users"

# Disabled flag
http POST localhost:8000/flags \
  flag_name="experimental_ai" \
  status:=false \
  rollout_percentage:=5.0 \
  description="Experimental AI features (currently disabled)"
```

### 2. List All Feature Flags

#### curl
```bash
curl -X GET "http://localhost:8000/flags"
```

#### HTTPie
```bash
http GET localhost:8000/flags
```

### 3. Get a Specific Feature Flag

#### curl
```bash
curl -X GET "http://localhost:8000/flags/new_dashboard"
```

#### HTTPie
```bash
http GET localhost:8000/flags/new_dashboard
```

### 4. Update a Feature Flag

#### curl
```bash
# Enable a flag
curl -X PUT "http://localhost:8000/flags/experimental_ai" \
  -H "Content-Type: application/json" \
  -d '{
    "status": true
  }'

# Change rollout percentage
curl -X PUT "http://localhost:8000/flags/beta_feature" \
  -H "Content-Type: application/json" \
  -d '{
    "rollout_percentage": 50.0
  }'

# Update multiple fields
curl -X PUT "http://localhost:8000/flags/experimental_ai" \
  -H "Content-Type: application/json" \
  -d '{
    "status": true,
    "rollout_percentage": 10.0,
    "description": "Experimental AI features (limited rollout)"
  }'
```

#### HTTPie
```bash
# Enable a flag
http PUT localhost:8000/flags/experimental_ai \
  status:=true

# Change rollout percentage
http PUT localhost:8000/flags/beta_feature \
  rollout_percentage:=50.0

# Update multiple fields
http PUT localhost:8000/flags/experimental_ai \
  status:=true \
  rollout_percentage:=10.0 \
  description="Experimental AI features (limited rollout)"
```

### 5. Delete a Feature Flag

#### curl
```bash
curl -X DELETE "http://localhost:8000/flags/experimental_ai"
```

#### HTTPie
```bash
http DELETE localhost:8000/flags/experimental_ai
```

## User-Specific Flag Evaluation

### 1. Get All Flags for a User

#### curl
```bash
curl -X GET "http://localhost:8000/users/user123/flags"
```

#### HTTPie
```bash
http GET localhost:8000/users/user123/flags
```

**Expected Response:**
```json
{
  "user_id": "user123",
  "flags": [
    {
      "flag_name": "new_dashboard",
      "enabled": true,
      "description": "Enable new dashboard UI"
    },
    {
      "flag_name": "beta_feature",
      "enabled": false,
      "description": "Beta feature for 25% of users"
    }
  ]
}
```

### 2. Get a Specific Flag for a User

#### curl
```bash
curl -X GET "http://localhost:8000/users/user123/flags/beta_feature"
```

#### HTTPie
```bash
http GET localhost:8000/users/user123/flags/beta_feature
```

**Expected Response:**
```json
{
  "flag_name": "beta_feature",
  "enabled": false,
  "description": "Beta feature for 25% of users"
}
```

## Testing Rollout Logic

To test the rollout percentage logic, try the same flag with different user IDs:

```bash
# Test with multiple users
for user in user1 user2 user3 user4 user5; do
  echo "User: $user"
  curl -s "http://localhost:8000/users/$user/flags/beta_feature" | jq .enabled
done
```

With HTTPie:
```bash
# Test with multiple users
for user in user1 user2 user3 user4 user5; do
  echo "User: $user"
  http --body GET localhost:8000/users/$user/flags/beta_feature | jq .enabled
done
```

## Error Cases

### 1. Creating Duplicate Flag
```bash
curl -X POST "http://localhost:8000/flags" \
  -H "Content-Type: application/json" \
  -d '{
    "flag_name": "new_dashboard",
    "status": true
  }'
```

**Expected Response (400 Bad Request):**
```json
{
  "detail": "Feature flag with name 'new_dashboard' already exists"
}
```

### 2. Getting Non-existent Flag
```bash
curl -X GET "http://localhost:8000/flags/nonexistent"
```

**Expected Response (404 Not Found):**
```json
{
  "detail": "Feature flag 'nonexistent' not found"
}
```

### 3. Invalid Rollout Percentage
```bash
curl -X POST "http://localhost:8000/flags" \
  -H "Content-Type: application/json" \
  -d '{
    "flag_name": "invalid_flag",
    "status": true,
    "rollout_percentage": 150.0
  }'
```

**Expected Response (422 Validation Error):**
```json
{
  "detail": [
    {
      "loc": ["body", "rollout_percentage"],
      "msg": "ensure this value is less than or equal to 100",
      "type": "value_error.number.not_le",
      "ctx": {"limit_value": 100.0}
    }
  ]
}
```

## Complete Test Sequence

Here's a complete sequence to test all functionality:

```bash
# 1. Health check
curl http://localhost:8000/health

# 2. Create flags
curl -X POST http://localhost:8000/flags \
  -H "Content-Type: application/json" \
  -d '{"flag_name": "feature_a", "status": true}'

curl -X POST http://localhost:8000/flags \
  -H "Content-Type: application/json" \
  -d '{"flag_name": "feature_b", "status": true, "rollout_percentage": 30}'

# 3. List flags
curl http://localhost:8000/flags

# 4. Test user evaluation
curl http://localhost:8000/users/testuser/flags

# 5. Update flag
curl -X PUT http://localhost:8000/flags/feature_b \
  -H "Content-Type: application/json" \
  -d '{"rollout_percentage": 60}'

# 6. Test again
curl http://localhost:8000/users/testuser/flags/feature_b

# 7. Clean up
curl -X DELETE http://localhost:8000/flags/feature_a
curl -X DELETE http://localhost:8000/flags/feature_b
```