# Enhanced Backend with Security - Implementation Plan
# This document outlines changes needed to integrate security into backend/app.py

## Changes Required:

### 1. Imports
```python
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import time
from collections import OrderedDict

# Import security module
from backend.security import (
    validate_room_code, validate_developer_id, validate_subdomain_url,
    validate_commit_hash, validate_branch, validate_commit_message,
    validate_project_name, require_admin_auth, validate_request_json,
    ValidationError, get_client_ip, sanitize_html
)
```

### 2. Rate Limiting Setup
```python
# Initialize rate limiter
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per hour", "50 per minute"],
    storage_uri="memory://",
)
```

### 3. Update Each Endpoint

#### /rooms/create
- Add `@limiter.limit("10 per minute")`
- Add `@validate_request_json('project_name', 'developer_id', 'subdomain_url')`
- Wrap field access in try/except ValidationError
- Use `validate_project_name()`, `validate_developer_id()`, `validate_subdomain_url()`

#### /rooms/join
- Add `@limiter.limit("20 per minute")`
- Add `@validate_request_json('room_code', 'developer_id', 'subdomain_url')`
- Use validation functions

#### /rooms/leave
- Add `@limiter.limit("20 per minute")`
- Add `@validate_request_json('room_code', 'developer_id')`
- Use validation functions

#### /report-commit
- Add `@limiter.limit("100 per hour")`
- Add `@validate_request_json('room_code', 'developer_id', 'commit_hash', 'branch', 'commit_message')`
- Use all commit validation functions

#### /get-active-url
- Add `@limiter.limit("200 per minute")`
- Validate room_code from query param

#### /rooms/status
- Add `@limiter.limit("100 per minute")`
- Validate room_code from query param

#### /rooms/<room_code>/commits
- Add `@limiter.limit("100 per minute")`
- Validate room_code from URL path

#### /admin/rooms
- Add `@require_admin_auth`
- Add `@limiter.limit("10 per minute")`

#### /health
- Add `@limiter.exempt` (no rate limit for health checks)

### 4. HTML Sanitization in Dashboard
- Sanitize commit messages before returning in /rooms/status and /rooms/<room_code>/commits

### 5. Error Handling
```python
@app.errorhandler(ValidationError)
def handle_validation_error(e):
    return jsonify({"error": "Validation error", "message": str(e)}), 400

@app.errorhandler(429)
def handle_rate_limit(e):
    return jsonify({
        "error": "Rate limit exceeded",
        "message": "Too many requests. Please slow down."
    }), 429
```

## Testing Additions:

### test_security.py (new file)
- test_validate_room_code_valid()
- test_validate_room_code_invalid()
- test_validate_developer_id_valid()
- test_validate_developer_id_invalid()
- test_validate_subdomain_url_valid()
- test_validate_subdomain_url_invalid()
- test_validate_commit_hash_valid()
- test_validate_commit_hash_invalid()
- test_validate_branch_valid()
- test_validate_branch_invalid()
- test_validate_commit_message_strips_html()
- test_admin_auth_valid_key()
- test_admin_auth_invalid_key()
- test_admin_auth_missing_key()
- test_rate_limiting() (requires test client)

### Update existing tests
- Add validation error test cases to test_app.py
- Test rate limiting (may need to mock or skip)

## Environment Variable:
- Add MACT_ADMIN_API_KEY to environment files

## Deployment Updates:
- Update mact-backend.env.template with MACT_ADMIN_API_KEY
- Document API key generation in DEPLOYMENT.md

## Documentation Updates:
- Update backend/README.md with security features
- Add SECURITY.md with threat model
- Update API examples with rate limit headers
