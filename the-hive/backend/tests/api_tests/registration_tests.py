"""
Registration API tests using pytest
"""
import pytest
import requests

BASE_URL = "http://localhost:5001/api"


class TestRegistration:
    """Test registration endpoint edge cases"""

    def test_registration_without_email(self):
        """Test that registration fails when email is missing"""
        user_data = {
            "email": "",
            "password": "SecurePass123!",
            "first_name": "Alex",
            "last_name": "Chen",
        }
        
        response = requests.post(
            f"{BASE_URL}/auth/register",
            json=user_data,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code >= 400
        assert "error" in response.json()

    def test_registration_with_weak_password(self):
        """Test that registration fails with weak password"""
        user_data = {
            "email": "test@example.com",
            "password": "123",
            "first_name": "Alex",
            "last_name": "Chen",
        }
        
        response = requests.post(
            f"{BASE_URL}/auth/register",
            json=user_data,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code >= 400

    def test_registration_with_invalid_email(self):
        """Test that registration fails with invalid email format"""
        user_data = {
            "email": "not-an-email",
            "password": "SecurePass123!",
            "first_name": "Alex",
            "last_name": "Chen",
        }
        
        response = requests.post(
            f"{BASE_URL}/auth/register",
            json=user_data,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code >= 400

    def test_registration_with_missing_fields(self):
        """Test that registration fails when required fields are missing"""
        user_data = {
            "email": "test@example.com",
            "password": "SecurePass123!",
        }
        
        response = requests.post(
            f"{BASE_URL}/auth/register",
            json=user_data,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code >= 400