#!/usr/bin/env python3
"""
Basic tests for the FastAPI application to verify conversion from Flask.
Updated to handle business hours restrictions.
"""

from fastapi.testclient import TestClient
from unittest.mock import patch
from datetime import datetime
import pytz
from main import app


def test_fastapi_application():
    """Test FastAPI application endpoints outside business hours."""
    print("Testing FastAPI application...")

    client = TestClient(app)
    est = pytz.timezone("US/Eastern")

    # Test outside business hours (6 PM EST) to ensure normal functionality
    after_hours = est.localize(datetime(2024, 1, 15, 18, 0, 0))  # Monday 6 PM
    with patch("main.datetime") as mock_datetime:
        mock_datetime.now.return_value = after_hours

        # Test home page (redirects to login)
        response = client.get("/")
        assert response.status_code == 200
        assert "Monopoly Deal" in response.text
        assert "Login" in response.text
        print("✓ Home page test passed")

        # Test login page GET
        response = client.get("/login")
        assert response.status_code == 200
        assert "username" in response.text
        assert "password" in response.text
        print("✓ Login page GET test passed")

        # Test docs page (FastAPI feature)
        response = client.get("/docs")
        assert response.status_code == 200
        print("✓ API docs test passed")

        # Test invalid login POST
        response = client.post(
            "/login", data={"username": "invalid", "password": "wrong"}
        )
        assert response.status_code == 200
        assert "Invalid username or password" in response.text
        print("✓ Invalid login test passed")

        # Test play page without session (should redirect)
        response = client.get("/play", follow_redirects=False)
        assert response.status_code == 303  # Redirect
        print("✓ Play page auth test passed")

        # Test logout
        response = client.get("/logout", follow_redirects=False)
        assert response.status_code == 303  # Redirect
        print("✓ Logout test passed")

    print("✅ All FastAPI tests passed!")


def test_game_logic():
    """Test game logic still works after conversion."""
    print("Testing game logic...")

    from game import start_game, draw_card, play_card

    # Test game creation
    game_state = start_game(["TestPlayer"])
    assert game_state["started"] is True
    assert len(game_state["players"]) == 1
    assert game_state["players"][0]["name"] == "TestPlayer"
    print("✓ Game creation test passed")

    # Test draw card
    initial_hand_size = len(game_state["players"][0]["hand"])
    draw_card(game_state)
    new_hand_size = len(game_state["players"][0]["hand"])
    assert new_hand_size == initial_hand_size + 1
    print("✓ Draw card test passed")

    # Test play card
    if game_state["players"][0]["hand"]:
        play_card(game_state, 0)
        print("✓ Play card test passed")

    print("✅ All game logic tests passed!")


def main():
    """Run all tests."""
    print("Running FastAPI Conversion Tests")
    print("=" * 40)

    try:
        test_fastapi_application()
        test_game_logic()
        print("\n" + "=" * 40)
        print("✅ All tests passed! Flask to FastAPI conversion successful!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        raise


if __name__ == "__main__":
    main()
