"""
Database module for Monopoly Deal - A shareable database project.

This module provides database connection management and data access operations
that can be shared across multiple projects.
"""

import os
import psycopg2
from typing import List, Tuple, Optional


class DatabaseManager:
    """
    Manages database connections and configuration.

    This class centralizes database connection logic and can be easily
    shared across multiple projects.
    """

    def __init__(
        self,
        db_name: Optional[str] = None,
        db_user: Optional[str] = None,
        db_password: Optional[str] = None,
        db_host: str = "db",
        db_port: int = 5432,
    ):
        """
        Initialize database manager with connection parameters.

        Args:
            db_name: Database name (defaults to env POSTGRES_DB or "monopoly")
            db_user: Database user (defaults to env POSTGRES_USER or "nihar")
            db_password: Database password (defaults to env POSTGRES_PASSWORD)
            db_host: Database host (defaults to "db")
            db_port: Database port (defaults to 5432)
        """
        self.db_name = db_name or os.getenv("POSTGRES_DB", "monopoly")
        self.db_user = db_user or os.getenv("POSTGRES_USER", "nihar")
        self.db_password = db_password or os.getenv("POSTGRES_PASSWORD")
        self.db_host = db_host
        self.db_port = db_port

    def get_connection(self):
        """
        Create and return a new database connection.

        Returns:
            psycopg2.connection: Database connection object

        Raises:
            psycopg2.Error: If connection fails
        """
        return psycopg2.connect(
            dbname=self.db_name,
            user=self.db_user,
            password=self.db_password,
            host=self.db_host,
            port=self.db_port,
        )

    def execute_query(
        self, query: str, params: Optional[Tuple] = None, fetch: bool = False
    ):
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
            conn = self.get_connection()
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


class UserRepository:
    """
    Repository class for user-related database operations.

    This class provides a clean API for user management operations
    and can be easily extended or shared across projects.
    """

    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize user repository with a database manager.

        Args:
            db_manager: DatabaseManager instance for database operations
        """
        self.db = db_manager

    def create_users_table(self):
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
        self.db.execute_query(create_table_query)

    def get_all_users(self) -> List[Tuple]:
        """
        Get all users from the database.

        Returns:
            List of tuples containing user data (id, username, password)
        """
        query = "SELECT * FROM users;"
        return self.db.execute_query(query, fetch=True) or []

    def get_usernames(self) -> List[str]:
        """
        Get all usernames from the database.

        Returns:
            List of usernames
        """
        query = "SELECT username FROM users;"
        results = self.db.execute_query(query, fetch=True) or []
        return [row[0] for row in results]

    def user_exists(self, username: str) -> bool:
        """
        Check if a user exists in the database.

        Args:
            username: Username to check

        Returns:
            True if user exists, False otherwise
        """
        return username in self.get_usernames()

    def create_user(self, username: str, password: str = "") -> bool:
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
        if self.user_exists(username):
            return False

        query = "INSERT INTO users (username, password) VALUES (%s, %s);"
        self.db.execute_query(query, (username, password))
        return True


def initialize_database(db_manager: Optional[DatabaseManager] = None) -> UserRepository:
    """
    Initialize the database and return a UserRepository instance.

    This function sets up the database tables and returns a repository
    instance that can be used for user operations.

    Args:
        db_manager: Optional DatabaseManager instance. If None, creates a new one.

    Returns:
        UserRepository instance ready for use

    Raises:
        psycopg2.Error: If database initialization fails
    """
    if db_manager is None:
        db_manager = DatabaseManager()

    user_repo = UserRepository(db_manager)
    user_repo.create_users_table()

    return user_repo
