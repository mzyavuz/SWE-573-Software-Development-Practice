# Software Requirements Specification (SRS)



**Project Title:** Hive - Community TimeBank Platform

**Version:** 3.0  

**Date:** December 15, 2025  

**Authors:** M.Zeynep Çakmakcı



---



## 1. Introduction



### 1.1 Purpose

This Software Requirements Specification (SRS) document provides a comprehensive description of the Hive platform, a community-based TimeBank system that facilitates skill and service exchanges using time as currency. This document is intended for:
- Project stakeholders (The neighbors, developer & instructor/guidance counselor) and product owners (Me)
- Future developers (For extra features)
- Academic instructor (Suzan Üskdarlı)


### 1.2 Scope

Hive is a web-based TimeBank platform that enables community members to exchange skills and services using time credits (hours) as the medium of exchange. The system allows users to:
- Create "Offers" (services they can provide) and "Needs" (services they require)
- Search and filter services using semantic tags, location, and availability
- Apply for and accept service exchanges
- Communicate through automated private messaging
- Track time credit balances and transactions
- Review service exchanges
- Participate in community forums

The platform includes:
- User authentication and profile management
- Map-based service discovery
- TimeBank currency system with transaction management
- Semantic tagging system for categorizing services
- Administrative dashboard for moderation and oversight
- Community forum for active discussions


### 1.3 Definitions, Acronyms, and Abbreviations

| Term | Definition |
|------|------------|
| **Neighbor** | Non-registered person on the platform. (Anonymous user)|
| **User**     | Any individual registered on the platform. |
| **Provider** | A user offering a service to fulfill someone's Need |
| **Consumer** | A user requesting a service by posting a Need |
| **Offer** | A service that a Provider is willing to provide to others |
| **Need** | A service that a Consumer requires from others |
| **Service** | The incorporative concept for an Offer or a Need. |
| **Service Map** | The interactive, filterable map at the heart of the platform where all active Offers and Needs are displayed.  |
| **TimeBank** | The platform's currency system where all exchanges are measured in hours of service. (Non-monetary value)|
| **Time Credit** | The currency unit in the TimeBank system, measured in hours |
| **Balance** | The number of TimeBank Hours a User currently has available. |
| **Schedule Proposal** | A proposed date and time for service delivery, which can be accepted only if both parties have sufficient balance and won't exceed the maximum balance cap. |
| **TimeBank Transaction** | A record of the transfer of TimeBank Hours from a Consumer to a Provider upon successful completion of a Need.|
| **Semantic Tag** | A categorical label used to describe and search for services |
| **Private Messaging** | A temporary, direct communication channel automatically created between a Provider and Consumer once a Need is accepted. |
| **Completion Confirmation** | The mandatory step where a Consumer verifies that a Need has been fulfilled satisfactorily.|
| **Evaluation** | Feedback provided by Consumer and Provider for theirself after a Need is completed.|
| **The Commons** | The community forums and discussion groups, representing the platform's shared social space.|
| **Forum Category** | A high-level section within The Commons (e.g., "Project Collaboration," "Storytelling Corner").|
| **Discussion Thread** | A conversation within a Forum Category, started by a single post.|
| **Post** | A single message within a Discussion Thread.|
| **Comment** | A respond for a post or thread |
| **Report** | A user-submitted notice flagging inappropriate content or behavior for admin review. |
| **Warning** | An admin-issued notice that a user's content or behavior violated rules. |
| **Ban** | Temporary or permanent removal of a user's access by an admin. |
| **SRS** | Software Requirements Specification |
| **FR** | Functional Requirement |
| **NFR** | Non-Functional Requirement |
| **Admin** | Administrator with elevated permissions for moderation |



### 1.4 References

- Hive Project Requirements Document (Requirements.md)
- Hive Project Use Cases (Use-Cases.md)
- Hive Project Scenarios (Scenarios.md)
- Hive Project Mockups (Mockups.md, mockups/ directory)



### 1.5 Overview

This document is organized into seven main sections:
- **Section 2** provides an overall description of the Hive platform, including product perspective, user classes, operating environment, and constraints.
- **Section 3** details system features and requirements using Agile user stories with acceptance criteria and functional requirements.
- **Section 4** specifies non-functional requirements including performance, security, usability, and reliability.
- **Section 5** references system models including use case diagrams.
- **Section 6** provides a glossary of additional terms.
- **Section 7** contains appendices with links to mockups and related artifacts.


---



## 2. Overall Description



### 2.1 Product Perspective

Hive is a standalone web-based platform that operates independently, though it may interface with:
- **Email Service Providers** for user verification and notifications
- **Mapping Services** (e.g., OpenStreetMap, Google Maps) for location-based service discovery
- **Database Systems** for persistent data storage (user accounts, services, transactions, messages)

The system architecture includes:
- Frontend web application (responsive design for desktop and mobile browsers)
- Backend API server handling business logic and data management
- Database layer for structured data storage

The platform is designed to be self-contained with the potential for future integration with calendar applications, file storage system for media assets, email notification system, or external community platforms.



### 2.2 Product Functions

The Hive platform provides the following high-level functions:

1. **User Management**: Registration, authentication, profile management, and role-based access control
2. **Service Management**: Creation, editing, deletion, and lifecycle management of Offers and Needs
3. **Discovery & Search**: Map-based visualization, filtering by tags/location/time, and text search
4. **Application & Matching**: Providers apply for Needs, Consumers review and select Providers
5. **Communication**: Automated private messaging between matched users
6. **TimeBank System**: Initial credits, balance tracking, hour reservation, and transaction processing
7. **Rating & Feedback**: Mutual evaluation after service completion and provider surveys
8. **Semantic Tagging**: User-generated and admin-managed tags for service categorization
9. **Community Forum**: Discussion threads for community engagement
10. **Administration**: User moderation, content management, dispute resolution, and reporting dashboards



### 2.3 User Classes and Characteristics



| User Role | Description | Technical Expertise | Typical Goals |
|------------|--------------|---------------------|----------------|
| **Guest User (Neighbor)** | Unregistered visitor browsing the platform | Low - Basic web browsing skills | View public service listings, understand platform features, register for an account |
| **Registered User (Consumer)** | Verified user posting service Needs | Low to Medium - Can create posts, use search filters, communicate via messaging | Request services, find reliable Providers, manage time credits, complete transactions |
| **Registered User (Provider)** | Verified user posting service Offers | Low to Medium - Can create detailed offers, respond to applications | Offer skills, earn time credits, build reputation, complete service exchanges |
> A user should be both Consumer and Provider.
| **Admin/Moderator** | Platform administrator with elevated permissions | Medium to High - Understands platform operations, content moderation, user management | Maintain platform integrity, moderate content, resolve disputes, manage tags, analyze platform metrics |


### 2.4 Operating Environment

**Client-Side Requirements:**
- **Browsers**: Modern web browsers
- **Devices**: Desktop computers, laptops, tablets, smartphones
- **Screen Resolution**: Responsive design supporting 320px(mobile) to 2560px(large screen) widths
- **Internet Connection**: Broadband or mobile data connection (minimum 3G)
- **JavaScript**: Must be enabled
- **Geolocation**: Optional but recommended for location-based features

**Server-Side Environment:**
- **Frontend**: HTML, CSS
- **Web Server**: Python backend
- **Database**: PostgreSQL for data persistence
- **Operating System**: Linux-based server environment

**Third-Party Services:**
- Mapping API (Google Maps)


### 2.5 Constraints

**Technical Constraints:**
- Must be accessible via standard web browsers
- Must support responsive design for various screen sizes
- Database design must efficiently handle concurrent transactions for the TimeBank system

**Legal & Regulatory Constraints:**
- Must comply with GDPR (KVKK if the location is Türkiye) for user data protection
- Must comply with local data privacy regulations
- Must have clear terms of service and privacy policy
- User-generated content must be moderatable to prevent illegal activities

**Operational Constraints:**
- Email verification required for account activation (dependent on email service availability)
- Map features dependent on third-party mapping service availability

**Business Constraints:**
- Must be maintainable by only one developer (myself)
- Academic timeline constraints for initial release 


### 2.6 Assumptions and Dependencies

**Assumptions:**
- Users have access to email for account verification
- Users are willing to enable location services for map-based discovery 
- Community members will act in good faith when exchanging services
- The time-based economy will naturally balance over time with appropriate incentives
- Users have basic digital literacy to navigate web applications

**Dependencies:**
- Email service provider uptime and deliverability
- Mapping service API availability and rate limits
- SSL certificate provider for secure connections
- Browser compatibility with modern web standards (ES6+, CSS3, HTML5)

---



## 3. System Features and Requirements



> Requirements are described using Agile user stories with acceptance criteria and detailed functional requirements.



### 3.1 Feature 1 – User Registration and Authentication



#### 3.1.1 Description

This feature enables new users to create accounts, verify their email addresses, and authenticate to access the platform. It provides secure account creation with email verification to ensure valid user identities and prevent spam accounts.



#### 3.1.2 User Story

> As a **new visitor**, I want to **register for an account using my email address, password, and date of birth** so that **I can access the TimeBank platform and start exchanging services**.


#### 3.1.3 Acceptance Criteria

- Given a new user on the registration page, when they submit a valid email, a secure password, and the required personal details (first name, surname, and birth date), then the system validates their age.
- Given a user clicks the verification link in their email, when the link is valid and not expired, then their account is activated.
- Given a verified user, when they log in with correct credentials, then they are authenticated and redirected to their dashboard.
- Given a user provides an already-registered email, when they attempt to register, then the system displays a clear error and offers password reset option.
- Given a user provides a weak password, when they attempt to register, then the system rejects it with helpful guidance on password requirements.
- Given a verification link expires, when a user clicks it, then the system allows resending a new verification email.




#### 3.1.4 Functional Requirements



| ID | Requirement | Priority | Notes |
|----|--------------|-----------|-------|
| FR-1.1 | The system shall allow users to register using a valid email address and secure password. | High | Password must meet minimum security requirements (8+ characters, mixed case, numbers) |
| FR-1.2 | The system shall require users to provide their date of birth during registration. | High | Used for age verification |
| FR-1.3 | The system shall send a verification email with a unique activation link upon registration. | High | Link should expire after 24 hours |
| FR-1.4 | The system shall activate the user account when they click the verification link. | High | |
| FR-1.5 | A verified user shall be able to log in using their email and password. | High | |
| FR-1.6 | The system shall display appropriate error messages for invalid credentials. | Medium | |
| FR-1.7 | The system shall prevent registration with duplicate email addresses. | High | |
| FR-1.8 | The system shall provide a password reset mechanism for forgotten passwords. | Medium | |
| FR-1.9 | The system shall allow users to resend verification emails if the initial one expires. | Medium | |



#### 3.1.5 Nonfunctional Requirements



| Type | Description | Priority |
|------|--------------|-----------|
| Security | Passwords must be hashed using bcrypt or similar before storage. | High |
| Security | Verification links must be cryptographically secure and single-use. | High |
| Security | Date of birth must be stored securely and used only for age verification. | High |
| Legal | The system must comply with age restrictions (minimum 16 years old). | High |
| Performance | Registration and login processes should complete within 2 seconds. | Medium |
| Usability | Error messages must be clear and guide users to resolution. | High |
| Usability | Age verification errors must be respectful and explain the policy. | Medium |
| Reliability | Email delivery must be tracked and retried on failure. | Medium |
| Privacy | Date of birth shall not be publicly visible on user profiles. | High |



---



### 3.2 Feature 2 – User Profile Management



#### 3.2.1 Description

This feature allows verified users to create and update their profiles with personal information, biography, and interest areas (semantic tags). A complete profile helps build trust within the community and provides context for service exchanges.



#### 3.2.2 User Story

> As a **registered user**, I want to **update my profile with personal details, biography and interest areas (semantic tags)** so that **other users can learn about me and feel confident in service exchanges**.



#### 3.2.3 Acceptance Criteria

- Given a logged-in user, when they access their profile page, then they can view and edit their name and surname, biography.. 
- Given a user saves profile changes, when the data is valid, then the changes are persisted and a confirmation message is displayed.
- Given invalid data (e.g., invalid phone format), when a user attempts to save, then appropriate validation errors are shown.
- Given a user views another user's profile, when the profile is public, then they see the user's name, biography, and reviews.



#### 3.2.4 Functional Requirements



| ID | Requirement | Priority | Notes |
|----|--------------|-----------|-------|
| FR-2.1 | Users shall be able to update their name and surname. | High | |
| FR-2.2 | Users shall be able to add or update their phone number. | Medium | Optional field with format validation |
| FR-2.3 | Users shall be able to write and edit a biography (up to 500 characters). | Medium | |
| FR-2.5 | The system shall display profile information on public user pages. | High | Private contact info excluded |
| FR-2.6 | Users shall be able to view their own complete profile including private details. | High | |
| FR-2.7 | The system shall validate phone number format before saving. | Medium | |



#### 3.2.5 Nonfunctional Requirements



| Type | Description | Priority |
|------|--------------|-----------|
| Performance | Profile updates should save within 2 seconds. | Medium |
| Usability | Profile editing interface should be intuitive with inline validation. | Medium |


---



### 3.3 Feature 3 – Create Service Offers



#### 3.3.1 Description

This feature enables users (as Providers) to create service "Offers" that describe skills or services they can provide to the community. Offers include details such as title, description, time estimate, location type (online/in-person), availability, and semantic tags for categorization.



#### 3.3.2 User Story

> As a **Provider**, I want to **create a service Offer with details about what I can provide** so that **Consumers can discover my skills and request my services in exchange for time credits**.



#### 3.3.3 Acceptance Criteria

- Given a logged-in user navigates to Create Offer, when they fill in all required fields (title, description, time estimate, location type), then the Offer is created successfully.
- Given a user adds semantic tags, when they search for existing tags or create new ones, then the tags are associated with the Offer.
- Given missing required fields, when a user attempts to publish, then validation errors prevent submission with clear guidance.
- Given a published Offer, when viewed by other users, then it appears in search results and on the services map.
- Given a Provider owns an Offer, when they access it, then they can edit/update, unpublish, or delete it.



#### 3.3.4 Functional Requirements



| ID | Requirement | Priority | Notes |
|----|--------------|-----------|-------|
| FR-3.1 | Providers shall be able to create a new Offer with title and description. | High | |
| FR-3.2 | Offers shall include an estimated time value in hours (minimum 1 hour). | High | |
| FR-3.3 | Providers shall specify if the service is online or in-person. | High | |
| FR-3.4 | Providers shall be able to add one or more semantic tags to categorize the Offer. | High | |
| FR-3.5 | Providers shall be able to set availability windows (days and hours). | Medium | |
| FR-3.6 | Providers shall be able to set an expiration date for their Offers. | Medium | Offer becomes passive after expiration |
| FR-3.7 | Providers shall be able to edit their own Offers. | High | |
| FR-3.8 | Providers shall be able to delete their own Offers. | High | Only if no active applications |
| FR-3.9 | Providers shall be able to unpublish (deactivate) Offers. | Medium | |
| FR-3.10 | The system shall validate all required fields before publishing an Offer. | High | |



#### 3.3.5 Nonfunctional Requirements



| Type | Description | Priority |
|------|--------------|-----------|
| Performance | Offer creation should complete(submit) within 2 seconds. | Medium |
| Usability | The create Offer form should guide users with clear labels and examples. | High |
| Scalability | System should handle thousands of active Offers efficiently. | Medium |



---



### 3.4 Feature 4 – Create Service Needs



#### 3.4.1 Description

This feature allows users (as Consumers) to post service "Needs" describing what assistance they require from the community. Similar to Offers, Needs include title, description, time estimate, location type, availability, and tags. Posting a Need initiates the service request workflow.



#### 3.4.2 User Story

> As a **Consumer**, I want to **post a service Need describing what help I require** so that **qualified Providers can apply to fulfill my request in exchange for time credits**.



#### 3.4.3 Acceptance Criteria

- Given a logged-in user, when they create a Need with all required fields, then the Need is published and visible to Providers.
- Given a user sets time estimate, when they publish the Need, then that amount is displayed as the expected time for the service.
- Given a Consumer posts a Need, when Providers search or browse, then the Need appears in results matching the tags and location.
- Given a Consumer has insufficient balance, when they attempt to post a Need requiring more hours than available, then the system prevents publication with a clear message.
- Given a published Need receives applications, when the Consumer views it, then they can see all applicants and their profiles.



#### 3.4.4 Functional Requirements



| ID | Requirement | Priority | Notes |
|----|--------------|-----------|-------|
| FR-4.1 | Consumers shall be able to create a new Need with title and description. | High | |
| FR-4.2 | Needs shall include an estimated time value in hours (minimum 1 hour). | High | |
| FR-4.3 | Consumers shall specify if the service is online or in-person. | High | |
| FR-4.4 | Consumers shall be able to add one or more semantic tags to categorize the Need. | High | |
| FR-4.5 | Consumers shall be able to set availability windows for when service is needed. | Medium | |
| FR-4.6 | Consumers shall be able to set an expiration date for their Needs. | Medium | Need becomes passive after expiration |
| FR-4.7 | Consumers shall be able to edit their own Needs. | High | Only before Provider selection |
| FR-4.8 | Consumers shall be able to delete their own Needs. | High | Only if no active selection |
| FR-4.9 | The system shall validate all required fields before publishing a Need. | High | |



#### 3.4.4 Nonfunctional Requirements



| Type | Description | Priority |
|------|--------------|-----------|
| Performance | Need creation should complete within 2 seconds. | Medium |
| Usability | Interface should clearly show the estimated time for the service. | High |
| Data Integrity | Need data must be validated and sanitized. | High |



---



### 3.5 Feature 5 – Map-Based Service Discovery



#### 3.5.1 Description

This feature provides an interactive map view displaying all active Offers and Needs based on location. Users can search, filter by semantic tags, distance, and time estimates, and visually discover nearby services. The map centers on the user's neighborhood by default.



#### 3.5.2 User Story

> As a **user searching for services**, I want to **view Offers and Needs on a map with filters** so that **I can easily find nearby services that match my interests and availability**.



#### 3.5.3 Acceptance Criteria

- Given a user accesses the services page, when they select map view, then active Offers and Needs are displayed as markers on the map.
- Given the user has enabled location services, when the map loads, then it centers on their neighborhood.
- Given a user applies filters (tags, distance, hours), when they update filters, then the map updates to show only matching services.
- Given a user clicks a map marker, when the popup opens, then they see service summary with option to view details.
- Given no services match filters, when the map is empty, then a helpful message suggests relaxing filters.
- Given the user's location is unavailable, when the map loads, then it defaults to a general city view and allows manual location entry.



#### 3.5.4 Functional Requirements



| ID | Requirement | Priority | Notes |
|----|--------------|-----------|-------|
| FR-5.1 | The system shall display active Offers and Needs on an interactive map. | High | |
| FR-5.2 | The map shall center on the user's neighborhood by default. | High | Requires geolocation permission |
| FR-5.3 | Users shall be able to filter services by semantic tags. | High | Multi-select tags |
| FR-5.4 | Users shall be able to filter services by distance radius. | High | E.g., within 2km, 5km, 10km |
| FR-5.5 | Users shall be able to filter services by estimated hours. | Medium | E.g., 1-2 hours, 3-5 hours |
| FR-5.6 | Users shall be able to filter by service type (Offer vs Need). | Medium | |
| FR-5.7 | Users shall be able to search services by keyword. | Medium | Searches title and description |
| FR-5.8 | Clicking a map marker shall display a summary popup with link to full details. | High | |
| FR-5.9 | The system shall provide a list view alternative to the map. | Medium | |
| FR-5.10 | The map shall allow manual location entry if geolocation is unavailable. | Medium | |



#### 3.5.5 Nonfunctional Requirements



| Type | Description | Priority |
|------|--------------|-----------|
| Performance | Map should load and display markers within 3 seconds. | High |
| Performance | Filter updates should reflect on map within 1 second. | Medium |
| Usability | Map controls should be intuitive with clear filter options. | High |
| Accessibility | List view alternative must be available for users who cannot use maps. | High |
| Scalability | Map should efficiently handle hundreds of service markers. | Medium |



---



### 3.6 Feature 6 – Provider Application to Needs



#### 3.6.1 Description

This feature allows Providers to browse available Needs and submit applications to fulfill them. Providers can view Need details, assess if they have the required skills, and express interest. The Consumer receives notifications of applications and can review Provider profiles before selection.



#### 3.6.2 User Story

> As a **Provider**, I want to **browse Needs and apply to fulfill ones that match my skills** so that **I can earn time credits by helping community members**.



#### 3.6.3 Acceptance Criteria

- Given a Provider views a Need, when they click "Apply", then their application is submitted and the Consumer is notified.
- Given a Provider has already applied to a Need, when they view it again, then the "Apply" button is replaced with "Application Pending".
- Given a Provider's application is successful, when the Consumer selects them, then both parties receive notifications and a private message thread is created.
- Given a Need has been fulfilled or closed, when a Provider views it, then the application option is disabled with an explanation.
- Given a Provider lacks required tags/skills mentioned in the Need, when they apply, then the system may warn them but allows the application.



#### 3.6.4 Functional Requirements



| ID | Requirement | Priority | Notes |
|----|--------------|-----------|-------|
| FR-6.1 | Providers shall be able to view detailed information about any Need. | High | |
| FR-6.2 | Providers shall be able to submit an application to fulfill a Need. | High | |
| FR-6.3 | The system shall notify the Consumer when a Provider applies. | High | Email and in-app notification |
| FR-6.4 | Providers shall not be able to apply to the same Need multiple times. | High | |
| FR-6.5 | Providers shall be able to view the status of their applications. | High | Pending, Accepted, Rejected |
| FR-6.6 | Providers shall be able to withdraw their application before selection. | Medium | |
| FR-6.7 | The system shall prevent applications to expired or completed Needs. | High | |
| FR-6.8 | Providers shall be able to view their application history. | Medium | |



#### 3.6.5 Nonfunctional Requirements



| Type | Description | Priority |
|------|--------------|-----------|
| Performance | Application submission should complete within 2 seconds. | Medium |
| Usability | Application interface should clearly show Need requirements. | High |
| Notifications | Consumers should receive real-time notifications of new applications. | High |
| Data Integrity | Application records must be accurately maintained. | High |



---



### 3.7 Feature 7 – Consumer Selection of Provider



#### 3.7.1 Description

This feature enables Consumers to review applications from Providers, view their profiles and ratings, and select the most suitable Provider for their Need. Upon selection, status updates and a private messaging channel opens for coordination and schedule proposal negotiation.



#### 3.7.2 User Story

> As a **Consumer**, I want to **review Provider applications and select the best candidate** so that **I can ensure quality service and coordinate details for the exchange**.



#### 3.7.3 Acceptance Criteria

- Given a Consumer's Need has applications, when they view the Need, then they see a list of all applicants with profile summaries.
- Given a Consumer clicks on an applicant, when the profile loads, then they see the Provider's biography, ratings, and past service history.
- Given a Consumer selects a Provider, when they confirm the selection, then both parties are notified and a private chat is created.
- Given the system processes the selection, when complete, then the Need status changes to "Provider Selected".



#### 3.7.4 Functional Requirements



| ID | Requirement | Priority | Notes |
|----|--------------|-----------|-------|
| FR-7.1 | Consumers shall be able to view all applications for their Needs. | High | |
| FR-7.2 | Consumers shall be able to view detailed profiles of applicant Providers. | High | Including ratings and reviews |
| FR-7.3 | Consumers shall be able to select one Provider from the applicants. | High | |
| FR-7.4 | The system shall automatically create a private messaging channel upon selection. | High | |
| FR-7.5 | The system shall update the Need status to "Provider Selected". | High | |
| FR-7.6 | Consumers shall be able to reject applications with optional reason. | Medium | |



#### 3.7.5 Nonfunctional Requirements



| Type | Description | Priority |
|------|--------------|-----------|
| Performance | Profile loading should complete within 2 seconds. | Medium |
| Security | Hour reservation must be atomic to prevent double-spending. | High |
| Usability | Selection interface should clearly show all applicant information. | High |
| Notifications | Both parties must receive immediate notifications. | High |



---



### 3.8 Feature 8 – TimeBank Currency System



#### 3.8.1 Description

This feature manages the time-based currency system that powers service exchanges. It handles initial credit allocation, balance tracking, schedule proposal validation, and transfer upon completion. The system enforces a balance cap and ensures transaction integrity.



#### 3.8.2 User Story

> As a **platform user**, I want **a fair and transparent time credit system** so that **I can exchange services equitably without monetary transactions**.



#### 3.8.3 Acceptance Criteria

- Given a new user completes registration and verification, when their account activates, then they receive 1 hour initial balance.
- Given a user views their dashboard, when the page loads, then their current time credit balance is prominently displayed.
- Given a Provider or Consumer proposes a schedule, when the other party attempts to accept, then the system validates both parties have sufficient balance and won't exceed the maximum cap.
- Given a schedule proposal would cause the Consumer to have insufficient balance, when they attempt to accept, then the system prevents acceptance with a clear message.
- Given a schedule proposal would cause the Provider to exceed the 10-hour balance cap upon completion, when they attempt to accept, then the system prevents acceptance and suggests spending hours first.
- Given a service is completed and mutually confirmed, when both parties approve, then the specified hours transfer from Consumer to Provider.
- Given a Provider marks a service complete, when 48 hours pass without Consumer confirmation, then the system auto-confirms and transfers hours.



#### 3.8.4 Functional Requirements



| ID | Requirement | Priority | Notes |
|----|--------------|-----------|-------|
| FR-8.1 | New verified users shall receive 1 hour initial time credit. | High | |
| FR-8.2 | Users shall be able to view their current time credit balance. | High | On dashboard and profile |
| FR-8.3 | Either party shall be able to propose a schedule with date, time, and location details. | High | |
| FR-8.4 | The system shall validate that the Consumer has sufficient balance before allowing schedule acceptance. | High | |
| FR-8.5 | The system shall validate that the Provider won't exceed the 10-hour balance cap before allowing schedule acceptance. | High | |
| FR-8.6 | Upon mutual completion confirmation, the specified hours shall transfer from Consumer to Provider. | High | |
| FR-8.7 | The system shall enforce a maximum balance of 10 hours per user. | High | |
| FR-8.8 | The system shall auto-confirm service completion after 48 hours of Provider marking complete. | Medium | Auto-transfer hours |
| FR-8.9 | Transaction records shall include timestamps, parties, amount, and status. | High | |
| FR-8.10 | The number of participants in a task shall not affect hour exchange amount. | High | Always 1:1 as specified |



#### 3.8.5 Nonfunctional Requirements



| Type | Description | Priority |
|------|--------------|-----------|
| Security | All balance and transaction operations must be atomic and logged. | High |
| Data Integrity | The system must prevent double-spending and balance corruption. | High |
| Performance | Balance queries should return within 1 second. | Medium |
| Auditability | All transactions must be logged immutably for dispute resolution. | High |
| Reliability | Transaction failures must rollback cleanly without data loss. | High |



---



### 3.9 Feature 9 – Mutual Evaluation and Rating



#### 3.9.1 Description

After service completion, both Consumer and Provider can evaluate each other through ratings and reviews. This builds trust, provides feedback, and helps users make informed decisions. Providers also complete a survey about the task's accuracy and difficulty.



#### 3.9.2 User Story

> As a **user who completed a service exchange**, I want to **rate and review the other party** so that **the community can make informed decisions and maintain quality standards**.



#### 3.9.3 Acceptance Criteria

- Given a service is marked complete, when both parties confirm, then they each receive a prompt to rate and review the other.
- Given a user submits a rating (1-5 stars) and optional review, when they save it, then the rating is permanently associated with the other user's profile.
- Given a user views another user's profile, when the page loads, then they see the average rating and recent reviews.
- Given a Provider completes a Need, when they submit their evaluation, then they also fill a survey about task difficulty and accuracy.
- Given neither party submits evaluation within 7 days, when the deadline passes, then the opportunity closes but transaction remains recorded.



#### 3.9.4 Functional Requirements



| ID | Requirement | Priority | Notes |
|----|--------------|-----------|-------|
| FR-9.1 | After service completion, Consumers shall be able to rate and review Providers. | High | 1-5 stars + text review |
| FR-9.2 | After service completion, Providers shall be able to rate and review Consumers. | High | 1-5 stars + text review |
| FR-9.3 | Providers shall complete a post-service survey about task accuracy. | Medium | Difficulty, relevance, time accuracy |
| FR-9.4 | User profiles shall display average rating and review count. | High | |
| FR-9.5 | User profiles shall show recent reviews (up to 10). | Medium | |
| FR-9.6 | The system shall prevent users from editing ratings after submission. | High | Maintain integrity |
| FR-9.7 | Users shall be able to report inappropriate reviews to admins. | Medium | |
| FR-9.8 | Ratings shall be visible to all users viewing the profile. | High | |



#### 3.9.5 Nonfunctional Requirements



| Type | Description | Priority |
|------|--------------|-----------|
| Data Integrity | Ratings must be immutable after submission. | High |
| Usability | Rating interface should be simple and quick to complete. | High |
| Moderation | Admins must be able to remove abusive or false reviews. | Medium |
| Trust | Rating system must be transparent and tamper-proof. | High |



---



### 3.10 Feature 10 – Private Messaging



#### 3.10.1 Description

When a Consumer selects a Provider (or vice versa for Offers), the system automatically creates a private messaging channel for the two parties to coordinate service details, discuss logistics, and communicate throughout the exchange.



#### 3.10.2 User Story

> As a **user engaged in a service exchange**, I want to **message the other party privately** so that **we can coordinate details, clarify expectations, and ensure smooth service delivery**.



#### 3.10.3 Acceptance Criteria

- Given a Consumer selects a Provider, when the selection confirms, then a private message thread is automatically created between them.
- Given users have an active message thread, when either sends a message, then the other receives a real-time notification.
- Given a user views their messages, when the page loads, then they see all active conversations with unread indicators.
- Given a service exchange completes, when both parties confirm, then the message thread remains accessible but is marked as archived.
- Given a user blocks another user, when blocking occurs, then message thread is closed and further messages are prevented.



#### 3.10.4 Functional Requirements



| ID | Requirement | Priority | Notes |
|----|--------------|-----------|-------|
| FR-10.1 | Upon Provider selection, the system shall create a private messaging channel. | High | |
| FR-10.2 | Users shall be able to send text messages to their matched party. | High | |
| FR-10.3 | Users shall receive notifications for new messages. | High | Email and in-app |
| FR-10.4 | Users shall be able to view message history. | High | |
| FR-10.5 | The system shall display unread message indicators. | Medium | |
| FR-10.6 | Completed service threads shall be archived but remain accessible. | Medium | |
| FR-10.7 | Users shall be able to report inappropriate messages. | Medium | |
| FR-10.8 | The system shall support real-time message delivery. | Medium | Using WebSockets or polling |



#### 3.10.5 Nonfunctional Requirements



| Type | Description | Priority |
|------|--------------|-----------|
| Performance | Messages should be delivered within 2 seconds. | Medium |
| Security | Messages must be encrypted in transit. | High |
| Privacy | Users can only message matched parties, not arbitrary users. | High |
| Usability | Interface should clearly show conversation context (related service). | High |



---



### 3.11 Feature 11 – Schedule Proposal and Acceptance



#### 3.11.1 Description

This feature enables matched Provider-Consumer pairs to negotiate and confirm service schedules through a proposal-acceptance workflow. Either party can propose a schedule with specific date, time, and location details. The system validates that both parties have sufficient balance before allowing schedule acceptance, ensuring the Consumer has enough hours to pay and the Provider won't exceed the 10-hour balance cap.



#### 3.11.2 User Story

> As a **matched Provider or Consumer**, I want to **propose and negotiate service schedules** so that **we can coordinate the service delivery time and location, with the system ensuring we both have valid balances before confirming**.



#### 3.11.3 Acceptance Criteria

- Given matched parties in a private message thread, when either party proposes a schedule with date, time, and location, then the proposal is sent to the other party for review.
- Given a Consumer receives a schedule proposal, when they attempt to accept, then the system validates they have sufficient balance to pay for the service hours.
- Given a Provider receives a schedule proposal, when they attempt to accept, then the system validates they won't exceed the 10-hour balance cap upon service completion.
- Given a party has insufficient balance or would exceed the cap, when they attempt to accept a proposal, then the system prevents acceptance and displays a clear explanation.
- Given a schedule proposal is accepted by both parties, when confirmation completes, then the agreed schedule is recorded and both parties are notified.
- Given a party rejects a proposal, when they decline, then the other party is notified and can make a new proposal.
- Given an accepted schedule needs changes, when either party requests modification, then a new proposal cycle begins.



#### 3.11.4 Functional Requirements



| ID | Requirement | Priority | Notes |
|----|--------------|-----------|-------|
| FR-11.1 | Either party shall be able to propose a schedule with date, time, and location details. | High | Via messaging interface |
| FR-11.2 | The system shall validate Consumer's balance is sufficient before allowing schedule acceptance. | High | Must have ≥ estimated hours |
| FR-11.3 | The system shall validate Provider won't exceed 10-hour cap before allowing schedule acceptance. | High | Current balance + hours ≤ 10 |
| FR-11.4 | The system shall prevent schedule acceptance if validation fails. | High | With clear error message |
| FR-11.5 | Both parties shall be able to view pending schedule proposals. | High | |
| FR-11.6 | Either party shall be able to reject a schedule proposal. | High | |
| FR-11.7 | The system shall notify both parties when a schedule is accepted. | High | Email and in-app |
| FR-11.8 | The system shall record the accepted schedule with service details. | High | |
| FR-11.9 | Either party shall be able to request schedule changes after acceptance. | Medium | Requires mutual re-agreement |
| FR-11.10 | The system shall display validation warnings before users attempt to accept. | Medium | Show if balance insufficient |



#### 3.11.5 Nonfunctional Requirements



| Type | Description | Priority |
|------|--------------|-----------|
| Security | Balance validation must be atomic to prevent race conditions. | High |
| Usability | Validation errors must clearly explain why acceptance is prevented. | High |
| Usability | Schedule proposal interface should be intuitive with calendar integration. | Medium |
| Performance | Balance validation should complete within 1 second. | Medium |
| Data Integrity | Accepted schedules must be immutably recorded. | High |



---



### 3.12 Feature 12 – Administration Dashboard



#### 3.12.1 Description

This feature provides administrators with comprehensive dashboards to monitor platform activity, moderate content, manage users, resolve disputes, and maintain system integrity. Admins have elevated permissions to ensure community safety and platform quality.



#### 3.12.2 User Story

> As an **administrator**, I want **dashboards to monitor users, services, and reported content** so that **I can maintain platform integrity and resolve issues efficiently**.



#### 3.12.3 Acceptance Criteria

- Given an admin logs in, when they access the admin panel, then they see dashboards for users, Offers, Needs, evaluations, and reports.
- Given an admin views a reported service, when they review it, then they can deactivate it with a reason sent to the user.
- Given an admin identifies a problematic user, when they take action, then they can issue a warning or ban with clear documentation.
- Given content is reported as illegal, when an admin reviews it, then they can immediately delete it and flag the user.
- Given an admin manages semantic tags, when they access the tag manager, then they can add, edit, delete, or approve user-suggested tags.



#### 3.12.4 Functional Requirements



| ID | Requirement | Priority | Notes |
|----|--------------|-----------|-------|
| FR-12.1 | Admins shall have access to dashboards showing all users. | High | |
| FR-12.2 | Admins shall view lists of all Offers (active and passive). | High | |
| FR-12.3 | Admins shall view lists of all Needs (active and passive). | High | |
| FR-12.4 | Admins shall be able to deactivate any Offer or Need with reason. | High | Reason communicated to user |
| FR-12.5 | Admins shall be able to issue formal warnings to users. | High | |
| FR-12.6 | Admins shall be able to ban users following warnings. | High | |
| FR-12.7 | Admins shall be able to immediately delete illegal content. | High | |
| FR-12.8 | Admins shall be able to manage semantic tags (add, edit, delete). | High | |
| FR-12.9 | Admins shall be able to approve user-suggested tags. | Medium | |
| FR-12.10 | Admins shall view and respond to dispute flags. | High | |
| FR-12.11 | Admin actions shall be logged for audit trail. | High | |



#### 3.12.5 Nonfunctional Requirements



| Type | Description | Priority |
|------|--------------|-----------|
| Security | Admin access must be restricted with role-based authentication. | High |
| Auditability | All admin actions must be logged immutably. | High |
| Usability | Dashboards should provide clear overviews with filtering options. | High |
| Performance | Dashboards should load within 3 seconds. | Medium |



---



### 3.13 Feature 13 – Community Forum (The Commons)

#### 3.13.1 Description
This feature provides a digital "town square" called The Commons, where users can engage in discussions outside of specific service transactions. It allows for organized categories, threaded conversations, and community building, facilitating social trust which is essential for a TimeBank economy.

#### 3.13.2 User Story
> As a **Registered User**, I want to **participate in discussion threads within specific categories** so that **I can share ideas, ask general questions, and build relationships with my neighbors**.

#### 3.13.3 Acceptance Criteria
- Given a logged-in user, when they access The Commons, then they see a list of Admin-defined Forum Categories (e.g., "General Chat," "Project Collaboration").
- Given a user is viewing a Category, when they click "New Thread," then they can compose a title and body text.
- Given a created thread, when other users view it, then they can add comments to the discussion.
- Given a user is the author of a post or thread, when they select edit/delete, then the content is updated or removed accordingly.
- Given a thread contains inappropriate content, when a user clicks "Report," then the thread is flagged for Admin review.
- Given a guest user (Neighbor), when they attempt to post or comment, then they are redirected to the registration page.

#### 3.13.4 Functional Requirements

| ID | Requirement | Priority | Notes |
|----|--------------|-----------|-------|
| FR-13.1 | The system shall display a list of Forum Categories managed by Admins. | High | e.g., "Announcements," "Help." |
| FR-13.2 | Registered users shall be able to create new Discussion Threads within a category. | High | Requires Title and Body. |
| FR-13.3 | Registered users shall be able to post Comments on existing threads. | High | |
| FR-13.4 | The system shall support rich text formatting for posts and comments. | Medium | Basic Markdown or WYSIWYG. |
| FR-13.5 | Users shall be able to edit or delete their own posts and threads. | Medium | Deleting a thread hides all comments. |
| FR-13.6 | The system shall display the "Last Activity" timestamp for each thread. | Medium | Used for sorting threads. |
| FR-13.7 | Users shall be able to "Report" threads or comments to Admins. | High | For moderation. |
| FR-13.8 | Admins shall be able to lock threads to prevent further commenting. | Medium | |
| FR-13.9 | Admins shall be able to pin important threads to the top of a category. | Medium | |
| FR-13.10 | The system shall allow users to search for keywords within The Commons. | Low | |

#### 3.13.5 Nonfunctional Requirements

| Type | Description | Priority |
|------|--------------|-----------|
| Performance | Forum thread lists shall load within 2 seconds. | Medium |
| Usability | The distinction between a "Need" (Service) and a "Thread" (Discussion) must be visually clear. | High |
| Security | Inputs in the forum must be sanitized to prevent XSS attacks. | High |
| Moderation | Automated profanity filters should flag posts before publication. | Low |

---



## 4. Nonfunctional Requirements



### 4.1 Performance Requirements

**NFR-P1: Response Time**
- Web pages shall load within 3 seconds under normal network conditions.
- Database queries shall return results within 2 seconds for 95% of requests.
- Map rendering with up to 500 markers shall complete within 3 seconds.

**NFR-P2: Throughput**
- The system shall support at least 100 concurrent users without performance degradation.
- The system shall handle at least 1,000 service searches per hour.

**NFR-P3: Resource Utilization**
- Server CPU usage shall not exceed 80% under normal load.
- Database storage shall be optimized to minimize redundancy.

**NFR-P4: Scalability**
- The system architecture shall support horizontal scaling to accommodate user growth.
- The database shall be designed to efficiently handle growth to 10,000+ users and 50,000+ services.



### 4.2 Security Requirements

**NFR-S1: Authentication & Authorization**
- All passwords must be hashed using bcrypt or similar secure algorithm (minimum cost factor 10).
- Session tokens must expire after 24 hours of inactivity.
- Role-based access control must prevent unauthorized access to admin features.

**NFR-S2: Data Protection**
- All sensitive user data must be encrypted at rest using AES-256.
- All data in transit must be encrypted using TLS 1.3 or higher.
- Personal information shall not be exposed through API responses to unauthorized users.

**NFR-S3: Input Validation**
- All user inputs must be validated and sanitized to prevent XSS attacks.
- SQL injection prevention through parameterized queries or ORM.
- File uploads must be scanned for malware and restricted to approved formats.

**NFR-S4: Compliance**
- The system must comply with GDPR requirements for user data handling.
- Users must be able to export their data and request account deletion.
- Privacy policy and terms of service must be clearly accessible.

**NFR-S5: Transaction Security**
- TimeBank transactions must be atomic and logged immutably.
- Concurrent transaction requests must be handled to prevent race conditions.
- Failed transactions must rollback cleanly without data corruption.



### 4.3 Usability Requirements

**NFR-U1: User Interface**
- The interface shall be intuitive for users with basic web literacy.
- Critical actions (e.g., service creation, Provider selection) shall require no more than 3 clicks.
- Error messages shall be clear, specific, and provide guidance for resolution.

**NFR-U2: Responsiveness**
- The UI shall be fully responsive, adapting to screen widths from 320px to 2560px+.
- All features shall be accessible on mobile devices (smartphones and tablets).
- Touch interactions shall be optimized with appropriately sized tap targets (minimum 44x44px).

**NFR-U3: Accessibility**
- The system shall comply with WCAG 2.1 Level AA standards.
- All interactive elements shall be keyboard-navigable.
- Images shall have descriptive alt text.
- Color contrast shall meet accessibility standards (minimum 4.5:1 for normal text).

**NFR-U4: Learnability**
- New users shall be able to register, verify email, and post their first service within 10 minutes.
- Help documentation and tooltips shall be contextually available.
- The platform shall provide guided tutorials for first-time users.



### 4.4 Reliability and Availability

**NFR-R1: Availability**
- The system shall maintain 99.5% uptime excluding planned maintenance.
- Planned maintenance windows shall be scheduled during low-traffic periods and announced 48 hours in advance.

**NFR-R2: Data Integrity**
- All data must be saved and retrieved correctly without loss or corruption.
- Database backups shall be performed daily with 30-day retention.
- Critical data (transactions, messages) shall be backed up in real-time to redundant storage.

**NFR-R3: Error Handling**
- The system shall handle errors gracefully without exposing sensitive information.
- User-facing error messages shall be helpful without revealing system internals.
- Critical errors shall be logged and alert administrators automatically.

**NFR-R4: Recovery**
- The system shall be able to recover from crashes within 15 minutes.
- Data recovery procedures shall be documented and tested quarterly.



### 4.5 Portability

**NFR-PO1: Browser Compatibility**
- The system shall function correctly on Chrome 90+, Firefox 88+, Safari 14+, and Edge 90+.
- Progressive enhancement shall ensure core functionality on older browsers.

**NFR-PO2: Device Independence**
- The system shall not require any browser plugins or extensions.
- Core features shall work without JavaScript, with enhanced experience when enabled.

**NFR-PO3: Platform Independence**
- Server-side code shall be deployable on Linux, macOS, or Windows servers.
- The application shall be containerized (e.g., Docker) for easy deployment across platforms.



### 4.6 Scalability

**NFR-SC1: User Scalability**
- The system architecture shall support growth from 100 to 10,000+ users without requiring major refactoring.
- Load balancing shall distribute traffic across multiple server instances.

**NFR-SC2: Data Scalability**
- Database schema shall accommodate millions of service records efficiently.
- Indexing strategy shall maintain query performance as data volume grows.

**NFR-SC3: Geographic Scalability**
- The system shall support expansion to multiple geographic regions.
- Content Delivery Network (CDN) integration shall optimize asset delivery globally.



### 4.7 Maintainability

**NFR-M1: Code Quality**
- Code shall follow established style guides and best practices for the chosen programming language.
- Code comments shall explain complex logic and business rules.
- Code coverage by automated tests shall be at least 70% for critical paths.

**NFR-M2: Modularity**
- The codebase shall be organized into logical modules with clear separation of concerns.
- Frontend and backend shall be decoupled through well-defined APIs.
- New features shall be addable without requiring extensive refactoring.

**NFR-M3: Documentation**
- API endpoints shall be documented with request/response examples.
- Database schema shall be documented with entity-relationship diagrams.
- Deployment procedures shall be documented in a runbook.

**NFR-M4: Monitoring**
- The system shall log all critical operations (transactions, admin actions, errors).
- Performance metrics (response times, error rates) shall be tracked and visualized.
- Alerts shall notify administrators of critical issues (downtime, security breaches).



### 4.8 Business Rules & Policies

**NFR-B1: Dispute Resolution**
- If a Consumer does not confirm or deny completion within 48 hours after a Provider marks the task complete, the system shall auto-confirm and transfer hours.
- Either party shall be able to flag a transaction for administrative review after auto-confirmation.

**NFR-B2: Content Moderation**
- Reported content shall be queued for admin review within 24 hours.
- Illegal content shall be removable immediately by admins with user flagging.

**NFR-B3: Fair Use**
- Users attempting to game the system (e.g., fake services, rating manipulation) shall be warned then banned.
- Automated detection of suspicious patterns shall flag accounts for admin review.



---



## 5. System Models



This section references visual models and diagrams that illustrate system architecture, user flows, and data structures. These models are maintained in separate project documents.



### 5.1 Use Case Diagram

Refer to **Use-Cases.md** in the project repository for detailed use case descriptions including:
- User registration and authentication
- Service creation and management (Offers and Needs)
- Service discovery and application
- TimeBank transactions
- Rating and evaluation
- Administrative functions

### 5.2 User Flow / Wireframes

Interactive mockups and wireframes are available in the **mockups/** directory:
- **Registration & Authentication Flow**: `signup-mockup.html`, `signin-mockup.html`, `verification-success.html`
- **Profile Management**: `profile-mockup.html`, `profile-public.html`
- **Service Creation**: `create-service-mockup.html`
- **Service Discovery**: `index.html`, `services-map.html`, `need-detail.html`, `offer-detail.html`
- **Service Matching**: `approved-need-status-consumer.html`, `approved-need-status-provider.html`
- **Confirmation**: `confirmation-form-consumer.html`, `confirmation-form-provider.html`
- **Admin Dashboard**: `admin-dashboard.html`, `admin-users.html`, `admin-services.html`, `admin-reports.html`
- **Error Handling**: `empty-error-states.html`

See **Mockups.md** for complete documentation with HTML and PDF links.

### 5.3 Sequence Diagrams

Key sequence diagrams illustrating system interactions:

**5.3.1 Need Posting and Provider Selection**
1. Consumer creates Need → System validates fields → Need published
2. Provider searches and applies → System notifies Consumer
3. Consumer reviews applications → Selects Provider → Status updated to "Provider Selected"
4. System creates message channel and ServiceProgress record → Both parties notified

**5.3.2 Schedule Proposal and Acceptance**
1. Either party proposes schedule (date, time, location) → Message sent with proposal details
2. Other party views proposal → System validates balances (Consumer has sufficient, Provider won't exceed cap)
3. If validation passes → Other party accepts → Schedule confirmed in ServiceProgress
4. If validation fails → System prevents acceptance with clear error message
5. Both parties notified of confirmed schedule → Service status updated to "scheduled"

**5.3.3 Service Execution and Completion**
1. Both parties confirm service start → ServiceProgress updated (provider_start_confirmed, consumer_start_confirmed)
2. Service performed according to schedule
3. Provider marks service complete → System notifies Consumer
4. Consumer confirms completion (or auto-confirms after 48 hours)
5. System transfers hours from Consumer to Provider
6. Both parties prompted to complete surveys and rate/review
7. ServiceProgress status updated to "completed"

**5.3.4 Dispute Resolution**
1. Provider marks complete → 48-hour timer starts
2. If no Consumer response → System auto-confirms → Hours transferred
3. Either party flags for review → Report created → Admin notified
4. Admin reviews ServiceProgress, Messages, and evidence → Makes decision
5. Admin can adjust hours or status if necessary → AdminLog created

### 5.4 Data Model (Entity-Relationship Diagram)

**Key Entities:**

**User**
- id (PK), email, password_hash, first_name, last_name, phone_number, biography, profile_photo
- role (user/admin), time_balance, is_verified, is_active, user_status (active/banned/warning)
- date_joined, last_login

**EmailVerification**
- id (PK), user_id (FK), token, created_at, expires_at, is_used

**PasswordResetToken**
- id (PK), user_id (FK), token, created_at, expires_at, is_used

**Service** (Offers and Needs)
- id (PK), user_id (FK), service_type (offer/need), title, description
- hours_required, location_type (online/in-person/both), location_address
- latitude, longitude, status (open/in_progress/completed/cancelled/expired)
- service_date, start_time, end_time, created_at, updated_at

**Tag**
- id (PK), name, created_by (FK user_id), is_approved, created_at

**ServiceTag** (Many-to-Many relationship)
- service_id (FK), tag_id (FK)

**ServiceAvailability**
- id (PK), service_id (FK), day_of_week (0-6), start_time, end_time

**ServiceApplication**
- id (PK), service_id (FK), applicant_id (FK user_id)
- status (pending/accepted/rejected/cancelled/withdrawn), message
- applied_at, updated_at

**ServiceProgress**
- id (PK), service_id (FK), application_id (FK), provider_id (FK), consumer_id (FK)
- hours, status (selected/scheduled/in_progress/awaiting_confirmation/completed/disputed/cancelled)
- scheduled_date, scheduled_time, agreed_location, special_instructions
- provider_confirmed, consumer_confirmed, provider_start_confirmed, consumer_start_confirmed
- provider_start_confirmed_at, consumer_start_confirmed_at
- proposed_date, proposed_time, proposed_location, proposed_by, proposed_at
- schedule_accepted_by_consumer, schedule_accepted_by_provider
- service_end_date, service_start_date
- provider_survey_submitted, consumer_survey_submitted
- provider_survey_submitted_at, consumer_survey_submitted_at
- provider_survey_data (JSON), consumer_survey_data (JSON), survey_deadline
- selected_at, scheduled_at, started_at, completed_at, created_at, updated_at

**Message**
- id (PK), service_id (FK, nullable), application_id (FK, nullable)
- sender_id (FK user_id), receiver_id (FK user_id), message
- is_read, message_type (text/proposal)
- proposal_date, proposal_start_time, proposal_end_time, proposal_location
- proposal_status (pending/accepted/rejected), created_at

**ForumCategory**
- id (PK), name, description, is_active, created_at, updated_at

**ForumThread**
- id (PK), category_id (FK), user_id (FK), title, content
- is_pinned, is_locked, view_count, created_at, updated_at

**ForumComment**
- id (PK), thread_id (FK), user_id (FK), content
- parent_comment_id (FK, nullable, for nested replies)
- created_at, updated_at

**Report**
- id (PK), reporter_id (FK user_id), reported_user_id (FK, nullable)
- content_type (service/thread/comment/user/message), content_id
- reason, description, status (open/resolved/dismissed)
- resolved_by (FK user_id), resolved_at, resolution_notes, created_at

**AdminLog**
- id (PK), admin_id (FK user_id), action, target_type, target_id
- details (JSON), ip_address, created_at

**Relationships:**
- User 1:N Service (user creates many services)
- User 1:N ServiceApplication (user applies to many services)
- Service 1:N ServiceApplication (service receives many applications)
- Service M:N Tag (services have multiple tags via ServiceTag)
- Service 1:N ServiceAvailability (service has multiple availability windows)
- Service 1:N ServiceProgress (service can have progress tracking)
- ServiceApplication 1:1 ServiceProgress (accepted application creates progress)
- ServiceProgress N:1 User as Provider (provider handles many services)
- ServiceProgress N:1 User as Consumer (consumer requests many services)
- User 1:N Message as Sender (user sends many messages)
- User 1:N Message as Receiver (user receives many messages)
- Service 1:N Message (service-related messages)
- ServiceApplication 1:N Message (application-related messages)
- ForumCategory 1:N ForumThread (category contains many threads)
- ForumThread 1:N ForumComment (thread contains many comments)
- User 1:N ForumThread (user creates many threads)
- User 1:N ForumComment (user creates many comments)
- ForumComment N:1 ForumComment (comments can be replies to other comments)
- User 1:N Report as Reporter (user can report many items)
- User 1:N Report as Reported (user can be reported)
- User 1:N AdminLog (admin performs many actions)
- User 1:N EmailVerification (user can have multiple verification tokens)
- User 1:N PasswordResetToken (user can have multiple reset tokens)



---



## 6. Glossary



| Term | Definition |
|------|------------|
| **Active Service** | An Offer or Need that is currently available for applications or matching. |
| **Admin/Administrator** | A user with elevated permissions to moderate content, manage users, and resolve disputes. |
| **Application** | A Provider's expression of interest in fulfilling a Consumer's Need. |
| **Auto-Confirmation** | Automatic confirmation of service completion after 48 hours if Consumer doesn't respond. |
| **Balance Cap** | Maximum time credit balance of 10 hours per user. |
| **Consumer** | A user who posts a Need requesting a service from the community. |
| **Geolocation** | The use of device location services to determine user's physical position for map features. |
| **In-Person Service** | A service that requires physical presence at a specific location. |
| **Initial Credit** | The 1-hour time credit given to new users upon account verification. |
| **Need** | A service request posted by a Consumer seeking assistance from Providers. |
| **Offer** | A service advertisement posted by a Provider offering their skills. |
| **Online Service** | A service that can be provided remotely via internet. |
| **Passive Service** | An expired or deactivated Offer or Need no longer available for matching. |
| **Provider** | A user who offers services to fulfill Consumers' Needs in exchange for time credits. |
| **Schedule Proposal** | A proposed date, time, and location for service delivery that requires validation of both parties' balances before acceptance. |
| **Semantic Tag** | A descriptive label used to categorize and search for services. |
| **Service Exchange** | The complete process from service posting to completion and evaluation. |
| **Time Credit** | The platform's currency unit, measured in hours, used for service exchanges. |
| **TimeBank** | A reciprocal service exchange system where time serves as currency. |
| **Transaction** | A record of time credit movement between users upon service completion. |
| **Verified User** | A user who has completed email verification and can access platform features. |



---



## 7. Appendices



### 7.1 Mockup and Prototype Links

**Interactive HTML Mockups** (see `mockups/` directory):
- Homepage/Dashboard: `index.html`
- Authentication: `signup-mockup.html`, `signin-mockup.html`, `verification-success.html`
- Services: `need-detail.html`, `offer-detail.html`, `service-detail.html`, `services-map.html`
- Service Creation: `create-service-mockup.html`
- Status Tracking: `approved-need-status.html`, `approved-need-status-consumer.html`, `approved-need-status-provider.html`
- Confirmation: `confirmation-form-consumer.html`, `confirmation-form-provider.html`
- Profile: `profile-mockup.html`, `profile-public.html`
- Admin: `admin-dashboard.html`, `admin-users.html`, `admin-services.html`, `admin-reports.html`
- Error States: `empty-error-states.html`

**PDF Screenshots** are available in `mockups/mockup-screens-pdf/` for all pages.

**Mockup Documentation**: See `Mockups.md` for detailed descriptions and scenario mappings.



### 7.2 Related Project Documents

- **Requirements.md**: Detailed functional and non-functional requirements catalog
- **Use-Cases.md**: Complete use case descriptions with actors and flows
- **Scenarios.md**: User scenarios with step-by-step walkthroughs
- **Mockups.md**: Mockup inventory with scenario mappings
- **README.md**: Project overview and repository structure



### 7.3 Agile Artifacts

**Product Backlog** (prioritized features for implementation):
1. User registration, authentication, and email verification (High priority)
2. User profile management (High priority)
3. Service creation (Offers and Needs) (High priority)
4. TimeBank system - initial credits and balance tracking (High priority)
5. Map-based service discovery with filters (High priority)
6. Application and Provider selection workflow (High priority)
7. Hour reservation and transaction processing (High priority)
8. Private messaging system (High priority)
9. Service completion and confirmation (High priority)
10. Rating and evaluation system (Medium priority)
11. Admin dashboard and moderation tools (Medium priority)
12. Semantic tag management (Medium priority)
13. Community forums (Low priority)
14. Advanced search and recommendations (Low priority)

**Sprint Planning**: Features will be implemented iteratively following Agile sprints of 2 weeks each.

**Definition of Done**:
- Code implemented and peer-reviewed
- Unit tests written with 70%+ coverage
- Integration tests passing
- Documentation updated
- Mockups/wireframes validated
- Deployed to staging environment
- Acceptance criteria met and verified



### 7.4 Technology Stack (Proposed)

**Frontend:**
- HTML5, CSS3, JavaScript (ES6+)
- Responsive framework (Bootstrap or Tailwind CSS)
- Mapping library (OpenStreetMap)

**Backend:**
- Python with Flask
- RESTful API architecture

**Database:**
- PostgreSQL (relational data with JSONB support)

**Authentication:**
- JWT (JSON Web Tokens) for session management
- bcrypt for password hashing

**Email Service:**
- Gmail

**Hosting & Deployment:**
- DigitalOcean
- Docker for containerization
- CI/CD pipeline (GitHub Actions or GitLab CI)

**Testing:**
- Jest or Mocha (JavaScript) / pytest (Python)
- Selenium or Cypress for end-to-end testing



### 7.5 Development Milestones

**Phase 1 - MVP (Minimum Viable Product)**
- User registration and authentication
- Basic profile management
- Service creation (Offers and Needs)
- Simple list-based service discovery
- Basic TimeBank functionality (initial credits, balance display)

**Phase 2 - Core Features**
- Map-based discovery with filters
- Application and matching workflow
- Hour reservation and transaction processing
- Private messaging
- Service completion workflow

**Phase 3 - Community Features**
- Rating and evaluation system
- Admin dashboard and moderation
- Semantic tag management
- Enhanced search

**Phase 4 - Polish & Scale**
- Community forums
- Advanced recommendations
- Performance optimization
- Mobile-specific enhancements



---



**Document Version History:**

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | October 21, 2025 | M.Zeynep Çakmakcı | Initial comprehensive SRS document created |
| 2.0 | November 25, 2025 | M.Zeynep Çakmakcı | Forum requirements has been added to SRS document |
| 3.0 | December 15, 2025 | M.Zeynep Çakmakcı | "Reserved hours" requirements has been removed and "Prosal Schedule" requirements has been added |

---

**End of Software Requirements Specification**
