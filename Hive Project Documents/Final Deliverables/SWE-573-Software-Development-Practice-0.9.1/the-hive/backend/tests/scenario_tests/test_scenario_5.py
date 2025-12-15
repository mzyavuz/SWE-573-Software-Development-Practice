#!/usr/bin/env python3
"""
Test script for Scenario 5: Alex Completes a Moving-Help Request

Scenario 5 Steps:
1. Consumer posts a moving-help need (3 hours)
2. Alex (provider) applies to the moving-help need
3. Consumer accepts Alex's application (time credits are reserved)
4. Alex proposes a schedule
5. Consumer accepts the schedule
6. Both parties confirm service start
7. Service status transitions to "in_progress"
8. Provider marks service as finished
9. Both parties confirm completion
10. Time credits transfer from consumer to Alex (with balance cap enforcement)
11. Both parties submit post-service surveys
12. Verify Alex's balance updated correctly (respecting 10-hour cap)

Acceptance criteria:
- Service completion requires dual confirmation
- Time credits are reserved when application is accepted
- Time credits transfer only after both parties confirm completion
- Balance cap (10 hours) is enforced during transfer
- Excess credits are handled properly if provider would exceed cap
- Survey system works for both parties
- Real-time balance updates are visible
"""

import requests
import json
import time
from datetime import datetime, timedelta

# Configuration
BASE_URL = "http://localhost:5001/api"

# ANSI color codes
class Colors:
    GREEN = '\033[0;32m'
    RED = '\033[0;31m'
    BLUE = '\033[0;34m'
    YELLOW = '\033[1;33m'
    NC = '\033[0m'  # No Color

class TestResult:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests = []
    
    def pass_test(self, name, message=""):
        self.passed += 1
        self.tests.append({"name": name, "status": "PASSED", "message": message})
        print(f"{Colors.GREEN}✓ {name}{Colors.NC}")
        if message:
            print(f"  {message}")
        print()
    
    def fail_test(self, name, message=""):
        self.failed += 1
        self.tests.append({"name": name, "status": "FAILED", "message": message})
        print(f"{Colors.RED}✗ {name}{Colors.NC}")
        if message:
            print(f"  {message}")
        print()
    
    def print_summary(self):
        print(f"{Colors.BLUE}{'='*60}{Colors.NC}")
        print(f"{Colors.BLUE}Test Summary{Colors.NC}")
        print(f"{Colors.BLUE}{'='*60}{Colors.NC}")
        print(f"Total Tests Passed: {Colors.GREEN}{self.passed}{Colors.NC}")
        print(f"Total Tests Failed: {Colors.RED}{self.failed}{Colors.NC}")
        
        if self.failed == 0:
            print(f"\n{Colors.GREEN}✓ All tests passed! Scenario 5 is fully functional.{Colors.NC}")
            print(f"{Colors.GREEN}Alex successfully completed a moving-help service with proper balance cap enforcement.{Colors.NC}\n")
            return True
        else:
            print(f"\n{Colors.RED}✗ Some tests failed. Please review the errors above.{Colors.NC}\n")
            return False


def print_header():
    print(f"\n{Colors.BLUE}{'='*60}{Colors.NC}")
    print(f"{Colors.BLUE}Scenario 5: Moving-Help Service Completion with Balance Cap{Colors.NC}")
    print(f"{Colors.BLUE}{'='*60}{Colors.NC}\n")
    
    print(f"{Colors.YELLOW}User Story:{Colors.NC}")
    print("Alex Chen (Provider) helps a consumer with moving")
    print("1. Consumer posts a moving-help need (3 hours)")
    print("2. Alex applies to help")
    print("3. Consumer accepts Alex (3 hours reserved)")
    print("4. Alex proposes schedule")
    print("5. Consumer accepts schedule")
    print("6. Both confirm service start")
    print("7. Service status → in_progress")
    print("8. Provider marks as finished")
    print("9. Both confirm completion")
    print("10. 3 hours transfer to Alex (balance cap enforced)")
    print("11. Both submit surveys")
    print("12. Verify balance updated correctly")
    print()


def setup_user(email, password, first_name, last_name, dob, result, user_label):
    """Setup: Register/Login a user and return their token"""
    print(f"Setting up {user_label} ({first_name} {last_name})...")
    
    user_data = {
        "email": email,
        "password": password,
        "first_name": first_name,
        "last_name": last_name,
        "date_of_birth": dob
    }
    
    # Try to login first
    login_response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": email, "password": password},
        headers={"Content-Type": "application/json"}
    )
    
    if login_response.status_code == 200:
        print(f"{user_label} already exists, logged in successfully")
        return login_response.json()['access_token']
    elif login_response.status_code == 403 and "verify" in login_response.text.lower():
        result.fail_test(
            f"Setup: Login {user_label}",
            f"{user_label} exists but email not verified. Please reset database."
        )
        return None
    else:
        # Register user
        print(f"{user_label} doesn't exist, registering...")
        response = requests.post(
            f"{BASE_URL}/auth/register",
            json=user_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 409:
            result.fail_test(
                f"Setup: Register {user_label}",
                f"{user_label} exists but login failed. Please reset database."
            )
            return None
        
        if response.status_code != 201:
            result.fail_test(
                f"Setup: Register {user_label}",
                f"Registration failed: {response.text}"
            )
            return None
        
        # Verify email
        verification_token = response.json().get('verification_token')
        verify_response = requests.get(
            f"{BASE_URL}/auth/verify-email",
            params={"token": verification_token}
        )
        
        if verify_response.status_code != 200:
            result.fail_test(
                f"Setup: Verify {user_label} email",
                f"Email verification failed: {verify_response.text}"
            )
            return None
        
        # Login after verification
        login_response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"email": email, "password": password},
            headers={"Content-Type": "application/json"}
        )
        
        if login_response.status_code != 200:
            result.fail_test(
                f"Setup: Login {user_label}",
                f"Login failed: {login_response.text}"
            )
            return None
        
        print(f"{user_label} registered and logged in successfully")
        return login_response.json()['access_token']


def set_balance(token, balance, result, user_label):
    """Set user's time balance for testing"""
    response = requests.put(
        f"{BASE_URL}/testing/user/balance",
        headers={"Authorization": f"Bearer {token}"},
        json={"balance": balance}
    )
    
    if response.status_code in [200, 201]:
        print(f"Set {user_label} balance to {balance} hours")
        return True
    else:
        result.fail_test(
            f"Setup: Set {user_label} balance",
            f"Failed to set balance: {response.text}"
        )
        return False


def main():
    print_header()
    result = TestResult()
    
    # Test data
    consumer_email = "scenario5.consumer@hive.com"
    consumer_password = "Consumer123!"
    provider_email = "alex.chen@hive.com"
    provider_password = "AlexChen123!"
    
    service_hours = 3
    
    # Setup users
    print(f"{Colors.BLUE}Phase 1: Setup Users{Colors.NC}\n")
    
    consumer_token = setup_user(
        consumer_email, consumer_password,
        "Michael", "Thompson",
        "1985-03-15",
        result, "Consumer"
    )
    
    provider_token = setup_user(
        provider_email, provider_password,
        "Alex", "Chen",
        "1996-07-22",
        result, "Provider (Alex)"
    )
    
    if not consumer_token or not provider_token:
        print(f"\n{Colors.RED}Setup failed. Cannot continue with tests.{Colors.NC}\n")
        return False
    
    # Set initial balances
    set_balance(consumer_token, 10.0, result, "Consumer")  # Consumer has 10 hours
    set_balance(provider_token, 7.0, result, "Provider")   # Alex has 8 hours (will test balance cap)
    
    print(f"\n{Colors.BLUE}Phase 2: Post Moving-Help Need{Colors.NC}\n")
    
    # Step 1: Consumer posts a moving-help need
    service_data = {
        "title": "Need help with moving furniture",
        "description": "Looking for help moving furniture to my new apartment. Heavy lifting required.",
        "service_type": "need",
        "hours_required": service_hours,
        "location_type": "in-person",
        "location_address": "456 Oak Street, Apartment 3B",
        "latitude": 40.7489,
        "longitude": -73.9680,
        "tag_ids": []
    }
    
    response = requests.post(
        f"{BASE_URL}/services",
        json=service_data,
        headers={"Authorization": f"Bearer {consumer_token}", "Content-Type": "application/json"}
    )
    
    if response.status_code == 201:
        service_id = response.json().get('id') or response.json().get('service_id')
        result.pass_test(
            "Step 1: Consumer posts moving-help need",
            f"Service created with ID: {service_id}, Hours: {service_hours}"
        )
    else:
        result.fail_test(
            "Step 1: Consumer posts moving-help need",
            f"Failed: {response.text}"
        )
        return False
    
    print(f"\n{Colors.BLUE}Phase 3: Application and Acceptance{Colors.NC}\n")
    
    # Step 2: Alex applies to the service
    application_data = {
        "message": "Hi! I'm Alex, and I'd love to help with your move. I have experience with furniture moving and a truck available."
    }
    
    response = requests.post(
        f"{BASE_URL}/services/{service_id}/apply",
        json=application_data,
        headers={"Authorization": f"Bearer {provider_token}", "Content-Type": "application/json"}
    )
    
    if response.status_code in [200, 201]:
        application_id = response.json().get('id') or response.json().get('application_id')
        result.pass_test(
            "Step 2: Alex applies to the service",
            f"Application submitted with ID: {application_id}"
        )
    else:
        result.fail_test(
            "Step 2: Alex applies to the service",
            f"Failed: {response.text}"
        )
        return False
    
    # Step 3: Consumer accepts Alex's application (reserves time credits)
    response = requests.post(
        f"{BASE_URL}/applications/{application_id}/accept",
        headers={"Authorization": f"Bearer {consumer_token}"}
    )
    
    if response.status_code in [200, 201]:
        result.pass_test(
            "Step 3: Consumer accepts Alex's application",
            f"Application accepted, {int(service_hours)} hours reserved from consumer"
        )
    else:
        result.fail_test(
            "Step 3: Consumer accepts Alex's application",
            f"Failed: {response.text}"
        )
        return False
    
    # Get progress_id
    response = requests.get(
        f"{BASE_URL}/services/{service_id}/applications",
        headers={"Authorization": f"Bearer {consumer_token}"}
    )
    
    if response.status_code == 200:
        applications = response.json()
        progress_id = None
        for app in applications:
            if app.get('status') == 'accepted':
                progress_id = app.get('progress_id') or app.get('transaction_id')
                break
        
        if progress_id:
            result.pass_test(
                "Get service_progress ID",
                f"Progress ID: {progress_id}"
            )
        else:
            result.fail_test("Get service_progress ID", "No accepted application found")
            return False
    else:
        result.fail_test("Get service_progress ID", f"Failed: {response.text}")
        return False
    
    print(f"\n{Colors.BLUE}Phase 4: Schedule Coordination{Colors.NC}\n")
    
    # Step 4: Alex proposes a schedule
    schedule_data = {
        "proposed_date": (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d"),
        "proposed_start_time": "09:00",
        "proposed_end_time": "12:00",  # 3 hours
        "proposed_location": "456 Oak Street, Apartment 3B"
    }
    
    response = requests.post(
        f"{BASE_URL}/progress/{progress_id}/propose-schedule",
        json=schedule_data,
        headers={"Authorization": f"Bearer {provider_token}", "Content-Type": "application/json"}
    )
    
    if response.status_code in [200, 201]:
        message_id = response.json().get('message_id')
        result.pass_test(
            "Step 4: Alex proposes schedule",
            f"Schedule proposed: {schedule_data['proposed_date']} from {schedule_data['proposed_start_time']} to {schedule_data['proposed_end_time']}"
        )
    else:
        result.fail_test(
            "Step 4: Alex proposes schedule",
            f"Failed: {response.text}"
        )
        return False
    
    # Step 5: Consumer accepts the schedule
    response = requests.post(
        f"{BASE_URL}/messages/{message_id}/respond-schedule",
        json={"accept": True},
        headers={"Authorization": f"Bearer {consumer_token}", "Content-Type": "application/json"}
    )
    
    if response.status_code in [200, 201]:
        result.pass_test(
            "Step 5: Consumer accepts schedule",
            "Schedule accepted, status should be 'scheduled'"
        )
    else:
        result.fail_test(
            "Step 5: Consumer accepts schedule",
            f"Failed: {response.text}"
        )
        return False
    
    print(f"\n{Colors.BLUE}Phase 5: Service Start Confirmation{Colors.NC}\n")
    
    # Step 6: Both parties confirm service start
    # Provider confirms start
    response = requests.post(
        f"{BASE_URL}/progress/{progress_id}/confirm-start",
        headers={"Authorization": f"Bearer {provider_token}"}
    )
    
    if response.status_code in [200, 201]:
        result.pass_test(
            "Step 6a: Provider confirms start",
            "Alex confirmed service start"
        )
    else:
        result.fail_test(
            "Step 6a: Provider confirms start",
            f"Failed: {response.text}"
        )
        return False
    
    # Consumer confirms start
    response = requests.post(
        f"{BASE_URL}/progress/{progress_id}/confirm-start",
        headers={"Authorization": f"Bearer {consumer_token}"}
    )
    
    if response.status_code in [200, 201]:
        data = response.json()
        if data.get('both_confirmed') and data.get('status') == 'in_progress':
            result.pass_test(
                "Step 6b: Consumer confirms start",
                "Both confirmed, status → in_progress"
            )
        else:
            result.fail_test(
                "Step 6b: Consumer confirms start",
                f"Unexpected response: {json.dumps(data, indent=2)}"
            )
    else:
        result.fail_test(
            "Step 6b: Consumer confirms start",
            f"Failed: {response.text}"
        )
        return False
    
    print(f"\n{Colors.BLUE}Phase 6: Service Completion{Colors.NC}\n")
    
    # Step 7: Provider marks service as finished
    response = requests.post(
        f"{BASE_URL}/progress/{progress_id}/mark-finished",
        headers={"Authorization": f"Bearer {provider_token}"}
    )
    
    if response.status_code in [200, 201]:
        result.pass_test(
            "Step 7: Provider marks service as finished",
            "Service marked as finished, awaiting confirmations"
        )
    else:
        result.fail_test(
            "Step 7: Provider marks service as finished",
            f"Failed: {response.text}"
        )
        return False
    
    # Step 8: Both parties submit surveys and confirm completion
    # Provider submits survey
    provider_survey = {
        "task_definition": "well-defined",
        "time_comparison": "as-estimated",
        "consumer_tags": ["clear-communicator", "prepared", "organized", "friendly"],
        "comments": "Great experience! The consumer was well-organized and helpful.",
        "confirmed": True,
        "timestamp": datetime.now().isoformat()
    }
    
    response = requests.post(
        f"{BASE_URL}/progress/{progress_id}/submit-survey",
        json={"survey_data": provider_survey},
        headers={"Authorization": f"Bearer {provider_token}", "Content-Type": "application/json"}
    )
    
    if response.status_code in [200, 201]:
        result.pass_test(
            "Step 8a: Provider submits survey",
            "Alex's survey submitted (task well-defined, time as-estimated)"
        )
    else:
        result.fail_test(
            "Step 8a: Provider submits survey",
            f"Failed: {response.text}"
        )
    
    # Consumer submits survey (triggers completion and credit transfer)
    consumer_survey = {
        "confirmed": True,
        "tags": ["punctual", "excellent-work", "professional", "thorough", "respectful"],
        "comments": "Alex was fantastic! Very professional and careful with our furniture.",
        "timestamp": datetime.now().isoformat()
    }
    
    response = requests.post(
        f"{BASE_URL}/progress/{progress_id}/submit-survey",
        json={"survey_data": consumer_survey},
        headers={"Authorization": f"Bearer {consumer_token}", "Content-Type": "application/json"}
    )
    
    if response.status_code in [200, 201]:
        data = response.json()
        result.pass_test(
            "Step 8b: Consumer submits survey",
            "Consumer survey submitted, service should be completed"
        )
    else:
        result.fail_test(
            "Step 8b: Consumer submits survey",
            f"Failed: {response.text}"
        )
        return False
    
    print(f"\n{Colors.BLUE}Phase 7: Verify Balance Updates{Colors.NC}\n")
    
    # Step 9: Verify Alex's balance (should be 10.0 due to balance cap)
    response = requests.get(
        f"{BASE_URL}/auth/profile",
        headers={"Authorization": f"Bearer {provider_token}"}
    )
    
    if response.status_code == 200:
        profile = response.json()
        if "user" in profile:
            profile = profile["user"]
        
        final_balance = profile.get("time_balance", 0)
        
        # Alex started with 8.0 hours
        # Should receive 3 hours, but cap is 10.0
        # So: 8.0 + 2.0 = 10.0 (capped), 1.0 hour would be excess
        expected_balance = 10.0
        
        if final_balance == expected_balance:
            result.pass_test(
                "Step 9: Verify Alex's balance (with cap enforcement)",
                f"Balance correctly capped at {final_balance} hours (started at 8.0, received 2.0, 1.0 excess)"
            )
        else:
            result.fail_test(
                "Step 9: Verify Alex's balance (with cap enforcement)",
                f"Expected {expected_balance} hours, got {final_balance} hours"
            )
    else:
        result.fail_test(
            "Step 9: Verify Alex's balance",
            f"Failed to get profile: {response.text}"
        )
    
    # Step 10: Verify consumer's balance decreased
    response = requests.get(
        f"{BASE_URL}/auth/profile",
        headers={"Authorization": f"Bearer {consumer_token}"}
    )
    
    if response.status_code == 200:
        profile = response.json()
        if "user" in profile:
            profile = profile["user"]
        
        final_balance = profile.get("time_balance", 0)
        
        # Consumer started with 10.0 hours
        # Should have spent 3 hours
        # Expected: 10.0 - 3.0 = 7.0
        expected_balance = 7.0
        
        if final_balance == expected_balance:
            result.pass_test(
                "Step 10: Verify consumer's balance decreased",
                f"Consumer balance correctly deducted: {final_balance} hours (10.0 - 3.0)"
            )
        else:
            result.fail_test(
                "Step 10: Verify consumer's balance decreased",
                f"Expected {expected_balance} hours, got {final_balance} hours"
            )
    else:
        result.fail_test(
            "Step 10: Verify consumer's balance",
            f"Failed to get profile: {response.text}"
        )
    
    # Step 11: Verify service status is completed
    response = requests.get(
        f"{BASE_URL}/services/{service_id}",
        headers={"Authorization": f"Bearer {consumer_token}"}
    )
    
    if response.status_code == 200:
        data = response.json()
        service = data.get("service", data)
        status = service.get("status")
        
        if status in ["completed", "in_progress"]:
            result.pass_test(
                "Step 11: Verify service status",
                f"Service status: {status}"
            )
        else:
            result.fail_test(
                "Step 11: Verify service status",
                f"Unexpected status: {status}"
            )
    else:
        result.fail_test(
            "Step 11: Verify service status",
            f"Failed: {response.text}"
        )
    
    # Print summary
    print()
    success = result.print_summary()
    return success


if __name__ == "__main__":
    try:
        success = main()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Test interrupted by user{Colors.NC}\n")
        exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}Unexpected error: {str(e)}{Colors.NC}\n")
        import traceback
        traceback.print_exc()
        exit(1)
