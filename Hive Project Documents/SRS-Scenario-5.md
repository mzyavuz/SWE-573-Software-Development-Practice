# Software Requirements Specification (SRS)
## Scenario 5: Alex Completes a Moving-Help Request

### 1. Introduction

#### 1.1 Purpose
This document specifies the software requirements for implementing Scenario 5 of The Hive time-banking platform, where a provider (Alex Chen) completes a moving-help service request and the system handles time currency transfers, balance updates, and post-service surveys.

#### 1.2 Scope
This scenario covers the complete workflow from service acceptance through completion, including:
- Service completion confirmation
- Time currency transfer with balance cap enforcement

#### 1.3 Definitions and Acronyms
- **Provider**: User offering/providing a service (Alex in this scenario)
- **Consumer**: User requesting/consuming a service
- **Time Credits**: Hours earned or spent on the platform
- **Balance Cap**: Maximum time currency balance a user can hold (10 hours)
- **THS**: Time HourBank System

### 2. Overall Description

#### 2.1 Product Perspective
This functionality is part of The Hive time-banking platform's core service completion workflow. It integrates with:
- User authentication system
- Service management system
- Time currency accounting system
- Survey/feedback system

#### 2.2 User Characteristics
**Primary Actor**: Alex Chen (The Curious Newcomer)
- 28-year-old freelance graphic designer
- Tech-savvy
- New to the neighborhood
- Providing moving-help service

**Secondary Actor**: Service Consumer (Need Owner)
- User who posted the moving-help need
- Has sufficient time credit balance to pay for service

#### 2.3 Assumptions and Dependencies
- User authentication is already implemented
- Service application and acceptance workflow exists
- Database supports atomic transactions
- Users have verified email addresses

### 3. Functional Requirements

#### 3.1 Time Credit Reservation (TCS-3)

**FR-1: Reserve Hours Upon Acceptance**
- **Description**: When Alex is accepted for the moving-help service, the system must reserve the agreed hours from the consumer's balance
- **Input**: 
  - Service ID
  - Provider ID (Alex)
  - Consumer ID
  - Hours required (1.0 - 3.0 hours)
- **Process**:
  1. Validate consumer has sufficient balance
  2. Validate provider's balance won't exceed cap after transfer
  3. Reserve hours from consumer's balance
  4. Update service status to "accepted" or "scheduled"
  5. Create service_progress record
- **Output**: 
  - Updated consumer balance (reserved hours)
  - Service progress record created
  - Notifications sent to both parties
- **Error Handling**:
  - If consumer has insufficient balance: reject acceptance, notify both parties
  - If provider balance would exceed cap: notify and handle according to policy

#### 3.2 Service Completion (TCS-5)

**FR-2: Dual Confirmation of Service Completion**
- **Description**: Both Alex (provider) and the consumer must confirm the service is completed before time credits transfer
- **Input**:
  - Service progress ID
  - User ID (provider or consumer)
  - Confirmation status
- **Process**:
  1. Record confirmation from user
  2. Check if both parties have confirmed
  3. If both confirmed, trigger time credit transfer
  4. Update service status to "completed"
  5. Trigger post-service surveys
- **Output**:
  - Updated service_progress record with confirmation timestamps
  - Time credits transferred (if both confirmed)
  - Survey requests sent
- **Business Rules**:
  - Service cannot be marked complete until both parties confirm
  - Confirmation deadline: 48 hours after scheduled end time
  - After deadline, escalation to admin review

#### 3.3 Time Credit Transfer with Cap Enforcement (TCS-4)

**FR-3: Transfer Credits with Balance Cap**
- **Description**: Transfer time credits from consumer to provider, enforcing the maximum balance cap
- **Input**:
  - Service progress ID
  - Hours to transfer
  - Provider current balance
  - Consumer current balance
- **Process**:
  1. Calculate provider's new balance: current + hours
  2. If new balance ≤ 10 hours: transfer full amount
  3. If new balance > 10 hours:
     - Transfer amount = (10 - current balance)
     - Excess = hours - transfer amount
     - Log excess for policy handling
  4. Deduct hours from consumer's reserved amount
  5. Add transferred hours to provider's balance
  6. Update service_progress status to "completed"
  7. Record transaction in audit log
- **Output**:
  - Updated provider balance
  - Updated consumer balance
  - Transaction record
  - Notification to both users with final balances
- **Balance Cap Policy**:
  - Maximum balance: 10.0 hours
  - Excess credits: Logged and returned to consumer
  - Clear messaging to provider about capped amount

#### 3.4 Post-Service Survey (SM-11)

**FR-4: Provider Survey Collection**
- **Description**: Alex receives a survey about the consumer and the task after confirming completion
- **Input**:
  - Service progress ID
  - Provider ID
- **Process**:
  1. Display survey to provider after confirmation
  2. Validate all required fields
  3. Store survey responses in service_progress table (provider_survey_data JSONB)
  4. Mark provider_survey_submitted = TRUE
  5. Set provider_survey_submitted_at timestamp
- **Output**:
  - Survey data stored
  - Confirmation message
  - Updated service_progress record
- **Business Rules**:
  - Survey is optional but encouraged (not available at that point)
  - Responses are private (only visible to admin for dispute resolution)

#### 3.5 Balance Display Update (TCS-2)

**FR-5: Real-Time Balance Display**
- **Description**: Alex's profile and dashboard must display updated time credit balance immediately after transfer
- **Input**:
  - User ID (Alex)
- **Display Elements**:
  - Current balance (hours with 1 decimal place)
  - Recent transactions (last 5)
  - Balance change indicator (+/- hours)
  - Warning if balance is low (< 1 hour)
  - Notification if balance was capped
- **Process**:
  1. Query user's current balance from database
  2. Query recent transactions
  3. Calculate balance trend
  4. Display with visual indicators
- **Output**:
  - Updated balance display on profile page
  - Updated balance in navigation bar
  - Transaction history with details

### 4. Non-Functional Requirements

#### 4.1 Performance
- **NFR-1**: Time credit transfer must complete within 2 seconds
- **NFR-2**: Balance updates must be atomic (all-or-nothing)
- **NFR-3**: Survey submission must respond within 1 second

#### 4.2 Reliability
- **NFR-4**: System must prevent double-spending of time credits
- **NFR-5**: All balance changes must be logged for audit
- **NFR-6**: Transaction failures must rollback completely

#### 4.3 Security
- **NFR-7**: Only authenticated users can access their own balance
- **NFR-8**: Time credit transfers require dual confirmation
- **NFR-9**: Survey responses are encrypted in database

#### 4.4 Usability
- **NFR-10**: Balance display must be visible on every page (nav bar)
- **NFR-11**: Survey should be mobile-friendly
- **NFR-12**: Confirmation buttons must have clear labels and confirmation dialogs

### 5. System Features

#### 5.1 Service Progress Tracking
**Description**: Track the lifecycle of a service from acceptance to completion

**Transitions**:
- Consumer accepts provider → `selected`
- Both agree on schedule → `scheduled`
- Service start time reached → `in_progress`
- Provider confirms completion → `awaiting_confirmation`
- Both confirm completion → `completed` (with credit transfer)

#### 5.2 Balance Management
**Description**: Manage user time credit balances with validation and caps

**Operations**:
- Reserve hours (consumer)
- Release reserved hours (cancellation)
- Transfer hours (provider ← consumer)
- Query current balance
- Query transaction history

**Constraints**:
- Minimum balance: 0.0 hours
- Maximum balance: 10.0 hours
- Initial balance: 1.0 hour
- Transfer amount: 1.0 - 3.0 hours per service

### 6. Data Requirements

#### 6.1 Database Schema

**service_progress table**:
```sql
- id (PK)
- service_id (FK → services)
- application_id (FK → service_applications)
- provider_id (FK → users) -- Alex
- consumer_id (FK → users)
- hours (decimal)
- status (enum: selected, scheduled, in_progress, awaiting_confirmation, completed, disputed, cancelled)
- provider_confirmed (boolean)
- consumer_confirmed (boolean)
- provider_start_confirmed (boolean)
- consumer_start_confirmed (boolean)
- provider_survey_submitted (boolean)
- consumer_survey_submitted (boolean)
- provider_survey_data (jsonb)
- consumer_survey_data (jsonb)
- survey_deadline (timestamp)
- completed_at (timestamp)
- created_at (timestamp)
- updated_at (timestamp)
```

**users table** (balance fields):
```sql
- id (PK)
- time_balance (decimal, default 1.0)
- (other user fields...)
```

#### 6.2 API Endpoints

**POST /api/progress/{progress_id}/confirm-completion**
- Confirm service completion by provider or consumer
- Request body: `{ "confirmed": true }`
- Response: Updated progress status, balance if both confirmed

**POST /api/progress/{progress_id}/survey**
- Submit post-service survey
- Request body: Survey responses JSON
- Response: Confirmation message

**GET /api/auth/profile**
- Get current user profile including balance
- Response: User data with current time_balance

**GET /api/users/{user_id}/transactions**
- Get transaction history
- Response: List of time credit transactions

### 7. User Interface Requirements

#### 7.1 Progress Status Page (Provider View)
**Components**:
- Service details (title, description, hours, date/time)
- Consumer information (name, profile photo)
- Status indicator with progress bar
- Confirm completion button (when service is done)
- Survey form (after confirmation)
- Cancel service button (if before start time)

**Actions**:
- Click "Confirm Completion" → Show confirmation dialog → Submit confirmation
- Fill survey → Submit → Show success message

#### 7.2 Balance Display (Profile Page)
**Components**:
- Large balance number (e.g., "2 hours")
- Recent transactions list
  - Date, type (earned/spent), amount, service title
- Balance trend indicator
- Warning messages (low balance, capped amount)

### 8. Acceptance Criteria

#### Test Case 1: Successful Service Completion
**Given**: Alex is accepted for a 2-hour moving service, consumer has 3 hours balance, Alex has 8 hours balance
**When**: Both parties confirm completion
**Then**: 
- Consumer balance: 3 - 2 = 1 hour
- Alex balance: 8 + 2 = 10 hours (at cap)
- Service status: completed
- Both receive survey requests
- Both receive completion notifications

#### Test Case 2: Balance Cap Enforcement
**Given**: Alex has 9 hours, accepts a 2-hour service
**When**: Both parties confirm completion
**Then**:
- Alex balance: 10 hours (capped)
- Excess 1 hour returned to consumer
- Alex receives notification about capped amount
- Consumer receives refund notification

#### Test Case 3: Single Confirmation
**Given**: Service is in progress
**When**: Only Alex confirms completion
**Then**:
- Service status: awaiting_confirmation
- Alex's confirmation recorded
- Consumer receives reminder notification
- No credit transfer occurs yet

#### Test Case 4: Survey Submission
**Given**: Alex confirmed completion and credits transferred
**When**: Alex submits survey with all fields filled
**Then**:
- Survey data saved to service_progress
- provider_survey_submitted set to TRUE
- Success message displayed
- Survey no longer shows on dashboard

#### Test Case 5: Insufficient Consumer Balance
**Given**: Consumer has 1.5 hours, tries to accept Alex for 2-hour service
**When**: Consumer attempts to accept
**Then**:
- Acceptance rejected
- Error message: "Insufficient time balance..."
- Service remains in "pending" status
- No reservation occurs

### 9. Error Handling

#### 9.1 Error Scenarios

**E-1: Consumer Insufficient Balance**
- Message: "Insufficient time balance. You have X hours, but this service requires Y hours. Please earn more hours before accepting."
- Action: Prevent acceptance, suggest earning opportunities

**E-2: Provider Balance Would Exceed Cap**
- Message: "Provider time balance would exceed maximum limit of 10 hours. This service would add X hours to their current Y hours."
- Action: Allow acceptance but cap transfer, notify both parties

**E-3: Confirmation Deadline Passed**
- Message: "Confirmation deadline has passed. This service requires admin review."
- Action: Escalate to admin, freeze status

**E-4: Network Failure During Transfer**
- Message: "Transfer in progress. Please wait..."
- Action: Retry transaction, rollback on failure, notify users of status

**E-5: Duplicate Confirmation Attempt**
- Message: "You have already confirmed this service."
- Action: Show current status, no database change

### 11. Glossary

- **Acceptance**: When a consumer chooses a provider for their service need
- **Confirmation**: User verification that service was completed satisfactorily
- **Reservation**: Holding time credits from consumer's balance pending service completion
- **Transfer**: Moving time credits from consumer to provider after mutual confirmation
- **Cap**: Maximum allowed time credit balance (10 hours)
- **Excess**: Credits beyond the cap that cannot be received
- **Survey**: Post-service feedback questionnaire

---
