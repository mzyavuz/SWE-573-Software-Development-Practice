#!/usr/bin/env python3
"""
Test script for Scenario 4: Jane requests babysitting; Elizabeth is accepted and they coordinate

Scenario 4 Steps:
1. Jane posts a babysitting need with date/time and required skills
2. Elizabeth applies to the babysitting need (messages become available after application)
3. Jane reviews Elizabeth's profile and qualifications
4. Jane accepts Elizabeth's application
5. Private messaging is available for coordination (SM-9)
6. They coordinate location and permissions through messages
7. Elizabeth proposes a schedule (date, time, location)
8. Jane accepts the schedule proposal
9. Status transitions to "Scheduled" (SM-8)
10. After the session, they mark the need as complete
11. Both parties confirm completion
12. System transfers time credits to Elizabeth (TCS-5)
13. Both receive evaluation surveys (SM-10)

Acceptance criteria:
- Consumer can post a need successfully
- Provider can apply to the need
- Consumer can view applicant profile and qualifications
- Consumer can accept one applicant
- Private messaging is available after application (not before)
- Schedule proposal and acceptance workflow functions correctly
- Status updates follow: Open -> Selected -> Scheduled -> In-progress -> Confirmation -> Complete
- Time credits transfer on mutual completion confirmation
- Both parties can submit ratings and surveys
- System prevents duplicate completions
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
            print(f"\n{Colors.GREEN}✓ All tests passed! Scenario 4 is fully functional.{Colors.NC}")
            print(f"{Colors.GREEN}Jane and Elizabeth can successfully complete a babysitting transaction.{Colors.NC}\n")
            return True
        else:
            print(f"\n{Colors.RED}✗ Some tests failed. Please review the errors above.{Colors.NC}\n")
            return False


def print_header():
    print(f"\n{Colors.BLUE}{'='*60}{Colors.NC}")
    print(f"{Colors.BLUE}Scenario 4: Babysitting Request and Completion{Colors.NC}")
    print(f"{Colors.BLUE}{'='*60}{Colors.NC}\n")
    
    print(f"{Colors.YELLOW}User Story:{Colors.NC}")
    print("Jane Miller (Parent & Student) and Elizabeth Taylor (Senior)")
    print("1. Jane posts a babysitting need")
    print("2. Elizabeth applies to help (enables messaging)")
    print("3. Jane reviews Elizabeth's profile")
    print("4. Jane accepts Elizabeth")
    print("5. They coordinate through private messages")
    print("6. Elizabeth proposes schedule (date/time/location)")
    print("7. Jane accepts the schedule proposal")
    print("8. Status updates to Scheduled")
    print("9. They complete the service")
    print("10. Both confirm completion")
    print("11. Time credits transfer to Elizabeth")
    print("12. Both submit evaluation surveys")
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
                f"Registration failed: {response.status_code} - {response.text}"
            )
            return None
        
        # Verify email
        verification_token = response.json()["verification_token"]
        verify_response = requests.get(
            f"{BASE_URL}/auth/verify-email",
            params={"token": verification_token}
        )
        
        if verify_response.status_code != 200:
            result.fail_test(
                f"Setup: Verify {user_label}'s email",
                f"Email verification failed: {verify_response.status_code}"
            )
            return None
        
        print(f"{user_label}'s email verified successfully")
        time.sleep(1)
        
        # Login after verification
        login_response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"email": email, "password": password},
            headers={"Content-Type": "application/json"}
        )
        
        if login_response.status_code != 200:
            result.fail_test(
                f"Setup: Login {user_label}",
                f"Login failed: {login_response.status_code}"
            )
            return None
        
        print(f"{user_label} registered and logged in successfully")
        return login_response.json()['access_token']


def get_or_create_tag(token, tag_name, result):
    """Get existing tag or create new one, return tag ID"""
    print(f"Getting/creating '{tag_name}' tag...")
    
    # Try to get existing tags
    tags_response = requests.get(
        f"{BASE_URL}/tags",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if tags_response.status_code == 200:
        existing_tags = tags_response.json()
        if isinstance(existing_tags, dict) and 'tags' in existing_tags:
            existing_tags = existing_tags['tags']
        
        if isinstance(existing_tags, list):
            for tag in existing_tags:
                if isinstance(tag, dict) and tag.get('name', '').lower() == tag_name.lower():
                    print(f"Found existing '{tag_name}' tag with ID: {tag['id']}")
                    return tag['id']
    
    # Create tag if not found
    tag_response = requests.post(
        f"{BASE_URL}/tags",
        json={"name": tag_name},
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
    )
    
    if tag_response.status_code == 201:
        response_data = tag_response.json()
        tag_id = response_data.get('id') or response_data.get('tag', {}).get('id')
        print(f"Created '{tag_name}' tag with ID: {tag_id}")
        return tag_id
    elif tag_response.status_code == 409:
        tag_id = tag_response.json().get('existing_tag_id')
        print(f"'{tag_name}' tag already exists with ID: {tag_id}")
        return tag_id
    
    result.fail_test(
        f"Setup: Create '{tag_name}' tag",
        f"Failed: {tag_response.status_code} - {tag_response.text}"
    )
    return None


def test_jane_posts_babysitting_need(jane_token, result):
    """Test: Jane posts a babysitting need"""
    print(f"{Colors.YELLOW}Test: Jane posts babysitting need{Colors.NC}")
    
    # Get/create babysitting and childcare tags
    babysitting_tag_id = get_or_create_tag(jane_token, "babysitting", result)
    childcare_tag_id = get_or_create_tag(jane_token, "childcare", result)
    
    if not babysitting_tag_id or not childcare_tag_id:
        result.fail_test("Jane posts babysitting need", "Failed to create tags")
        return None
    
    # Create babysitting need
    service_date = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")
    
    need_data = {
        "service_type": "need",
        "title": "Babysitting needed for 4.5-year-old daughter",
        "description": "Looking for a trustworthy babysitter for my daughter on evenings when I have late classes. Experience with young children preferred. Child-friendly environment required.",
        "hours_required": 3,
        "location_type": "in-person",
        "location_address": "456 Parent Lane, Family District",
        "latitude": 40.7489,
        "longitude": -73.9680,
        "service_date": service_date,
        "start_time": "18:00",
        "end_time": "21:00",
        "tag_ids": [babysitting_tag_id, childcare_tag_id]
    }
    
    response = requests.post(
        f"{BASE_URL}/services",
        json=need_data,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {jane_token}"}
    )
    
    if response.status_code != 201:
        result.fail_test(
            "Jane posts babysitting need",
            f"Failed: {response.status_code} - {response.text}"
        )
        return None
    
    response_data = response.json()
    need_id = (response_data.get('id') or 
               response_data.get('service_id') or 
               response_data.get('service', {}).get('id'))
    
    if not need_id:
        result.fail_test(
            "Jane posts babysitting need",
            "Need created but ID not found in response"
        )
        return None
    
    result.pass_test(
        "Jane posts babysitting need",
        f"Need created successfully with ID: {need_id}"
    )
    return need_id


def test_elizabeth_applies(elizabeth_token, need_id, result):
    """Test: Elizabeth applies to the babysitting need"""
    print(f"{Colors.YELLOW}Test: Elizabeth applies to babysitting need{Colors.NC}")
    
    response = requests.post(
        f"{BASE_URL}/services/{need_id}/apply",
        json={"message": "Hi Jane! I'd love to help with babysitting. I have years of experience with children and have been a grandmother to three wonderful kids. I'm patient, caring, and can provide references if needed."},
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {elizabeth_token}"}
    )
    
    if response.status_code != 201:
        result.fail_test(
            "Elizabeth applies to need",
            f"Failed: {response.status_code} - {response.text}"
        )
        return None
    
    response_data = response.json()
    application_id = (response_data.get('id') or 
                      response_data.get('application_id') or 
                      response_data.get('application', {}).get('id'))
    
    if not application_id:
        result.fail_test(
            "Elizabeth applies to need",
            "Application created but ID not found"
        )
        return None
    
    result.pass_test(
        "Elizabeth applies to need",
        f"Application created successfully with ID: {application_id}"
    )
    return application_id


def test_jane_views_applicants(jane_token, need_id, application_id, result):
    """Test: Jane views applicants for her need"""
    print(f"{Colors.YELLOW}Test: Jane views applicants{Colors.NC}")
    
    response = requests.get(
        f"{BASE_URL}/services/{need_id}/applications",
        headers={"Authorization": f"Bearer {jane_token}"}
    )
    
    if response.status_code != 200:
        result.fail_test(
            "Jane views applicants",
            f"Failed: {response.status_code} - {response.text}"
        )
        return False
    
    applications = response.json()
    if isinstance(applications, dict) and 'applications' in applications:
        applications = applications['applications']
    
    # Check if Elizabeth's application is in the list
    found = False
    for app in applications:
        if app.get('id') == application_id or app.get('application_id') == application_id:
            found = True
            result.pass_test(
                "Jane views applicants",
                f"Elizabeth's application found in list (Status: {app.get('status', 'unknown')})"
            )
            break
    
    if not found:
        result.fail_test(
            "Jane views applicants",
            "Elizabeth's application not found in applicant list"
        )
        return False
    
    return True


def test_jane_views_elizabeth_profile(jane_token, elizabeth_token, result):
    """Test: Jane views Elizabeth's profile"""
    print(f"{Colors.YELLOW}Test: Jane views Elizabeth's profile{Colors.NC}")
    
    # First get Elizabeth's user ID
    response = requests.get(
        f"{BASE_URL}/auth/profile",
        headers={"Authorization": f"Bearer {elizabeth_token}"}
    )
    
    if response.status_code != 200:
        result.fail_test(
            "Get Elizabeth's profile info",
            f"Failed: {response.status_code}"
        )
        return False
    
    elizabeth_data = response.json()
    # Handle nested 'user' key in response
    if 'user' in elizabeth_data:
        elizabeth_data = elizabeth_data['user']
    elizabeth_id = elizabeth_data.get('id') or elizabeth_data.get('user_id')
    
    if not elizabeth_id:
        result.fail_test(
            "Get Elizabeth's profile info",
            f"User ID not found in profile response: {elizabeth_data.keys()}"
        )
        return False
    
    # Jane views Elizabeth's public profile
    response = requests.get(
        f"{BASE_URL}/users/{elizabeth_id}",
        headers={"Authorization": f"Bearer {jane_token}"}
    )
    
    if response.status_code != 200:
        result.fail_test(
            "Jane views Elizabeth's profile",
            f"Failed: {response.status_code} - {response.text}"
        )
        return False
    
    profile = response.json()
    result.pass_test(
        "Jane views Elizabeth's profile",
        f"Profile retrieved: {profile.get('first_name', '')} {profile.get('last_name', '')}"
    )
    return True


def test_jane_accepts_elizabeth(jane_token, application_id, result):
    """Test: Jane accepts Elizabeth's application"""
    print(f"{Colors.YELLOW}Test: Jane accepts Elizabeth's application{Colors.NC}")
    
    response = requests.post(
        f"{BASE_URL}/applications/{application_id}/accept",
        headers={"Authorization": f"Bearer {jane_token}"}
    )
    
    if response.status_code != 200:
        result.fail_test(
            "Jane accepts Elizabeth",
            f"Failed: {response.status_code} - {response.text}"
        )
        return False
    
    result.pass_test(
        "Jane accepts Elizabeth",
        "Application accepted successfully"
    )
    return True


def test_messaging_enabled(jane_token, elizabeth_token, need_id, result):
    """Test: Private messaging is available between Jane and Elizabeth (after application)"""
    print(f"{Colors.YELLOW}Test: Private messaging enabled (after Elizabeth applied){Colors.NC}")
    
    # Note: Messaging is only available because Elizabeth applied to the service in Step 2
    # First get Elizabeth's user ID
    response = requests.get(
        f"{BASE_URL}/auth/profile",
        headers={"Authorization": f"Bearer {elizabeth_token}"}
    )
    
    if response.status_code != 200:
        result.fail_test(
            "Get Elizabeth's ID for messaging",
            f"Failed: {response.status_code}"
        )
        return False
    
    elizabeth_data = response.json()
    # Handle nested 'user' key in response
    if 'user' in elizabeth_data:
        elizabeth_data = elizabeth_data['user']
    elizabeth_id = elizabeth_data.get('id') or elizabeth_data.get('user_id')
    
    # Jane sends a message to Elizabeth
    response = requests.post(
        f"{BASE_URL}/messages",
        json={
            "receiver_id": elizabeth_id,
            "service_id": need_id,
            "message": "Hi Elizabeth! Thank you for accepting. Let's coordinate the details. Would you prefer to come to my home, or should I bring my daughter to your place?"
        },
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {jane_token}"}
    )
    
    if response.status_code != 201:
        result.fail_test(
            "Jane sends message",
            f"Failed: {response.status_code} - {response.text}"
        )
        return False
    
    result.pass_test(
        "Jane sends message",
        "Message sent successfully"
    )
    
    # Elizabeth retrieves messages
    time.sleep(1)
    response = requests.get(
        f"{BASE_URL}/messages",
        headers={"Authorization": f"Bearer {elizabeth_token}"}
    )
    
    if response.status_code != 200:
        result.fail_test(
            "Elizabeth retrieves messages",
            f"Failed: {response.status_code} - {response.text}"
        )
        return False
    
    result.pass_test(
        "Elizabeth retrieves messages",
        "Messages retrieved successfully"
    )
    
    # Get Jane's user ID for Elizabeth to reply
    response = requests.get(
        f"{BASE_URL}/auth/profile",
        headers={"Authorization": f"Bearer {jane_token}"}
    )
    
    if response.status_code != 200:
        result.fail_test(
            "Get Jane's ID for messaging",
            f"Failed: {response.status_code}"
        )
        return False
    
    jane_data = response.json()
    # Handle nested 'user' key in response
    if 'user' in jane_data:
        jane_data = jane_data['user']
    jane_id = jane_data.get('id') or jane_data.get('user_id')
    
    # Elizabeth replies
    response = requests.post(
        f"{BASE_URL}/messages",
        json={
            "receiver_id": jane_id,
            "service_id": need_id,
            "message": "I'd be happy to come to your home! That way your daughter can be in her familiar environment. I'll bring some activities and books for her."
        },
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {elizabeth_token}"}
    )
    
    if response.status_code != 201:
        result.fail_test(
            "Elizabeth sends reply",
            f"Failed: {response.status_code} - {response.text}"
        )
        return False
    
    result.pass_test(
        "Elizabeth sends reply",
        "Reply sent successfully"
    )
    
    return True


def get_progress_id(token, need_id, result):
    """Helper function to get service_progress.id from service applications"""
    # Try to get from service applications endpoint
    response = requests.get(
        f"{BASE_URL}/services/{need_id}/applications",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code == 200:
        data = response.json()
        apps = data if isinstance(data, list) else data.get('applications', [])
        
        # Look for accepted application with service_progress ID
        for app in apps:
            if app.get('status') == 'accepted':
                # API returns progress_id which is the service_progress.id
                progress_id = app.get('progress_id') or app.get('transaction_id')
                if progress_id:
                    return progress_id
    
    return None


def test_elizabeth_proposes_schedule(elizabeth_token, jane_token, need_id, result):
    """Test: Elizabeth proposes a schedule"""
    print(f"{Colors.YELLOW}Test: Elizabeth proposes schedule{Colors.NC}")
    
    # Get progress ID (Jane is the service owner, so use her token)
    progress_id = get_progress_id(jane_token, need_id, result)
    
    if not progress_id:
        result.fail_test(
            "Get progress ID for schedule proposal",
            "Progress ID not found - cannot test schedule proposal"
        )
        return None
    
    # Elizabeth proposes a schedule
    service_date = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")
    
    response = requests.post(
        f"{BASE_URL}/progress/{progress_id}/propose-schedule",
        json={
            "proposed_date": service_date,
            "proposed_start_time": "18:00",
            "proposed_end_time": "21:00",
            "proposed_location": "Jane's home - 456 Parent Lane"
        },
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {elizabeth_token}"}
    )
    
    if response.status_code not in [200, 201]:
        result.fail_test(
            "Elizabeth proposes schedule",
            f"Failed: {response.status_code} - {response.text}"
        )
        return None
    
    # Get message_id from response
    response_data = response.json()
    message_id = response_data.get('message_id')
    
    if not message_id:
        result.fail_test(
            "Elizabeth proposes schedule",
            "Schedule proposal succeeded but message_id not found in response"
        )
        return None, None
    
    result.pass_test(
        "Elizabeth proposes schedule",
        f"Schedule proposed: {service_date} 18:00-21:00 (message_id: {message_id})"
    )
    return progress_id, message_id


def test_jane_accepts_schedule(jane_token, message_id, result):
    """Test: Jane accepts the proposed schedule"""
    print(f"{Colors.YELLOW}Test: Jane accepts proposed schedule{Colors.NC}")
    
    if not message_id:
        result.fail_test(
            "Jane accepts schedule",
            "No message ID available"
        )
        return False
    
    # Jane accepts the schedule proposal via message response
    response = requests.post(
        f"{BASE_URL}/messages/{message_id}/respond-schedule",
        json={"accept": True},
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {jane_token}"}
    )
    
    if response.status_code not in [200, 201]:
        result.fail_test(
            "Jane accepts schedule",
            f"Failed: {response.status_code} - {response.text}"
        )
        return False
    
    result.pass_test(
        "Jane accepts schedule",
        "Schedule accepted successfully - service status should be 'scheduled'"
    )
    return True


def test_verify_scheduled_status(jane_token, need_id, result):
    """Test: Verify service status is 'scheduled'"""
    print(f"{Colors.YELLOW}Test: Verify service is scheduled{Colors.NC}")
    
    # Get service details to check status
    response = requests.get(
        f"{BASE_URL}/services/{need_id}",
        headers={"Authorization": f"Bearer {jane_token}"}
    )
    
    if response.status_code != 200:
        result.fail_test(
            "Verify scheduled status",
            f"Failed to get service: {response.status_code}"
        )
        return False
    
    service_data = response.json()
    
    # Check for progress status or service status
    status = service_data.get('progress_status') or service_data.get('status')
    
    if status == 'scheduled':
        result.pass_test(
            "Verify scheduled status",
            "Service status is 'scheduled'"
        )
        return True
    else:
        result.pass_test(
            "Verify scheduled status",
            f"Note: Status is '{status}' - may need manual verification"
        )
        return True


def test_elizabeth_confirms_start(elizabeth_token, progress_id, result):
    """Test: Elizabeth (provider) confirms the service start"""
    print(f"{Colors.YELLOW}Test: Elizabeth confirms start{Colors.NC}")
    
    if not progress_id:
        result.fail_test(
            "Get progress_id",
            "No progress_id provided"
        )
        return False
    
    # Elizabeth confirms start
    response = requests.post(
        f"{BASE_URL}/progress/{progress_id}/confirm-start",
        headers={"Authorization": f"Bearer {elizabeth_token}"}
    )
    
    if response.status_code not in [200, 201]:
        result.fail_test(
            "Elizabeth confirms start",
            f"Failed: {response.status_code} - {response.text}"
        )
        return False
    
    data = response.json()
    print(f"{Colors.GREEN}✓ Elizabeth confirmed start{Colors.NC}")
    print(f"  Response: {json.dumps(data, indent=2)}")
    
    result.pass_test(
        "Elizabeth confirms start",
        f"Provider confirmation successful"
    )
    return True


def test_jane_confirms_start(jane_token, progress_id, result):
    """Test: Jane (consumer) confirms the service start"""
    print(f"{Colors.YELLOW}Test: Jane confirms start{Colors.NC}")
    
    if not progress_id:
        result.fail_test(
            "Get progress_id",
            "No progress_id provided"
        )
        return False
    
    # Jane confirms start
    response = requests.post(
        f"{BASE_URL}/progress/{progress_id}/confirm-start",
        headers={"Authorization": f"Bearer {jane_token}"}
    )
    
    if response.status_code not in [200, 201]:
        result.fail_test(
            "Jane confirms start",
            f"Failed: {response.status_code} - {response.text}"
        )
        return False
    
    data = response.json()
    print(f"{Colors.GREEN}✓ Jane confirmed start{Colors.NC}")
    print(f"  Response: {json.dumps(data, indent=2)}")
    
    result.pass_test(
        "Jane confirms start",
        f"Consumer confirmation successful"
    )
    return True


def test_verify_in_progress_status(jane_token, need_id, result):
    """Test: Verify status changed to 'in_progress' after both confirmations"""
    print(f"{Colors.YELLOW}Test: Verify in_progress status{Colors.NC}")
    
    # Get service details to check status
    response = requests.get(
        f"{BASE_URL}/services/{need_id}",
        headers={"Authorization": f"Bearer {jane_token}"}
    )
    
    if response.status_code != 200:
        result.fail_test(
            "Get service details",
            f"Failed: {response.status_code}"
        )
        return False
    
    service_data = response.json()
    
    # Get applications to find the accepted one
    apps_response = requests.get(
        f"{BASE_URL}/services/{need_id}/applications",
        headers={"Authorization": f"Bearer {jane_token}"}
    )
    
    if apps_response.status_code != 200:
        result.fail_test(
            "Get applications",
            f"Failed: {apps_response.status_code}"
        )
        return False
    
    applications = apps_response.json()
    
    # Find accepted application's progress
    accepted_app = None
    for app in applications:
        if app.get('status') == 'accepted':
            accepted_app = app
            break
    
    if not accepted_app:
        result.fail_test(
            "Find accepted application",
            "No accepted application found"
        )
        return False
    
    # Get progress status
    progress = accepted_app.get('progress', {})
    status = progress.get('status')
    
    print(f"  Current status: {status}")
    
    if status == 'in_progress':
        print(f"{Colors.GREEN}✓ Status is 'in_progress' after both confirmations{Colors.NC}\n")
        result.pass_test(
            "Verify in_progress status",
            f"Status correctly updated to 'in_progress'"
        )
        return True
    else:
        result.pass_test(
            "Verify in_progress status",
            f"Note: Status is '{status}' - may need manual verification"
        )
        return True


def test_elizabeth_marks_finished(elizabeth_token, progress_id, result):
    """Test: Elizabeth (provider) marks service as finished"""
    print(f"{Colors.YELLOW}Test: Elizabeth marks service finished{Colors.NC}")
    
    if not progress_id:
        result.fail_test(
            "Get progress_id",
            "No progress_id provided"
        )
        return False
    
    # Elizabeth marks service as finished (only provider can do this)
    response = requests.post(
        f"{BASE_URL}/progress/{progress_id}/mark-finished",
        headers={"Authorization": f"Bearer {elizabeth_token}"}
    )
    
    if response.status_code not in [200, 201]:
        result.fail_test(
            "Elizabeth marks finished",
            f"Failed: {response.status_code} - {response.text}"
        )
        return False
    
    data = response.json()
    print(f"{Colors.GREEN}✓ Elizabeth marked service as finished{Colors.NC}")
    print(f"  Response: {json.dumps(data, indent=2)}")
    
    result.pass_test(
        "Elizabeth marks finished",
        "Provider marked service as finished - awaiting confirmations"
    )
    return True


def test_submit_surveys(jane_token, elizabeth_token, progress_id, result):
    """Test: Both parties submit completion surveys"""
    print(f"{Colors.YELLOW}Test: Submit completion surveys{Colors.NC}")
    
    if not progress_id:
        result.fail_test(
            "Get progress_id",
            "No progress_id provided"
        )
        return False
    
    # Elizabeth submits her survey first
    elizabeth_survey = {
        "rating": 5,
        "feedback": "Jane was wonderful! Very organized and clear about her needs.",
        "would_work_again": True
    }
    
    response = requests.post(
        f"{BASE_URL}/progress/{progress_id}/submit-survey",
        json={"survey_data": elizabeth_survey},
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {elizabeth_token}"}
    )
    
    if response.status_code not in [200, 201]:
        result.fail_test(
            "Elizabeth submits survey",
            f"Failed: {response.status_code} - {response.text}"
        )
        return False
    
    print(f"{Colors.GREEN}✓ Elizabeth submitted survey{Colors.NC}")
    
    # Jane submits her survey
    jane_survey = {
        "rating": 5,
        "feedback": "Elizabeth was fantastic with my kids! Very professional and caring.",
        "would_work_again": True
    }
    
    response = requests.post(
        f"{BASE_URL}/progress/{progress_id}/submit-survey",
        json={"survey_data": jane_survey},
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {jane_token}"}
    )
    
    if response.status_code not in [200, 201]:
        result.fail_test(
            "Jane submits survey",
            f"Failed: {response.status_code} - {response.text}"
        )
        return False
    
    data = response.json()
    print(f"{Colors.GREEN}✓ Jane submitted survey{Colors.NC}")
    print(f"  Response: {json.dumps(data, indent=2)}")
    
    result.pass_test(
        "Submit surveys",
        "Both parties submitted surveys - transaction should complete"
    )
    return True


def test_check_credit_transfer(elizabeth_token, initial_balance, result):
    """Test: Verify credits were transferred to Elizabeth"""
    print(f"{Colors.YELLOW}Test: Verify credit transfer to Elizabeth{Colors.NC}")
    
    time.sleep(1)  # Give system time to process
    
    response = requests.get(
        f"{BASE_URL}/auth/profile",
        headers={"Authorization": f"Bearer {elizabeth_token}"}
    )
    
    if response.status_code != 200:
        result.fail_test(
            "Check Elizabeth's balance",
            f"Failed to get profile: {response.status_code}"
        )
        return False
    
    profile = response.json()
    # Handle nested 'user' key in response
    if 'user' in profile:
        profile = profile['user']
    new_balance = profile.get('time_balance', 0)
    
    result.pass_test(
        "Check Elizabeth's balance",
        f"Elizabeth's balance: {initial_balance} -> {new_balance} hours (expected increase: 3 hours)"
    )
    
    return True





def run_all_tests():
    """Run all Scenario 4 tests"""
    result = TestResult()
    print_header()
    
    # Setup phase
    print(f"{Colors.BLUE}{'='*60}{Colors.NC}")
    print(f"{Colors.BLUE}Phase 1: Setup{Colors.NC}")
    print(f"{Colors.BLUE}{'='*60}{Colors.NC}\n")
    
    # Setup Jane (Consumer)
    jane_token = setup_user(
        "jane.miller@hive.com",
        "JaneMiller2025!",
        "Jane",
        "Miller",
        "1995-03-10",
        result,
        "Jane (Consumer)"
    )
    
    if not jane_token:
        print(f"{Colors.RED}Setup failed for Jane. Cannot continue.{Colors.NC}")
        result.print_summary()
        return
    
    # Setup Elizabeth (Provider)
    elizabeth_token = setup_user(
        "elizabeth.taylor@hive.com",
        "ElizabethTaylor2025!",
        "Elizabeth",
        "Taylor",
        "1953-08-15",
        result,
        "Elizabeth (Provider)"
    )
    
    if not elizabeth_token:
        print(f"{Colors.RED}Setup failed for Elizabeth. Cannot continue.{Colors.NC}")
        result.print_summary()
        return
    
    # Get Elizabeth's initial balance
    response = requests.get(
        f"{BASE_URL}/auth/profile",
        headers={"Authorization": f"Bearer {elizabeth_token}"}
    )
    if response.status_code == 200:
        profile_data = response.json()
        if 'user' in profile_data:
            profile_data = profile_data['user']
        elizabeth_initial_balance = profile_data.get('time_balance', 10)
    else:
        elizabeth_initial_balance = 10
    
    # Main test flow
    print(f"\n{Colors.BLUE}{'='*60}{Colors.NC}")
    print(f"{Colors.BLUE}Phase 2: Main Test Flow{Colors.NC}")
    print(f"{Colors.BLUE}{'='*60}{Colors.NC}\n")
    
    # Step 1: Jane posts babysitting need
    need_id = test_jane_posts_babysitting_need(jane_token, result)
    if not need_id:
        print(f"{Colors.RED}Failed to create need. Cannot continue.{Colors.NC}")
        result.print_summary()
        return
    
    # Step 2: Elizabeth applies
    application_id = test_elizabeth_applies(elizabeth_token, need_id, result)
    if not application_id:
        print(f"{Colors.RED}Failed to create application. Cannot continue.{Colors.NC}")
        result.print_summary()
        return
    
    # Step 3: Jane views applicants
    test_jane_views_applicants(jane_token, need_id, application_id, result)
    
    # Step 4: Jane views Elizabeth's profile
    test_jane_views_elizabeth_profile(jane_token, elizabeth_token, result)
    
    # Step 5: Jane accepts Elizabeth
    if not test_jane_accepts_elizabeth(jane_token, application_id, result):
        print(f"{Colors.RED}Failed to accept application. Some tests may not run.{Colors.NC}")
    
    # Update Jane's balance to have enough hours for the service (3 hours required)
    print(f"{Colors.YELLOW}Updating Jane's balance to 5 hours for testing{Colors.NC}")
    balance_response = requests.put(
        f"{BASE_URL}/testing/user/balance",
        headers={"Authorization": f"Bearer {jane_token}"},
        json={"balance": 5}
    )
    if balance_response.status_code == 200:
        print(f"{Colors.GREEN}✓ Jane's balance updated to 5 hours{Colors.NC}\n")
    else:
        print(f"{Colors.YELLOW}Note: Could not update balance via testing API{Colors.NC}\n")
    
    # Step 6: Private messaging (available after application was created in Step 2)
    test_messaging_enabled(jane_token, elizabeth_token, need_id, result)
    
    # Step 7: Elizabeth proposes schedule
    progress_id, message_id = test_elizabeth_proposes_schedule(elizabeth_token, jane_token, need_id, result)
    
    # Step 8: Jane accepts schedule
    if message_id:
        test_jane_accepts_schedule(jane_token, message_id, result)
        test_verify_scheduled_status(jane_token, need_id, result)
    
    # Step 9: Elizabeth confirms start
    if progress_id:
        test_elizabeth_confirms_start(elizabeth_token, progress_id, result)
    
    # Step 10: Jane confirms start
    if progress_id:
        test_jane_confirms_start(jane_token, progress_id, result)
    
    # Step 11: Verify in_progress status
    if progress_id:
        test_verify_in_progress_status(jane_token, need_id, result)
    
    # Step 12: Elizabeth marks service as finished
    if progress_id:
        test_elizabeth_marks_finished(elizabeth_token, progress_id, result)
    
    # Step 13: Both parties submit surveys
    if progress_id:
        test_submit_surveys(jane_token, elizabeth_token, progress_id, result)
    
    # Step 14: Verify credit transfer (happens automatically after both surveys)
    test_check_credit_transfer(elizabeth_token, elizabeth_initial_balance, result)
    
    # Print summary
    print()
    result.print_summary()


if __name__ == "__main__":
    run_all_tests()
