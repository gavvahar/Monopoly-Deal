#!/usr/bin/env python3
"""
Basic tests for the database module to verify functionality.
"""

import os
from unittest.mock import patch, MagicMock
from database import DatabaseManager, UserRepository


def test_database_manager_configuration():
    """Test DatabaseManager configuration handling."""
    print("Testing DatabaseManager configuration...")

    # Test default configuration
    db_manager = DatabaseManager()
    assert db_manager.db_name == os.getenv("POSTGRES_DB", "monopoly")
    assert db_manager.db_user == os.getenv("POSTGRES_USER", "nihar")
    assert db_manager.db_host == "db"
    assert db_manager.db_port == 5432
    print("✓ Default configuration test passed")

    # Test custom configuration
    custom_manager = DatabaseManager(
        db_name="test_db",
        db_user="test_user",
        db_password="test_pass",
        db_host="localhost",
        db_port=5433,
    )
    assert custom_manager.db_name == "test_db"
    assert custom_manager.db_user == "test_user"
    assert custom_manager.db_password == "test_pass"
    assert custom_manager.db_host == "localhost"
    assert custom_manager.db_port == 5433
    print("✓ Custom configuration test passed")


def test_user_repository_logic():
    """Test UserRepository logic with mocked database."""
    print("Testing UserRepository logic...")

    # Mock the database manager
    mock_db = MagicMock()
    user_repo = UserRepository(mock_db)

    # Test create_users_table
    user_repo.create_users_table()
    mock_db.execute_query.assert_called_once()
    create_table_call = mock_db.execute_query.call_args[0][0]
    assert "CREATE TABLE IF NOT EXISTS users" in create_table_call
    print("✓ create_users_table test passed")

    # Reset mock
    mock_db.reset_mock()

    # Test get_usernames
    mock_db.execute_query.return_value = [("alice",), ("bob",), ("charlie",)]
    usernames = user_repo.get_usernames()
    assert usernames == ["alice", "bob", "charlie"]
    mock_db.execute_query.assert_called_once_with(
        "SELECT username FROM users;", fetch=True
    )
    print("✓ get_usernames test passed")

    # Reset mock
    mock_db.reset_mock()

    # Test user_exists (with mocked get_usernames)
    with patch.object(user_repo, "get_usernames", return_value=["alice", "bob"]):
        assert user_repo.user_exists("alice") is True
        assert user_repo.user_exists("charlie") is False
    print("✓ user_exists test passed")

    # Test create_user - new user
    mock_db.reset_mock()
    with patch.object(user_repo, "user_exists", return_value=False):
        result = user_repo.create_user("new_user", "password")
        assert result is True
        mock_db.execute_query.assert_called_once_with(
            "INSERT INTO users (username, password) VALUES (%s, %s);",
            ("new_user", "password"),
        )
    print("✓ create_user (new user) test passed")

    # Test create_user - existing user
    mock_db.reset_mock()
    with patch.object(user_repo, "user_exists", return_value=True):
        result = user_repo.create_user("existing_user", "password")
        assert result is False
        mock_db.execute_query.assert_not_called()
    print("✓ create_user (existing user) test passed")


def main():
    """Run all tests."""
    print("Running Database Module Tests")
    print("=" * 40)

    try:
        test_database_manager_configuration()
        test_user_repository_logic()
        print("\n" + "=" * 40)
        print("✅ All tests passed!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        raise


if __name__ == "__main__":
    main()
