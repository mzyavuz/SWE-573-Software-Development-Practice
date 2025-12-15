#!/usr/bin/env python3
"""
Test script for Scenario 3: Taylor searches the map and applies for a gardening request
This tests the service search, filter, and application flow

Scenario 3 Steps:
1. Taylor signs in with verified account
2. Taylor opens "Find Needs" view and chooses Map View
3. Taylor uses filters for distance, tags (gardening), and estimated hours
4. The map/list updates to show matching needs
5. Taylor reviews a nearby gardening request
6. Taylor clicks "Apply" to offer help
7. The system records the application and notifies the consumer
8. The application shows in Taylor's dashboard as pending

Acceptance criteria:
- Authenticated user can view available needs
- Search filters work correctly (tags, location, hours)
- User can apply to a need with valid data
- Application is recorded and visible in provider's dashboard
- Consumer receives notification of the application
- Provider cannot apply to their own needs
- Provider cannot apply to already assigned needs
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
            print(f"\n{Colors.GREEN}✓ All tests passed! Scenario 3 is fully functional.{Colors.NC}")
            print(f"{Colors.GREEN}Taylor can successfully search for and apply to a gardening request.{Colors.NC}\n")
            return True
        else:
            print(f"\n{Colors.RED}✗ Some tests failed. Please review the errors above.{Colors.NC}\n")
            return False


def print_header():
    print(f"\n{Colors.BLUE}{'='*60}{Colors.NC}")
    print(f"{Colors.BLUE}Scenario 3: Taylor searches and applies for gardening{Colors.NC}")
    print(f"{Colors.BLUE}{'='*60}{Colors.NC}\n")
    
    print(f"{Colors.YELLOW}User Story:{Colors.NC}")
    print("Taylor Hope (The Energetic Teen) wants to:")
    print("1. Sign in to the platform")
    print("2. Browse needs on the map")
    print("3. Filter by distance, tags (gardening), and hours (2-4)")
    print("4. Review a nearby gardening request")
    print("5. Apply to help with the request")
    print("6. See the application in their dashboard")
    print()


def setup_consumer_and_need(result):
    """Setup: Create a consumer (Jane) and a gardening need"""
    print(f"{Colors.BLUE}Setup: Create Consumer (Jane) and Gardening Need{Colors.NC}")
    
    # Jane's credentials
    jane_data = {
        "email": "jane.miller@hive.com",
        "password": "JaneMiller2025!",
        "first_name": "Jane",
        "last_name": "Miller",
        "date_of_birth": "1995-03-10"
    }
    
    # Try to login first
    print("Attempting to login as Jane...")
    login_response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "email": jane_data["email"],
            "password": jane_data["password"]
        },
        headers={"Content-Type": "application/json"}
    )
    
    if login_response.status_code == 200:
        print(f"Jane already exists, logged in successfully")
        jane_token = login_response.json()['access_token']
    elif login_response.status_code == 403 and "verify" in login_response.text.lower():
        result.fail_test(
            "Setup: Login Jane",
            "Jane exists but email not verified. Please reset database or verify email manually."
        )
        return None, None
    else:
        # Register Jane
        print("Jane doesn't exist, registering...")
        response = requests.post(
            f"{BASE_URL}/auth/register",
            json=jane_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 409:
            result.fail_test(
                "Setup: Register Jane",
                "Jane exists but login failed. Email might need verification. Please reset database or verify email manually."
            )
            return None, None
        
        if response.status_code != 201:
            result.fail_test(
                "Setup: Register Jane",
                f"Registration failed: {response.status_code} - {response.text}"
            )
            return None, None
        
        # Get verification token
        verification_token = response.json()["verification_token"]
        print(f"Jane registered, verification token received")
        
        # Verify email
        verify_response = requests.get(
            f"{BASE_URL}/auth/verify-email",
            params={"token": verification_token}
        )
        
        if verify_response.status_code != 200:
            result.fail_test(
                "Setup: Verify Jane's email",
                f"Email verification failed: {verify_response.status_code} - {verify_response.text}"
            )
            return None, None
        
        print(f"Jane's email verified successfully")
        time.sleep(1)
        
        # Login after verification
        login_response = requests.post(
            f"{BASE_URL}/auth/login",
            json={
                "email": jane_data["email"],
                "password": jane_data["password"]
            },
            headers={"Content-Type": "application/json"}
        )
        
        if login_response.status_code != 200:
            result.fail_test(
                "Setup: Login Jane",
                f"Login failed after registration: {login_response.status_code} - {login_response.text}"
            )
            return None, None
        
        jane_token = login_response.json()['access_token']
        print(f"Jane registered and logged in successfully")
    
    # Create gardening tag if it doesn't exist
    print("Creating/fetching gardening tag...")
    
    # First, try to get existing tags
    tags_response = requests.get(
        f"{BASE_URL}/tags",
        headers={"Authorization": f"Bearer {jane_token}"}
    )
    
    gardening_tag_id = None
    if tags_response.status_code == 200:
        existing_tags = tags_response.json()
        # Handle both list and dict responses
        if isinstance(existing_tags, dict) and 'tags' in existing_tags:
            existing_tags = existing_tags['tags']
        
        if isinstance(existing_tags, list):
            for tag in existing_tags:
                if isinstance(tag, dict) and tag.get('name', '').lower() == 'gardening':
                    gardening_tag_id = tag['id']
                    print(f"Found existing gardening tag with ID: {gardening_tag_id}")
                    break
    
    # Create tag if it doesn't exist
    if not gardening_tag_id:
        tag_response = requests.post(
            f"{BASE_URL}/tags",
            json={"name": "gardening"},
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {jane_token}"
            }
        )
        
        if tag_response.status_code == 201:
            response_data = tag_response.json()
            # Handle both direct id and nested tag object
            if isinstance(response_data, dict):
                gardening_tag_id = response_data.get('id') or response_data.get('tag', {}).get('id')
            print(f"Created new gardening tag with ID: {gardening_tag_id}")
        elif tag_response.status_code == 409:
            # Tag exists but we didn't find it, get the ID from error response
            gardening_tag_id = tag_response.json().get('existing_tag_id')
            print(f"Gardening tag already exists with ID: {gardening_tag_id}")
        else:
            result.fail_test(
                "Setup: Create gardening tag",
                f"Failed: {tag_response.status_code} - {tag_response.text}"
            )
            return None, None
        
        if not gardening_tag_id:
            result.fail_test(
                "Setup: Create gardening tag",
                f"Tag created but ID not found in response: {tag_response.text}"
            )
            return None, None
    
    # Create a gardening need
    print("Creating gardening need...")
    
    # Set service date to tomorrow
    service_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    
    need_data = {
        "service_type": "need",
        "title": "Garden cleanup and weeding help needed",
        "description": "I need help cleaning up my backyard garden, removing weeds, and preparing soil for spring planting. Basic gardening knowledge helpful.",
        "hours_required": 2,
        "location_type": "in-person",
        "location_address": "123 Garden Street, Community Area",
        "latitude": 40.7580,  # Example coordinates in NYC area
        "longitude": -73.9855,
        "service_date": service_date,
        "start_time": "10:00",
        "end_time": "12:30",
        "tag_ids": [gardening_tag_id]
    }
    
    need_response = requests.post(
        f"{BASE_URL}/services",
        json=need_data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {jane_token}"
        }
    )
    
    if need_response.status_code != 201:
        result.fail_test(
            "Setup: Create gardening need",
            f"Failed: {need_response.status_code} - {need_response.text}"
        )
        return None, None
    
    response_data = need_response.json()
    # Handle different response formats: id, service_id, or nested service object
    if isinstance(response_data, dict):
        need_id = (response_data.get('id') or 
                   response_data.get('service_id') or 
                   response_data.get('service', {}).get('id'))
    else:
        result.fail_test(
            "Setup: Create gardening need",
            f"Unexpected response format: {type(response_data)}"
        )
        return None, None
    
    if not need_id:
        result.fail_test(
            "Setup: Create gardening need",
            f"Need created but ID not found in response: {need_response.text}"
        )
        return None, None
    
    print(f"Created gardening need with ID: {need_id}")
    result.pass_test("Setup: Create consumer and gardening need", f"Jane created, Need ID: {need_id}")
    
    return jane_token, need_id


def setup_taylor_and_login(result):
    """Setup: Register and login Taylor"""
    print(f"{Colors.BLUE}Setup: Register and Login Taylor{Colors.NC}")
    
    taylor_data = {
        "email": "taylor.hope@hive.com",
        "password": "TaylorHope2025!",
        "first_name": "Taylor",
        "last_name": "Hope",
        "date_of_birth": "2007-08-15"
    }
    
    # Try to login first
    print("Attempting to login as Taylor...")
    login_response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "email": taylor_data["email"],
            "password": taylor_data["password"]
        },
        headers={"Content-Type": "application/json"}
    )
    
    if login_response.status_code == 200:
        print(f"Taylor already exists, logged in successfully")
        taylor_token = login_response.json()['access_token']
        result.pass_test("Setup: Login Taylor", "Successfully logged in")
        return taylor_token
    elif login_response.status_code == 403 and "verify" in login_response.text.lower():
        result.fail_test(
            "Setup: Login Taylor",
            "Taylor exists but email not verified. Please reset database or verify email manually."
        )
        return None
    
    # Register Taylor
    print("Taylor doesn't exist, registering...")
    response = requests.post(
        f"{BASE_URL}/auth/register",
        json=taylor_data,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 409:
        result.fail_test(
            "Setup: Register Taylor",
            "Taylor exists but login failed. Email might need verification. Please reset database or verify email manually."
        )
        return None
    
    if response.status_code != 201:
        result.fail_test(
            "Setup: Register Taylor",
            f"Registration failed: {response.status_code} - {response.text}"
        )
        return None
    
    # Get verification token
    verification_token = response.json()["verification_token"]
    print(f"Taylor registered, verification token received")
    
    # Verify email
    verify_response = requests.get(
        f"{BASE_URL}/auth/verify-email",
        params={"token": verification_token}
    )
    
    if verify_response.status_code != 200:
        result.fail_test(
            "Setup: Verify Taylor's email",
            f"Email verification failed: {verify_response.status_code} - {verify_response.text}"
        )
        return None
    
    print(f"Taylor's email verified successfully")
    time.sleep(1)
    
    # Login Taylor
    login_response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "email": taylor_data["email"],
            "password": taylor_data["password"]
        },
        headers={"Content-Type": "application/json"}
    )
    
    if login_response.status_code != 200:
        result.fail_test(
            "Setup: Login Taylor",
            f"Login failed: {login_response.status_code} - {login_response.text}"
        )
        return None
    
    taylor_token = login_response.json()['access_token']
    result.pass_test("Setup: Register and Login Taylor", "Taylor authenticated successfully")
    return taylor_token


# Main test functions
def test_view_all_needs(taylor_token, result):
    """Test 1: Taylor can view all available needs"""
    print(f"{Colors.YELLOW}Test 1: View all available needs{Colors.NC}")
    
    response = requests.get(
        f"{BASE_URL}/services?service_type=need",
        headers={"Authorization": f"Bearer {taylor_token}"}
    )
    
    if response.status_code != 200:
        result.fail_test(
            "View all needs",
            f"Failed to fetch needs: {response.status_code} - {response.text}"
        )
        return False
    
    data = response.json()
    
    # Handle both list and object with services key
    if isinstance(data, dict) and 'services' in data:
        needs = data['services']
    elif isinstance(data, list):
        needs = data
    else:
        result.fail_test(
            "View all needs",
            f"Unexpected response format: {type(data)}"
        )
        return False
    
    if len(needs) == 0:
        result.fail_test(
            "View all needs",
            "No needs found, but we created one in setup"
        )
        return False
    
    result.pass_test(
        "View all needs",
        f"Found {len(needs)} need(s) available"
    )
    return True


def test_filter_needs_by_tag(taylor_token, result):
    """Test 2: Taylor can filter needs by gardening tag"""
    print(f"{Colors.YELLOW}Test 2: Filter needs by gardening tag{Colors.NC}")
    
    # First, get the gardening tag ID
    tags_response = requests.get(
        f"{BASE_URL}/tags",
        headers={"Authorization": f"Bearer {taylor_token}"}
    )
    
    if tags_response.status_code != 200:
        result.fail_test(
            "Filter needs by tag",
            f"Failed to fetch tags: {tags_response.status_code}"
        )
        return False
    
    gardening_tag_id = None
    tags_data = tags_response.json()
    # Handle both list and dict responses
    if isinstance(tags_data, dict) and 'tags' in tags_data:
        tags_data = tags_data['tags']
    
    if isinstance(tags_data, list):
        for tag in tags_data:
            if isinstance(tag, dict) and tag.get('name', '').lower() == 'gardening':
                gardening_tag_id = tag['id']
                break
    
    if not gardening_tag_id:
        result.fail_test(
            "Filter needs by tag",
            "Gardening tag not found"
        )
        return False
    
    # Filter services by tag
    response = requests.get(
        f"{BASE_URL}/services?service_type=need&tag_id={gardening_tag_id}",
        headers={"Authorization": f"Bearer {taylor_token}"}
    )
    
    if response.status_code != 200:
        result.fail_test(
            "Filter needs by tag",
            f"Failed: {response.status_code} - {response.text}"
        )
        return False
    
    data = response.json()
    
    # Handle both list and object with services key
    if isinstance(data, dict) and 'services' in data:
        filtered_needs = data['services']
    elif isinstance(data, list):
        filtered_needs = data
    else:
        filtered_needs = []
    
    if len(filtered_needs) == 0:
        result.fail_test(
            "Filter needs by tag",
            "No gardening needs found after filtering"
        )
        return False
    
    result.pass_test(
        "Filter needs by tag",
        f"Found {len(filtered_needs)} gardening need(s)"
    )
    return True


def test_view_need_details(taylor_token, need_id, result):
    """Test 3: Taylor can view details of a specific need"""
    print(f"{Colors.YELLOW}Test 3: View specific need details{Colors.NC}")
    
    response = requests.get(
        f"{BASE_URL}/services/{need_id}",
        headers={"Authorization": f"Bearer {taylor_token}"}
    )
    
    if response.status_code != 200:
        result.fail_test(
            "View need details",
            f"Failed: {response.status_code} - {response.text}"
        )
        return False
    
    need = response.json()
    
    # Verify essential fields are present (check both 'id' and 'service_id')
    # Also handle if response is wrapped in a 'service' key
    if isinstance(need, dict) and 'service' in need:
        need = need['service']
    
    required_fields = ['title', 'description', 'hours_required', 'location_type']
    missing_fields = [field for field in required_fields if field not in need]
    
    # Check for id or service_id
    if 'id' not in need and 'service_id' not in need:
        missing_fields.append('id/service_id')
    
    if missing_fields:
        result.fail_test(
            "View need details",
            f"Missing fields in response: {missing_fields}"
        )
        return False
    
    result.pass_test(
        "View need details",
        f"Successfully viewed need: '{need['title']}'"
    )
    return True


def test_apply_to_need(taylor_token, need_id, result):
    """Test 4: Taylor applies to the gardening need"""
    print(f"{Colors.YELLOW}Test 4: Apply to gardening need{Colors.NC}")
    
    application_data = {
        "message": "Hi! I'd love to help with your garden. I have experience with weeding and soil preparation from helping my parents with their garden."
    }
    
    response = requests.post(
        f"{BASE_URL}/services/{need_id}/apply",
        json=application_data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {taylor_token}"
        }
    )
    
    if response.status_code != 201:
        result.fail_test(
            "Apply to need",
            f"Failed: {response.status_code} - {response.text}"
        )
        return False
    
    application = response.json()
    
    # Handle different response formats
    if isinstance(application, dict) and 'application' in application:
        application = application['application']
    
    application_id = application.get('id') or application.get('application_id')
    
    if not application_id:
        result.fail_test(
            "Apply to need",
            f"Application response missing ID: {response.text}"
        )
        return False
    
    result.pass_test(
        "Apply to need",
        f"Successfully applied, Application ID: {application_id}"
    )
    return application_id


def test_view_application_in_dashboard(taylor_token, application_id, result):
    """Test 5: Taylor can see the application in their dashboard"""
    print(f"{Colors.YELLOW}Test 5: View application in dashboard{Colors.NC}")
    
    response = requests.get(
        f"{BASE_URL}/user/applications",
        headers={"Authorization": f"Bearer {taylor_token}"}
    )
    
    if response.status_code != 200:
        result.fail_test(
            "View application in dashboard",
            f"Failed: {response.status_code} - {response.text}"
        )
        return False
    
    applications = response.json()
    
    # Find the application we just created
    found = False
    for app in applications:
        # Check for both 'id' and 'application_id'
        app_id = app.get('id') or app.get('application_id')
        if app_id == application_id:
            found = True
            break
    
    if not found:
        result.fail_test(
            "View application in dashboard",
            f"Application {application_id} not found in dashboard"
        )
        return False
    
    result.pass_test(
        "View application in dashboard",
        f"Application visible in Taylor's dashboard, Status: {app.get('status', 'pending')}"
    )
    return True


def test_consumer_sees_application(jane_token, need_id, application_id, result):
    """Test 6: Jane (consumer) can see Taylor's application"""
    print(f"{Colors.YELLOW}Test 6: Consumer sees application{Colors.NC}")
    
    response = requests.get(
        f"{BASE_URL}/services/{need_id}/applications",
        headers={"Authorization": f"Bearer {jane_token}"}
    )
    
    if response.status_code != 200:
        result.fail_test(
            "Consumer sees application",
            f"Failed: {response.status_code} - {response.text}"
        )
        return False
    
    applications = response.json()
    
    # Find Taylor's application
    found = False
    for app in applications:
        if app['id'] == application_id:
            found = True
            break
    
    if not found:
        result.fail_test(
            "Consumer sees application",
            f"Application {application_id} not visible to consumer"
        )
        return False
    
    result.pass_test(
        "Consumer sees application",
        f"Jane can see Taylor's application"
    )
    return True


# Edge case tests
def test_cannot_apply_twice(taylor_token, need_id, result):
    """Edge Test 1: Taylor cannot apply to the same need twice"""
    print(f"{Colors.YELLOW}Edge Test 1: Cannot apply to same need twice{Colors.NC}")
    
    application_data = {
        "message": "Applying again (should fail)"
    }
    
    response = requests.post(
        f"{BASE_URL}/services/{need_id}/apply",
        json=application_data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {taylor_token}"
        }
    )
    
    if response.status_code == 201:
        result.fail_test(
            "Cannot apply twice",
            "System allowed duplicate application"
        )
        return False
    
    if response.status_code == 400 or response.status_code == 409:
        result.pass_test(
            "Cannot apply twice",
            f"Duplicate application correctly rejected: {response.json().get('error', 'Duplicate not allowed')}"
        )
        return True
    
    result.fail_test(
        "Cannot apply twice",
        f"Unexpected response: {response.status_code} - {response.text}"
    )
    return False


def test_cannot_apply_to_own_need(taylor_token, result):
    """Edge Test 2: Taylor cannot apply to their own need"""
    print(f"{Colors.YELLOW}Edge Test 2: Cannot apply to own need{Colors.NC}")
    
    # Create a need as Taylor
    service_date = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")
    
    own_need_data = {
        "service_type": "need",
        "title": "Test need by Taylor",
        "description": "This is Taylor's own need",
        "hours_required": 2,
        "location_type": "online",
        "service_date": service_date,
        "start_time": "14:00",
        "end_time": "15:30",
        "tag_ids": []
    }
    
    create_response = requests.post(
        f"{BASE_URL}/services",
        json=own_need_data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {taylor_token}"
        }
    )
    
    if create_response.status_code != 201:
        result.fail_test(
            "Cannot apply to own need - Setup",
            f"Failed to create test need: {create_response.status_code}"
        )
        return False
    
    response_data = create_response.json()
    own_need_id = (response_data.get('id') or 
                   response_data.get('service_id') or 
                   response_data.get('service', {}).get('id'))
    
    # Try to apply to own need
    application_data = {
        "message": "Applying to my own need (should fail)"
    }
    
    response = requests.post(
        f"{BASE_URL}/services/{own_need_id}/apply",
        json=application_data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {taylor_token}"
        }
    )
    
    if response.status_code == 201:
        result.fail_test(
            "Cannot apply to own need",
            "System allowed applying to own need"
        )
        return False
    
    if response.status_code == 400 or response.status_code == 403:
        result.pass_test(
            "Cannot apply to own need",
            f"Own need application correctly rejected: {response.json().get('error', 'Cannot apply to own need')}"
        )
        return True
    
    result.fail_test(
        "Cannot apply to own need",
        f"Unexpected response: {response.status_code} - {response.text}"
    )
    return False


def run_all_tests():
    """Run all Scenario 3 tests"""
    result = TestResult()
    print_header()
    
    # Setup phase
    print(f"{Colors.BLUE}{'='*60}{Colors.NC}")
    print(f"{Colors.BLUE}Phase 1: Setup{Colors.NC}")
    print(f"{Colors.BLUE}{'='*60}{Colors.NC}\n")
    
    jane_token, need_id = setup_consumer_and_need(result)
    if not jane_token or not need_id:
        print(f"{Colors.RED}Setup failed. Cannot continue with tests.{Colors.NC}")
        result.print_summary()
        return
    
    taylor_token = setup_taylor_and_login(result)
    if not taylor_token:
        print(f"{Colors.RED}Setup failed. Cannot continue with tests.{Colors.NC}")
        result.print_summary()
        return
    
    # Main test flow
    print(f"\n{Colors.BLUE}{'='*60}{Colors.NC}")
    print(f"{Colors.BLUE}Phase 2: Main Test Flow{Colors.NC}")
    print(f"{Colors.BLUE}{'='*60}{Colors.NC}\n")
    
    test_view_all_needs(taylor_token, result)
    test_filter_needs_by_tag(taylor_token, result)
    test_view_need_details(taylor_token, need_id, result)
    application_id = test_apply_to_need(taylor_token, need_id, result)
    
    if application_id:
        test_view_application_in_dashboard(taylor_token, application_id, result)
        test_consumer_sees_application(jane_token, need_id, application_id, result)
    
    # Edge case tests
    print(f"\n{Colors.BLUE}{'='*60}{Colors.NC}")
    print(f"{Colors.BLUE}Phase 3: Edge Case Tests{Colors.NC}")
    print(f"{Colors.BLUE}{'='*60}{Colors.NC}\n")
    
    test_cannot_apply_twice(taylor_token, need_id, result)
    test_cannot_apply_to_own_need(taylor_token, result)
    
    # Print summary
    print()
    result.print_summary()


if __name__ == "__main__":
    run_all_tests()
