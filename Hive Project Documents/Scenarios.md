# Scenarios: 

## 1. Alex signs up, verifies email, and sees starting balance
- Primary persona: Alex Chen (The Curious Newcomer)
- Goal: Create an account, verify email, sign in, and confirm the initial time-credit balance is displayed.

Steps:
1. Alex opens the app and chooses "Sign up".
2. He fills in name, email, date of birth and passwords and accepts Terms and Services & Privacy Policy.
3. The system creates a provisional account and sends a verification email (UR-1, UR-2).
4. Alex clicks the verification link, which marks the email verified and activates the account (UR-2).
5. Alex signs in with his email and password (UR-3).
6. The dashboard shows a starting balance (TCS-1).

Requirement mapping: UR-1, UR-2, UR-3, TCS-1

Acceptance criteria:
- Account creation succeeds with valid input and sends a verification email.
- Clicking the verification link sets the account to active and allows authentication.
- After first login the dashboard displays the initial time-credit balance and at least one suggested item.

Edge cases:
- User provides an already-registered email (system shows a clear error and offers password reset).
- Verification link expires (system allows resending verification).
- Weak password rejected with helpful guidance.

Pages:
- [x] Homepage, 
- [x] Sign-up form/page, 
- [x] Sign-in form/page, 
- [x] Reset Password form/page, 
- [x] User profile page / Owner

## 2. Austin posts a guitar lesson offering with tags and availability
- Primary persona: Austin Page (The Newcomer & Provider)
- Goal: Create a clear, discoverable service offering to earn time credits.

Steps:
1. Austin signs in and navigates to "Create Offer" (SM-1).
2. He enters title, description, hourly estimate, location preference (in-person/remote), and his hourly cap (SM-2).
3. He attaches tags (guitar, tutoring) and optionally creates a new tag if needed (STS-1, STS-2).
4. He sets availability windows and chooses to publish the offer (SM-3).
5. The system validates inputs, publishes the service, and shows it in the Provider's dashboard and search results.

Requirement mapping: SM-1, SM-2, SM-3, STS-1, STS-2

Acceptance criteria:
- Offer is created only with required fields and valid attributes.
- Tags are associated properly and appear in search filters.
- Offer lifecycle actions (publish, unpublish, edit, delete) are available from the dashboard.

Edge cases:
- Missing required fields prevents publish with clear errors.
- Duplicate or abusive tags are flagged for moderation.
- Provider sets availability that overlaps with an existing accepted booking (system warns of conflict).

Pages:
- [x] Create Service Page / Offer View
- [x] Services Page / Offers View

## 3. Taylor searches the map and applies for a gardening request

- Primary persona: Taylor Hope (The Energetic Teen)
- Goal: Find a nearby gardening need, filter by duration and tags, and apply.

Steps:
1. Taylor opens the "Find Needs" view and chooses Map View (SM-4).
2. He uses filters for distance (< 2 km), tags (gardening), and estimated hours (2-4) (SM-5).
3. The map updates to show matching needs; he taps a nearby request with a clear description.
4. He reviews the request and clicks "Apply" to offer help (SM-6).
5. The system records his application and notifies the consumer.

Requirement mapping: SM-4, SM-5, SM-6

Acceptance criteria:
- Map and list views reflect active filters and nearby results.
- Applying sends a notification to the requester and records the provider's interest.
- Provider's application shows in their dashboard as pending.

Edge cases:
- No matching needs in filters (system suggests relaxing filters or subscribing for alerts).
- User's location not available (fallback to manual location entry).
- Provider tries to apply to a need already assigned (application blocked and explained).

Pages:
- [x] Services Page / Needs View
- [x] Service Detail Page / Need View

## 4. Jane requests babysitting; Elizabeth is accepted and they decide where the child will stay

- Primary persona: Jane Miller (The Parent & Student) as Consumer; Elizabeth Taylor as Provider
- Goal: Consumer posts a need, reviews applicant(s), accepts a provider, completes the need, and the parties decide whether the child will stay at the consumer's home or the provider's home.

Steps:
1. Jane posts a babysitting need with date/time and required skills.
2. Elizabeth applies; Jane reviews Elizabeth's profile, past tags, and any caregiver qualifications (biography) (SM-7).
3. Jane accepts Elizabeth and the system opens a private chat thread for logistics and permissions (SM-9) and the system prompts evaluations (SM-10).
4. During the chat they explicitly agree which home the child will stay in during the session (Jane's home or Elizabeth's home), and the system records the chosen location and any special instructions or permissions.
5. Status transitions to "Scheduled" and reserved hours are held from Jane's balance (SM-8, TCS-3).
6. After the session they mark the need as complete; both confirm completion and the system transfers time credits to Elizabeth (TCS-5).

Requirement mapping: SM-7, SM-9, SM-8, TCS-5, SM-10, (TCS-3 implicitly referenced)

Acceptance criteria:
- Consumers can view applicants, accept one, and initiate a private message.
- The private chat supports recording of agreed location (home of consumer or provider) and any necessary permissions.
- Status updates follow the expected flow: Open -> Applied -> Scheduled -> In-progress -> Complete.
- Time credit reservation and transfer occur atomically on completion confirmation.
- Both parties can submit ratings; system prevents fake duplicate evaluations.

Edge cases:
- Provider cancels after acceptance (system offers rescheduling or refund path to consumer and releases reserved hours).
- Disagreement about location or permissions arises (system records pre-session agreement and offers mediation/escalation flow).
- Consumer fails to confirm completion (escalation/reminder flow to ensure fairness).

Pages:
- [x] User Profile Page / Public View
- [x] Approved Need Page (with status and messages)
- [x] Confirmation Need Form / Consumer View

## 5. Alex completes a moving-help request and checks balances and caps

- Primary persona: Alex Chen (The Curious Newcomer)
- Goal: Provide help with moving, confirm completion, see transferred time credits, and ensure balances respect caps.

Steps:
1. Alex is accepted for a moving-help need and the system reserves the agreed hours from the consumer (TCS-3).
2. He completes the job and both parties confirm completion (TCS-5).
3. System transfers hours and updates both users' balances; if Alex's new balance would exceed cap, credits are capped and overflow handled per policy (TCS-4).
4. Alex receives a short survey about consumer and the task (SM-11).
5. The updated balance is visible on Alex's profile (TCS-2).

Requirement mapping: TCS-3, TCS-5, TCS-2, TCS-4, SM-11

Acceptance criteria:
- Hour reservation prevents double-booking and shows in both user dashboards.
- Completion of mutual confirmation triggers the transfer of hours (or applies cap rules correctly).
- Balance display reflects new balance and any capped amounts with clear messaging.
- Provider receives and can submit the post-service survey.

Edge cases:
- Transfer would exceed recipient's balance cap (system credits up to cap and queues/returns remainder according to policy).
- One party disputes completion (initiates Admin moderation flow).
- Network or service failure during transfer (system retries and notifies users of transient state).

Pages:
- [x] Approved Need Status / Provider View
- [x] Confirmation Need Form / Provider View
- [x] User profile page / Owner

## 6. Elmira flags abusive content; Admin reviews and resolves

- Primary persona: Elmira McArthur (The Community Guardian) reporting; Admin persona (community moderator)
- Goal: Report content or user, have admin review, and take moderation actions if needed.

Steps:
1. Elmira flags a service listing and a message she deems abusive through the "Report" action.
2. The system creates a dispute ticket and notifies moderators (NFR-4).
3. An admin opens the admin dashboard, reviews the ticket, inspects the user history. (AM-1, AM-2).
4. Admin can take actions: warn user, temporary suspension, remove content, or escalate to full ban (AM-3).
5. Resolution is recorded, both reporter and affected user receive notifications, and any automated reversals (for time-credit transfers) are carried out if required.

Requirement mapping: NFR-4, AM-1, AM-2, AM-3

Acceptance criteria:
- Reports create auditable tickets and appear on the admin dashboard.
- Admins can view full context and execute moderation actions with confirmations.
- Users receive clear notices about outcomes and appeal instructions.

Edge cases:
- False reports (admin can mark as dismissed and optionally warn the reporter about misuse).
- Multiple simultaneous reports for the same content (system consolidates tickets for triage).
- Urgent safety issues (system supports priority routing and temporary automatic takedown while under review).

Pages:
- [] Admin Dashboard
- [] Admin Services View / Service View
- [] Admin Users View / User View
- [] Admin Reports View

# Persona List:

## 1) Alex Chen (The Curious Newcomer)
Alex is a 28-year-old freelance graphic designer who moved the neighborhood recently. He enjoys his work but feels disconnected from his new neighborhood. He's tech-savvy and active on local social media groups, which is where he discovered the time-banking platform. Intrigued by the idea of meeting people and trading skills without money, Alex decides to sign up. He's hoping to offer his design skills and maybe get some help assembling new furniture in return.

## 2) Jane Miller (The Parent & Student)
Jane Miller is a dedicated master's student and a mother to a lively 4.5-year-old daughter. With her husband working long hours, she often struggles to find a trustworthy babysitter for the evenings when her classes run late. She's hoping to find someone in her neighborhood and, in return, can offer her academic skills like proofreading or research help.

## 3) Austin Page (The Newcomer & Provider)
Austin Page is a college student living in a dorm, new to the city. To earn some time credits and connect with his new community, he's offering guitar lessons and help with household chores. He's a friendly and reliable individual hoping to make his new neighborhood feel more like home.

## 4) Elizabeth Taylor (The Senior & Community Pillar)
Elizabeth Taylor is a 70-year-old retiree who has lived in her home for over 40 years. Since her husband passed, she sometimes needs a hand with heavier chores like gardening or moving boxes. She's an avid art history enthusiast, loves talking about her grandchildren, and is eager to share her knowledge with a friendly neighbor.

## 5) Taylor Hope (The Energetic Teen)
Taylor Hope is an energetic 16-year-old high school student who's always on the move. When he's not playing basketball, he's looking to earn hours by running errands or making local deliveries on his bike. He's saving up his time credits to get tutoring for his upcoming math exams.

## 6) Elmira McArthur (The Community Guardian)
Elmira is a 45-year-old retired project manager who now runs a local community center. As one of the platform's founding members, she volunteers as an administrator because she is passionate about fostering a safe and fair environment for her neighbors. She is patient, detail-oriented, and has a strong sense of justice. Her main goal is to resolve conflicts thoughtfully to maintain trust within the community.
