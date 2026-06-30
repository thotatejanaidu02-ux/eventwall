from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import List, Optional

# Organization Schemas
class OrganizationCreate(BaseModel):
    admin_name: str
    email: EmailStr
    password: str
    company_name: Optional[str] = None

class OrganizationResponse(BaseModel):
    org_id: str
    admin_name: str
    email: str
    company_name: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

# Event Schemas
class EventCreate(BaseModel):
    title: str
    description: Optional[str] = None
    ai_prompt: Optional[str] = None
    wallpaper_urls: Optional[List[str]] = []
    rotation_interval: int = Field(default=60, ge=5, le=1440)
    start_date: datetime
    end_date: datetime

class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    rotation_interval: Optional[int] = None
    is_active: Optional[bool] = None

class EventResponse(BaseModel):
    event_id: str
    org_id: str
    title: str
    description: Optional[str]
    wallpaper_urls: List[str]
    rotation_interval: int
    start_date: datetime
    end_date: datetime
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Device Schemas
class DeviceCreate(BaseModel):
    device_name: str
    os_type: str
    os_version: Optional[str] = None

class DeviceResponse(BaseModel):
    device_id: str
    org_id: str
    device_name: str
    os_type: str
    status: str
    last_sync: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True

# Join Code Schemas
class JoinCodeResponse(BaseModel):
    code: str
    expires_at: datetime

class JoinCodeValidate(BaseModel):
    code: str
    device_name: str
    os_type: str
    os_version: Optional[str] = None

class DeviceJoinResponse(BaseModel):
    device_id: str
    device_token: str
    org_id: str
    status: str

# Authentication Schemas
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: OrganizationResponse

class DeviceAuthRequest(BaseModel):
    device_id: str
    device_token: str

class DeviceAuthResponse(BaseModel):
    access_token: str
    token_type: str
    org_id: str

# AI Generation Schemas
class WallpaperGenerationRequest(BaseModel):
    prompt: str
    model: str = "flux"  # 'flux', 'stable_diffusion', 'grok'
    width: int = 1920
    height: int = 1080

class WallpaperGenerationResponse(BaseModel):
    wallpaper_id: str
    image_url: str
    prompt: str
    model: str
    created_at: datetime

# Sync Schemas
class DeviceSyncRequest(BaseModel):
    device_id: str
    current_wallpaper_url: Optional[str] = None

class ActiveEvent(BaseModel):
    event_id: str
    title: str
    wallpaper_urls: List[str]
    rotation_interval: int

class DeviceSyncResponse(BaseModel):
    active_events: List[ActiveEvent]
    next_sync_time: int  # seconds
    timestamp: datetime
