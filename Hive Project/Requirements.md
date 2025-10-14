# Functional Requirements

## 1) User Management & Authentication

### UR-1 User Registration: 
The system shall allow users to register for an account using a valid email address and a secure password.

### UR-2 Email Verification: 
The system shall send a verification link to the user's email upon registration, which must be clicked to activate the account.

### UR-3 User Authentication: 
A verified user shall be able to log in to the system using their email and password.

### UR-4 User Roles & Permissions: 
The system shall support distinct user roles with different permission levels, beginning with "Admin" and "User" roles. The administrative interface shall change dynamically based on the logged-in user's role.

## 2) Service Map ("Offer" & "Need" Management)

### SM-1 Service Creation: 
A logged-in user shall be able to create "Offers" (as a Provider) and "Needs" (as a Consumer).

### SM-2 Service Attributes: 
Each "Offer" or "Need" must include:
<br>2.1 One or more semantic tags.
<br>2.2 A value in hours (minimum 1 hour).
<br>2.3 Specification of whether the service is online or in-person.
<br>2.4 An expiration date.

### SM-3 Service Lifecycle Management: 
A Provider shall be able to update and delete their own "Offers." A Consumer can set an expiration date for a "Need," after which it becomes passive.

### SM-4 Map View: 
The system shall display "Offers" and "Needs" on a map, which defaults to centering on the user's neighborhood.

### SM-5 Search and Filtering: 
Users shall be able to search and filter "Offers" and "Needs" by semantic tags, dates, and value in hours.

### SM-6 Provider Application: 
A Provider shall be able to view "Needs" and submit an application to fulfill one.

### SM-7 Application Review & Acceptance:
7.1 For a "Need": The Consumer shall be able to review all applications from Providers and select one to accept.
<br>7.2 For an "Offer": The Provider shall be able to review Consumers who have accepted the offer and approve one to initiate the exchange.

### SM-8 Status Flow: 
Every service exchange shall follow a clear, visible step-by-step status flow ( Open -> Provider Selected -> In Progress -> Awaiting Confirmation -> Completed).

### SM-9 Automated Private Messaging: 
Upon mutual acceptance (Consumer selects Provider for a "Need" or Provider approves Consumer for an "Offer"), the system shall automatically create a private messaging channel between the two parties to coordinate details.

### SM-10 Mutual Evaluation: 
After a service is completed, the Consumer shall be able to evaluate the Provider, and the Provider shall be able to evaluate the Consumer.

### SM-11 Provider Survey: 
After completing a "Need," the Provider shall be prompted to fill out a survey regarding the task's difficulty, its relevance to the original description, and the accuracy of the time estimate.

## 3) TimeBank Currency System

### TCS-1 Initial Balance: 
Upon successful registration and verification, a new user's account shall be credited with one time unit (1 hour).

### TCS-2 Balance Display: 
Users shall be able to view their current TimeBank balance in their profile and on their main dashboard.

### TCS-3 Hour Reservation: 
When a Consumer creates a "Need," the specified number of hours shall be reserved (locked) from their balance. If the "Need" expires, the reserved hours shall be unlocked.

### TCS-4 Balance Cap: 
A user's TimeBank balance cannot exceed 10 hours. To earn more, they must first spend hours by creating and completing a "Need."

### TCS-5 Completion Confirmation & Transfer:
5.1 The Provider marks the service as finished.
<br>5.2 The Consumer receives a notification and must confirm completion.
<br>5.3 The Provider must also approve the completion.
<br>5.4 Upon mutual approval, the reserved hours are transferred from the Consumer's balance to the Provider's balance.

### TCS-6 Transaction Invariance: 
The number of people involved in a task shall not affect the amount of hours exchanged.

## 4) Semantic Tag System

### STS-1 Tag Association: 
Users shall be able to select one or more existing semantic tags from a searchable list to label their "Offers" and "Needs."

### STS-2 User-Generated Tags: 
If a desired tag does not exist, a user shall be able to suggest or create a new one.

### STS-3 Admin Tag Management: 
An Admin shall be able to add, edit, and delete semantic tags, as well as view and approve user-suggested tags.

## 5) Community Forums

### CF-1 Active Threads View: 
Users shall be able to view a global list of the most recently active threads in the community forum.

## 6) Administration & Moderation

### AM-1 Admin Dashboard Views: 
Admins shall have access to dashboards to view lists of all users, "Offers" (active and passive), "Needs" (active and passive), evaluations, and reported content.

### AM-2 Content Moderation: 
Admins shall be able to deactivate any "Offer" or "Need," providing a reason to the user.

### AM-3 User Moderation: 
3.1 Admins shall be able to issue a formal warning to a user with a clear reason. 
<br>3.2 Following a warning, an Admin can ban the user.

### AM-4 Illegal Content Takedown: 
Admins shall be able to immediately delete any content reported as illegal and flag the user who posted it for further review.

# Non-Functional Requirements (NFR)

## Security
### NFR-1.1 Data Protection: 
The system must protect all private user data. Passwords must be securely hashed before being stored in the database. All sensitive data must be encrypted in transit.

### NFR-1.2 Secure Transactions: 
The TimeBank system must be designed to securely track, reserve, and transfer hours, preventing unauthorized manipulation or loss of balances.

## Reliability
### NFR-2.1 Data Integrity: 
All data must be saved and retrieved correctly without loss or corruption.

### NFR-2.2 Testing: 
All core operations and features of the system must be thoroughly tested to ensure they function as expected.

## Maintainability
### NFR-3 Extensibility: 
The system's codebase and architecture shall be designed in a modular way to allow for the addition of future features without requiring a complete rebuild.

## Business Rules & Policies
### NFR-4 Dispute Resolution: 
If a Consumer does not confirm or deny completion within 48 hours after a Provider has marked the task as complete, the system shall auto-confirm the service and transfer the hours. However, either party shall have the ability to flag the transaction for administrative review after the auto-confirmation.

***

