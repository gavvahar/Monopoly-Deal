#!/usr/bin/env python3
"""
Example script demonstrating how to use the database module independently.

This script shows how the database module can be used as a shared component
across different projects.
"""

from database import (
    configure_database,
    initialize_database,
    create_user,
    user_exists,
    get_usernames,
    get_all_users,
    execute_query,
)


def main():
    """Demonstrate database module usage."""
    print("Database Module Demo")
    print("=" * 40)

    # Method 1: Use the convenience function
    print("\n1. Using initialize_database() convenience function:")
    try:
        initialize_database()
        print("✓ Database initialized successfully")
    except Exception as e:
        print(f"✗ Database initialization failed: {e}")
        print("Note: This is expected if PostgreSQL is not running")

    # Method 2: Manual setup with custom configuration
    print("\n2. Manual setup with custom configuration:")
    try:
        # Configure database with custom settings
        configure_database(
            db_name="my_custom_db",
            db_user="my_user",
            db_password="my_password",
            db_host="localhost",
            db_port=5432,
        )
        print("✓ Custom database configuration set successfully")

        # Try to initialize the database (will fail without actual DB)
        initialize_database()
        print("✓ Database initialized with custom configuration")

    except Exception as e:
        print(f"✗ Custom setup failed: {e}")
        print("Note: This is expected if PostgreSQL is not running")

    print("\n3. Available operations:")
    print("- configure_database(db_name, db_user, db_password, db_host, db_port)")
    print("- initialize_database()")
    print("- create_user(username, password)")
    print("- user_exists(username)")
    print("- get_usernames()")
    print("- get_all_users()")
    print("- execute_query(query, params, fetch)")

    print("\n4. Database Module features:")
    print("- Function-based architecture")
    print("- Centralized connection management")
    print("- Environment variable support")
    print("- Proper error handling")
    print("- Connection cleanup")
    print("- Reusable across projects")

    # Example usage with try-catch for actual database operations
    print("\n5. Example operations (will show errors without running database):")
    try:
        # These operations will fail without a running database
        usernames = get_usernames()
        print(f"✓ Current users: {usernames}")
        
        # Try creating a user
        success = create_user("demo_user", "demo_password")
        print(f"✓ User creation result: {success}")
        
    except Exception as e:
        print(f"✗ Database operations failed: {e}")
        print("Note: This is expected if PostgreSQL is not running")


if __name__ == "__main__":
    main()
