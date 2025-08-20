# FastAPI Conversion

The Monopoly Deal game has been successfully converted from Flask to FastAPI.

## Changes Made

### New Files
- `main.py` - New FastAPI application (replaces `app.py`)
- `test_fastapi.py` - Tests for the FastAPI application
- `app_flask_backup.py` - Backup of the original Flask app

### Updated Files
- `requirements.txt` - Updated dependencies for FastAPI
- `Dockerfile` - Updated to use FastAPI/uvicorn
- `templates/*.html` - Updated URL references (removed Flask's `url_for()`)

## Key Benefits of FastAPI over Flask

1. **Better Performance** - FastAPI is generally faster than Flask
2. **Automatic API Documentation** - `/docs` and `/redoc` endpoints
3. **Type Hints** - Better IDE support and validation
4. **Async Support** - Built-in async/await support
5. **Modern Python Features** - Uses latest Python standards

## Running the Application

### Development
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Production
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Docker

First, copy the environment file and customize it:
```bash
cp .env.example .env
# Edit .env with your preferred database credentials
```

If you encounter port conflicts, clean up existing containers first:
```bash
docker compose down --remove-orphans --volumes
```

Then start the application:
```bash
docker compose up
```

**Service Access Points:**
- Web Application: http://localhost:8000
- pgAdmin: http://localhost:5050  
- PostgreSQL: localhost:5434 (external connections)
- API Documentation: http://localhost:8000/docs

**Troubleshooting Port Conflicts:**
If you get "port already in use" errors, try these steps:
1. Stop existing containers: `docker compose down`
2. Check for conflicting services: `lsof -i :5434` or `netstat -tuln | grep 5434`
3. Change ports in `docker-compose.yml` if needed (e.g., 5434 → 5435)

## API Documentation

When running the application, you can access:
- Interactive API docs: `http://localhost:8000/docs`
- Alternative docs: `http://localhost:8000/redoc`

## Testing

Run the FastAPI tests:
```bash
python test_fastapi.py
```

Run the existing database tests:
```bash
python test_database.py
```

## Functionality

All original functionality has been preserved:
- User login/logout
- Game play interface
- Admin user management
- Database viewing
- Session management
- Static file serving

The game logic and database modules remain unchanged.