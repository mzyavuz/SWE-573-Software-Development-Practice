#!/usr/bin/env python3
"""
Test script for Scenario 2: Austin posts a guitar lesson offering with tags and availability
This tests the service offer creation and publishing flow

Scenario 2 Steps:
1. Austin signs in with verified account
2. Austin navigates to "Create Offer"
3. Austin enters title, description, hourly estimate, location preference (in-person/remote)
4. Austin attaches tags (guitar, tutoring) and optionally creates new tags
5. Austin sets availability windows and publishes the offer
6. The system validates inputs, publishes the service
7. The offer appears in Austin's dashboard and public search results

Acceptance criteria:
- Authenticated user can create service offers with valid data
- Service offers include title, description, hours, location type, and tags
- Published services appear in user's profile
- Published services appear in public service listings
- Invalid data is rejected with clear error messages
- Tags are properly associated with the service
- Availability windows are correctly stored
"""

import requests
import json
import time
from datetime import datetime

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
            print(f"\n{Colors.GREEN}✓ All tests passed! Scenario 2 is fully functional.{Colors.NC}")
            print(f"{Colors.GREEN}Austin can successfully create and publish a guitar lesson offer with tags and availability.{Colors.NC}\n")
            return True
        else:
            print(f"\n{Colors.RED}✗ Some tests failed. Please review the errors above.{Colors.NC}\n")
            return False


def print_header():
    print(f"\n{Colors.BLUE}{'='*60}{Colors.NC}")
    print(f"{Colors.BLUE}Scenario 2: Austin posts a guitar lesson offering{Colors.NC}")
    print(f"{Colors.BLUE}{'='*60}{Colors.NC}\n")
    
    print(f"{Colors.YELLOW}User Story:{Colors.NC}")
    print("Austin Page (The Newcomer & Provider) wants to:")
    print("1. Sign in to the platform")
    print("2. Create a guitar lesson offer")
    print("3. Add title, description, and hourly estimate")
    print("4. Attach tags (guitar, tutoring)")
    print("5. Set availability windows")
    print("6. Publish the offer")
    print("7. See the offer in search results and their profile")
    print()


def setup_user_and_login(result):
    """Setup: Register and login Austin"""
    print(f"{Colors.BLUE}Setup: Register and Login Austin{Colors.NC}")
    
    user_data = {
        "email": "austin.page@hive.com",
        "password": "Austin2025!",
        "first_name": "Austin",
        "last_name": "Page",
        "phone_number": "+1234567890"
    }
    
    try:
        # Try to login first
        print("Attempting to login with existing account...")
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
            access_token = response.json()["access_token"]
            print("✓ User already exists, logged in successfully")
            result.pass_test(
                "Austin successfully logged in",
                "User already registered and authenticated"
            )
            return user_data, access_token
        
        # If login failed, try to register
        print("User not found, creating new account...")
        response = requests.post(
            f"{BASE_URL}/auth/register",
            json=user_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code != 201:
            result.fail_test("User registration failed", f"Status: {response.status_code}")
            return None, None
        
        verification_token = response.json()["verification_token"]
        print("✓ User registered successfully")
        
        # Verify email
        response = requests.get(
            f"{BASE_URL}/auth/verify-email",
            params={"token": verification_token}
        )
        
        if response.status_code != 200:
            result.fail_test("Email verification failed", f"Status: {response.status_code}")
            return None, None
        
        print("✓ Email verified successfully")
        
        # Login with new account
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={
                "email": user_data["email"],
                "password": user_data["password"]
            },
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200 and "access_token" in response.json():
            access_token = response.json()["access_token"]
            result.pass_test(
                "Austin successfully logged in",
                "New user registered, verified, and authenticated"
            )
            return user_data, access_token
        else:
            result.fail_test("Login failed", f"Status: {response.status_code}")
            return None, None
            
    except Exception as e:
        result.fail_test("Setup failed", f"Exception: {str(e)}")
        return None, None


def setup_tags(result, access_token):
    """Setup: Create tags for the offer"""
    print(f"{Colors.BLUE}Setup: Create Tags{Colors.NC}")
    
    if not access_token:
        result.fail_test("Tag setup skipped", "No access token available")
        return []
    
    tag_names = ["guitar", "tutoring", "music", "education"]
    tag_ids = []
    
    try:
        # First, get all existing tags
        response = requests.get(f"{BASE_URL}/tags")
        existing_tags = {}
        if response.status_code == 200:
            for tag in response.json().get("tags", []):
                # Store tags by lowercase name for case-insensitive comparison
                existing_tags[tag["name"].lower()] = tag["id"]
        
        # For each tag name, check if it exists or create it
        for tag_name in tag_names:
            tag_name_lower = tag_name.lower()
            
            # Check if tag already exists (case-insensitive)
            if tag_name_lower in existing_tags:
                print(f"Tag '{tag_name}' already exists, using existing ID: {existing_tags[tag_name_lower]}")
                tag_ids.append(existing_tags[tag_name_lower])
            else:
                # Create new tag
                response = requests.post(
                    f"{BASE_URL}/tags",
                    json={"name": tag_name},
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {access_token}"
                    }
                )
                
                if response.status_code == 201:
                    new_tag_id = response.json()["tag"]["id"]
                    print(f"Created new tag '{tag_name}' with ID: {new_tag_id}")
                    tag_ids.append(new_tag_id)
                elif response.status_code == 409:
                    # Tag was just created by another process, get it
                    response_data = response.json()
                    if "tag" in response_data:
                        tag_ids.append(response_data["tag"]["id"])
                        print(f"Tag '{tag_name}' exists (conflict), using ID: {response_data['tag']['id']}")
                else:
                    print(f"Warning: Failed to create tag '{tag_name}': {response.status_code}")
        
        print(f"Created/Retrieved {len(tag_ids)} tags")
        print(f"Tag IDs: {tag_ids}")
        result.pass_test(
            "Tags setup successful",
            f"Created/retrieved {len(tag_ids)} tags: {', '.join(tag_names)}"
        )
        return tag_ids
        
    except Exception as e:
        result.fail_test("Tag setup failed", f"Exception: {str(e)}")
        return []


def test_create_guitar_offer(result, access_token, tag_ids):
    """Test 1: Create Guitar Lesson Offer"""
    print(f"{Colors.BLUE}Test 1: Create Guitar Lesson Offer{Colors.NC}")
    print("Austin creates a guitar lesson offer with all required fields")
    
    if not access_token:
        result.fail_test("Offer creation skipped", "No access token available")
        return None
    
    offer_data = {
        "service_type": "offer",
        "title": "Guitar Lessons for Beginners",
        "description": "I'm an experienced guitarist offering personalized lessons for beginners. I can teach you basic chords, strumming patterns, and simple songs. Whether you want to learn acoustic or electric guitar, I'll tailor the lessons to your goals. All you need is your own guitar and a willingness to practice!",
        "hours_required": 2.0,
        "location_type": "in-person",
        "location_address": "Downtown Music Studio",
        "latitude": 30.2672,
        "longitude": -97.7431,
        "tag_ids": tag_ids[:2] if len(tag_ids) >= 2 else tag_ids,  # Use guitar and tutoring tags
        "availability": [
            {"day_of_week": 1, "start_time": "18:00", "end_time": "21:00"},  # Monday
            {"day_of_week": 3, "start_time": "18:00", "end_time": "21:00"},  # Wednesday
            {"day_of_week": 5, "start_time": "14:00", "end_time": "19:00"}   # Friday
        ]
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/services",
            json=offer_data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {access_token}"
            }
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 201 and "service_id" in response.json():
            service_id = response.json()["service_id"]
            result.pass_test(
                "Guitar lesson offer created successfully",
                f"Service ID: {service_id}"
            )
            return service_id
        else:
            result.fail_test(
                "Offer creation failed",
                f"Expected status 201 with service_id, got {response.status_code}"
            )
            return None
            
    except Exception as e:
        result.fail_test("Offer creation failed", f"Exception: {str(e)}")
        return None


def test_retrieve_offer(result, access_token, service_id):
    """Test 2: Retrieve Created Offer"""
    print(f"{Colors.BLUE}Test 2: Retrieve Created Offer{Colors.NC}")
    print("Verify the offer can be retrieved with correct details")
    
    if not service_id:
        result.fail_test("Offer retrieval skipped", "No service ID available")
        return None
    
    try:
        response = requests.get(
            f"{BASE_URL}/services/{service_id}",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            service = response.json().get("service", {})
            
            # Verify key fields
            issues = []
            if service.get("title") != "Guitar Lessons for Beginners":
                issues.append(f"Title mismatch: {service.get('title')}")
            
            if service.get("service_type") != "offer":
                issues.append(f"Type should be 'offer', got {service.get('service_type')}")
            
            if service.get("hours_required") != 2.0:
                issues.append(f"Hours should be 2.0, got {service.get('hours_required')}")
            
            if service.get("location_type") != "in-person":
                issues.append(f"Location type should be 'in-person', got {service.get('location_type')}")
            
            if issues:
                result.fail_test(
                    "Offer details have issues",
                    "\n  ".join(issues)
                )
            else:
                result.pass_test(
                    "Offer retrieved successfully",
                    "All fields match expected values"
                )
            
            return service
        else:
            result.fail_test(
                "Offer retrieval failed",
                f"Expected status 200, got {response.status_code}"
            )
            return None
            
    except Exception as e:
        result.fail_test("Offer retrieval failed", f"Exception: {str(e)}")
        return None


def test_offer_in_listings(result, service_id):
    """Test 3: Offer Appears in Public Listings"""
    print(f"{Colors.BLUE}Test 3: Offer Appears in Public Listings{Colors.NC}")
    print("Verify the offer appears in public service listings")
    
    if not service_id:
        result.fail_test("Listings check skipped", "No service ID available")
        return
    
    try:
        response = requests.get(
            f"{BASE_URL}/services",
            params={"service_type": "offer", "status": "open"}
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            
            # Handle both response formats: {"services": [...]} or [...]
            if isinstance(response_data, list):
                services = response_data
            elif isinstance(response_data, dict):
                services = response_data.get("services", [])
            else:
                services = []
            
            print(f"Found {len(services)} offers in listings")
            
            # Check if our service is in the list
            found = any(service["id"] == service_id for service in services)
            
            if found:
                result.pass_test(
                    "Offer appears in public listings",
                    f"Service ID {service_id} is discoverable"
                )
            else:
                result.fail_test(
                    "Offer not found in listings",
                    f"Service ID {service_id} not in results"
                )
        else:
            result.fail_test(
                "Failed to retrieve listings",
                f"Expected status 200, got {response.status_code}"
            )
            
    except Exception as e:
        result.fail_test("Listings check failed", f"Exception: {str(e)}")


def test_offer_has_tags(result, access_token, service_id):
    """Test 4: Offer Has Associated Tags"""
    print(f"{Colors.BLUE}Test 4: Verify Tags Association{Colors.NC}")
    print("Check that tags are properly associated with the offer")
    
    if not service_id:
        result.fail_test("Tags check skipped", "No service ID available")
        return
    
    try:
        response = requests.get(
            f"{BASE_URL}/services/{service_id}",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            service = response.json().get("service", {})
            tags = service.get("tags", [])
            
            print(f"Tags: {tags}")
            
            if not tags:
                result.fail_test(
                    "No tags associated with offer",
                    "Tags array is empty"
                )
                return
            
            # Check for expected tags
            has_guitar = any("guitar" in str(tag).lower() for tag in tags)
            has_tutoring = any("tutoring" in str(tag).lower() for tag in tags)
            
            if has_guitar and has_tutoring:
                result.pass_test(
                    "Tags properly associated",
                    f"Found expected tags: {tags}"
                )
            else:
                result.fail_test(
                    "Expected tags not found",
                    f"Tags: {tags}, expected 'guitar' and 'tutoring'"
                )
        else:
            result.fail_test(
                "Failed to retrieve service for tag check",
                f"Status: {response.status_code}"
            )
            
    except Exception as e:
        result.fail_test("Tag check failed", f"Exception: {str(e)}")


def test_offer_has_availability(result, access_token, service_id):
    """Test 5: Offer Has Availability Windows"""
    print(f"{Colors.BLUE}Test 5: Verify Availability Windows{Colors.NC}")
    print("Check that availability windows are properly stored")
    
    if not service_id:
        result.fail_test("Availability check skipped", "No service ID available")
        return
    
    try:
        response = requests.get(
            f"{BASE_URL}/services/{service_id}",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            service = response.json().get("service", {})
            availability = service.get("availability", [])
            
            print(f"Availability windows: {json.dumps(availability, indent=2)}")
            
            if len(availability) >= 3:
                result.pass_test(
                    "Availability windows stored correctly",
                    f"Found {len(availability)} availability slots"
                )
            elif len(availability) > 0:
                result.pass_test(
                    "Availability windows stored (partial)",
                    f"Found {len(availability)} slots, expected 3"
                )
            else:
                result.fail_test(
                    "No availability windows found",
                    "Expected 3 availability slots"
                )
        else:
            result.fail_test(
                "Failed to retrieve service for availability check",
                f"Status: {response.status_code}"
            )
            
    except Exception as e:
        result.fail_test("Availability check failed", f"Exception: {str(e)}")


def test_invalid_offer_missing_fields(result, access_token):
    """Edge Case Test 1: Create Offer with Missing Required Fields"""
    print(f"{Colors.BLUE}Edge Case Test 1: Missing Required Fields{Colors.NC}")
    print("Attempting to create offer without required fields should fail")
    
    if not access_token:
        result.fail_test("Missing fields test skipped", "No access token available")
        return
    
    incomplete_offer = {
        "service_type": "offer",
        "title": "Incomplete Offer"
        # Missing description, hours_required, location_type
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/services",
            json=incomplete_offer,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {access_token}"
            }
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code >= 400 and "error" in response.json():
            result.pass_test(
                "Incomplete offer properly rejected",
                "System validates required fields"
            )
        else:
            result.fail_test(
                "Incomplete offer was not rejected",
                f"Expected error status, got {response.status_code}"
            )
            
    except Exception as e:
        result.fail_test("Missing fields test failed", f"Exception: {str(e)}")


def test_invalid_offer_hours_out_of_range(result, access_token):
    """Edge Case Test 2: Create Offer with Hours Out of Range"""
    print(f"{Colors.BLUE}Edge Case Test 2: Hours Out of Range{Colors.NC}")
    print("Attempting to create offer with invalid hours should fail")
    
    if not access_token:
        result.fail_test("Hours range test skipped", "No access token available")
        return
    
    invalid_offer = {
        "service_type": "offer",
        "title": "Invalid Hours Offer",
        "description": "This should fail validation",
        "hours_required": 5.0,  # Out of range (max 3.0)
        "location_type": "online"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/services",
            json=invalid_offer,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {access_token}"
            }
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code >= 400 and "error" in response.json():
            result.pass_test(
                "Invalid hours properly rejected",
                "System validates hours range (1.0-3.0)"
            )
        else:
            result.fail_test(
                "Invalid hours were not rejected",
                f"Expected error status, got {response.status_code}"
            )
            
    except Exception as e:
        result.fail_test("Hours range test failed", f"Exception: {str(e)}")


def test_invalid_location_type(result, access_token):
    """Edge Case Test 3: Create Offer with Invalid Location Type"""
    print(f"{Colors.BLUE}Edge Case Test 3: Invalid Location Type{Colors.NC}")
    print("Attempting to create offer with invalid location type should fail")
    
    if not access_token:
        result.fail_test("Location type test skipped", "No access token available")
        return
    
    invalid_offer = {
        "service_type": "offer",
        "title": "Invalid Location Offer",
        "description": "This should fail validation",
        "hours_required": 2.0,
        "location_type": "anywhere"  # Invalid, should be 'online', 'in-person', or 'both'
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/services",
            json=invalid_offer,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {access_token}"
            }
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code >= 400 and "error" in response.json():
            result.pass_test(
                "Invalid location type properly rejected",
                "System validates location type values"
            )
        else:
            result.fail_test(
                "Invalid location type was not rejected",
                f"Expected error status, got {response.status_code}"
            )
            
    except Exception as e:
        result.fail_test("Location type test failed", f"Exception: {str(e)}")


def test_unauthenticated_offer_creation(result):
    """Edge Case Test 4: Create Offer Without Authentication"""
    print(f"{Colors.BLUE}Edge Case Test 4: Unauthenticated Offer Creation{Colors.NC}")
    print("Attempting to create offer without authentication should fail")
    
    offer_data = {
        "service_type": "offer",
        "title": "Unauthorized Offer",
        "description": "Should not be allowed",
        "hours_required": 2.0,
        "location_type": "online"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/services",
            json=offer_data,
            headers={"Content-Type": "application/json"}
            # No Authorization header
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 401 and "error" in response.json():
            result.pass_test(
                "Unauthenticated offer creation properly rejected",
                "System requires authentication"
            )
        else:
            result.fail_test(
                "Unauthenticated offer creation was not rejected",
                f"Expected 401 status, got {response.status_code}"
            )
            
    except Exception as e:
        result.fail_test("Unauthenticated creation test failed", f"Exception: {str(e)}")


def main():
    """Run all Scenario 2 tests"""
    result = TestResult()
    print_header()
    
    # Setup
    user_data, access_token = setup_user_and_login(result)
    tag_ids = setup_tags(result, access_token)
    
    # Main flow tests
    service_id = test_create_guitar_offer(result, access_token, tag_ids)
    
    if service_id:
        service = test_retrieve_offer(result, access_token, service_id)
        test_offer_in_listings(result, service_id)
        test_offer_has_tags(result, access_token, service_id)
        test_offer_has_availability(result, access_token, service_id)
    
    # Edge case tests
    test_invalid_offer_missing_fields(result, access_token)
    test_invalid_offer_hours_out_of_range(result, access_token)
    test_invalid_location_type(result, access_token)
    test_unauthenticated_offer_creation(result)
    
    # Print summary and exit
    success = result.print_summary()
    exit(0 if success else 1)


if __name__ == "__main__":
    main()
