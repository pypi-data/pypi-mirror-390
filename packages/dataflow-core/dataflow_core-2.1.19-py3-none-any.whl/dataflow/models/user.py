"""models.py"""
from sqlalchemy import Column, Integer, String, Boolean, LargeBinary, Enum, ForeignKey, DateTime, func
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy import Index
from sqlalchemy.orm import relationship
from dataflow.db import Base
import enum

class User(Base):
    """Table USER

    Attributes:
        user_id (int): Primary key for the user entry.
        user_name (str): Unique username for the user.
        first_name (str): First name of the user.
        last_name (str): Last name of the user.
        email (str): Unique email address of the user.
        image (LargeBinary): Binary data for the user's profile image.
        image_url (str): URL for the user's profile image.  
        active (bool): Flag indicating whether the user is active.
        password (str): Hashed password for the user.
        active_org_id (int): Foreign key referencing the active organization of the user.
    
    Relationships:
        org_user_assocs: Relationship to OrganizationUser model.
        teams: Many-to-many relationship with Team model via USER_TEAM association table.
        onboarding_requests: Relationship to UserOnboarding model.
        organization_onboarding: Relationship to OrganizationOnboarding model.  
    """

    __tablename__ = 'USER'

    user_id = Column(Integer, primary_key=True, index=True, autoincrement=True, nullable=False)
    user_name = Column(String, unique=True, nullable=False)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True)
    image = Column(LargeBinary)
    image_url = Column(String, nullable=True)
    active = Column(Boolean, nullable=False, default=True, server_default='true')
    password = Column(String, nullable=False)
    active_org_id = Column(Integer, ForeignKey('ORGANIZATION.id'))
    is_super_admin = Column(Boolean, nullable=False, default=False, server_default='false')

    # Relationships
    org_user_assocs = relationship("OrganizationUser", back_populates="user", cascade="all, delete-orphan")
    teams = relationship("Team", secondary="USER_TEAM", back_populates="users")
    onboarding_requests = relationship("UserOnboarding", back_populates="user", cascade="all, delete-orphan")
    organization_onboarding = relationship("OrganizationOnboarding", back_populates="user", cascade="all, delete-orphan")


class OnboardingStatus(enum.Enum):

    """Enumeration for onboarding application status."""

    pending = 'pending'
    rejected = 'rejected'
    accepted = 'accepted'

class UserOnboarding(Base):
    """TABLE 'USER_ONBOARDING'

    Attributes:
        id (int): Primary key for the user onboarding entry.
        user_id (int): Foreign key referencing the USER table.
        org_id (int): Foreign key referencing the ORGANIZATION table.
        status (OnboardingStatus): Current status of the onboarding application.
        created_at (datetime): Timestamp of when the onboarding entry was created.
        updated_at (datetime): Timestamp of the last update to the onboarding entry.
    
    Relationships:
        user: Relationship to the User model.
        organization: Relationship to the Organization model.
    
    Constraints:
        Index: Ensures unique applications based on user and organization.
    """

    __tablename__ = "USER_ONBOARDING"
    __table_args__ = (
        Index(
            'idx_pending_user_org_application',
            'user_id',
            'org_id',
            unique=True,
            postgresql_where=Column('status').in_([
                OnboardingStatus.pending.value,
                OnboardingStatus.accepted.value
            ])
        ),
    )

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = Column(Integer, ForeignKey("USER.user_id", ondelete="CASCADE"), nullable=False)
    org_id = Column(Integer, ForeignKey("ORGANIZATION.id", ondelete="CASCADE"), nullable=False)
    status = Column(Enum(OnboardingStatus, name='onboarding_status'), nullable=False, default=OnboardingStatus.pending.value, server_default='pending')
    created_at = Column(DateTime, default=func.now(), nullable=False, server_default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False, server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="onboarding_requests")
    organization = relationship("Organization", back_populates="onboarding_requests")