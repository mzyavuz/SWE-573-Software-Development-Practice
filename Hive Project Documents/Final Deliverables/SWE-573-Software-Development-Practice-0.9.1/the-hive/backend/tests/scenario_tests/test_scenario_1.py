#!/usr/bin/env python3
"""
Test script for Scenario 1: Alex signs up, verifies email, and sees starting balance
This tests the complete user onboarding flow including time-credit balance display

Scenario 1 Steps:
1. Alex opens the app and chooses "Sign up"
2. He fills in name, email, date of birth and passwords and accepts Terms and Services & Privacy Policy
3. The system creates a provisional account and sends a verification email (UR-1, UR-2)
4. Alex clicks the verification link, which marks the email verified and activates the account (UR-2)
5. Alex signs in with his email and password (UR-3)
6. The dashboard shows a starting balance (TCS-1)

Acceptance criteria:
- Account creation succeeds with valid input and sends a verification email
- Clicking the verification link sets the account to active and allows authentication
- After first login the dashboard displays the initial time-credit balance
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5001/api"
EXPECTED_INITIAL_BALANCE = 1

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
            print(f"\n{Colors.GREEN}✓ All tests passed! Scenario 1 is fully functional.{Colors.NC}")
            print(f"{Colors.GREEN}Alex can successfully sign up, verify email, login, and see the initial time-credit balance.{Colors.NC}\n")
            return True
        else:
            print(f"\n{Colors.RED}✗ Some tests failed. Please review the errors above.{Colors.NC}\n")
            return False


def print_header():
    print(f"\n{Colors.BLUE}{'='*60}{Colors.NC}")
    print(f"{Colors.BLUE}Scenario 1: Alex signs up, verifies email, and sees starting balance{Colors.NC}")
    print(f"{Colors.BLUE}{'='*60}{Colors.NC}\n")
    
    print(f"{Colors.YELLOW}User Story:{Colors.NC}")
    print("Alex Chen (The Curious Newcomer) wants to:")
    print("1. Sign up for the platform")
    print("2. Verify their email address")
    print("3. Sign in with credentials")
    print("4. See their initial time-credit balance")
    print()


def test_user_registration(result):
    """Test 1: User Registration (Steps 1-3)"""
    print(f"{Colors.BLUE}Test 1: User Registration{Colors.NC}")
    print("Alex signs up with email, password, first name, last name, and phone number")
    
    # Generate unique email
    timestamp = int(time.time())
    user_data = {
        "email": f"alex.chen.{timestamp}@gmail.com",
        "password": "SecurePass123!",
        "first_name": "Alex",
        "last_name": "Chen",
        "phone_number": "+1234567890"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/register",
            json=user_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 201 and "verification_token" in response.json():
            verification_token = response.json()["verification_token"]
            result.pass_test(
                "User registration successful",
                "Account created with verification email sent"
            )
            return user_data, verification_token
        else:
            result.fail_test(
                "User registration failed",
                f"Expected status 201 with verification_token, got {response.status_code}"
            )
            return None, None
            
    except Exception as e:
        result.fail_test("User registration failed", f"Exception: {str(e)}")
        return None, None


def test_email_verification(result, verification_token):
    """Test 2: Email Verification (Step 4)"""
    print(f"{Colors.BLUE}Test 2: Email Verification{Colors.NC}")
    print("Alex clicks the verification link to activate the account")
    
    if not verification_token:
        result.fail_test("Email verification skipped", "No verification token available")
        return False
    
    try:
        response = requests.get(
            f"{BASE_URL}/auth/verify-email",
            params={"token": verification_token}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200 and "Email verified successfully" in response.json().get("message", ""):
            result.pass_test(
                "Email verification successful",
                "Account is now active"
            )
            return True
        else:
            result.fail_test(
                "Email verification failed",
                f"Expected success message, got status {response.status_code}"
            )
            return False
            
    except Exception as e:
        result.fail_test("Email verification failed", f"Exception: {str(e)}")
        return False


def test_user_login(result, user_data):
    """Test 3: User Login (Step 5)"""
    print(f"{Colors.BLUE}Test 3: User Login{Colors.NC}")
    print("Alex signs in with email and password")
    
    if not user_data:
        result.fail_test("User login skipped", "No user data available")
        return None
    
    try:
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
                "User login successful",
                "Access token received"
            )
            return access_token
        else:
            result.fail_test(
                "User login failed",
                f"Expected status 200 with access_token, got {response.status_code}"
            )
            return None
            
    except Exception as e:
        result.fail_test("User login failed", f"Exception: {str(e)}")
        return None


def test_initial_balance(result, access_token):
    """Test 4: Check Initial Time-Credit Balance (Step 6)"""
    print(f"{Colors.BLUE}Test 4: Check Initial Time-Credit Balance{Colors.NC}")
    print("Alex views their dashboard to see the starting balance")
    
    if not access_token:
        result.fail_test("Balance check skipped", "No access token available")
        return None
    
    try:
        response = requests.get(
            f"{BASE_URL}/auth/profile",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            user_profile = response.json().get("user", {})
            time_balance = user_profile.get("time_balance")
            
            if time_balance is not None:
                if time_balance == EXPECTED_INITIAL_BALANCE:
                    result.pass_test(
                        "Initial time-credit balance displayed correctly",
                        f"Balance: {time_balance} hour(s)"
                    )
                    return user_profile
                else:
                    result.fail_test(
                        "Initial time-credit balance incorrect",
                        f"Expected: {EXPECTED_INITIAL_BALANCE}, Got: {time_balance}"
                    )
                    return user_profile
            else:
                result.fail_test(
                    "Time balance not found",
                    "Profile response missing time_balance field"
                )
                return user_profile
        else:
            result.fail_test(
                "Failed to retrieve profile",
                f"Expected status 200, got {response.status_code}"
            )
            return None
            
    except Exception as e:
        result.fail_test("Balance check failed", f"Exception: {str(e)}")
        return None


def test_profile_completeness(result, user_profile, user_data):
    """Test 5: Verify Profile Data Completeness"""
    print(f"{Colors.BLUE}Test 5: Verify Profile Data Completeness{Colors.NC}")
    print("Checking that all user data is correctly stored and retrieved")
    
    if not user_profile or not user_data:
        result.fail_test("Profile completeness check skipped", "No profile or user data available")
        return
    
    issues = []
    
    if user_profile.get("email") != user_data["email"]:
        issues.append(f"Email mismatch: expected {user_data['email']}, got {user_profile.get('email')}")
    
    if user_profile.get("first_name") != user_data["first_name"]:
        issues.append(f"First name mismatch: expected {user_data['first_name']}, got {user_profile.get('first_name')}")
    
    if user_profile.get("last_name") != user_data["last_name"]:
        issues.append(f"Last name mismatch: expected {user_data['last_name']}, got {user_profile.get('last_name')}")
    
    if not user_profile.get("is_verified"):
        issues.append("Account not verified")
    
    if issues:
        result.fail_test(
            "Profile data has issues",
            "\n  ".join(issues)
        )
    else:
        result.pass_test(
            "Profile data is complete and accurate",
            "All fields match expected values"
        )


def test_duplicate_registration(result, user_data):
    """Edge Case Test 1: Duplicate Email Registration"""
    print(f"{Colors.BLUE}Edge Case Test 1: Duplicate Email Registration{Colors.NC}")
    print("Attempting to register with the same email should fail")
    
    if not user_data:
        result.fail_test("Duplicate registration test skipped", "No user data available")
        return
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/register",
            json={
                "email": user_data["email"],
                "password": "AnotherPass123!",
                "first_name": "Another",
                "last_name": "User",
                "phone_number": "+9876543210"
            },
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code >= 400 and "error" in response.json():
            result.pass_test(
                "Duplicate email registration properly rejected",
                f"System returned error as expected"
            )
        else:
            result.fail_test(
                "Duplicate email registration was not rejected",
                f"Expected error status, got {response.status_code}"
            )
            
    except Exception as e:
        result.fail_test("Duplicate registration test failed", f"Exception: {str(e)}")


def test_wrong_password(result, user_data):
    """Edge Case Test 2: Login with Wrong Password"""
    print(f"{Colors.BLUE}Edge Case Test 2: Login with Wrong Password{Colors.NC}")
    print("Attempting to login with incorrect password should fail")
    
    if not user_data:
        result.fail_test("Wrong password test skipped", "No user data available")
        return
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={
                "email": user_data["email"],
                "password": "WrongPassword123!"
            },
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code >= 400 and "error" in response.json():
            result.pass_test(
                "Login with wrong password properly rejected",
                "System returned error as expected"
            )
        else:
            result.fail_test(
                "Login with wrong password was not rejected",
                f"Expected error status, got {response.status_code}"
            )
            
    except Exception as e:
        result.fail_test("Wrong password test failed", f"Exception: {str(e)}")


def test_unauthorized_access(result):
    """Edge Case Test 3: Access Profile Without Token"""
    print(f"{Colors.BLUE}Edge Case Test 3: Access Profile Without Token{Colors.NC}")
    print("Attempting to access profile without authentication should fail")
    
    try:
        response = requests.get(f"{BASE_URL}/auth/profile")
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 401 and "error" in response.json():
            result.pass_test(
                "Unauthorized profile access properly rejected",
                "System requires authentication as expected"
            )
        else:
            result.fail_test(
                "Unauthorized profile access was not rejected",
                f"Expected 401 status, got {response.status_code}"
            )
            
    except Exception as e:
        result.fail_test("Unauthorized access test failed", f"Exception: {str(e)}")


def main():
    """Run all Scenario 1 tests"""
    result = TestResult()
    print_header()
    
    # Main flow tests
    user_data, verification_token = test_user_registration(result)
    
    if verification_token:
        verified = test_email_verification(result, verification_token)
    else:
        verified = False
    
    if verified and user_data:
        access_token = test_user_login(result, user_data)
    else:
        access_token = None
    
    if access_token:
        user_profile = test_initial_balance(result, access_token)
        test_profile_completeness(result, user_profile, user_data)
    else:
        user_profile = None
    
    # Edge case tests
    test_duplicate_registration(result, user_data)
    test_wrong_password(result, user_data)
    test_unauthorized_access(result)
    
    # Print summary and exit
    success = result.print_summary()
    exit(0 if success else 1)


if __name__ == "__main__":
    main()
