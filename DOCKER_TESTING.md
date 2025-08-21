# Docker Test Container

This directory contains a Docker test container that runs all the tests and code quality checks from the GitHub Actions workflow (`main.yml`).

## What It Tests

The Docker test container runs the same checks as the CI pipeline:

### Code Quality Checks:
- **Black formatting** - Ensures Python code follows consistent formatting
- **Flake8 linting** - Checks Python code style and quality (max-line-length=88)
- **Prettier formatting** - Formats HTML, CSS, and JavaScript files
- **Class detection** - Ensures no Python classes are used (function-based architecture)

### Application Tests:
- **FastAPI tests** (`test_fastapi.py`) - Tests the web application endpoints
- **Lobby tests** (`test_lobby.py`) - Tests the game lobby and multiplayer functionality  
- **Database tests** (`test_database.py`) - Tests database operations (may fail without PostgreSQL)

## Usage

### Option 1: Using Docker Compose (Recommended)

Run the test container in isolation:
```bash
docker compose --profile test run --rm test
```

Run tests with database support:
```bash
# Start PostgreSQL first
docker compose up --build -d db

# Run tests (database tests will pass)
docker compose --profile test run --rm test

# Clean up
docker compose down
```

### Option 2: Manual Docker Build

Build the test container:
```bash
docker build -f Dockerfile.test -t monopoly-test .
```

Run all tests:
```bash
docker run --rm monopoly-test
```

Run tests with access to database (if running):
```bash
docker run --rm --network monopoly_deal_app_default monopoly-test
```

### Option 3: Local Testing (No Docker)

If Docker networking doesn't work in your environment, you can run the tests locally:

```bash
# Install dependencies (if not already installed)
pip install -r requirements.txt
npm install --global prettier

# Run the test script directly
./run_tests.sh
```

## Test Script Details

The `run_tests.sh` script runs all checks in sequence:

1. **Black formatting check** - `black --check .`
2. **Flake8 linting** - `flake8 --max-line-length=88 .`
3. **Prettier formatting** - `prettier --check "**/*.{html,css,js}"`
4. **Class detection** - `grep` command to find Python class definitions
5. **FastAPI tests** - `python test_fastapi.py`
6. **Lobby tests** - `python test_lobby.py`
7. **Database tests** - `python test_database.py` (allows failure)

## Expected Behavior

- **All code quality checks** should pass
- **FastAPI and Lobby tests** should pass
- **Database tests** may fail if PostgreSQL is not available (this is expected and allowed)
- The script exits with **status 0** on success, **status 1** on failure

## Integration with CI

This Docker container replicates the exact same tests as the GitHub Actions workflow in `main.yml`. You can use it to:

- Test changes locally before pushing
- Debug CI failures in a local environment
- Ensure consistency between local and CI testing

## Troubleshooting

### Network/SSL Issues
If you encounter SSL certificate errors during Docker build:
- This is expected in some sandboxed environments
- Use the local testing option instead
- The dependencies are likely already installed

### Port Conflicts
If ports are already in use:
- Stop existing containers: `docker compose down`
- Check for conflicts: `lsof -i :8001` or `netstat -tuln | grep 8001`
- Modify ports in `.env` file

### Database Connection Issues
Database tests failing is normal without PostgreSQL running:
- Start database: `docker compose up --build -d db`
- Wait a few seconds for PostgreSQL to initialize
- Run tests again

### Docker Cache Issues
If tests report unexpected results (e.g., class definitions found when none exist):
- Clear Docker cache: `docker compose down --remove-orphans`
- Rebuild without cache: `docker compose --profile test build --no-cache test`
- Run tests again: `docker compose --profile test run --rm test`
- Check mounted files are current: `docker exec <container> ls -la /app`