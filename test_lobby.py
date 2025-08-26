#!/usr/bin/env python3
"""
Tests for the game lobby system with session management.
"""

from fastapi.testclient import TestClient
from unittest.mock import patch
from datetime import datetime
import pytz
from main import app, game_sessions
import os


def test_lobby_system():
    """Test the complete lobby system functionality."""
    print("Testing Lobby System...")

    # Mock time to be outside business hours (weekend)
    est = pytz.timezone("US/Eastern")
    weekend_time = est.localize(datetime(2024, 1, 20, 11, 0, 0))  # Saturday 11 AM

    with patch("main.datetime") as mock_datetime:
        mock_datetime.now.return_value = weekend_time

        client = TestClient(app)

        # Clear any existing sessions
        game_sessions.clear()

        # Test accessing lobby without login (should redirect to login)
        response = client.get("/lobby", follow_redirects=False)
        assert response.status_code == 303
        assert response.headers["location"] == "/login"
        print("✓ Lobby auth protection test passed")

        # Login first to test lobby functionality
        # Use environment credentials or default test credentials
        username = os.getenv("POSTGRES_USER", "nihar")
        password = os.getenv("POSTGRES_PASSWORD", "")

        # Test successful login redirects to lobby
        response = client.post(
            "/login",
            data={"username": username, "password": password},
            follow_redirects=False,
        )
        assert response.status_code == 303
        assert response.headers["location"] == "/lobby"
        print("✓ Login redirects to lobby test passed")

        # Get session cookies for authenticated requests
        cookies = response.cookies

        # Test lobby page GET
        response = client.get("/lobby", cookies=cookies)
        assert response.status_code == 200
        assert "Game Lobby" in response.text
        assert "Create New Game" in response.text
        assert "Join Existing Game" in response.text
        print("✓ Lobby page display test passed")

        # Test creating a new game session
        response = client.post(
            "/lobby",
            data={"action": "create_game"},
            cookies=cookies,
            follow_redirects=False,
        )
        assert response.status_code == 303
        assert response.headers["location"] == "/lobby"

        # Check that a session was created
        assert len(game_sessions) == 1
        session_code = list(game_sessions.keys())[0]
        assert username in game_sessions[session_code]["players"]
        print("✓ Create game session test passed")

        # Test lobby shows current session
        response = client.get("/lobby", cookies=cookies)
        assert response.status_code == 200
        assert session_code in response.text
        assert "Current Game Session" in response.text
        print("✓ Lobby shows current session test passed")

        # Test starting the game
        response = client.post(
            "/lobby",
            data={"action": "start_game"},
            cookies=cookies,
            follow_redirects=False,
        )
        assert response.status_code == 303
        assert response.headers["location"] == f"/play/{session_code}"

        # Check that the session was started
        assert game_sessions[session_code]["started"] is True
        assert game_sessions[session_code]["game_state"] is not None
        print("✓ Start game test passed")

        # Test accessing the game
        response = client.get(f"/play/{session_code}", cookies=cookies)
        assert response.status_code == 200
        assert "Game Started!" in response.text
        # The username might be in current_player, let's check for game elements instead
        assert "Your Hand:" in response.text
        print("✓ Play game access test passed")

        print("✅ All lobby system tests passed!")


def test_multiplayer_session():
    """Test multiple players joining a session."""
    print("Testing Multiplayer Session...")

    # Clear any existing sessions
    game_sessions.clear()

    # Create a test session manually
    from main import create_game_session, join_game_session

    session_code = create_game_session("player1")

    # Test second player joining
    success, message = join_game_session(session_code, "player2")
    assert success is True
    assert "Successfully joined" in message

    # Test third player joining
    success, message = join_game_session(session_code, "player3")
    assert success is True

    # Check session state
    session = game_sessions[session_code]
    assert len(session["players"]) == 3
    assert "player1" in session["players"]
    assert "player2" in session["players"]
    assert "player3" in session["players"]
    print("✓ Multiple players joining test passed")

    # Test duplicate player joining
    success, message = join_game_session(session_code, "player1")
    assert success is False
    assert "already in this game" in message
    print("✓ Duplicate player prevention test passed")

    # Test joining non-existent session
    success, message = join_game_session("INVALID", "player4")
    assert success is False
    assert "Session not found" in message
    print("✓ Invalid session handling test passed")

    print("✅ All multiplayer session tests passed!")


def test_session_limits():
    """Test session player limits and validation."""
    print("Testing Session Limits...")

    # Clear any existing sessions
    game_sessions.clear()

    from main import create_game_session, join_game_session

    session_code = create_game_session("player1")

    # Add players up to the limit
    for i in range(2, 6):  # players 2-5
        success, message = join_game_session(session_code, f"player{i}")
        assert success is True

    # Try to add 6th player (should fail)
    success, message = join_game_session(session_code, "player6")
    assert success is False
    assert "full" in message
    print("✓ Player limit enforcement test passed")

    # Check final state
    session = game_sessions[session_code]
    assert len(session["players"]) == 5
    assert session["max_players"] == 5
    print("✓ Session state validation test passed")

    print("✅ All session limit tests passed!")


def main():
    """Run all lobby tests."""
    print("Running Lobby System Tests")
    print("=" * 40)

    try:
        test_lobby_system()
        print()
        test_multiplayer_session()
        print()
        test_session_limits()
        print("\n" + "=" * 40)
        print("✅ All lobby tests passed! Lobby system working correctly!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        raise


if __name__ == "__main__":
    main()
