"""
Request/Response Models for API validation.

This module defines Pydantic models for all API endpoints to ensure
proper input validation and type safety.
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, validator
from datetime import datetime


class UploadRequest(BaseModel):
    """Model for file upload validation."""
    # File validation happens at FastAPI level with UploadFile
    pass


class ProfileUpdateRequest(BaseModel):
    """Model for profile update requests."""
    full_name: Optional[str] = Field(None, max_length=100, description="User's full name")
    company_name: Optional[str] = Field(None, max_length=100, description="Company name")
    job_title: Optional[str] = Field(None, max_length=100, description="Job title")
    phone: Optional[str] = Field(None, max_length=20, description="Phone number")
    use_case: Optional[str] = Field(None, max_length=500, description="Use case description")
    
    @validator('phone')
    def validate_phone(cls, v):
        if v and not v.replace('+', '').replace('-', '').replace(' ', '').replace('(', '').replace(')', '').isdigit():
            raise ValueError('Invalid phone number format')
        return v
    
    @validator('full_name', 'company_name', 'job_title')
    def validate_text_fields(cls, v):
        if v and len(v.strip()) == 0:
            raise ValueError('Field cannot be empty or whitespace only')
        return v.strip() if v else v


class BookmarkRequest(BaseModel):
    """Model for bookmark operations."""
    project_id: str = Field(..., description="Project ID to bookmark")
    
    @validator('project_id')
    def validate_project_id(cls, v):
        # Basic UUID format validation
        if not v or len(v) != 36:
            raise ValueError('Invalid project ID format')
        return v


class ApiKeyCreateRequest(BaseModel):
    """Model for API key creation."""
    key_name: str = Field(..., min_length=1, max_length=50, description="Name for the API key")
    expires_days: Optional[int] = Field(30, ge=1, le=365, description="Days until expiration")
    
    @validator('key_name')
    def validate_key_name(cls, v):
        if not v.strip():
            raise ValueError('API key name cannot be empty')
        # Only allow alphanumeric, spaces, hyphens, underscores
        import re
        if not re.match(r'^[a-zA-Z0-9\s\-_]+$', v):
            raise ValueError('API key name contains invalid characters')
        return v.strip()


class LoginRequest(BaseModel):
    """Model for login requests."""
    email: str = Field(..., description="User email")
    password: str = Field(..., min_length=8, description="User password")
    
    @validator('email')
    def validate_email(cls, v):
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, v):
            raise ValueError('Invalid email format')
        return v.lower().strip()


class RegisterRequest(BaseModel):
    """Model for registration requests."""
    email: str = Field(..., description="User email")
    password: str = Field(..., min_length=8, description="User password")
    full_name: Optional[str] = Field(None, max_length=100, description="User's full name")
    
    @validator('email')
    def validate_email(cls, v):
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, v):
            raise ValueError('Invalid email format')
        return v.lower().strip()
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        # Check for at least one letter and one number
        import re
        if not re.search(r'[A-Za-z]', v) or not re.search(r'\d', v):
            raise ValueError('Password must contain at least one letter and one number')
        return v


class PasswordResetRequest(BaseModel):
    """Model for password reset requests."""
    email: str = Field(..., description="User email")
    
    @validator('email')
    def validate_email(cls, v):
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, v):
            raise ValueError('Invalid email format')
        return v.lower().strip()


class PasswordUpdateRequest(BaseModel):
    """Model for password update requests."""
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password")
    
    @validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        import re
        if not re.search(r'[A-Za-z]', v) or not re.search(r'\d', v):
            raise ValueError('Password must contain at least one letter and one number')
        return v


# Response Models

class ApiResponse(BaseModel):
    """Base API response model."""
    success: bool = True
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None


class ErrorResponse(BaseModel):
    """Error response model."""
    success: bool = False
    error: str
    details: Optional[Dict[str, Any]] = None


class ProjectResponse(BaseModel):
    """Project response model."""
    id: str
    name: str
    status: str
    uploaded_at: datetime
    analysis_completed_at: Optional[datetime] = None


class UserStatsResponse(BaseModel):
    """User statistics response model."""
    total_reports: int
    total_tokens_saved: int
    estimated_time_saved_hours: float
    total_projects: int
    completed_projects: int


class UsageResponse(BaseModel):
    """Usage statistics response model."""
    credits_consumed: int
    credits_remaining: int
    credits_granted: int
    overage_analyses_count: int
    storage_bytes_used: int
    period_start: str
    period_end: str