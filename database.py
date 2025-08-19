"""
Database module for Monopoly Deal - A shareable database project.

This module provides database connection management and data access operations
that can be shared across multiple projects using function-based approach.
"""

import os
import psycopg2
from typing import List, Tuple, Optional


# Global database configuration
_db_config = {
    "db_name": None,
    "db_user": None,
    "db_password": None,
    "db_host": "172.20.0.12",  # Default PostgreSQL container IP
    "db_port": 5432,
}


def configure_database(
    db_name: Optional[str] = None,
    db_user: Optional[str] = None,
    db_password: Optional[str] = None,
    db_host: str = "172.20.0.12",  # Default to PostgreSQL container IP
    db_port: int = 5432,
):
    """
    Configure database connection parameters.

    Args:
        db_name: Database name (defaults to env POSTGRES_DB or "monopoly")
        db_user: Database user (defaults to env POSTGRES_USER or "nihar")
        db_password: Database password (defaults to env POSTGRES_PASSWORD)
        db_host: Database host (defaults to PostgreSQL container IP "172.20.0.12")
        db_port: Database port (defaults to 5432)
    """
    global _db_config
    
    # Allow override via environment variables for flexible deployment
    default_host = os.getenv("DB_HOST", db_host)
    if default_host == "db":  # Convert Docker service name to IP for IP-based access
        default_host = "172.20.0.12"
    
    _db_config.update({
        "db_name": db_name or os.getenv("POSTGRES_DB", "monopoly"),
        "db_user": db_user or os.getenv("POSTGRES_USER", "nihar"),
        "db_password": db_password or os.getenv("POSTGRES_PASSWORD"),
        "db_host": default_host,
        "db_port": db_port,
    })


def get_database_connection():
    """
    Create and return a new database connection using current configuration.

    Returns:
        psycopg2.connection: Database connection object

    Raises:
        psycopg2.Error: If connection fails
    """
    # Ensure configuration is set
    if _db_config["db_name"] is None:
        configure_database()
    
    return psycopg2.connect(
        dbname=_db_config["db_name"],
        user=_db_config["db_user"],
        password=_db_config["db_password"],
        host=_db_config["db_host"],
        port=_db_config["db_port"],
    )


def execute_query(query: str, params: Optional[Tuple] = None, fetch: bool = False):
    """
    Execute a database query with proper connection management.

    Args:
        query: SQL query to execute
        params: Query parameters (optional)
        fetch: Whether to fetch and return results

    Returns:
        Query results if fetch=True, None otherwise

    Raises:
        psycopg2.Error: If query execution fails
    """
    conn = None
    cur = None
    try:
        conn = get_database_connection()
        cur = conn.cursor()

        if params:
            cur.execute(query, params)
        else:
            cur.execute(query)

        if fetch:
            result = cur.fetchall()
            conn.commit()
            return result
        else:
            conn.commit()
            return None

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


def create_users_table():
    """
    Create the users table if it doesn't exist.
    """
    create_table_query = """
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        username VARCHAR(255) UNIQUE NOT NULL,
        password VARCHAR(255)
    );
    """
    execute_query(create_table_query)


def get_all_users() -> List[Tuple]:
    """
    Get all users from the database.

    Returns:
        List of tuples containing user data (id, username, password)
    """
    query = "SELECT * FROM users;"
    return execute_query(query, fetch=True) or []


def get_usernames() -> List[str]:
    """
    Get all usernames from the database.

    Returns:
        List of usernames
    """
    query = "SELECT username FROM users;"
    results = execute_query(query, fetch=True) or []
    return [row[0] for row in results]


def user_exists(username: str) -> bool:
    """
    Check if a user exists in the database.

    Args:
        username: Username to check

    Returns:
        True if user exists, False otherwise
    """
    return username in get_usernames()


def create_user(username: str, password: str = "") -> bool:
    """
    Create a new user in the database.

    Args:
        username: Username for the new user
        password: Password for the new user (optional)

    Returns:
        True if user was created successfully, False if user already exists

    Raises:
        psycopg2.Error: If database operation fails
    """
    if user_exists(username):
        return False

    query = "INSERT INTO users (username, password) VALUES (%s, %s);"
    execute_query(query, (username, password))
    return True


def initialize_database():
    """
    Initialize the database by creating necessary tables.

    This function sets up the database tables and ensures the database
    is ready for use.

    Raises:
        psycopg2.Error: If database initialization fails
    """
    # Ensure configuration is set
    configure_database()
    create_users_table()
