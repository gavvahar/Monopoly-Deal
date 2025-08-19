#!/usr/bin/env python3
"""
Example script demonstrating how to use the database module independently.

This script shows how the database module can be used as a shared component
across different projects.
"""

from database import DatabaseManager, UserRepository, initialize_database


def main():
    """Demonstrate database module usage."""
    print("Database Module Demo")
    print("=" * 40)

    # Method 1: Use the convenience function
    print("\n1. Using initialize_database() convenience function:")
    try:
        user_repo = initialize_database()
        print("✓ Database initialized successfully")
    except Exception as e:
        print(f"✗ Database initialization failed: {e}")
        print("Note: This is expected if PostgreSQL is not running")

    # Method 2: Manual setup for custom configuration
    print("\n2. Manual setup with custom configuration:")
    try:
        # Create a database manager with custom settings
        db_manager = DatabaseManager(
            db_name="my_custom_db",
            db_user="my_user",
            db_password="my_password",
            db_host="localhost",
            db_port=5432,
        )

        # Create a user repository
        user_repo = UserRepository(db_manager)
        print("✓ Custom database manager created successfully")

        # Try to create the users table (will fail without actual DB)
        user_repo.create_users_table()
        print("✓ Users table created successfully")

    except Exception as e:
        print(f"✗ Custom setup failed: {e}")
        print("Note: This is expected if PostgreSQL is not running")

    print("\n3. Available operations:")
    print("- user_repo.create_users_table()")
    print("- user_repo.get_all_users()")
    print("- user_repo.get_usernames()")
    print("- user_repo.user_exists(username)")
    print("- user_repo.create_user(username, password)")

    print("\n4. Database Manager features:")
    print("- Centralized connection management")
    print("- Environment variable support")
    print("- Proper error handling")
    print("- Connection cleanup")
    print("- Reusable across projects")


if __name__ == "__main__":
    main()
