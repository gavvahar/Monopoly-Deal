# Database Module

A reusable database module for Monopoly Deal and other projects. This module provides a clean abstraction layer for PostgreSQL database operations with proper connection management and error handling.

## Features

- **Centralized Configuration**: Environment variable support with sensible defaults
- **Connection Management**: Proper connection handling with automatic cleanup
- **Error Handling**: Comprehensive error handling for database operations
- **Reusable Design**: Can be easily shared across multiple projects
- **Clean API**: Simple, intuitive interface for database operations

## Components

### DatabaseManager

The `DatabaseManager` class handles database connections and low-level operations:

```python
from database import DatabaseManager

# Use environment variables (recommended)
db_manager = DatabaseManager()

# Or specify custom configuration
db_manager = DatabaseManager(
    db_name="my_db",
    db_user="my_user", 
    db_password="my_password",
    db_host="localhost",
    db_port=5432
)

# Execute queries
results = db_manager.execute_query("SELECT * FROM users;", fetch=True)
```

### UserRepository

The `UserRepository` class provides high-level user management operations:

```python
from database import UserRepository, DatabaseManager

db_manager = DatabaseManager()
user_repo = UserRepository(db_manager)

# Create users table
user_repo.create_users_table()

# User operations
user_repo.create_user("john_doe", "password123")
user_exists = user_repo.user_exists("john_doe")
all_users = user_repo.get_all_users()
usernames = user_repo.get_usernames()
```

### Convenience Functions

For quick setup, use the convenience function:

```python
from database import initialize_database

# Initialize database and get UserRepository instance
user_repo = initialize_database()

# Ready to use
user_repo.create_user("alice", "secret")
```

## Environment Variables

The module reads configuration from environment variables:

- `POSTGRES_DB`: Database name (default: "monopoly")
- `POSTGRES_USER`: Database user (default: "nihar")
- `POSTGRES_PASSWORD`: Database password (required)

## Usage in Flask Apps

```python
from flask import Flask
from database import initialize_database

app = Flask(__name__)

# Initialize database
user_repository = initialize_database()

@app.route('/users')
def list_users():
    users = user_repository.get_all_users()
    return {'users': users}
```

## Example

See `database_example.py` for a complete usage example:

```bash
python3 database_example.py
```

## Integration

This module is designed to be easily shared across projects. You can:

1. Copy `database.py` to your project
2. Install dependencies: `pip install psycopg2-binary`
3. Set environment variables
4. Import and use: `from database import initialize_database`

## Dependencies

- `psycopg2-binary`: PostgreSQL adapter for Python
- Python 3.6+

## Error Handling

All database operations include proper error handling. Connection failures, SQL errors, and other database issues are propagated as `psycopg2.Error` exceptions with descriptive messages.