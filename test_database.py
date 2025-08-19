#!/usr/bin/env python3
"""
Basic tests for the database module to verify functionality.
"""

import os
from unittest.mock import patch, MagicMock
import database


def test_database_configuration():
    """Test database configuration handling."""
    print("Testing database configuration...")

    # Test configure_database function
    database.configure_database(
        db_name="test_db",
        db_user="test_user",
        db_password="test_pass",
        db_host="localhost",
        db_port=5433,
    )
    
    # Check that configuration was set correctly
    assert database._db_config["db_name"] == "test_db"
    assert database._db_config["db_user"] == "test_user"
    assert database._db_config["db_password"] == "test_pass"
    assert database._db_config["db_host"] == "localhost"
    assert database._db_config["db_port"] == 5433
    print("✓ Custom configuration test passed")

    # Test default configuration
    database.configure_database()
    assert database._db_config["db_name"] == os.getenv("POSTGRES_DB", "monopoly")
    assert database._db_config["db_user"] == os.getenv("POSTGRES_USER", "nihar")
    assert database._db_config["db_host"] == "172.20.0.12"  # Updated default IP
    assert database._db_config["db_port"] == 5432
    print("✓ Default configuration test passed")


def test_database_functions():
    """Test database functions with mocked connections."""
    print("Testing database functions...")

    # Mock the execute_query function
    with patch('database.execute_query') as mock_execute:
        # Test create_users_table
        database.create_users_table()
        mock_execute.assert_called_once()
        create_table_call = mock_execute.call_args[0][0]
        assert "CREATE TABLE IF NOT EXISTS users" in create_table_call
        print("✓ create_users_table test passed")

        # Reset mock
        mock_execute.reset_mock()

        # Test get_usernames
        mock_execute.return_value = [("alice",), ("bob",), ("charlie",)]
        usernames = database.get_usernames()
        assert usernames == ["alice", "bob", "charlie"]
        mock_execute.assert_called_once_with("SELECT username FROM users;", fetch=True)
        print("✓ get_usernames test passed")

        # Reset mock
        mock_execute.reset_mock()

        # Test get_all_users
        mock_execute.return_value = [(1, "alice", "pass1"), (2, "bob", "pass2")]
        users = database.get_all_users()
        assert users == [(1, "alice", "pass1"), (2, "bob", "pass2")]
        mock_execute.assert_called_once_with("SELECT * FROM users;", fetch=True)
        print("✓ get_all_users test passed")

    # Test user_exists (with mocked get_usernames)
    with patch('database.get_usernames', return_value=["alice", "bob"]):
        assert database.user_exists("alice") is True
        assert database.user_exists("charlie") is False
    print("✓ user_exists test passed")

    # Test create_user - new user
    with patch('database.user_exists', return_value=False), \
         patch('database.execute_query') as mock_execute:
        result = database.create_user("new_user", "password")
        assert result is True
        mock_execute.assert_called_once_with(
            "INSERT INTO users (username, password) VALUES (%s, %s);",
            ("new_user", "password"),
        )
    print("✓ create_user (new user) test passed")

    # Test create_user - existing user
    with patch('database.user_exists', return_value=True), \
         patch('database.execute_query') as mock_execute:
        result = database.create_user("existing_user", "password")
        assert result is False
        mock_execute.assert_not_called()
    print("✓ create_user (existing user) test passed")


def test_initialize_database():
    """Test database initialization function."""
    print("Testing initialize_database...")

    with patch('database.configure_database') as mock_config, \
         patch('database.create_users_table') as mock_create_table:
        
        database.initialize_database()
        
        mock_config.assert_called_once()
        mock_create_table.assert_called_once()
        print("✓ initialize_database test passed")


def main():
    """Run all tests."""
    print("Running Database Module Tests")
    print("=" * 40)

    try:
        test_database_configuration()
        test_database_functions()
        test_initialize_database()
        print("\n" + "=" * 40)
        print("✅ All tests passed!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        raise


if __name__ == "__main__":
    main()