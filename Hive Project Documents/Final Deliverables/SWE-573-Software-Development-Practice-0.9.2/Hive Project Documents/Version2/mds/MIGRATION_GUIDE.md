# Flask Refactoring Migration Guide

## Overview

Your Flask application has been successfully refactored from a **monolithic** `app.py` file into a **modular blueprint-based architecture**. This guide will help you understand the new structure and complete the migration.

## What Has Been Completed

### ✅ Core Infrastructure (100% Complete)

1. **Directory Structure** - All module directories created
2. **Configuration** (`config.py`) - All environment variables and settings
3. **Database Module** (`app/db.py`) - Database connection and initialization
4. **Utilities Module** (`app/utils.py`) - All validation and helper functions
5. **Application Factory** (`app/__init__.py`) - Flask app creation with blueprint registration
6. **Auth Blueprint** (`app/auth/routes.py`) - **FULLY IMPLEMENTED** with all routes:
   - `POST /api/auth/register` - User registration
   - `POST /api/auth/login` - User login
   - `GET /api/auth/verify-email` - Email verification
   - `GET /api/auth/profile` - Get user profile
   - `PUT /api/auth/profile` - Update user profile
   - `POST /api/auth/forgot-password` - Request password reset
   - `POST /api/auth/reset-password` - Reset password
7. **Frontend Blueprint** (`app/frontend/routes.py`) - All template rendering routes
8. **Entry Point** (`run.py`) - Application launcher

### ⚠️ Placeholder Blueprints (Need Implementation)

These modules have basic structure but need routes extracted from `app.py`:

1. **Users Blueprint** (`app/users/routes.py`)
2. **Services Blueprint** (`app/services/routes.py`)
3. **Progress Blueprint** (`app/progress/routes.py`)
4. **Messages Blueprint** (`app/messages/routes.py`)
5. **Admin Blueprint** (`app/admin/routes.py`)
6. **Forum Blueprint** (`app/forum/routes.py`)

---

## New Directory Structure

```
backend/
├── config.py                    # ✅ Configuration classes
├── run.py                       # ✅ Application entry point
├── app.py                       # ⚠️ OLD FILE - Keep as reference, will be replaced
├── app/                         # 🆕 New modular structure
│   ├── __init__.py             # ✅ Application factory
│   ├── db.py                   # ✅ Database functions
│   ├── utils.py                # ✅ Utility functions
│   ├── auth/                   # ✅ COMPLETE
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── frontend/               # ✅ COMPLETE
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── users/                  # ⚠️ Needs implementation
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── services/               # ⚠️ Needs implementation
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── progress/               # ⚠️ Needs implementation
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── messages/               # ⚠️ Needs implementation
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── admin/                  # ⚠️ Needs implementation
│   │   ├── __init__.py
│   │   └── routes.py
│   └── forum/                  # ⚠️ Needs implementation
│       ├── __init__.py
│       └── routes.py
├── frontend/
│   ├── templates/
│   └── static/
```

---

## How to Run the New Application

### Option 1: Using run.py (Recommended)

```bash
cd backend
python run.py
```

### Option 2: Using Flask CLI

```bash
cd backend
export FLASK_APP=run.py
export FLASK_ENV=development
flask run
```

### Option 3: In Docker

Update your `Dockerfile` to use `run.py` instead of `app.py`:

```dockerfile
CMD ["python", "run.py"]
```

---

## Migration Steps for Remaining Blueprints

### General Process

For each blueprint module, follow these steps:

1. **Find the routes in `app.py`** - Search for `@app.route` with the relevant URL pattern
2. **Copy the route function** to the appropriate blueprint file
3. **Update imports** - Change `from app import` to `from app.db import` or `from app.utils import`
4. **Change decorators** - Replace `@app.route` with `@<blueprint_name>_bp.route`
5. **Update references** - Replace `app.config` with `current_app.config` (import from Flask)
6. **Remove `bcrypt` references** - Use `from app import bcrypt` at the top of the file

### Example: Extracting a Service Route

**OLD (in app.py):**
```python
@app.route("/api/services", methods=['GET'])
def get_services():
    user_id, error, status = get_user_from_token(request.headers.get('Authorization'))
    conn = get_db_connection()
    # ... rest of the logic
```

**NEW (in app/services/routes.py):**
```python
from flask import Blueprint, request, jsonify, current_app
from app.db import get_db_connection
from app.utils import get_user_from_token

services_bp = Blueprint('services', __name__)

@services_bp.route("/services", methods=['GET'])
def get_services():
    user_id, error, status = get_user_from_token(request.headers.get('Authorization'))
    conn = get_db_connection()
    # ... rest of the logic (stays the same)
```

---

## Blueprint-Specific Migration Guides

### 1. Users Blueprint (`app/users/routes.py`)

**Routes to extract from app.py:**

| Old Route | Line # (approx) | New Route | Method |
|-----------|----------------|-----------|--------|
| `/api/users/<id>` | ~1011 | `/<int:user_id>` | GET |

**Key imports needed:**
```python
from flask import Blueprint, request, jsonify
from app.db import get_db_connection
```

---

### 2. Services Blueprint (`app/services/routes.py`)

**Routes to extract from app.py:**

| Old Route | Line # (approx) | New Route | Method |
|-----------|----------------|-----------|--------|
| `/api/tags` | ~1420 | `/tags` | GET, POST |
| `/api/tags/search` | ~1480 | `/tags/search` | GET |
| `/api/services` | ~1540, ~1620 | `/services` | GET, POST |
| `/api/services/<id>` | ~1730, ~1920 | `/services/<int:service_id>` | GET, PUT, DELETE |
| `/api/services/<id>/apply` | ~2074 | `/services/<int:service_id>/apply` | POST |
| `/api/services/<id>/user-application` | ~1801 | `/services/<int:service_id>/user-application` | GET |
| `/api/upload-image` | Search for it | `/upload-image` | POST |

**Key imports needed:**
```python
from flask import Blueprint, request, jsonify, current_app
from flask_bcrypt import Bcrypt
from app.db import get_db_connection
from app.utils import get_user_from_token, validate_time_balance, allowed_file
from werkzeug.utils import secure_filename
import uuid, os
```

**Note:** The `/api` and `/health` routes are already in the placeholder.

---

### 3. Progress Blueprint (`app/progress/routes.py`)

**Routes to extract from app.py:**

Search for all routes containing `/api/progress` in app.py. These typically include:
- List progress items for a user
- Get specific progress details
- Update progress status (schedule, start, complete)
- Submit surveys
- Accept/reject schedule proposals

**Key imports needed:**
```python
from flask import Blueprint, request, jsonify
from app.db import get_db_connection
from app.utils import get_user_from_token, validate_time_balance
from datetime import datetime, timedelta, timezone
```

---

### 4. Messages Blueprint (`app/messages/routes.py`)

**Routes to extract from app.py:**

Search for all routes containing `/api/messages` in app.py:
- List messages for a user
- Send message
- Mark message as read
- Get conversation thread

**Key imports needed:**
```python
from flask import Blueprint, request, jsonify
from app.db import get_db_connection
from app.utils import get_user_from_token
```

---

### 5. Admin Blueprint (`app/admin/routes.py`)

**Routes to extract from app.py:**

Search for all routes containing `/api/admin` in app.py:
- Dashboard statistics
- User management (list, ban, warn, delete)
- Service moderation
- Reports handling
- Forum moderation

**Key imports needed:**
```python
from flask import Blueprint, request, jsonify
from app.db import get_db_connection
from app.utils import get_admin_from_token, log_admin_action
```

---

### 6. Forum Blueprint (`app/forum/routes.py`)

**Routes to extract from app.py:**

Search for all routes containing `/api/forum` in app.py:
- Categories CRUD
- Threads CRUD
- Comments CRUD
- Thread pinning/locking

**Key imports needed:**
```python
from flask import Blueprint, request, jsonify
from app.db import get_db_connection
from app.utils import get_user_from_token, get_admin_from_token
```

---

## Common Import Patterns

When migrating routes, update these imports:

### OLD (in app.py):
```python
from flask import Flask, jsonify, request
from flask_bcrypt import Bcrypt
import jwt
# Direct access to app, bcrypt
```

### NEW (in blueprint):
```python
from flask import Blueprint, request, jsonify, current_app
from app import bcrypt  # If you need bcrypt
from app.db import get_db_connection
from app.utils import get_user_from_token, validate_password, etc.
import jwt
```

### Accessing Config:
- **OLD:** `app.config['SECRET_KEY']`
- **NEW:** `current_app.config['SECRET_KEY']` (import `current_app` from Flask)

---

## Testing the Migration

### 1. Test the Auth Routes (Already Working)

```bash
# Register a user
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test1234","first_name":"Test","last_name":"User"}'

# Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test1234"}'
```

### 2. Test Frontend Routes

Visit: `http://localhost:5000/`

All HTML pages should render correctly.

### 3. Test Placeholder Routes

Try accessing unimplemented routes - they should return 501 errors:

```bash
curl http://localhost:5000/api/services
# Expected: {"error": "Not yet implemented"}
```

---

## Docker Configuration

Update your `docker-compose.yml` if needed:

```yaml
services:
  backend:
    build: ./backend
    command: python run.py
    # OR use gunicorn for production:
    # command: gunicorn -w 4 -b 0.0.0.0:5000 'app:create_app()'
```

---

## Keeping the Old app.py as Reference

**DO NOT DELETE `app.py` yet!** Keep it as a reference while you migrate routes.

Once all routes are migrated and tested, you can:
1. Rename it to `app_old.py` or `app.py.backup`
2. Or delete it entirely

---

## Benefits of the New Structure

1. **Separation of Concerns** - Each module handles its own domain
2. **Easier Testing** - Test individual blueprints in isolation
3. **Better Collaboration** - Multiple developers can work on different modules
4. **Cleaner Code** - No more 4000+ line files
5. **Scalability** - Easy to add new features as new blueprints
6. **Reusability** - Utils and DB functions can be imported anywhere

---

## Quick Reference: Where Things Are

| Old Location | New Location |
|--------------|--------------|
| `get_db_connection()` | `app/db.py` |
| `init_db()` | `app/db.py` |
| `validate_password()` | `app/utils.py` |
| `validate_phone()` | `app/utils.py` |
| `get_user_from_token()` | `app/utils.py` |
| `get_admin_from_token()` | `app/utils.py` |
| `validate_time_balance()` | `app/utils.py` |
| `log_admin_action()` | `app/utils.py` |
| Auth routes | `app/auth/routes.py` ✅ |
| Frontend routes | `app/frontend/routes.py` ✅ |
| Service routes | `app/services/routes.py` ⚠️ |
| User routes | `app/users/routes.py` ⚠️ |
| Progress routes | `app/progress/routes.py` ⚠️ |
| Message routes | `app/messages/routes.py` ⚠️ |
| Admin routes | `app/admin/routes.py` ⚠️ |
| Forum routes | `app/forum/routes.py` ⚠️ |

---

## Troubleshooting

### Issue: "ImportError: cannot import name 'bcrypt'"

**Solution:** Add this to the blueprint file:
```python
from app import bcrypt
```

### Issue: "RuntimeError: Working outside of application context"

**Solution:** Use `current_app` instead of direct `app`:
```python
from flask import current_app
# Then use:
current_app.config['SECRET_KEY']
```

### Issue: "Blueprint not registered"

**Solution:** Check `app/__init__.py` to ensure the blueprint is imported and registered.

### Issue: Routes returning 404

**Solution:** Check the URL prefix when registering the blueprint. For example:
- Auth routes use `/api/auth` prefix
- Service routes use `/api` prefix (no sub-path)

---

## Next Steps

1. **Start with Services Blueprint** - It's the largest and most important
2. **Then Progress Blueprint** - Core workflow functionality
3. **Then Messages, Users, Admin, Forum** - In any order
4. **Test each module** after implementation
5. **Update Dockerfile** to use `run.py`
6. **Deploy** once all routes are migrated and tested

---

## Need Help?

Reference the completed **Auth Blueprint** (`app/auth/routes.py`) as a template for how to structure other blueprints. It demonstrates:
- Proper imports
- Blueprint creation
- Route definitions
- Error handling
- Database operations
- JWT token handling

Good luck with the migration! 🚀
