#!/usr/bin/env python3
"""
Tests for 2FA functionality.
"""

import os
import pyotp
from fastapi.testclient import TestClient
from unittest.mock import patch
from main import app, get_admin_totp_secret, validate_admin_totp, generate_admin_qr_code


def test_totp_functions():
    """Test TOTP utility functions."""
    print("Testing TOTP utility functions...")

    # Test secret generation
    with patch.dict(os.environ, {"ADMIN_TOTP_SECRET": "JBSWY3DPEHPK3PXP"}):
        secret = get_admin_totp_secret()
        assert secret == "JBSWY3DPEHPK3PXP"
        print("✓ TOTP secret retrieval test passed")

    # Test TOTP validation with known secret
    with patch.dict(os.environ, {"ADMIN_TOTP_SECRET": "JBSWY3DPEHPK3PXP"}):
        # Generate a valid TOTP code
        totp = pyotp.TOTP("JBSWY3DPEHPK3PXP")
        valid_code = totp.now()

        assert validate_admin_totp(valid_code) is True
        print("✓ Valid TOTP code acceptance test passed")

        assert validate_admin_totp("000000") is False
        print("✓ Invalid TOTP code rejection test passed")

        assert validate_admin_totp("") is False
        print("✓ Empty TOTP code rejection test passed")

        assert validate_admin_totp("12345") is False  # Wrong length
        print("✓ Wrong length TOTP code rejection test passed")


def test_qr_code_generation():
    """Test QR code generation."""
    print("Testing QR code generation...")

    with patch.dict(
        os.environ, {"ADMIN_TOTP_SECRET": "JBSWY3DPEHPK3PXP", "ADMIN_USER": "testadmin"}
    ):
        qr_code = generate_admin_qr_code()
        assert qr_code.startswith("data:image/png;base64,")
        assert len(qr_code) > 100  # Should be a substantial base64 string
        print("✓ QR code generation test passed")


def test_2fa_setup_route():
    """Test the 2FA setup route."""
    print("Testing 2FA setup route...")

    client = TestClient(app)

    # Test without admin login (should redirect)
    response = client.get("/admin-2fa-setup", follow_redirects=False)
    assert response.status_code == 303  # Redirect to login
    print("✓ 2FA setup requires admin login test passed")

    # Mock admin session and test access
    with patch.dict(
        os.environ, {"ADMIN_TOTP_SECRET": "JBSWY3DPEHPK3PXP", "ADMIN_USER": "testadmin"}
    ):
        # Mock get_current_admin to return admin username
        with patch("main.get_current_admin") as mock_admin:
            mock_admin.return_value = "testadmin"

            response = client.get("/admin-2fa-setup")
            assert response.status_code == 200
            assert "Two-Factor Authentication Setup" in response.text
            assert "data:image/png;base64," in response.text
            assert "JBSWY3DPEHPK3PXP" in response.text
            print("✓ 2FA setup page access test passed")


def test_admin_bypass_2fa_validation():
    """Test comprehensive 2FA validation in admin bypass."""
    print("Testing admin bypass 2FA validation...")

    client = TestClient(app)

    with patch.dict(
        os.environ,
        {"ADMIN_PASSWORD": "test_pass", "ADMIN_TOTP_SECRET": "JBSWY3DPEHPK3PXP"},
    ):
        # Test with valid password and valid TOTP
        totp = pyotp.TOTP("JBSWY3DPEHPK3PXP")
        valid_code = totp.now()

        response = client.post(
            "/admin-bypass",
            data={
                "admin_password": "test_pass",
                "totp_code": valid_code,
                "redirect_url": "/",
            },
            follow_redirects=False,
        )
        assert response.status_code == 303  # Should redirect
        print("✓ Valid password and TOTP acceptance test passed")

        # Test with valid password but invalid TOTP
        response = client.post(
            "/admin-bypass",
            data={
                "admin_password": "test_pass",
                "totp_code": "000000",
                "redirect_url": "/",
            },
        )
        assert response.status_code == 200  # Should return error page
        assert "Invalid 2FA code" in response.text
        print("✓ Valid password but invalid TOTP rejection test passed")

        # Test with invalid password (should fail before TOTP check)
        response = client.post(
            "/admin-bypass",
            data={
                "admin_password": "wrong_pass",
                "totp_code": valid_code,
                "redirect_url": "/",
            },
        )
        assert response.status_code == 200  # Should return error page
        assert "Invalid admin password" in response.text
        print("✓ Invalid password rejection test passed")


def test_business_hours_template_updates():
    """Test that business hours template includes 2FA fields."""
    print("Testing business hours template 2FA updates...")

    client = TestClient(app)

    # Mock business hours to force restriction
    with patch("main.is_business_hours") as mock_hours:
        mock_hours.return_value = True

        response = client.get("/")
        assert response.status_code == 200
        assert "2FA Code (6 digits)" in response.text
        assert "authenticator app" in response.text
        assert "Admin Access (2FA Required)" in response.text
        print("✓ Business hours template 2FA updates test passed")


def main():
    """Run all 2FA tests."""
    print("Running 2FA Tests")
    print("=" * 40)

    test_totp_functions()
    test_qr_code_generation()
    test_2fa_setup_route()
    test_admin_bypass_2fa_validation()
    test_business_hours_template_updates()

    print("=" * 40)
    print("✅ All 2FA tests passed!")


if __name__ == "__main__":
    main()
