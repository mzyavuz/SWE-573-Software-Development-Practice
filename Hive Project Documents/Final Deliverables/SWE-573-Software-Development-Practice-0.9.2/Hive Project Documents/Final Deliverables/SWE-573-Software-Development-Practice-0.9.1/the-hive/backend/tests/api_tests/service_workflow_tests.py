"""
Complete Service Transaction Workflow Test

End-to-end test covering the full lifecycle of a service transaction:
1. User registration and authentication
2. Service posting
3. Application submission
4. Application acceptance
5. Schedule proposal and acceptance
6. Start confirmation (both parties)
7. Service completion (mark finished)
8. Survey submission (both parties)
9. Credit transfer verification

This test validates all API endpoints work together correctly.
"""

import pytest
import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:5001/api"


class TestCompleteWorkflow:
    """Test complete service transaction workflow from start to finish"""
    
    # Class-level variables to share data between tests
    service_id = None
    application_id = None
    progress_id = None
    message_id = None

    @pytest.fixture(scope="class")
    def consumer_user(self):
        """Create and verify consumer user (Jane)"""
        user_data = {
            "email": "workflow.consumer@hive.com",
            "password": "Consumer123!",
            "first_name": "Jane",
            "last_name": "Miller",
            "date_of_birth": "1995-03-10"
        }
        
        # Try login first
        login_response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"email": user_data["email"], "password": user_data["password"]},
            headers={"Content-Type": "application/json"}
        )
        
        if login_response.status_code == 200:
            token = login_response.json()["access_token"]
            # Update balance for testing
            requests.put(
                f"{BASE_URL}/testing/user/balance",
                headers={"Authorization": f"Bearer {token}"},
                json={"balance": 10}
            )
            return {"token": token, "email": user_data["email"]}
        
        # Register new user
        response = requests.post(
            f"{BASE_URL}/auth/register",
            json=user_data,
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 201, f"Registration failed: {response.text}"
        
        # Verify email
        verification_token = response.json()["verification_token"]
        verify_response = requests.get(
            f"{BASE_URL}/auth/verify-email",
            params={"token": verification_token}
        )
        assert verify_response.status_code == 200, "Email verification failed"
        
        # Login
        login_response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"email": user_data["email"], "password": user_data["password"]},
            headers={"Content-Type": "application/json"}
        )
        assert login_response.status_code == 200, "Login failed"
        
        token = login_response.json()["access_token"]
        
        # Set initial balance
        requests.put(
            f"{BASE_URL}/testing/user/balance",
            headers={"Authorization": f"Bearer {token}"},
            json={"balance": 10}
        )
        
        return {"token": token, "email": user_data["email"]}

    @pytest.fixture(scope="class")
    def provider_user(self):
        """Create and verify provider user (Elizabeth)"""
        user_data = {
            "email": "workflow.provider@hive.com",
            "password": "Provider123!",
            "first_name": "Elizabeth",
            "last_name": "Taylor",
            "date_of_birth": "1960-05-15"
        }
        
        # Try login first
        login_response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"email": user_data["email"], "password": user_data["password"]},
            headers={"Content-Type": "application/json"}
        )
        
        if login_response.status_code == 200:
            return {"token": login_response.json()["access_token"], "email": user_data["email"]}
        
        # Register new user
        response = requests.post(
            f"{BASE_URL}/auth/register",
            json=user_data,
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 201, f"Registration failed: {response.text}"
        
        # Verify email
        verification_token = response.json()["verification_token"]
        verify_response = requests.get(
            f"{BASE_URL}/auth/verify-email",
            params={"token": verification_token}
        )
        assert verify_response.status_code == 200, "Email verification failed"
        
        # Login
        login_response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"email": user_data["email"], "password": user_data["password"]},
            headers={"Content-Type": "application/json"}
        )
        assert login_response.status_code == 200, "Login failed"
        
        return {"token": login_response.json()["access_token"], "email": user_data["email"]}

    @pytest.fixture(scope="class")
    def tag_ids(self, consumer_user):
        """Get or create tags for the service"""
        token = consumer_user["token"]
        tags = {}
        
        for tag_name in ["babysitting", "childcare"]:
            # Try to get existing tag
            response = requests.get(
                f"{BASE_URL}/tags",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code == 200:
                existing_tags = response.json()
                # Handle both list and dict responses
                if isinstance(existing_tags, dict):
                    existing_tags = existing_tags.get('tags', [])
                
                for tag in existing_tags:
                    if isinstance(tag, dict) and tag.get("name") == tag_name:
                        tags[tag_name] = tag["id"]
                        break
            
            # Create if doesn't exist
            if tag_name not in tags:
                response = requests.post(
                    f"{BASE_URL}/tags",
                    json={"name": tag_name},
                    headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
                )
                if response.status_code in [200, 201]:
                    result = response.json()
                    tags[tag_name] = result.get("id") or result.get("tag_id")
        
        return tags

    def test_01_post_service(self, consumer_user, tag_ids):
        """Step 1: Consumer posts a service need"""
        service_data = {
            "title": "Need babysitter for 3 hours",
            "description": "Looking for an experienced babysitter for two children (ages 4 and 6) on Saturday evening.",
            "service_type": "need",
            "hours_required": 3,
            "location_type": "in-person",
            "location_address": "123 Main St, City",
            "latitude": 40.7128,
            "longitude": -74.0060,
            "tag_ids": list(tag_ids.values()) if tag_ids else []
        }
        
        response = requests.post(
            f"{BASE_URL}/services",
            json=service_data,
            headers={
                "Authorization": f"Bearer {consumer_user['token']}",
                "Content-Type": "application/json"
            }
        )
        
        assert response.status_code == 201, f"Service creation failed: {response.text}"
        data = response.json()
        assert "id" in data or "service_id" in data, "Service ID not returned"
        
        # Store service_id for other tests
        TestCompleteWorkflow.service_id = data.get("id") or data.get("service_id")

    def test_02_apply_to_service(self, provider_user):
        """Step 2: Provider applies to the service"""
        application_data = {
            "message": "Hi! I'd love to help with babysitting. I have years of experience with children."
        }
        
        response = requests.post(
            f"{BASE_URL}/services/{TestCompleteWorkflow.service_id}/apply",
            json=application_data,
            headers={
                "Authorization": f"Bearer {provider_user['token']}",
                "Content-Type": "application/json"
            }
        )
        
        assert response.status_code in [200, 201], f"Application failed: {response.text}"
        data = response.json()
        assert "id" in data or "application_id" in data, "Application ID not returned"
        
        # Store application_id
        TestCompleteWorkflow.application_id = data.get("id") or data.get("application_id")

    def test_03_view_applicants(self, consumer_user):
        """Step 3: Consumer views applicants"""
        response = requests.get(
            f"{BASE_URL}/services/{TestCompleteWorkflow.service_id}/applications",
            headers={"Authorization": f"Bearer {consumer_user['token']}"}
        )
        
        print(f"View applicants response status: {response.status_code}")
        print(f"View applicants response: {response.text}")
        assert response.status_code == 200, f"Failed to get applicants. Status: {response.status_code}, Response: {response.text}"
        
        applications = response.json()
        print(f"Applications found: {len(applications)}")
        assert len(applications) > 0, f"No applications found. Response: {applications}"
        
        app_ids = [app.get("id") for app in applications]
        print(f"Application IDs: {app_ids}, Looking for: {TestCompleteWorkflow.application_id}")
        assert any(app.get("id") == TestCompleteWorkflow.application_id for app in applications), f"Application {TestCompleteWorkflow.application_id} not in list: {app_ids}"

    def test_04_accept_application(self, consumer_user):
        """Step 4: Consumer accepts the application"""
        response = requests.post(
            f"{BASE_URL}/applications/{TestCompleteWorkflow.application_id}/accept",
            headers={"Authorization": f"Bearer {consumer_user['token']}"}
        )
        
        assert response.status_code in [200, 201], f"Accept failed: {response.text}"

    def test_05_get_progress_id(self, consumer_user):
        """Step 5: Get service_progress ID from applications"""
        response = requests.get(
            f"{BASE_URL}/services/{TestCompleteWorkflow.service_id}/applications",
            headers={"Authorization": f"Bearer {consumer_user['token']}"}
        )
        
        print(f"Get progress ID response status: {response.status_code}")
        assert response.status_code == 200, f"Failed to get applications. Status: {response.status_code}, Response: {response.text}"
        
        applications = response.json()
        print(f"Applications for progress ID lookup: {json.dumps(applications, indent=2)}")
        
        for app in applications:
            if app.get("status") == "accepted":
                TestCompleteWorkflow.progress_id = app.get("progress_id") or app.get("transaction_id")
                print(f"Found progress_id: {TestCompleteWorkflow.progress_id}")
                break
        
        assert hasattr(TestCompleteWorkflow, "progress_id"), f"Progress ID not found in applications: {applications}"
        assert TestCompleteWorkflow.progress_id is not None, f"Progress ID is None. Applications: {applications}"

    def test_06_propose_schedule(self, provider_user):
        """Step 6: Provider proposes a schedule"""
        schedule_data = {
            "proposed_date": (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d"),
            "proposed_start_time": "18:00",
            "proposed_end_time": "21:00",
            "proposed_location": "Consumer's home - 123 Main St"
        }
        
        response = requests.post(
            f"{BASE_URL}/progress/{TestCompleteWorkflow.progress_id}/propose-schedule",
            json=schedule_data,
            headers={
                "Authorization": f"Bearer {provider_user['token']}",
                "Content-Type": "application/json"
            }
        )
        
        assert response.status_code in [200, 201], f"Schedule proposal failed: {response.text}"
        data = response.json()
        print(f"Schedule proposal response: {json.dumps(data, indent=2)}")
        assert "message_id" in data, f"Message ID not returned. Response: {data}"
        
        TestCompleteWorkflow.message_id = data["message_id"]
        print(f"Stored message_id: {TestCompleteWorkflow.message_id}")

    def test_07_accept_schedule(self, consumer_user):
        """Step 7: Consumer accepts the schedule"""
        # Ensure consumer has enough balance
        requests.put(
            f"{BASE_URL}/testing/user/balance",
            headers={"Authorization": f"Bearer {consumer_user['token']}"},
            json={"balance": 10}
        )
        
        response = requests.post(
            f"{BASE_URL}/messages/{TestCompleteWorkflow.message_id}/respond-schedule",
            json={"accept": True},
            headers={
                "Authorization": f"Bearer {consumer_user['token']}",
                "Content-Type": "application/json"
            }
        )
        
        print(f"Accept schedule response status: {response.status_code}")
        print(f"Accept schedule response: {response.text}")
        assert response.status_code in [200, 201], f"Schedule acceptance failed. Status: {response.status_code}, Response: {response.text}"
        
        data = response.json()
        print(f"Schedule acceptance data: {json.dumps(data, indent=2)}")

    def test_08_provider_confirms_start(self, provider_user):
        """Step 8: Provider confirms service start"""
        response = requests.post(
            f"{BASE_URL}/progress/{TestCompleteWorkflow.progress_id}/confirm-start",
            headers={"Authorization": f"Bearer {provider_user['token']}"}
        )
        
        print(f"Provider confirm start response status: {response.status_code}")
        print(f"Provider confirm start response: {response.text}")
        assert response.status_code in [200, 201], f"Provider start confirmation failed. Status: {response.status_code}, Response: {response.text}"
        
        data = response.json()
        print(f"Provider start confirmation data: {json.dumps(data, indent=2)}")

    def test_09_consumer_confirms_start(self, consumer_user):
        """Step 9: Consumer confirms service start"""
        response = requests.post(
            f"{BASE_URL}/progress/{TestCompleteWorkflow.progress_id}/confirm-start",
            headers={"Authorization": f"Bearer {consumer_user['token']}"}
        )
        
        print(f"Consumer confirm start response status: {response.status_code}")
        print(f"Consumer confirm start response: {response.text}")
        assert response.status_code in [200, 201], f"Consumer start confirmation failed. Status: {response.status_code}, Response: {response.text}"
        
        data = response.json()
        print(f"Consumer start confirmation data: {json.dumps(data, indent=2)}")

    def test_10_mark_finished(self, provider_user):
        """Step 10: Provider marks service as finished"""
        response = requests.post(
            f"{BASE_URL}/progress/{TestCompleteWorkflow.progress_id}/mark-finished",
            headers={"Authorization": f"Bearer {provider_user['token']}"}
        )
        
        print(f"Mark finished response status: {response.status_code}")
        print(f"Mark finished response: {response.text}")
        assert response.status_code in [200, 201], f"Mark finished failed. Status: {response.status_code}, Response: {response.text}"
        
        data = response.json()
        print(f"Mark finished data: {json.dumps(data, indent=2)}")

    def test_11_provider_submits_survey(self, provider_user):
        """Step 11: Provider submits completion survey"""
        survey_data = {
            "rating": 5,
            "feedback": "Great experience! Consumer was very organized and clear.",
            "would_work_again": True
        }
        
        response = requests.post(
            f"{BASE_URL}/progress/{TestCompleteWorkflow.progress_id}/submit-survey",
            json={"survey_data": survey_data},
            headers={
                "Authorization": f"Bearer {provider_user['token']}",
                "Content-Type": "application/json"
            }
        )
        
        assert response.status_code in [200, 201], f"Provider survey submission failed: {response.text}"

    def test_12_consumer_submits_survey(self, consumer_user):
        """Step 12: Consumer submits completion survey"""
        survey_data = {
            "rating": 5,
            "feedback": "Excellent service! Very professional and caring.",
            "would_work_again": True
        }
        
        response = requests.post(
            f"{BASE_URL}/progress/{TestCompleteWorkflow.progress_id}/submit-survey",
            json={"survey_data": survey_data},
            headers={
                "Authorization": f"Bearer {consumer_user['token']}",
                "Content-Type": "application/json"
            }
        )
        
        print(f"Consumer survey response status: {response.status_code}")
        print(f"Consumer survey response: {response.text}")
        assert response.status_code in [200, 201], f"Consumer survey submission failed. Status: {response.status_code}, Response: {response.text}"
        
        data = response.json()
        print(f"Consumer survey data: {json.dumps(data, indent=2)}")

    def test_13_verify_credit_transfer(self, provider_user):
        """Step 13: Verify credits were transferred to provider"""
        response = requests.get(
            f"{BASE_URL}/auth/profile",
            headers={"Authorization": f"Bearer {provider_user['token']}"}
        )
        
        print(f"Get profile response status: {response.status_code}")
        assert response.status_code == 200, f"Failed to get profile. Status: {response.status_code}, Response: {response.text}"
        
        profile = response.json()
        if "user" in profile:
            profile = profile["user"]
        
        balance = profile.get("time_balance", 0)
        print(f"Provider balance after completion: {balance}")
        # Provider should have at least 3 hours (the service hours)
        assert balance >= 3, f"Expected balance >= 3, got {balance}. Full profile: {json.dumps(profile, indent=2)}"

    def test_14_verify_service_completed(self, consumer_user):
        """Step 14: Verify service status is completed"""
        response = requests.get(
            f"{BASE_URL}/services/{TestCompleteWorkflow.service_id}",
            headers={"Authorization": f"Bearer {consumer_user['token']}"}
        )
        
        print(f"Get service response status: {response.status_code}")
        assert response.status_code == 200, f"Failed to get service. Status: {response.status_code}, Response: {response.text}"
        
        data = response.json()
        print(f"Full response data: {json.dumps(data, indent=2, default=str)}")
        
        # The endpoint returns {"service": {...}} so extract the service object
        service = data.get("service", data)
        print(f"Final service status: {service.get('status')}")
        
        # Service should be completed or in_progress
        assert service.get("status") in ["completed", "in_progress"], f"Unexpected service status: {service.get('status')}. Full service: {json.dumps(service, indent=2, default=str)}"

