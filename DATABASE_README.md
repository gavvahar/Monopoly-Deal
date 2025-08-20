# Database Module

A reusable database module for Monopoly Deal and other projects. This module provides a clean abstraction layer for PostgreSQL database operations with proper connection management and error handling using a **function-based architecture**.

## Features

- **Function-Based Design**: Simple functions instead of classes for easier integration
- **Centralized Configuration**: Environment variable support with sensible defaults
- **Connection Management**: Proper connection handling with automatic cleanup
- **Error Handling**: Comprehensive error handling for database operations
- **Reusable Design**: Can be easily shared across multiple projects
- **IP Address Support**: Configured for Docker container networking with IP addresses
- **Clean API**: Simple, intuitive interface for database operations

## Core Functions

### Configuration

Configure database connection parameters:

```python
from database import configure_database

# Use defaults (environment variables)
configure_database()

# Or specify custom configuration
configure_database(
    db_name="my_db",
    db_user="my_user", 
    db_password="my_password",
    db_host="172.20.0.12",  # PostgreSQL container IP
    db_port=5432
)
```

### Connection Management

```python
from database import get_database_connection, execute_query

# Get a connection
conn = get_database_connection()

# Execute queries with automatic connection management
results = execute_query("SELECT * FROM users;", fetch=True)
execute_query("INSERT INTO users (username, password) VALUES (%s, %s);", 
              ("john", "password123"))
```

### User Operations

High-level user management functions:

```python
from database import (
    create_users_table,
    create_user, 
    user_exists,
    get_usernames,
    get_all_users
)

# Initialize database
create_users_table()

# User operations
create_user("john_doe", "password123")
exists = user_exists("john_doe")
all_users = get_all_users()
usernames = get_usernames()
```

### Quick Setup

For quick initialization:

```python
from database import initialize_database

# Initialize database tables and configuration
initialize_database()

# Ready to use other functions
create_user("alice", "secret")
```

## Docker Integration

The module is configured for Docker containers with specific IP addresses:

- PostgreSQL: `172.20.0.12:5432`
- Database Service: `172.20.0.10`
- Web App: `172.20.0.11`
- PgAdmin: `172.20.0.13`

## Environment Variables

The module reads configuration from environment variables:

- `POSTGRES_DB`: Database name (default: "monopoly")
- `POSTGRES_USER`: Database user (default: "nihar")
- `POSTGRES_PASSWORD`: Database password (required)
- `DB_HOST`: Database host (default: "172.20.0.12")

## Usage in Flask Apps

```python
from flask import Flask
from database import initialize_database, get_all_users, create_user

app = Flask(__name__)

# Initialize database
initialize_database()

@app.route('/users')
def list_users():
    users = get_all_users()
    return {'users': users}

@app.route('/create_user', methods=['POST'])
def add_user():
    create_user(username, password)
    return {'status': 'created'}
```

## Docker Deployment

The module includes Docker support with separate containers:

```bash
# Start all services including separate database service
docker-compose up

# Access services by IP:
# - Web App: http://172.20.0.11:5000
# - PostgreSQL: 172.20.0.12:5432  
# - PgAdmin: http://172.20.0.13:80
# - Database Service: 172.20.0.10
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
4. Import and use: `from database import initialize_database, create_user`

## Dependencies

- `psycopg2-binary`: PostgreSQL adapter for Python
- Python 3.6+

## Error Handling

All database operations include proper error handling. Connection failures, SQL errors, and other database issues are propagated as `psycopg2.Error` exceptions with descriptive messages.

## Function Reference

### Configuration Functions
- `configure_database(db_name, db_user, db_password, db_host, db_port)`: Configure connection parameters
- `initialize_database()`: Initialize database and create tables

### Connection Functions  
- `get_database_connection()`: Get a database connection
- `execute_query(query, params, fetch)`: Execute SQL with connection management

### User Functions
- `create_users_table()`: Create users table if not exists
- `create_user(username, password)`: Create a new user
- `user_exists(username)`: Check if user exists
- `get_usernames()`: Get list of all usernames
- `get_all_users()`: Get all user data