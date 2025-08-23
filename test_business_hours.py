#!/usr/bin/env python3
"""
Tests for business hours restriction functionality.
"""

from fastapi.testclient import TestClient
from unittest.mock import patch
from datetime import datetime
import pytz
from main import app, is_business_hours


def test_business_hours_function():
    """Test the business hours checking function."""
    print("Testing business hours function...")

    # Test with different times using mock
    est = pytz.timezone("US/Eastern")

    # Test during business hours (10 AM EST)
    business_time = est.localize(datetime(2024, 1, 15, 10, 0, 0))  # Monday 10 AM
    with patch("main.datetime") as mock_datetime:
        mock_datetime.now.return_value = business_time
        assert is_business_hours() is True
    print("✓ Business hours detection (10 AM) test passed")

    # Test outside business hours (6 PM EST)
    after_hours = est.localize(datetime(2024, 1, 15, 18, 0, 0))  # Monday 6 PM
    with patch("main.datetime") as mock_datetime:
        mock_datetime.now.return_value = after_hours
        assert is_business_hours() is False
    print("✓ After hours detection (6 PM) test passed")

    # Test outside business hours (7 AM EST)
    early_hours = est.localize(datetime(2024, 1, 15, 7, 0, 0))  # Monday 7 AM
    with patch("main.datetime") as mock_datetime:
        mock_datetime.now.return_value = early_hours
        assert is_business_hours() is False
    print("✓ Early hours detection (7 AM) test passed")

    # Test edge case - exactly 9 AM (should be business hours)
    edge_start = est.localize(datetime(2024, 1, 15, 9, 0, 0))  # Monday 9 AM
    with patch("main.datetime") as mock_datetime:
        mock_datetime.now.return_value = edge_start
        assert is_business_hours() is True
    print("✓ Edge case 9 AM test passed")

    # Test edge case - exactly 5 PM (should NOT be business hours)
    edge_end = est.localize(datetime(2024, 1, 15, 17, 0, 0))  # Monday 5 PM
    with patch("main.datetime") as mock_datetime:
        mock_datetime.now.return_value = edge_end
        assert is_business_hours() is False
    print("✓ Edge case 5 PM test passed")


def test_business_hours_restriction():
    """Test that routes are properly restricted during business hours."""
    print("Testing business hours restriction on routes...")

    client = TestClient(app)
    est = pytz.timezone("US/Eastern")

    # Test during business hours
    business_time = est.localize(datetime(2024, 1, 15, 10, 0, 0))  # Monday 10 AM
    with patch("main.datetime") as mock_datetime:
        mock_datetime.now.return_value = business_time

        # Test home page
        response = client.get("/")
        assert response.status_code == 200
        assert "Service Temporarily Unavailable" in response.text
        assert "business hours" in response.text
        print("✓ Home page restriction test passed")

        # Test login page
        response = client.get("/login")
        assert response.status_code == 200
        assert "Service Temporarily Unavailable" in response.text
        print("✓ Login page restriction test passed")

        # Test login POST
        response = client.post("/login", data={"username": "test", "password": "test"})
        assert response.status_code == 200
        assert "Service Temporarily Unavailable" in response.text
        print("✓ Login POST restriction test passed")


def test_after_hours_access():
    """Test that routes work normally outside business hours."""
    print("Testing after hours access...")

    client = TestClient(app)
    est = pytz.timezone("US/Eastern")

    # Test outside business hours
    after_hours = est.localize(datetime(2024, 1, 15, 18, 0, 0))  # Monday 6 PM
    with patch("main.datetime") as mock_datetime:
        mock_datetime.now.return_value = after_hours

        # Test home page (should redirect to login)
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 200
        assert "Login" in response.text
        print("✓ After hours home page test passed")

        # Test login page
        response = client.get("/login")
        assert response.status_code == 200
        assert "Login" in response.text
        assert "Service Temporarily Unavailable" not in response.text
        print("✓ After hours login page test passed")


def test_current_time_display():
    """Test that the business hours page displays the current time."""
    print("Testing current time display...")

    client = TestClient(app)
    est = pytz.timezone("US/Eastern")

    # Test during business hours
    business_time = est.localize(datetime(2024, 1, 15, 10, 30, 0))  # Monday 10:30 AM
    with patch("main.datetime") as mock_datetime:
        mock_datetime.now.return_value = business_time

        response = client.get("/")
        assert response.status_code == 200
        assert "10:30 AM EST" in response.text
        print("✓ Current time display test passed")


def main():
    """Run all business hours tests."""
    print("Running Business Hours Tests")
    print("=" * 40)

    try:
        test_business_hours_function()
        test_business_hours_restriction()
        test_after_hours_access()
        test_current_time_display()

        print("=" * 40)
        print("✅ All business hours tests passed!")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        raise


if __name__ == "__main__":
    main()
