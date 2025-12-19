# Release Notes
## The Hive - Community TimeBank Platform
### Version 0.9.2

**Release Date:** December 15, 2025  
**Release Type:** Beta Release  
**Author:** M. Zeynep Çakmakcı  
**Project:** SWE 573 - Software Development Practice  
**Institution:** Boğaziçi University  
**Instructor:** Suzan Üskdarlı

---

## Table of Contents
1. [Release Overview](#release-overview)
2. [What's New in v0.9.2](#whats-new-in-v092)
3. [Features Delivered](#features-delivered)
4. [Fixed Bugs](#fixed-bugs)
5. [Known Bugs & Limitations](#known-bugs--limitations)
6. [System Requirements](#system-requirements)
7. [Installation & Upgrade](#installation--upgrade)
8. [Breaking Changes](#breaking-changes)

---

## Release Overview

Version 0.9.2 represents a significant milestone in The Hive platform's development, delivering **core TimeBank functionality** with **schedule proposal system** and **balance validation**. This release completes Phase 1 and Phase 2 of the development roadmap, providing a fully functional TimeBank platform for community service exchange.

### Release Highlights
- ✅ **Complete Schedule Proposal System** with balance validation
- ✅ **Dual-Start Confirmation** for services
- ✅ **TimeBank Balance Cap** enforcement (10-hour maximum)
- ✅ **Mutual Completion Confirmation** workflow
- ✅ **Map-Based Service Discovery** with filtering
- ✅ **Private Messaging** between matched users
- ✅ **Evaluation & Rating System**
- 🆕 **Admin Dashboard** (implemented, testing in progress)
- 🆕 **Community Forum** (implemented, testing in progress)


---

## What's New in v0.9.2

### Major Features

#### 🎯 Schedule Proposal System with Balance Validation
**The most significant addition in v0.9.2**

The new Schedule Proposal system offers:

- **Either party can propose schedules**: Consumer or Provider can initiate scheduling
- **Real-time balance validation**: System checks both parties' balances before acceptance
- **Consumer balance check**: Prevents scheduling if consumer doesn't have sufficient hours
- **Provider max balance enforcement**: Prevents scheduling if it would exceed provider's 10-hour cap
- **Clear error messages**: Users receive detailed explanations when proposals can't be accepted
- **Proposal history**: View all pending and historical proposals
- **Notification system**: Automatic notifications when proposals are created or accepted

**Balance Validation Rules:**
```
✅ Accept Conditions:
   - Consumer balance >= service hours
   - Provider balance + service hours <= 10 hours

❌ Reject Conditions:
   - Consumer balance < service hours → "Insufficient balance"
   - Provider balance + service hours > 10 → "Would exceed maximum balance"
```

#### 🚀 Dual-Start Confirmation
New safety feature for service execution:

- Both Consumer and Provider must confirm service start
- Prevents misunderstandings about service timing
- Tracks confirmation status separately for each party
- Service officially "in progress" only after both confirmations

#### ✅ Mutual Completion Confirmation
Enhanced completion workflow:

- Provider marks service as complete
- Consumer must confirm completion
- Hours transfer only after both confirmations
- Post-completion survey for both parties

#### 🛡️ Admin Dashboard (Beta)
**Status**: Implemented, testing in progress

New administrative capabilities:
- User management interface
- Service moderation tools
- Content deactivation with reasons
- User warnings and bans
- Semantic tag management
- Audit logging for all admin actions
- Dashboard analytics overview

**Note**: This feature is implemented but comprehensive testing is ongoing. Use with caution in production environments.

#### 💬 Community Forum - "The Commons" (Beta)
**Status**: Implemented, testing in progress

Foster community engagement:
- Admin-defined forum categories
- Create discussion threads
- Post comments and replies
- Rich text formatting
- Edit/delete own posts
- Report inappropriate content
- Lock and pin threads (admin only)
- Search within forums

**Note**: This feature is implemented but comprehensive testing is ongoing. Use with caution in production environments.

---

## Features Delivered

### Phase 1 - MVP (Completed in v0.9.1)
✅ **Feature 1: User Registration & Authentication**
- Email-based registration with verification
- Secure JWT authentication
- Password strength requirements
- Date of birth validation

✅ **Feature 2: Profile Management**
- User profiles with bio and contact info
- Public/private information separation
- Phone number validation
- Profile photo upload support

✅ **Feature 3 & 4: Service Creation**
- Create Offers (services to provide)
- Create Needs (services requested)
- Semantic tagging (Wikibase integration)
- Time estimation (1-3 hours)
- Location type (online/in-person)
- Service validation

✅ **Feature 5: Service Discovery**
- Interactive map display
- Filter by semantic tags
- Filter by distance radius
- Filter by estimated hours
- Keyword search
- List view alternative

✅ **Feature 6: Provider Applications**
- Apply to fulfill Needs
- Application notifications
- Duplicate prevention
- Application status tracking

✅ **Feature 7: Provider Selection**
- View all applications
- View Provider profiles and ratings
- Select Provider from applicants
- Automatic private messaging on selection

✅ **Feature 8: TimeBank System (Basic)**
- 1-hour initial credit for new users
- Real-time balance display
- Transaction history
- 1:1 hour exchange rate

✅ **Feature 9: Evaluation & Rating**
- Consumer rates Provider
- Provider rates Consumer
- Post-service surveys
- Average rating display
- Recent reviews visible

✅ **Feature 10: Private Messaging**
- Automatic channel creation on match
- Send/receive text messages
- Message notifications
- Message history
- Unread indicators
- Archived threads after completion

### Phase 2 - Core Features (Completed in v0.9.2)
✅ **Feature 11: Schedule Proposal System** ⭐ NEW
- Create schedule proposals (either party)
- Real-time balance validation
- Consumer insufficient balance check
- Provider max balance cap enforcement
- View pending proposals
- Accept/reject with validation
- Schedule notifications
- Recorded schedule details
- Dual start confirmation
- Mutual completion confirmation

✅ **Feature 8: TimeBank System (Enhanced)** ⭐ ENHANCED
- Consumer balance validation on proposal acceptance
- Provider 10-hour maximum balance cap
- Automatic credit transfer on completion
- Auto-confirmation after 48 hours
- Atomic transactions for data integrity
- Balance warnings and notifications

### Phase 3 - Community Features (Partially Complete)
🆕 **Feature 12: Admin Dashboard** ⚠️ BETA
- User management
- Service moderation
- Content deactivation
- User warnings/bans
- Tag management
- Audit logging
- **Status**: Implemented, testing in progress

🆕 **Feature 13: Community Forum** ⚠️ BETA
- Forum categories
- Discussion threads
- Post/comment system
- Rich text formatting
- Content reporting
- Thread management (lock/pin)
- Forum search
- **Status**: Implemented, testing in progress

---

## Fixed Bugs

### High Priority Fixes

#### BUG-001: Balance Cap Not Enforced (v0.9.1)
**Severity:** High  
**Status:** ✅ Fixed in v0.9.2  
**Description:** Provider balance could exceed 10 hours on service completion.  
**Resolution:** 
- Added validation in schedule acceptance workflow
- Added validation in completion workflow
- System now rejects proposals that would exceed cap
- Clear error messages for users

#### BUG-002: Duplicate Applications Allowed (v0.9.1)
**Severity:** High  
**Status:** ✅ Fixed in v0.9.2  
**Description:** Provider could apply multiple times to same Need.  
**Resolution:** 
- Added unique constraint on (provider_id, service_id) in applications table
- Added frontend validation to prevent duplicate submissions
- User-friendly error message when attempting duplicate

#### BUG-003: Balance Validation Missing on Schedule Acceptance (v0.9.1)
**Severity:** High  
**Status:** ✅ Fixed in v0.9.2  
**Description:** Users could accept schedules without sufficient balance or exceeding cap.  
**Resolution:** 
- Implemented comprehensive balance validation in proposal acceptance endpoint
- Added consumer insufficient balance check
- Added provider max balance cap check
- Real-time validation before database commit

### Medium Priority Fixes

#### BUG-004: Schedule Confirmation Messages Not Displaying
**Severity:** Medium  
**Status:** ✅ Fixed in v0.9.2  
**Description:** Schedule confirmation messages sometimes didn't display immediately.  
**Resolution:** 
- Fixed UI refresh logic for schedule confirmations
- Added real-time notification updates
- Improved WebSocket message handling

#### BUG-005: Survey Data JSON Validation
**Severity:** Medium  
**Status:** ✅ Fixed in v0.9.2  
**Description:** Survey submissions with special characters failed validation.  
**Resolution:** 
- Improved JSON escaping for survey text fields
- Added input sanitization
- Enhanced error handling for malformed data

#### BUG-006: Service Status Transition Logic
**Severity:** Medium  
**Status:** ✅ Fixed in v0.9.2  
**Description:** Services could transition to invalid states.  
**Resolution:** 
- Implemented state machine for service lifecycle
- Added validation for valid status transitions
- Prevented manual manipulation of service status

### Low Priority Fixes

#### BUG-007: Map Marker Click Precision
**Severity:** Low  
**Status:** ✅ Fixed in v0.9.2  
**Description:** Difficult to click map markers when many services in same location.  
**Resolution:** 
- Improved marker click handling
- Added slight offset for overlapping markers
- Note: Full clustering solution planned for v1.1

---

## Known Bugs & Limitations

### Known Issues

#### ISSUE-001: Message Thread Pagination Missing
**Severity:** Low  
**Status:** Open  
**Impact:** Message threads with 50+ messages load slowly and don't paginate.  
**Workaround:** Keep conversations concise.  

#### ISSUE-002: Map Marker Clustering Not Implemented
**Severity:** Low  
**Status:** Open  
**Impact:** Map markers overlap in areas with high service density.  
**Workaround:** Use list view instead of map view.  

#### ISSUE-003: Email Notifications Not Implemented
**Severity:** Medium  
**Status:** Not Implemented  
**Description:** Email notification system is not implemented in v0.9.2. Users do not receive email notifications for important events such as service applications, schedule proposals, messages, or service completions.  
**Impact:** Users must rely on in-app notifications and manual checking for updates.  
**Workaround:** In-app notifications work correctly for all user interactions. Users receive real-time notifications within the application.  
**Future Implementation:** Email notification system is planned for v1.1 release and will include:
- Email verification during registration
- Service application notifications
- Schedule proposal notifications
- New message alerts
- Service completion confirmations
- Weekly activity summaries


---

## System Requirements

### Server Requirements

**Operating System:**
- Ubuntu 20.04 LTS or higher (recommended)
- macOS 12 (Monterey) or higher
- Windows 10/11 via Docker or WSL2

**Hardware (Minimum):**
- CPU: 2 cores, 2.0 GHz
- RAM: 2 GB
- Storage: 10 GB free space

**Hardware (Recommended):**
- CPU: 4 cores, 2.5 GHz or higher
- RAM: 4 GB or higher
- Storage: 50 GB SSD

**Software:**
- Python 3.10 or higher
- PostgreSQL 14 or higher
- Docker 20.10+ (if using Docker deployment)
- Docker Compose 1.29+ (if using Docker deployment)

### Client Requirements

**Web Browser:**
- Chrome 90+ (recommended)
- Firefox 88+
- Safari 14+
- Edge 90+

**Browser Features:**
- JavaScript enabled
- Cookies enabled
- Local Storage enabled
- Geolocation API (optional)

**Device:**
- Desktop/Laptop: 1280x720 minimum resolution
- Tablet: 7 inches or larger
- Mobile: 5 inches or larger (responsive design, not extensively tested)

**Network:**
- Minimum: 5 Mbps download, 1 Mbps upload
- Recommended: 25 Mbps download, 5 Mbps upload

---

## Installation & Upgrade

### Fresh Installation

#### Option 1: Docker Deployment (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd the-hive

# Copy environment file
cp .env.example .env

# Edit .env with your configuration
nano .env

# Build and start containers
docker-compose up -d --build

# Initialize database
docker-compose exec backend python3 reset_db.py

# Access at http://localhost:5000
```

#### Option 2: Manual Installation

```bash
# Install system dependencies (Ubuntu)
sudo apt-get update
sudo apt-get install python3.10 python3-pip postgresql-14

# Clone repository
git clone <repository-url>
cd the-hive/backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Configure database
sudo -u postgres createdb hive_db
sudo -u postgres createuser hive_user

# Set up environment
cp .env.example .env
nano .env

# Initialize database
python3 reset_db.py

# Run application
flask run
```

### Upgrading from v0.9.1 to v0.9.2

⚠️ **Important:** This upgrade includes database schema changes. Backup your database before upgrading!

```bash
# 1. Backup database
pg_dump hive_db > backup_v0.9.1_$(date +%Y%m%d).sql

# 2. Stop the application
docker-compose down  # if using Docker
# or
sudo systemctl stop hive  # if using systemd

# 3. Pull latest code
git fetch
git checkout v0.9.2

# 4. Update dependencies
docker-compose build  # if using Docker
# or
pip install -r requirements.txt  # if manual

# 5. Run database migration
# No migration script provided - clean reset recommended for beta
python3 reset_db.py  # WARNING: Clears all data

# 6. Start application
docker-compose up -d  # if using Docker
# or
flask run  # if manual

# 7. Verify upgrade
# Check logs for errors
docker-compose logs -f  # if using Docker
```

**Migration Notes:**
- v0.9.2 includes new database tables for schedule proposals
- v0.9.2 adds admin and forum tables
- Existing user accounts and services are compatible
- Message history is compatible
- TimeBank transactions are compatible

---

## Breaking Changes

### Database Schema Changes

#### New Tables Added:
- `schedule_proposals` - Stores schedule proposals with balance validation
- `admin_actions` - Audit log for admin activities
- `forum_categories` - Forum category definitions
- `forum_threads` - Discussion threads
- `forum_posts` - Individual posts in threads
- `content_reports` - User-submitted content reports

#### Modified Tables:
- `services` table: Added `schedule_proposal_id` foreign key
- `service_progress` table: Added `start_confirmed_by_consumer`, `start_confirmed_by_provider` columns
- `service_progress` table: Added `completion_confirmed_by_consumer`, `completion_confirmed_by_provider` columns

#### Removed Tables:
- `reserved_hours` table (replaced by schedule_proposals)

### API Changes

#### New Endpoints:
- `POST /api/services/propose-schedule` - Create schedule proposal
- `GET /api/services/:id/proposals` - Get proposals for service
- `POST /api/services/proposals/:id/accept` - Accept proposal with validation
- `POST /api/services/proposals/:id/reject` - Reject proposal
- `POST /api/admin/*` - Admin endpoints (multiple)
- `POST /api/forum/*` - Forum endpoints (multiple)

#### Modified Endpoints:
- `POST /api/services/:id/start-confirm` - Now requires dual confirmation
- `POST /api/services/:id/complete-confirm` - Enhanced with mutual confirmation

---

## Support & Feedback

### Reporting Issues

**For Bugs:**
1. Check if issue is listed in "Known Bugs" section
2. Search existing GitHub issues
3. Create new issue with:
   - Version number (v0.9.2)
   - Steps to reproduce
   - Expected vs actual behavior
   - Screenshots if applicable
   - Browser/device information

**For Feature Requests:**
- Check "What's Coming Next" section
- Submit feature request via GitHub Issues
- Include use case and rationale

### Getting Help

- **Documentation:** See `INSTALL.md` for installation help
- **Wiki:** Project wiki for guides and tutorials
- **Issues:** GitHub Issues for bug reports
- **Discussions:** GitHub Discussions for questions

---

## Acknowledgments

### Contributors
- **M. Zeynep Çakmakcı** - Lead Developer & Project Manager

### Special Thanks
- **Suzan Üskdarlı** - Academic Instructor & Project Advisor
- **SWE 573 Course** - Boğaziçi University, Fall 2025

---

## License

This project is developed as part of academic coursework for SWE 573 - Software Development Practice at Boğaziçi University.

---

## Document Information

**Version:** 0.9.2  
**Date:** December 15, 2025  
**Author:** M. Zeynep Çakmakcı  
**Status:** Beta Release  

---

**For detailed technical documentation, see:**
- Software Requirements Specification v3.0
- System Requirements Document
- Installation Guide (INSTALL.md)
- API Documentation

**For testing information, see:**
- [Test Plan](Test-Plan.md)
- [Test Cases](Test-Cases.md)
- [Test Results Report](Test-Results-Report.md)

---

**End of Release Notes v0.9.2**
