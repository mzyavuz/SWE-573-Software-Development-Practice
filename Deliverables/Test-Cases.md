# Test Cases
## The Hive - Community TimeBank Platform

**Version:** 1.0  
**Date:** December 18, 2025  
**Author:** M. Zeynep Çakmakcı  
**Project:** SWE 573 - Software Development Practice

---

## Table of Contents
1. [Introduction](#1-introduction)
2. [Test Case Organization](#2-test-case-organization)
3. [Scenario-Based Tests](#3-scenario-based-tests)
4. [API Unit Tests](#4-api-unit-tests)
5. [Test Execution Guide](#5-test-execution-guide)
6. [Test Data Requirements](#6-test-data-requirements)

---

## 1. Introduction

### 1.1 Purpose
This document catalogs all test cases for The Hive application. Test cases are organized into two categories:
1. **Scenario-Based Tests**: End-to-end user journey tests based on real-world scenarios
2. **API Unit Tests**: Focused tests for specific API endpoints and edge cases

### 1.2 Test Framework
- **Language**: Python 3.10+
- **Testing Framework**: pytest (for unit tests) and custom test scripts (for scenario tests)
- **HTTP Client**: requests library
- **Location**: `/the-hive/backend/tests/`

### 1.3 Test Structure
```
tests/
├── scenario_tests/          # End-to-end scenario tests
│   ├── test_scenario_1.py   # User registration and onboarding
│   ├── test_scenario_2.py   # Service offer creation
│   ├── test_scenario_3.py   # Service discovery and application
│   ├── test_scenario_4.py   # Schedule proposal workflow
│   └── test_scenario_5.py   # Service completion and credit transfer
├── api_tests/               # Unit tests for specific API endpoints
│   ├── registration_tests.py
│   ├── service_creation_tests.py
│   ├── service_workflow_tests.py
│   ├── service_progress_tests.py
│   └── proposal_balance_tests.py
└── test_wikibase_search.py  # External API integration tests
```

---

## 2. Test Case Organization

### 2.1 Test Case Identification
Test cases are identified using the following format:
- **Scenario Tests**: `TC-S{scenario_number}-{test_number}`
- **API Tests**: `TC-API-{feature}-{test_number}`

### 2.2 Test Priority Levels
- **P0 (Critical)**: Core functionality, must pass for release
- **P1 (High)**: Important features, should pass for release
- **P2 (Medium)**: Secondary features, nice to have
- **P3 (Low)**: Edge cases and enhancements

### 2.3 Test Status
- ✅ **Pass**: Test executed successfully, all assertions passed
- ❌ **Fail**: Test failed, defect identified
- ⚠️ **Blocked**: Test cannot be executed due to dependency
- ⏭️ **Skipped**: Test intentionally not executed
- 🔄 **In Progress**: Test execution ongoing

---

## 3. Scenario-Based Tests

### 3.1 Test Scenario 1: User Registration and Onboarding

**File**: `test_scenario_1.py`  
**User Story**: Alex Chen (The Curious Newcomer) wants to sign up, verify email, and see initial balance  
**Priority**: P0 (Critical)

#### 3.1.1 Test Cases

| Test ID | Test Name | Description | Expected Result | Priority |
|---------|-----------|-------------|-----------------|----------|
| TC-S1-01 | User Registration with Valid Data | Test successful user registration with all required fields | Account created, verification email sent | P0 |
| TC-S1-02 | Email Verification | Test email verification link activation | Account activated, can login | P0 |
| TC-S1-03 | User Login | Test authentication with correct credentials | JWT token received, session created | P0 |
| TC-S1-04 | Initial Balance Display | Test initial time credit balance after first login | Dashboard shows 1 hour balance | P0 |

#### 3.1.2 Acceptance Criteria
- ✅ Account creation succeeds with valid input and sends verification email
- ✅ Clicking verification link sets account to active and allows authentication
- ✅ After first login, dashboard displays initial 1-hour time-credit balance
- ✅ Invalid data is rejected with appropriate error messages

#### 3.1.3 Test Steps

**TC-S1-01: User Registration**
1. POST `/api/auth/register` with valid user data
2. Verify response status is 201 Created
3. Verify response contains verification_token
4. Verify user record created in database with is_verified=False
5. Verify email sent (mock verification)

**TC-S1-02: Email Verification**
1. GET `/api/auth/verify-email?token={verification_token}`
2. Verify response status is 200 OK
3. Verify user is_verified changed to True
4. Verify account is_active changed to True

**TC-S1-03: User Login**
1. POST `/api/auth/login` with email and password
2. Verify response status is 200 OK
3. Verify JWT access_token is returned
4. Verify token can be used for authenticated requests

**TC-S1-04: Initial Balance Display**
1. GET `/api/timebank/balance` with valid token
2. Verify response status is 200 OK
3. Verify balance equals 1.0
4. Verify balance displayed on dashboard

---

### 3.2 Test Scenario 2: Service Offer Creation

**File**: `test_scenario_2.py`  
**User Story**: Austin posts a guitar lesson offering with tags and availability  
**Priority**: P0 (Critical)

#### 3.2.1 Test Cases

| Test ID | Test Name | Description | Expected Result | Priority |
|---------|-----------|-------------|-----------------|----------|
| TC-S2-01 | Create Service Offer | Test creating a service offer with all details | Offer created successfully | P0 |
| TC-S2-02 | Tag Association | Test attaching existing and new tags to service | Tags properly linked to service | P0 |
| TC-S2-03 | Service Visibility | Test offer appears in public listings | Offer visible on map and list view | P0 |
| TC-S2-04 | Input Validation | Test validation for required fields | Errors returned for invalid data | P1 |

#### 3.2.2 Test Steps

**TC-S2-01: Create Service Offer**
1. Authenticate as Austin (provider)
2. POST `/api/services` with offer data (title, description, hours, location_type, location_address)
3. Verify response status is 201 Created
4. Verify service_id returned
5. Verify service record in database with correct data

**TC-S2-02: Tag Association**
1. Get or create tags (e.g., "guitar", "tutoring")
2. POST tag IDs to service
3. Verify tags associated with service in database
4. GET `/api/services/{service_id}/tags` and verify tags returned

**TC-S2-03: Service Visibility**
1. GET `/api/services` (public listing)
2. Verify newly created offer is present
3. Verify offer has correct status="open"
4. Verify offer appears on map with location

---

### 3.3 Test Scenario 3: Service Discovery and Application

**File**: `test_scenario_3.py`  
**User Story**: Provider discovers a Need and applies to fulfill it  
**Priority**: P0 (Critical)

#### 3.3.1 Test Cases

| Test ID | Test Name | Description | Expected Result | Priority |
|---------|-----------|-------------|-----------------|----------|
| TC-S3-01 | Service Search by Tags | Test filtering services by semantic tags | Relevant services returned | P0 |
| TC-S3-02 | Service Search by Location | Test filtering services by distance | Services within radius returned | P1 |
| TC-S3-03 | Submit Application | Test provider applying to a Need | Application created successfully | P0 |
| TC-S3-04 | Application Notification | Test consumer receives notification | Consumer notified of new application | P1 |
| TC-S3-05 | Duplicate Application Prevention | Test provider cannot apply twice | Error returned for duplicate application | P1 |

#### 3.3.2 Test Steps

**TC-S3-01: Service Search by Tags**
1. GET `/api/services?tags=sewing` with authentication
2. Verify response status is 200 OK
3. Verify all returned services have "sewing" tag
4. Verify service_type="need" filtered correctly

**TC-S3-03: Submit Application**
1. Authenticate as provider
2. POST `/api/services/{service_id}/apply` with optional message
3. Verify response status is 201 Created
4. Verify application record created with status="pending"
5. Verify consumer_id matches Need owner

---

### 3.4 Test Scenario 4: Schedule Proposal Workflow

**File**: `test_scenario_4.py`  
**User Story**: Provider and Consumer negotiate service schedule  
**Priority**: P0 (Critical)

#### 3.4.1 Test Cases

| Test ID | Test Name | Description | Expected Result | Priority |
|---------|-----------|-------------|-----------------|----------|
| TC-S4-01 | Create Schedule Proposal | Test creating a schedule proposal | Proposal created successfully | P0 |
| TC-S4-02 | Balance Validation on Accept | Test balance check when accepting proposal | Validation performed correctly | P0 |
| TC-S4-03 | Accept Valid Proposal | Test accepting proposal with sufficient balance | Schedule confirmed | P0 |
| TC-S4-04 | Reject Insufficient Balance | Test rejection when consumer has low balance | Acceptance blocked with error | P0 |
| TC-S4-05 | Reject Exceeding Max Balance | Test rejection when provider would exceed cap | Acceptance blocked with error | P0 |
| TC-S4-06 | Schedule Confirmation | Test both parties confirming schedule | Service status updated to "scheduled" | P0 |

#### 3.4.2 Test Steps

**TC-S4-01: Create Schedule Proposal**
1. Authenticate as either provider or consumer
2. POST `/api/services/{service_id}/propose_schedule` with date, time, location
3. Verify response status is 201 Created
4. Verify proposal stored in ServiceProgress table
5. Verify other party notified

**TC-S4-02: Balance Validation on Accept**
1. GET consumer's current balance
2. Verify consumer balance >= service hours_required
3. GET provider's current balance
4. Verify provider balance + hours_required <= 10
5. If validation fails, return error with explanation

**TC-S4-03: Accept Valid Proposal**
1. Consumer has 3 hours, Need requires 2 hours → VALID
2. Provider has 8 hours, will receive 2 hours → VALID
3. POST `/api/services/{service_id}/accept_schedule`
4. Verify response status is 200 OK
5. Verify schedule_accepted flags updated

---

### 3.5 Test Scenario 5: Service Completion and Credit Transfer

**File**: `test_scenario_5.py`  
**User Story**: Service is completed and time credits are transferred  
**Priority**: P0 (Critical)

#### 3.5.1 Test Cases

| Test ID | Test Name | Description | Expected Result | Priority |
|---------|-----------|-------------|-----------------|----------|
| TC-S5-01 | Dual Start Confirmation | Test both parties confirming service start | Status changed to "in_progress" | P0 |
| TC-S5-02 | Provider Marks Complete | Test provider marking service as finished | Status changed to "awaiting_confirmation" | P0 |
| TC-S5-03 | Consumer Confirms Completion | Test consumer confirming service done | Status changed to "completed" | P0 |
| TC-S5-04 | Hour Transfer | Test time credits transferred correctly | Credits deducted from consumer, added to provider | P0 |
| TC-S5-05 | Balance Cap Enforcement | Test 10-hour maximum balance enforced | Excess hours not transferred if cap exceeded | P0 |
| TC-S5-06 | Survey Submission | Test post-service survey completion | Surveys stored correctly | P1 |
| TC-S5-07 | Auto-Confirmation (48 hours) | Test automatic completion after timeout | Service auto-confirmed and credits transferred | P1 |

#### 3.5.2 Test Steps

**TC-S5-01: Dual Start Confirmation**
1. POST `/api/services/{service_id}/confirm_start` as provider
2. Verify provider_start_confirmed = True
3. POST `/api/services/{service_id}/confirm_start` as consumer
4. Verify consumer_start_confirmed = True
5. Verify status changed to "in_progress"

**TC-S5-04: Hour Transfer**
1. Get consumer balance before = X hours
2. Get provider balance before = Y hours
3. Service requires Z hours
4. POST completion confirmations from both parties
5. Verify consumer balance after = X - Z
6. Verify provider balance after = Y + Z (if Y + Z <= 10)
7. Verify transaction recorded

**TC-S5-05: Balance Cap Enforcement**
1. Set provider balance to 9 hours
2. Complete service worth 3 hours
3. Verify provider balance after = 10 hours (capped)
4. Verify excess 2 hours not transferred
5. Verify consumer still charged full 3 hours

---

## 4. API Unit Tests

### 4.1 Registration API Tests

**File**: `registration_tests.py`  
**Framework**: pytest

#### 4.1.1 Test Cases

| Test ID | Test Name | Description | Expected Result | Priority |
|---------|-----------|-------------|-----------------|----------|
| TC-API-REG-01 | Registration Without Email | Test registration fails when email missing | 400 error returned | P1 |
| TC-API-REG-02 | Registration With Weak Password | Test registration fails with weak password | 400 error returned | P1 |
| TC-API-REG-03 | Registration With Invalid Email | Test registration fails with invalid email format | 400 error returned | P1 |
| TC-API-REG-04 | Duplicate Email Registration | Test registration fails with existing email | 409 error returned | P1 |

#### 4.1.2 Example Test Case

```python
def test_registration_without_email():
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
```

---

### 4.2 Service Creation Tests

**File**: `service_creation_tests.py`  
**Framework**: pytest

#### 4.2.1 Test Cases

| Test ID | Test Name | Description | Expected Result | Priority |
|---------|-----------|-------------|-----------------|----------|
| TC-API-SVC-01 | Create Service Without Auth | Test service creation requires authentication | 401 error returned | P0 |
| TC-API-SVC-02 | Create Service With Missing Fields | Test validation for required fields | 400 error returned | P1 |
| TC-API-SVC-03 | Create Service With Invalid Hours | Test hours must be between 1-3 | 400 error returned | P1 |
| TC-API-SVC-04 | Update Own Service | Test user can update their own service | 200 success returned | P1 |
| TC-API-SVC-05 | Update Others' Service | Test user cannot update others' services | 403 error returned | P1 |

---

### 4.3 Proposal Balance Tests

**File**: `proposal_balance_tests.py`  
**Framework**: pytest

#### 4.3.1 Test Cases

| Test ID | Test Name | Description | Expected Result | Priority |
|---------|-----------|-------------|-----------------|----------|
| TC-API-BAL-01 | Consumer Insufficient Balance | Test proposal rejected when consumer has < required hours | 400 error with explanation | P0 |
| TC-API-BAL-02 | Provider Exceeding Max Balance | Test proposal rejected when provider would exceed 10 hours | 400 error with explanation | P0 |
| TC-API-BAL-03 | Valid Balance Acceptance | Test proposal accepted when both balances valid | 200 success, schedule confirmed | P0 |
| TC-API-BAL-04 | Balance Check Before Acceptance | Test balance validated before confirming | Validation performed correctly | P0 |

#### 4.3.2 Example Test Case

```python
def test_consumer_insufficient_balance():
    """Test that proposal is rejected when consumer has insufficient balance"""
    # Setup: Consumer with 0 hours, Need requires 2 hours
    consumer_token = setup_consumer_with_balance(0)
    service_id = create_need_requiring_hours(2, consumer_token)
    
    # Provider proposes schedule
    provider_token = setup_provider()
    proposal_response = propose_schedule(service_id, provider_token, date="2025-12-20", time="14:00")
    
    # Consumer tries to accept
    accept_response = requests.post(
        f"{BASE_URL}/services/{service_id}/accept_schedule",
        headers={"Authorization": f"Bearer {consumer_token}"}
    )
    
    assert accept_response.status_code == 400
    assert "insufficient balance" in accept_response.json()['error'].lower()
```

---

### 4.4 Service Workflow Tests

**File**: `service_workflow_tests.py`  
**Framework**: pytest

#### 4.4.1 Test Cases

| Test ID | Test Name | Description | Expected Result | Priority |
|---------|-----------|-------------|-----------------|----------|
| TC-API-WRK-01 | Application Workflow | Test complete application process | Application created and managed | P0 |
| TC-API-WRK-02 | Service Status Transitions | Test valid status transitions | Status updated correctly | P0 |
| TC-API-WRK-03 | Invalid Status Transition | Test invalid transitions blocked | Error returned | P1 |
| TC-API-WRK-04 | Concurrent Applications | Test multiple providers can apply | All applications recorded | P1 |

---

### 4.5 Service Progress Tests

**File**: `service_progress_tests.py`  
**Framework**: pytest

#### 4.5.1 Test Cases

| Test ID | Test Name | Description | Expected Result | Priority |
|---------|-----------|-------------|-----------------|----------|
| TC-API-PRG-01 | Progress Creation on Selection | Test progress record created when provider selected | ServiceProgress entry created | P0 |
| TC-API-PRG-02 | Start Confirmation Tracking | Test both confirmations required | Both flags must be true | P0 |
| TC-API-PRG-03 | Completion Confirmation Tracking | Test both completions required | Both flags must be true | P0 |
| TC-API-PRG-04 | Survey Data Storage | Test survey responses stored | JSON data saved correctly | P1 |

---

### 4.6 Wikibase Integration Tests

**File**: `test_wikibase_search.py`

#### 4.6.1 Test Cases

| Test ID | Test Name | Description | Expected Result | Priority |
|---------|-----------|-------------|-----------------|----------|
| TC-API-WIKI-01 | Tag Search Integration | Test Wikibase entity search | Related entities returned | P2 |
| TC-API-WIKI-02 | Fallback on Failure | Test graceful degradation if Wikibase unavailable | Local tags still work | P2 |

---

## 5. Test Execution Guide

### 5.1 Prerequisites
1. Application running at `http://localhost:5001`
2. Database accessible and initialized
3. Python 3.10+ with required packages installed

### 5.2 Running Scenario Tests

```bash
# Navigate to test directory
cd the-hive/backend/tests/scenario_tests

# Run individual scenario
python3 test_scenario_1.py
python3 test_scenario_2.py
python3 test_scenario_3.py
python3 test_scenario_4.py
python3 test_scenario_5.py
```

### 5.3 Running API Tests with pytest

```bash
# Navigate to test directory
cd the-hive/backend/tests

# Run all API tests
pytest api_tests/ -v

# Run specific test file
pytest api_tests/registration_tests.py -v

# Run specific test
pytest api_tests/registration_tests.py::TestRegistration::test_registration_without_email -v

# Run with coverage
pytest api_tests/ --cov=app --cov-report=html
```

### 5.4 Test Output

Scenario tests provide colored console output:
- ✅ Green checkmark: Test passed
- ❌ Red X: Test failed
- Summary shows passed/failed count

pytest tests provide:
- Detailed assertion failures
- Test execution time
- Coverage reports

---

## 6. Test Data Requirements

### 6.1 User Test Data

| User Role | Email Pattern | Password | Balance | Purpose |
|-----------|---------------|----------|---------|---------|
| New User | `alex.chen.{timestamp}@gmail.com` | SecurePass123! | 1.0 (initial) | Registration testing |
| Consumer Low Balance | `consumer.lowbalance@hive.com` | Consumer123! | 0.0 | Insufficient balance tests |
| Provider High Balance | `provider.highbalance@hive.com` | Provider123! | 9.5 | Max balance cap tests |
| Regular Provider | `provider.{timestamp}@hive.com` | Provider123! | 5.0 | Normal workflow tests |
| Regular Consumer | `consumer.{timestamp}@hive.com` | Consumer123! | 5.0 | Normal workflow tests |

### 6.2 Service Test Data

| Service Type | Title | Hours | Location Type | Purpose |
|--------------|-------|-------|---------------|---------|
| Offer | "Guitar Lessons - Beginner to Intermediate" | 1.0 | in-person | Service creation tests |
| Need | "Help with Moving Furniture" | 3.0 | in-person | Application workflow tests |
| Need | "Website Design Assistance" | 2.0 | online | Remote service tests |
| Offer | "Math Tutoring for High School" | 1.5 | both | Flexible location tests |

### 6.3 Tag Test Data
- "guitar", "tutoring", "music", "teaching"
- "moving", "physical-help", "transportation"
- "web-design", "technology", "programming"
- "sewing", "repair", "clothing"

---

## 7. Test Coverage Summary

### 7.1 Feature Coverage

| Feature | Scenario Tests | API Tests | Coverage |
|---------|----------------|-----------|----------|
| User Registration & Auth | ✅ S1 | ✅ registration_tests | High |
| Service Creation | ✅ S2 | ✅ service_creation_tests | High |
| Service Discovery | ✅ S3 | ⚠️ Partial | Medium |
| Application Workflow | ✅ S3 | ✅ service_workflow_tests | High |
| Schedule Proposal | ✅ S4 | ✅ proposal_balance_tests | High |
| Service Completion | ✅ S5 | ✅ service_progress_tests | High |
| TimeBank System | ✅ S1, S5 | ✅ proposal_balance_tests | High |
| Balance Validation | ✅ S4, S5 | ✅ proposal_balance_tests | High |
| Messaging | ⚠️ Partial | ❌ Not tested | Low |
| Rating System | ⚠️ Partial | ❌ Not tested | Low |
| Forum | ❌ Not tested | ❌ Not tested | None |
| Admin Panel | ❌ Not tested | ❌ Not tested | None |

### 7.2 Testing Metrics
- **Total Scenario Test Cases**: 5 comprehensive scenarios
- **Total API Test Cases**: ~25+ unit tests
- **Estimated Test Coverage**: ~80% for core features
- **Critical Path Coverage**: 95%+

---

**End of Test Cases Document**
