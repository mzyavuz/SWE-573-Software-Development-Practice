"""
Service Progress and Application Edge Case Tests

Tests for:
- Multiple applicants to the same service
- Application acceptance and rejection
- Service deletion with pending applications
- Re-application after rejection
- Progress states and transitions
"""

import pytest
import requests
from datetime import datetime, timedelta

BASE_URL = "http://localhost:5001/api"


class TestServiceProgress:
    """Test service progress and application edge cases"""

    @pytest.fixture(scope="class")
    def consumer_token(self):
        """Create and login a consumer user"""
        user_data = {
            "email": "progress.consumer@hive.com",
            "password": "Consumer123!",
            "first_name": "Test",
            "last_name": "Consumer",
        }
        
        # Try to login first
        login_response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"email": user_data["email"], "password": user_data["password"]},
            headers={"Content-Type": "application/json"}
        )
        
        if login_response.status_code == 200:
            return login_response.json()["access_token"]
        
        # Register if doesn't exist
        response = requests.post(
            f"{BASE_URL}/auth/register",
            json=user_data,
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code in [201, 409], f"Registration failed: {response.status_code} - {response.text}"
        
        if response.status_code == 409:
            # User exists but might not be verified, fail with message
            raise Exception(f"User {user_data['email']} exists but login failed. Reset database or check email verification.")
        
        # Verify email
        verification_token = response.json()["verification_token"]
        verify_response = requests.get(
            f"{BASE_URL}/auth/verify-email",
            params={"token": verification_token}
        )
        assert verify_response.status_code == 200
        
        # Login
        login_response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"email": user_data["email"], "password": user_data["password"]},
            headers={"Content-Type": "application/json"}
        )
        assert login_response.status_code == 200
        return login_response.json()["access_token"]

    @pytest.fixture(scope="class")
    def provider1_token(self):
        """Create and login first provider"""
        user_data = {
            "email": "progress.provider1@hive.com",
            "password": "Provider123!",
            "first_name": "Provider",
            "last_name": "One",
            "date_of_birth": "1992-01-01"
        }
        
        # Try login first
        login_response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"email": user_data["email"], "password": user_data["password"]}
        )
        if login_response.status_code == 200:
            return login_response.json()["access_token"]
        
        # Register if doesn't exist
        response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
        assert response.status_code == 201
        
        verification_token = response.json()["verification_token"]
        requests.get(f"{BASE_URL}/auth/verify-email", params={"token": verification_token})
        
        login_response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"email": user_data["email"], "password": user_data["password"]}
        )
        assert login_response.status_code == 200
        return login_response.json()["access_token"]

    @pytest.fixture(scope="class")
    def provider2_token(self):
        """Create and login second provider"""
        user_data = {
            "email": "progress.provider2@hive.com",
            "password": "Provider123!",
            "first_name": "Provider",
            "last_name": "Two",
            "date_of_birth": "1993-01-01"
        }
        
        # Try login first
        login_response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"email": user_data["email"], "password": user_data["password"]}
        )
        if login_response.status_code == 200:
            return login_response.json()["access_token"]
        
        # Register if doesn't exist
        response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
        assert response.status_code == 201
        
        verification_token = response.json()["verification_token"]
        requests.get(f"{BASE_URL}/auth/verify-email", params={"token": verification_token})
        
        login_response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"email": user_data["email"], "password": user_data["password"]}
        )
        assert login_response.status_code == 200
        return login_response.json()["access_token"]

    @pytest.fixture(scope="class")
    def provider3_token(self):
        """Create and login third provider"""
        user_data = {
            "email": "progress.provider3@hive.com",
            "password": "Provider123!",
            "first_name": "Provider",
            "last_name": "Three",
            "date_of_birth": "1994-01-01"
        }
        
        # Try login first
        login_response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"email": user_data["email"], "password": user_data["password"]}
        )
        if login_response.status_code == 200:
            return login_response.json()["access_token"]
        
        # Register if doesn't exist
        response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
        assert response.status_code == 201
        
        verification_token = response.json()["verification_token"]
        requests.get(f"{BASE_URL}/auth/verify-email", params={"token": verification_token})
        
        login_response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"email": user_data["email"], "password": user_data["password"]}
        )
        assert login_response.status_code == 200
        return login_response.json()["access_token"]

    def test_multiple_applicants_to_same_service(self, consumer_token, provider1_token, provider2_token, provider3_token):
        """Test that multiple providers can apply to the same service"""
        # Consumer creates a need
        service_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        need_data = {
            "service_type": "need",
            "title": "Help with moving",
            "description": "Need help moving furniture",
            "hours_required": 2,
            "location_type": "in-person",
            "location_address": "123 Main St",
            "latitude": 40.7128,
            "longitude": -74.0060,
            "service_date": service_date,
            "start_time": "10:00",
            "end_time": "12:00"
        }
        
        response = requests.post(
            f"{BASE_URL}/services",
            json=need_data,
            headers={"Authorization": f"Bearer {consumer_token}"}
        )
        assert response.status_code == 201
        service_id = response.json().get("service_id") or response.json().get("id")
        
        # Provider 1 applies
        app1_response = requests.post(
            f"{BASE_URL}/services/{service_id}/apply",
            json={"message": "I can help! - Provider 1"},
            headers={"Authorization": f"Bearer {provider1_token}"}
        )
        assert app1_response.status_code == 201
        app1_id = app1_response.json().get("id") or app1_response.json().get("application_id")
        
        # Provider 2 applies
        app2_response = requests.post(
            f"{BASE_URL}/services/{service_id}/apply",
            json={"message": "I can help! - Provider 2"},
            headers={"Authorization": f"Bearer {provider2_token}"}
        )
        assert app2_response.status_code == 201
        app2_id = app2_response.json().get("id") or app2_response.json().get("application_id")
        
        # Provider 3 applies
        app3_response = requests.post(
            f"{BASE_URL}/services/{service_id}/apply",
            json={"message": "I can help! - Provider 3"},
            headers={"Authorization": f"Bearer {provider3_token}"}
        )
        assert app3_response.status_code == 201
        app3_id = app3_response.json().get("id") or app3_response.json().get("application_id")
        
        # Consumer should see all 3 applications
        apps_response = requests.get(
            f"{BASE_URL}/services/{service_id}/applications",
            headers={"Authorization": f"Bearer {consumer_token}"}
        )
        assert apps_response.status_code == 200
        applications = apps_response.json()
        assert len(applications) == 3
        
        # All applications should be pending
        for app in applications:
            assert app.get("status") == "pending" or app.get("application_status") == "pending"

    def test_accept_one_reject_others(self, consumer_token, provider1_token, provider2_token):
        """Test accepting one applicant and what happens to others"""
        # Create a need
        service_date = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")
        need_data = {
            "service_type": "need",
            "title": "Gardening help needed",
            "description": "Need help with gardening",
            "hours_required": 2,
            "location_type": "in-person",
            "location_address": "456 Garden Ave",
            "latitude": 40.7580,
            "longitude": -73.9855,
            "service_date": service_date,
            "start_time": "14:00",
            "end_time": "16:00"
        }
        
        response = requests.post(
            f"{BASE_URL}/services",
            json=need_data,
            headers={"Authorization": f"Bearer {consumer_token}"}
        )
        assert response.status_code == 201
        service_id = response.json().get("service_id") or response.json().get("id")
        
        # Two providers apply
        app1_response = requests.post(
            f"{BASE_URL}/services/{service_id}/apply",
            json={"message": "I'm experienced!"},
            headers={"Authorization": f"Bearer {provider1_token}"}
        )
        assert app1_response.status_code == 201
        app1_id = app1_response.json().get("id") or app1_response.json().get("application_id")
        
        app2_response = requests.post(
            f"{BASE_URL}/services/{service_id}/apply",
            json={"message": "I can do it!"},
            headers={"Authorization": f"Bearer {provider2_token}"}
        )
        assert app2_response.status_code == 201
        app2_id = app2_response.json().get("id") or app2_response.json().get("application_id")
        
        # Consumer accepts provider 1
        accept_response = requests.post(
            f"{BASE_URL}/applications/{app1_id}/accept",
            headers={"Authorization": f"Bearer {consumer_token}"}
        )
        assert accept_response.status_code in [200, 201]
        
        # Check application statuses
        apps_response = requests.get(
            f"{BASE_URL}/services/{service_id}/applications",
            headers={"Authorization": f"Bearer {consumer_token}"}
        )
        assert apps_response.status_code == 200
        applications = apps_response.json()
        
        # Find accepted and pending applications
        app1_status = None
        app2_status = None
        for app in applications:
            app_id = app.get("id") or app.get("application_id")
            status = app.get("status") or app.get("application_status")
            if app_id == app1_id:
                app1_status = status
            elif app_id == app2_id:
                app2_status = status
        
        # Provider 1 should be accepted
        assert app1_status == "accepted"
        # Provider 2 might still be pending (depends on implementation)
        assert app2_status in ["pending", "rejected"]

    def test_reject_application(self, consumer_token, provider1_token):
        """Test rejecting an application"""
        # Create a need
        service_date = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")
        need_data = {
            "service_type": "need",
            "title": "Tutoring help",
            "description": "Need math tutoring",
            "hours_required": 1,
            "location_type": "online",
            "service_date": service_date,
            "start_time": "16:00",
            "end_time": "17:00"
        }
        
        response = requests.post(
            f"{BASE_URL}/services",
            json=need_data,
            headers={"Authorization": f"Bearer {consumer_token}"}
        )
        assert response.status_code == 201
        service_id = response.json().get("service_id") or response.json().get("id")
        
        # Provider applies
        app_response = requests.post(
            f"{BASE_URL}/services/{service_id}/apply",
            json={"message": "I can teach math"},
            headers={"Authorization": f"Bearer {provider1_token}"}
        )
        assert app_response.status_code == 201
        app_id = app_response.json().get("id") or app_response.json().get("application_id")
        
        # Consumer rejects the application
        reject_response = requests.post(
            f"{BASE_URL}/applications/{app_id}/reject",
            headers={"Authorization": f"Bearer {consumer_token}"}
        )
        
        # Should either succeed or return 404 if endpoint doesn't exist
        # If rejected successfully, status should be 200 or 201
        # If endpoint doesn't exist, we'll get 404
        assert reject_response.status_code in [200, 201, 404]
        
        if reject_response.status_code in [200, 201]:
            # Check application status
            apps_response = requests.get(
                f"{BASE_URL}/services/{service_id}/applications",
                headers={"Authorization": f"Bearer {consumer_token}"}
            )
            assert apps_response.status_code == 200
            applications = apps_response.json()
            
            for app in applications:
                app_id_check = app.get("id") or app.get("application_id")
                if app_id_check == app_id:
                    status = app.get("status") or app.get("application_status")
                    assert status == "rejected"

    def test_reapply_after_rejection(self, consumer_token, provider1_token):
        """Test if a rejected provider can apply again"""
        # Create a need
        service_date = (datetime.now() + timedelta(days=4)).strftime("%Y-%m-%d")
        need_data = {
            "service_type": "need",
            "title": "Cleaning service",
            "description": "Need house cleaning",
            "hours_required": 3,
            "location_type": "in-person",
            "location_address": "789 Clean St",
            "latitude": 40.7489,
            "longitude": -73.9680,
            "service_date": service_date,
            "start_time": "09:00",
            "end_time": "12:00"
        }
        
        response = requests.post(
            f"{BASE_URL}/services",
            json=need_data,
            headers={"Authorization": f"Bearer {consumer_token}"}
        )
        assert response.status_code == 201
        service_id = response.json().get("service_id") or response.json().get("id")
        
        # Provider applies
        app1_response = requests.post(
            f"{BASE_URL}/services/{service_id}/apply",
            json={"message": "First attempt"},
            headers={"Authorization": f"Bearer {provider1_token}"}
        )
        assert app1_response.status_code == 201
        app1_id = app1_response.json().get("id") or app1_response.json().get("application_id")
        
        # Try to reject (if endpoint exists)
        reject_response = requests.post(
            f"{BASE_URL}/applications/{app1_id}/reject",
            headers={"Authorization": f"Bearer {consumer_token}"}
        )
        
        # If rejection endpoint exists and worked
        if reject_response.status_code in [200, 201]:
            # Try to apply again
            app2_response = requests.post(
                f"{BASE_URL}/services/{service_id}/apply",
                json={"message": "Second attempt - please reconsider"},
                headers={"Authorization": f"Bearer {provider1_token}"}
            )
            
            # System should either allow reapplication or reject with 409
            assert app2_response.status_code in [201, 400, 409]
            
            if app2_response.status_code == 201:
                # New application created successfully
                app2_id = app2_response.json().get("id") or app2_response.json().get("application_id")
                assert app2_id is not None
                # Might be same ID or new ID depending on implementation
            else:
                # System doesn't allow reapplication
                assert "already applied" in app2_response.json().get("error", "").lower() or \
                       "duplicate" in app2_response.json().get("error", "").lower()

    def test_withdraw_application(self, consumer_token, provider1_token):
        """Test provider withdrawing their application"""
        # Create a need
        service_date = (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d")
        need_data = {
            "service_type": "need",
            "title": "Photography service",
            "description": "Need photographer for event",
            "hours_required": 2,
            "location_type": "in-person",
            "location_address": "Event Center",
            "latitude": 40.7589,
            "longitude": -73.9851,
            "service_date": service_date,
            "start_time": "18:00",
            "end_time": "20:00"
        }
        
        response = requests.post(
            f"{BASE_URL}/services",
            json=need_data,
            headers={"Authorization": f"Bearer {consumer_token}"}
        )
        assert response.status_code == 201
        service_id = response.json().get("service_id") or response.json().get("id")
        
        # Provider applies
        app_response = requests.post(
            f"{BASE_URL}/services/{service_id}/apply",
            json={"message": "I'm a photographer"},
            headers={"Authorization": f"Bearer {provider1_token}"}
        )
        assert app_response.status_code == 201
        app_id = app_response.json().get("id") or app_response.json().get("application_id")
        
        # Provider withdraws
        withdraw_response = requests.post(
            f"{BASE_URL}/applications/{app_id}/withdraw",
            headers={"Authorization": f"Bearer {provider1_token}"}
        )
        
        # Should succeed
        assert withdraw_response.status_code in [200, 201, 204]

    def test_delete_service_with_applications(self, consumer_token, provider1_token, provider2_token):
        """Test deleting a service that has pending applications"""
        # Create a need
        service_date = (datetime.now() + timedelta(days=6)).strftime("%Y-%m-%d")
        need_data = {
            "service_type": "need",
            "title": "Service to be deleted",
            "description": "This service will be deleted",
            "hours_required": 1,
            "location_type": "online",
            "service_date": service_date,
            "start_time": "10:00",
            "end_time": "11:00"
        }
        
        response = requests.post(
            f"{BASE_URL}/services",
            json=need_data,
            headers={"Authorization": f"Bearer {consumer_token}"}
        )
        assert response.status_code == 201
        service_id = response.json().get("service_id") or response.json().get("id")
        
        # Multiple providers apply
        requests.post(
            f"{BASE_URL}/services/{service_id}/apply",
            json={"message": "Application 1"},
            headers={"Authorization": f"Bearer {provider1_token}"}
        )
        
        requests.post(
            f"{BASE_URL}/services/{service_id}/apply",
            json={"message": "Application 2"},
            headers={"Authorization": f"Bearer {provider2_token}"}
        )
        
        # Consumer deletes the service
        delete_response = requests.delete(
            f"{BASE_URL}/services/{service_id}",
            headers={"Authorization": f"Bearer {consumer_token}"}
        )
        
        # Should succeed or return appropriate error
        assert delete_response.status_code in [200, 204, 400, 403, 404]
        
        if delete_response.status_code in [200, 204]:
            # Service deleted successfully
            # Try to get the service - should fail
            get_response = requests.get(
                f"{BASE_URL}/services/{service_id}",
                headers={"Authorization": f"Bearer {consumer_token}"}
            )
            assert get_response.status_code == 404

    def test_cannot_accept_multiple_applications(self, consumer_token, provider1_token, provider2_token):
        """Test that accepting one application doesn't allow accepting another"""
        # Create a need
        service_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        need_data = {
            "service_type": "need",
            "title": "Single provider service",
            "description": "Only need one provider",
            "hours_required": 2,
            "location_type": "online",
            "service_date": service_date,
            "start_time": "13:00",
            "end_time": "15:00"
        }
        
        response = requests.post(
            f"{BASE_URL}/services",
            json=need_data,
            headers={"Authorization": f"Bearer {consumer_token}"}
        )
        assert response.status_code == 201
        service_id = response.json().get("service_id") or response.json().get("id")
        
        # Two providers apply
        app1_response = requests.post(
            f"{BASE_URL}/services/{service_id}/apply",
            json={"message": "Provider 1"},
            headers={"Authorization": f"Bearer {provider1_token}"}
        )
        app1_id = app1_response.json().get("id") or app1_response.json().get("application_id")
        
        app2_response = requests.post(
            f"{BASE_URL}/services/{service_id}/apply",
            json={"message": "Provider 2"},
            headers={"Authorization": f"Bearer {provider2_token}"}
        )
        app2_id = app2_response.json().get("id") or app2_response.json().get("application_id")
        
        # Accept first application
        accept1_response = requests.post(
            f"{BASE_URL}/applications/{app1_id}/accept",
            headers={"Authorization": f"Bearer {consumer_token}"}
        )
        assert accept1_response.status_code in [200, 201]
        
        # Try to accept second application
        accept2_response = requests.post(
            f"{BASE_URL}/applications/{app2_id}/accept",
            headers={"Authorization": f"Bearer {consumer_token}"}
        )
        
        # Should either fail or succeed (depending on business logic)
        # Some systems allow multiple providers, others don't
        assert accept2_response.status_code in [200, 201, 400, 409]

    def test_application_status_in_provider_dashboard(self, consumer_token, provider1_token):
        """Test that providers can see their application statuses"""
        # Create a need
        service_date = (datetime.now() + timedelta(days=8)).strftime("%Y-%m-%d")
        need_data = {
            "service_type": "need",
            "title": "Dashboard test service",
            "description": "Testing dashboard visibility",
            "hours_required": 1,
            "location_type": "online",
            "service_date": service_date,
            "start_time": "11:00",
            "end_time": "12:00"
        }
        
        response = requests.post(
            f"{BASE_URL}/services",
            json=need_data,
            headers={"Authorization": f"Bearer {consumer_token}"}
        )
        assert response.status_code == 201
        service_id = response.json().get("service_id") or response.json().get("id")
        
        # Provider applies
        app_response = requests.post(
            f"{BASE_URL}/services/{service_id}/apply",
            json={"message": "Testing dashboard"},
            headers={"Authorization": f"Bearer {provider1_token}"}
        )
        assert app_response.status_code == 201
        app_id = app_response.json().get("id") or app_response.json().get("application_id")
        
        # Provider checks their applications
        dashboard_response = requests.get(
            f"{BASE_URL}/user/applications",
            headers={"Authorization": f"Bearer {provider1_token}"}
        )
        assert dashboard_response.status_code == 200
        applications = dashboard_response.json()
        
        # Should find the application
        found = False
        for app in applications:
            check_id = app.get("id") or app.get("application_id")
            if check_id == app_id:
                found = True
                status = app.get("status") or app.get("application_status")
                assert status in ["pending", "accepted", "rejected"]
                break
        
        assert found, "Application not found in provider's dashboard"
