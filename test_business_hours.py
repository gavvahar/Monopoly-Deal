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

    # Test during business hours on weekday (Tuesday 10 AM EST)
    business_time = est.localize(datetime(2024, 1, 16, 10, 0, 0))  # Tuesday 10 AM
    with patch("main.datetime") as mock_datetime:
        mock_datetime.now.return_value = business_time
        assert is_business_hours() is True
    print("✓ Business hours detection (Tuesday 10 AM) test passed")

    # Test during business hours on weekend (Saturday 10 AM EST)
    weekend_time = est.localize(datetime(2024, 1, 20, 10, 0, 0))  # Saturday 10 AM
    with patch("main.datetime") as mock_datetime:
        mock_datetime.now.return_value = weekend_time
        assert is_business_hours() is False
    print("✓ Weekend access (Saturday 10 AM) test passed")

    # Test during business hours on weekend (Sunday 2 PM EST)
    sunday_time = est.localize(datetime(2024, 1, 21, 14, 0, 0))  # Sunday 2 PM
    with patch("main.datetime") as mock_datetime:
        mock_datetime.now.return_value = sunday_time
        assert is_business_hours() is False
    print("✓ Weekend access (Sunday 2 PM) test passed")

    # Test outside business hours on weekday (Monday 6 PM EST)
    after_hours = est.localize(datetime(2024, 1, 15, 18, 0, 0))  # Monday 6 PM
    with patch("main.datetime") as mock_datetime:
        mock_datetime.now.return_value = after_hours
        assert is_business_hours() is False
    print("✓ After hours detection (Monday 6 PM) test passed")

    # Test outside business hours on weekday (Friday 7 AM EST)
    early_hours = est.localize(datetime(2024, 1, 19, 7, 0, 0))  # Friday 7 AM
    with patch("main.datetime") as mock_datetime:
        mock_datetime.now.return_value = early_hours
        assert is_business_hours() is False
    print("✓ Early hours detection (Friday 7 AM) test passed")

    # Test edge case - exactly 9 AM on weekday (should be business hours)
    edge_start = est.localize(datetime(2024, 1, 17, 9, 0, 0))  # Wednesday 9 AM
    with patch("main.datetime") as mock_datetime:
        mock_datetime.now.return_value = edge_start
        assert is_business_hours() is True
    print("✓ Edge case Wednesday 9 AM test passed")

    # Test edge case - exactly 5 PM on weekday (should NOT be business hours)
    edge_end = est.localize(datetime(2024, 1, 18, 17, 0, 0))  # Thursday 5 PM
    with patch("main.datetime") as mock_datetime:
        mock_datetime.now.return_value = edge_end
        assert is_business_hours() is False
    print("✓ Edge case Thursday 5 PM test passed")


def test_business_hours_restriction():
    """Test that routes are properly restricted during business hours."""
    print("Testing business hours restriction on routes...")

    client = TestClient(app)
    est = pytz.timezone("US/Eastern")

    # Test during business hours on weekday
    business_time = est.localize(datetime(2024, 1, 16, 10, 0, 0))  # Tuesday 10 AM
    with patch("main.datetime") as mock_datetime:
        mock_datetime.now.return_value = business_time

        # Test home page
        response = client.get("/")
        assert response.status_code == 200
        assert "Service Temporarily Unavailable" in response.text
        assert "Monday-Friday" in response.text
        print("✓ Home page restriction test passed")

        # Test login page
        response = client.get("/login")
        assert response.status_code == 200
        assert "Service Temporarily Unavailable" in response.text
        assert "Admin Access" in response.text
        print("✓ Login page restriction test passed")

        # Test login POST
        response = client.post("/login", data={"username": "test", "password": "test"})
        assert response.status_code == 200
        assert "Service Temporarily Unavailable" in response.text
        print("✓ Login POST restriction test passed")


def test_weekend_access():
    """Test that routes work normally during weekends."""
    print("Testing weekend access...")

    client = TestClient(app)
    est = pytz.timezone("US/Eastern")

    # Test during business hours on weekend (Saturday 11 AM)
    weekend_time = est.localize(datetime(2024, 1, 20, 11, 0, 0))  # Saturday 11 AM
    with patch("main.datetime") as mock_datetime:
        mock_datetime.now.return_value = weekend_time

        # Test home page (should redirect to login, not show restriction)
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 200
        assert "Login" in response.text
        assert "Service Temporarily Unavailable" not in response.text
        print("✓ Weekend home page test passed")

        # Test login page
        response = client.get("/login")
        assert response.status_code == 200
        assert "Login" in response.text
        assert "Service Temporarily Unavailable" not in response.text
        print("✓ Weekend login page test passed")


def test_after_hours_weekday_access():
    """Test that routes work normally outside business hours on weekdays."""
    print("Testing after hours weekday access...")

    client = TestClient(app)
    est = pytz.timezone("US/Eastern")

    # Test outside business hours on weekday
    after_hours = est.localize(datetime(2024, 1, 16, 18, 0, 0))  # Tuesday 6 PM
    with patch("main.datetime") as mock_datetime:
        mock_datetime.now.return_value = after_hours

        # Test home page (should redirect to login)
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 200
        assert "Login" in response.text
        assert "Service Temporarily Unavailable" not in response.text
        print("✓ After hours home page test passed")

        # Test login page
        response = client.get("/login")
        assert response.status_code == 200
        assert "Login" in response.text
        assert "Service Temporarily Unavailable" not in response.text
        print("✓ After hours login page test passed")


def test_admin_bypass():
    """Test admin bypass functionality."""
    print("Testing admin bypass functionality...")

    import os

    # Set admin password for testing
    os.environ["ADMIN_PASSWORD"] = "test_admin_pass"

    client = TestClient(app)
    est = pytz.timezone("US/Eastern")

    # Test during business hours on weekday
    business_time = est.localize(datetime(2024, 1, 16, 10, 0, 0))  # Tuesday 10 AM
    with patch("main.datetime") as mock_datetime:
        mock_datetime.now.return_value = business_time

        # First, verify restriction is active
        response = client.get("/")
        assert response.status_code == 200
        assert "Service Temporarily Unavailable" in response.text
        print("✓ Restriction active before bypass")

        # Test admin bypass with correct password
        response = client.post(
            "/admin-bypass",
            data={"admin_password": "test_admin_pass", "redirect_url": "/"},
            follow_redirects=False,
        )
        assert response.status_code == 303  # Redirect after successful bypass
        print("✓ Admin bypass successful")

        # Follow the redirect and test that bypass is active
        # Need to use the same client session for the bypass to persist
        redirect_response = client.get("/")
        assert redirect_response.status_code == 200
        assert "Login" in redirect_response.text
        assert "Service Temporarily Unavailable" not in redirect_response.text
        print("✓ Access granted after admin bypass")

        # Test admin bypass with incorrect password
        new_client = TestClient(app)  # New client without bypass session
        response = new_client.post(
            "/admin-bypass",
            data={"admin_password": "wrong_password", "redirect_url": "/"},
        )
        assert response.status_code == 200
        assert "Invalid admin password" in response.text
        print("✓ Invalid admin password rejected")


def test_current_time_display():
    """Test that the business hours page displays the current time."""
    print("Testing current time display...")

    client = TestClient(app)
    est = pytz.timezone("US/Eastern")

    # Test during business hours
    business_time = est.localize(datetime(2024, 1, 16, 10, 30, 0))  # Tuesday 10:30 AM
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
        test_weekend_access()
        test_after_hours_weekday_access()
        test_admin_bypass()
        test_current_time_display()

        print("=" * 40)
        print("✅ All business hours tests passed!")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        raise


if __name__ == "__main__":
    main()
