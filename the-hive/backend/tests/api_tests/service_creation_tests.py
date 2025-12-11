"""
Test cases for service creation API endpoints
Tests both offers and needs with various edge cases
"""

import pytest
import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:5001/api"


class TestServiceCreation:
    """Test suite for service creation"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Create and login a test user, return auth token"""
        user_data = {
            "email": "test.user@hive.com",
            "password": "TestUser123!",
            "first_name": "Test",
            "last_name": "User",
            "phone_number": "+1234567890"
        }
        
        # Try to login first
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={
                "email": user_data["email"],
                "password": user_data["password"]
            },
            headers={"Content-Type": "application/json"}
        )
        
        # If login successful, user already exists
        if response.status_code == 200 and "access_token" in response.json():
            print("✓ Test user already exists, logged in successfully")
            return response.json()["access_token"]
        
        # If login failed, register new user
        print("✓ Test user not found, creating new account...")
        response = requests.post(
            f"{BASE_URL}/auth/register",
            json=user_data,
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 201, f"Registration failed: {response.json()}"
        
        verification_token = response.json()["verification_token"]
        
        # Verify email
        response = requests.get(
            f"{BASE_URL}/auth/verify-email",
            params={"token": verification_token}
        )
        assert response.status_code == 200, f"Email verification failed: {response.json()}"
        
        # Login with new account
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={
                "email": user_data["email"],
                "password": user_data["password"]
            },
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200, f"Login failed: {response.json()}"
        
        print("✓ Test user created and logged in successfully")
        return response.json()["access_token"]
    
    @pytest.fixture
    def sample_tags(self, auth_token):
        """Create sample tags for testing"""
        tag_names = ["test-tag", "sample"]
        tag_ids = []
        
        for tag_name in tag_names:
            response = requests.post(
                f"{BASE_URL}/tags",
                json={"name": tag_name},
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {auth_token}"
                }
            )
            
            if response.status_code == 201:
                tag_ids.append(response.json()["tag"]["id"])
            elif response.status_code == 409:
                # Tag exists, get its ID
                existing_tag = response.json().get("tag", {})
                if existing_tag.get("id"):
                    tag_ids.append(existing_tag["id"])
        
        return tag_ids
    
    # ==================== VALID OFFER TESTS ====================
    
    def test_create_valid_offer_online(self, auth_token, sample_tags):
        """Test creating a valid online offer"""
        offer_data = {
            "service_type": "offer",
            "title": "Online Tutoring",
            "description": "I offer online tutoring sessions for students",
            "hours_required": 2.0,
            "location_type": "online",
            "tag_ids": sample_tags,
            "availability": [
                {"day_of_week": 1, "start_time": "18:00", "end_time": "20:00"}
            ]
        }
        
        response = requests.post(
            f"{BASE_URL}/services",
            json=offer_data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {auth_token}"
            }
        )
        
        assert response.status_code == 201
        assert "service_id" in response.json()
    
    def test_create_valid_offer_in_person(self, auth_token, sample_tags):
        """Test creating a valid in-person offer with location"""
        offer_data = {
            "service_type": "offer",
            "title": "In-Person Guitar Lessons",
            "description": "Guitar lessons at my studio",
            "hours_required": 2,
            "location_type": "in-person",
            "location_address": "Downtown Music Studio",
            "latitude": 41.0082,
            "longitude": 28.9784,
            "tag_ids": sample_tags,
            "availability": [
                {"day_of_week": 3, "start_time": "14:00", "end_time": "18:00"}
            ]
        }
        
        response = requests.post(
            f"{BASE_URL}/services",
            json=offer_data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {auth_token}"
            }
        )
        
        assert response.status_code == 201
        assert "service_id" in response.json()
    
    # ==================== VALID NEED TESTS ====================
    
    def test_create_valid_need_online(self, auth_token, sample_tags):
        """Test creating a valid online need"""
        need_data = {
            "service_type": "need",
            "title": "Need Programming Help",
            "description": "I need help with Python programming",
            "hours_required": 2.0,
            "location_type": "online",
            "service_date": "2025-12-20",
            "start_time": "14:00",
            "end_time": "16:00",
            "tag_ids": sample_tags
        }
        
        response = requests.post(
            f"{BASE_URL}/services",
            json=need_data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {auth_token}"
            }
        )
        
        assert response.status_code == 201
        assert "service_id" in response.json()
    
    def test_create_valid_need_in_person(self, auth_token, sample_tags):
        """Test creating a valid in-person need with location"""
        need_data = {
            "service_type": "need",
            "title": "Need Moving Help",
            "description": "I need help moving furniture",
            "hours_required": 3.0,
            "location_type": "in-person",
            "location_address": "My apartment",
            "latitude": 41.0100,
            "longitude": 28.9800,
            "service_date": "2025-12-25",
            "start_time": "10:00",
            "end_time": "13:00",
            "tag_ids": sample_tags
        }
        
        response = requests.post(
            f"{BASE_URL}/services",
            json=need_data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {auth_token}"
            }
        )
        
        assert response.status_code == 201
        assert "service_id" in response.json()
    
    # ==================== EDGE CASE: MISSING REQUIRED FIELDS ====================
    
    def test_create_offer_missing_title(self, auth_token):
        """Test creating offer without title"""
        offer_data = {
            "service_type": "offer",
            "description": "Missing title",
            "hours_required": 2.0,
            "location_type": "online"
        }
        
        response = requests.post(
            f"{BASE_URL}/services",
            json=offer_data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {auth_token}"
            }
        )
        
        assert response.status_code == 400
        assert "error" in response.json()
    
    def test_create_need_missing_description(self, auth_token):
        """Test creating need without description"""
        need_data = {
            "service_type": "need",
            "title": "Missing Description",
            "hours_required": 2.0,
            "location_type": "online"
        }
        
        response = requests.post(
            f"{BASE_URL}/services",
            json=need_data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {auth_token}"
            }
        )
        
        assert response.status_code == 400
        assert "error" in response.json()
    
    # ==================== EDGE CASE: INVALID HOURS ====================
    
    def test_create_offer_hours_too_low(self, auth_token):
        """Test creating offer with hours less than 1"""
        offer_data = {
            "service_type": "offer",
            "title": "Invalid Hours",
            "description": "This should fail",
            "hours_required": 0,
            "location_type": "online"
        }
        
        response = requests.post(
            f"{BASE_URL}/services",
            json=offer_data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {auth_token}"
            }
        )
        
        assert response.status_code == 400
        assert "hours_required" in response.json()["error"].lower()
    
    def test_create_offer_hours_too_high(self, auth_token):
        """Test creating offer with hours more than 3.0"""
        offer_data = {
            "service_type": "offer",
            "title": "Invalid Hours",
            "description": "This should fail",
            "hours_required": 5.0,
            "location_type": "online"
        }
        
        response = requests.post(
            f"{BASE_URL}/services",
            json=offer_data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {auth_token}"
            }
        )
        
        assert response.status_code == 400
        assert "hours_required" in response.json()["error"].lower()
    
    def test_create_need_hours_exactly_minimum(self, auth_token):
        """Test creating need with exactly 1.0 hours (boundary)"""
        need_data = {
            "service_type": "need",
            "title": "Minimum Hours",
            "description": "Testing minimum valid hours",
            "hours_required": 1.0,
            "location_type": "online",
            "service_date": "2025-12-20",
            "start_time": "14:00",
            "end_time": "15:00"
        }
        
        response = requests.post(
            f"{BASE_URL}/services",
            json=need_data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {auth_token}"
            }
        )
        
        assert response.status_code == 201
    
    def test_create_offer_hours_exactly_maximum(self, auth_token):
        """Test creating offer with exactly 3.0 hours (boundary)"""
        offer_data = {
            "service_type": "offer",
            "title": "Maximum Hours",
            "description": "Testing maximum valid hours",
            "hours_required": 3.0,
            "location_type": "online",
            "availability": [
                {"day_of_week": 1, "start_time": "14:00", "end_time": "17:00"}
            ]
        }
        
        response = requests.post(
            f"{BASE_URL}/services",
            json=offer_data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {auth_token}"
            }
        )
        
        assert response.status_code == 201
    
    # ==================== EDGE CASE: INVALID LOCATION TYPE ====================
    
    def test_create_offer_invalid_location_type(self, auth_token):
        """Test creating offer with invalid location type"""
        offer_data = {
            "service_type": "offer",
            "title": "Invalid Location Type",
            "description": "This should fail",
            "hours_required": 2.0,
            "location_type": "anywhere"  # Invalid type
        }
        
        response = requests.post(
            f"{BASE_URL}/services",
            json=offer_data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {auth_token}"
            }
        )
        
        assert response.status_code == 400
        assert "location_type" in response.json()["error"].lower()
    
    # ==================== EDGE CASE: MISSING LOCATION FOR IN-PERSON ====================
    
    def test_create_offer_in_person_no_location(self, auth_token):
        """Test creating in-person offer without location coordinates"""
        offer_data = {
            "service_type": "offer",
            "title": "In-Person Without Location",
            "description": "This should fail - no coordinates",
            "hours_required": 2.0,
            "location_type": "in-person",
            "availability": [
                {"day_of_week": 1, "start_time": "14:00", "end_time": "16:00"}
            ]
        }
        
        response = requests.post(
            f"{BASE_URL}/services",
            json=offer_data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {auth_token}"
            }
        )
        
        assert response.status_code == 400
        assert "location" in response.json()["error"].lower()
    
    def test_create_need_both_type_no_location(self, auth_token):
        """Test creating 'both' type need without location coordinates"""
        need_data = {
            "service_type": "need",
            "title": "Both Type Without Location",
            "description": "This should fail - no coordinates",
            "hours_required": 2.0,
            "location_type": "both",
            "service_date": "2025-12-20",
            "start_time": "14:00",
            "end_time": "16:00"
        }
        
        response = requests.post(
            f"{BASE_URL}/services",
            json=need_data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {auth_token}"
            }
        )
        
        assert response.status_code == 400
        assert "location" in response.json()["error"].lower()
    
    def test_create_offer_in_person_only_latitude(self, auth_token):
        """Test creating in-person offer with only latitude (missing longitude)"""
        offer_data = {
            "service_type": "offer",
            "title": "Incomplete Location",
            "description": "This should fail - only latitude",
            "hours_required": 2.0,
            "location_type": "in-person",
            "latitude": 41.0082,
            "availability": [
                {"day_of_week": 1, "start_time": "14:00", "end_time": "16:00"}
            ]
        }
        
        response = requests.post(
            f"{BASE_URL}/services",
            json=offer_data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {auth_token}"
            }
        )
        
        assert response.status_code == 400
        assert "location" in response.json()["error"].lower()
    
    # ==================== EDGE CASE: INVALID SERVICE TYPE ====================
    
    def test_create_service_invalid_type(self, auth_token):
        """Test creating service with invalid service type"""
        service_data = {
            "service_type": "request",  # Invalid type
            "title": "Invalid Type",
            "description": "This should fail",
            "hours_required": 2.0,
            "location_type": "online"
        }
        
        response = requests.post(
            f"{BASE_URL}/services",
            json=service_data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {auth_token}"
            }
        )
        
        assert response.status_code == 400
        assert "service_type" in response.json()["error"].lower()
    
    # ==================== EDGE CASE: UNAUTHORIZED ACCESS ====================
    
    def test_create_service_no_auth(self):
        """Test creating service without authentication"""
        offer_data = {
            "service_type": "offer",
            "title": "Unauthorized Offer",
            "description": "This should fail - no auth",
            "hours_required": 2.0,
            "location_type": "online"
        }
        
        response = requests.post(
            f"{BASE_URL}/services",
            json=offer_data,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 401
        assert "error" in response.json()
    
    def test_create_service_invalid_token(self):
        """Test creating service with invalid token"""
        offer_data = {
            "service_type": "offer",
            "title": "Invalid Token Offer",
            "description": "This should fail - invalid token",
            "hours_required": 2.0,
            "location_type": "online"
        }
        
        response = requests.post(
            f"{BASE_URL}/services",
            json=offer_data,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer invalid_token_here"
            }
        )
        
        assert response.status_code == 401
        assert "error" in response.json()
    
    # ==================== EDGE CASE: EMPTY/WHITESPACE VALUES ====================
    
    def test_create_offer_empty_title(self, auth_token):
        """Test creating offer with empty title"""
        offer_data = {
            "service_type": "offer",
            "title": "   ",  # Only whitespace
            "description": "This should fail",
            "hours_required": 2.0,
            "location_type": "online"
        }
        
        response = requests.post(
            f"{BASE_URL}/services",
            json=offer_data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {auth_token}"
            }
        )
        
        # Should fail because title will be empty after strip()
        assert response.status_code in [400, 500]
    
    def test_create_need_empty_description(self, auth_token):
        """Test creating need with empty description"""
        need_data = {
            "service_type": "need",
            "title": "Valid Title",
            "description": "",  # Empty string
            "hours_required": 2.0,
            "location_type": "online",
            "service_date": "2025-12-20",
            "start_time": "14:00",
            "end_time": "16:00"
        }
        
        response = requests.post(
            f"{BASE_URL}/services",
            json=need_data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {auth_token}"
            }
        )
        
        # Should fail because description will be empty after strip()
        assert response.status_code in [400, 500]
    
    # ==================== EDGE CASE: BOUNDARY TESTING ====================
    
    def test_create_offer_hours_decimal(self, auth_token):
        """Test that creating offer with decimal hours (1.5) is rejected"""
        offer_data = {
            "service_type": "offer",
            "title": "Decimal Hours",
            "description": "Testing decimal hours value",
            "hours_required": 1.5,
            "location_type": "online",
            "availability": [
                {"day_of_week": 2, "start_time": "14:00", "end_time": "15:30"}
            ]
        }
        
        response = requests.post(
            f"{BASE_URL}/services",
            json=offer_data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {auth_token}"
            }
        )
        
        assert response.status_code == 400
        assert "integer" in response.json()["error"].lower()
    
    def test_create_offer_with_both_location_type(self, auth_token):
        """Test creating offer with 'both' location type and valid coordinates"""
        offer_data = {
            "service_type": "offer",
            "title": "Flexible Location Service",
            "description": "Available both online and in-person",
            "hours_required": 2.0,
            "location_type": "both",
            "latitude": 41.0082,
            "longitude": 28.9784,
            "availability": [
                {"day_of_week": 1, "start_time": "10:00", "end_time": "12:00"}
            ]
        }
        
        response = requests.post(
            f"{BASE_URL}/services",
            json=offer_data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {auth_token}"
            }
        )
        
        assert response.status_code == 201


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
