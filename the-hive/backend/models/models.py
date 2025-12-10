"""
Database Models for The Hive Application
This module defines the data models used throughout the application.
All models are dataclasses that correspond to database tables.
"""

from dataclasses import dataclass
from datetime import datetime, date, time
from typing import Optional, Dict, Any
from decimal import Decimal


# ==================== USER MANAGEMENT MODELS ====================

@dataclass
class User:
    """User model representing a registered user in the system."""
    id: Optional[int] = None
    email: str = ""
    password_hash: str = ""
    first_name: str = ""
    last_name: str = ""
    phone_number: Optional[str] = None
    biography: Optional[str] = None
    profile_photo: Optional[str] = None
    role: str = "user"  # 'user' or 'admin'
    time_balance: Decimal = Decimal('1.0')
    is_verified: bool = False
    is_active: bool = True
    user_status: str = "active"  # 'active', 'banned', 'warning'
    date_joined: Optional[datetime] = None
    last_login: Optional[datetime] = None

    def full_name(self) -> str:
        """Get user's full name."""
        return f"{self.first_name} {self.last_name}".strip()

    def is_admin(self) -> bool:
        """Check if user is an admin."""
        return self.role == "admin"


@dataclass
class EmailVerification:
    """Email verification token model."""
    id: Optional[int] = None
    user_id: int = 0
    token: str = ""
    created_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    is_used: bool = False


@dataclass
class PasswordResetToken:
    """Password reset token model."""
    id: Optional[int] = None
    user_id: int = 0
    token: str = ""
    created_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    is_used: bool = False


# ==================== SERVICE MANAGEMENT MODELS ====================

@dataclass
class Service:
    """Service model representing both offers and needs."""
    id: Optional[int] = None
    user_id: int = 0
    service_type: str = "offer"  # 'offer' or 'need'
    title: str = ""
    description: str = ""
    hours_required: Decimal = Decimal('1.0')
    location_type: str = "online"  # 'online', 'in-person', 'both'
    location_address: Optional[str] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    status: str = "open"  # 'open', 'in_progress', 'completed', 'cancelled', 'expired'
    service_date: Optional[datetime] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def is_active(self) -> bool:
        """Check if service is open and accepting applications."""
        return self.status == "open"


@dataclass
class Tag:
    """Tag model for categorizing services."""
    id: Optional[int] = None
    name: str = ""
    created_by: Optional[int] = None
    is_approved: bool = True
    created_at: Optional[datetime] = None


@dataclass
class ServiceTag:
    """Junction table for service-tag relationship."""
    service_id: int = 0
    tag_id: int = 0


@dataclass
class ServiceAvailability:
    """Service availability schedule."""
    id: Optional[int] = None
    service_id: int = 0
    day_of_week: int = 0  # 0 = Monday, 6 = Sunday
    start_time: Optional[time] = None
    end_time: Optional[time] = None


# ==================== APPLICATION MANAGEMENT MODELS ====================

@dataclass
class ServiceApplication:
    """Application model for service requests."""
    id: Optional[int] = None
    service_id: int = 0
    applicant_id: int = 0
    status: str = "pending"  # 'pending', 'accepted', 'rejected', 'cancelled', 'withdrawn'
    message: Optional[str] = None
    applied_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def is_pending(self) -> bool:
        """Check if application is pending."""
        return self.status == "pending"

    def is_accepted(self) -> bool:
        """Check if application is accepted."""
        return self.status == "accepted"


@dataclass
class ServiceProgress:
    """Track progress of service delivery workflow."""
    id: Optional[int] = None
    service_id: int = 0
    application_id: int = 0
    provider_id: int = 0
    consumer_id: int = 0
    hours: Decimal = Decimal('1.0')
    status: str = "selected"  # 'selected', 'scheduled', 'in_progress', 'awaiting_confirmation', 'completed', 'disputed', 'cancelled'
    scheduled_date: Optional[date] = None
    scheduled_time: Optional[time] = None
    agreed_location: Optional[str] = None
    special_instructions: Optional[str] = None
    provider_confirmed: bool = False
    consumer_confirmed: bool = False
    provider_start_confirmed: bool = False
    consumer_start_confirmed: bool = False
    provider_start_confirmed_at: Optional[datetime] = None
    consumer_start_confirmed_at: Optional[datetime] = None
    proposed_date: Optional[date] = None
    proposed_time: Optional[time] = None
    proposed_location: Optional[str] = None
    proposed_by: Optional[int] = None
    proposed_at: Optional[datetime] = None
    schedule_accepted_by_consumer: bool = False
    schedule_accepted_by_provider: bool = False
    service_end_date: Optional[date] = None
    service_start_date: Optional[date] = None
    provider_survey_submitted: bool = False
    consumer_survey_submitted: bool = False
    provider_survey_submitted_at: Optional[datetime] = None
    consumer_survey_submitted_at: Optional[datetime] = None
    provider_survey_data: Optional[Dict[str, Any]] = None
    consumer_survey_data: Optional[Dict[str, Any]] = None
    survey_deadline: Optional[datetime] = None
    selected_at: Optional[datetime] = None
    scheduled_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# ==================== MESSAGING MODELS ====================

@dataclass
class Message:
    """Message model for user communications."""
    id: Optional[int] = None
    service_id: Optional[int] = None
    application_id: Optional[int] = None
    sender_id: int = 0
    receiver_id: int = 0
    message: str = ""
    is_read: bool = False
    message_type: str = "text"  # 'text', 'proposal', etc.
    proposal_date: Optional[date] = None
    proposal_start_time: Optional[time] = None
    proposal_end_time: Optional[time] = None
    proposal_location: Optional[str] = None
    proposal_status: str = "pending"  # 'pending', 'accepted', 'rejected'
    created_at: Optional[datetime] = None


# ==================== FORUM MODELS ====================

@dataclass
class ForumCategory:
    """Forum category model."""
    id: Optional[int] = None
    name: str = ""
    description: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class ForumThread:
    """Forum thread model for The Commons."""
    id: Optional[int] = None
    category_id: int = 0
    user_id: int = 0
    title: str = ""
    content: str = ""
    is_pinned: bool = False
    is_locked: bool = False
    view_count: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def is_editable(self) -> bool:
        """Check if thread can be edited."""
        return not self.is_locked


@dataclass
class ForumComment:
    """Forum comment/reply model."""
    id: Optional[int] = None
    thread_id: int = 0
    user_id: int = 0
    content: str = ""
    parent_comment_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def is_reply(self) -> bool:
        """Check if this is a reply to another comment."""
        return self.parent_comment_id is not None


# ==================== REPORTING AND MODERATION MODELS ====================

@dataclass
class Report:
    """Report model for flagging inappropriate content."""
    id: Optional[int] = None
    reporter_id: int = 0
    reported_user_id: Optional[int] = None
    content_type: str = "service"  # 'service', 'thread', 'comment', 'user', 'message'
    content_id: Optional[int] = None
    reason: str = ""
    description: Optional[str] = None
    status: str = "open"  # 'open', 'resolved', 'dismissed'
    resolved_by: Optional[int] = None
    resolved_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None
    created_at: Optional[datetime] = None

    def is_pending(self) -> bool:
        """Check if report is pending review."""
        return self.status == "open"


@dataclass
class AdminLog:
    """Admin action log model for audit trail."""
    id: Optional[int] = None
    admin_id: Optional[int] = None
    action: str = ""
    target_type: str = ""
    target_id: Optional[int] = None
    details: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    created_at: Optional[datetime] = None


# ==================== MODEL COLLECTIONS ====================

ALL_MODELS = [
    User,
    EmailVerification,
    PasswordResetToken,
    Service,
    Tag,
    ServiceTag,
    ServiceAvailability,
    ServiceApplication,
    ServiceProgress,
    Message,
    ForumCategory,
    ForumThread,
    ForumComment,
    Report,
    AdminLog,
]


# ==================== HELPER FUNCTIONS ====================

def validate_email(email: str) -> bool:
    """Validate email format."""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_time_range(start_time: str, end_time: str) -> bool:
    """Validate time range format (HH:MM)."""
    import re
    time_pattern = r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$'
    return bool(re.match(time_pattern, start_time) and re.match(time_pattern, end_time))


def validate_day_of_week(day: int) -> bool:
    """Validate day of week (0-6)."""
    return 0 <= day <= 6


def validate_hours(hours: float) -> bool:
    """Validate hours required is between 1.0 and 3.0."""
    return 1.0 <= hours <= 3.0