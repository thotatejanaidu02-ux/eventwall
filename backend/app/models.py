from sqlalchemy import Column, String, DateTime, Boolean, Integer, Text, Float, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()

class Organization(Base):
    """Parent/Admin organization account"""
    __tablename__ = "organizations"
    
    org_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    admin_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    company_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Event(Base):
    """Scheduled wallpaper events"""
    __tablename__ = "events"
    
    event_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    org_id = Column(String, nullable=False, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    wallpaper_urls = Column(ARRAY(String), default=[])
    ai_prompt = Column(Text, nullable=True)  # For AI-generated wallpapers
    rotation_interval = Column(Integer, default=60)  # minutes
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Device(Base):
    """Child endpoint devices"""
    __tablename__ = "devices"
    
    device_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    org_id = Column(String, nullable=False, index=True)
    device_name = Column(String, nullable=False)
    os_type = Column(String, nullable=False)  # 'windows', 'macos', 'android', 'ios'
    os_version = Column(String, nullable=True)
    join_code = Column(String, unique=True, nullable=True, index=True)
    device_token = Column(String, unique=True, nullable=True, index=True)
    is_active = Column(Boolean, default=False)
    status = Column(String, default="offline")  # 'online', 'offline', 'revoked'
    last_sync = Column(DateTime, nullable=True)
    last_ip = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class JoinCode(Base):
    """Temporary join codes for device onboarding"""
    __tablename__ = "join_codes"
    
    code = Column(String, primary_key=True)
    org_id = Column(String, nullable=False, index=True)
    device_name = Column(String, nullable=True)
    is_used = Column(Boolean, default=False)
    used_by_device_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    used_at = Column(DateTime, nullable=True)

class WallpaperCache(Base):
    """Local cache for generated/uploaded wallpapers"""
    __tablename__ = "wallpaper_cache"
    
    wallpaper_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    event_id = Column(String, nullable=False, index=True)
    org_id = Column(String, nullable=False, index=True)
    image_url = Column(String, nullable=False)
    file_path = Column(String, nullable=True)
    prompt = Column(Text, nullable=True)
    ai_model = Column(String, nullable=True)  # 'replicate', 'vertex_ai', 'uploaded'
    size = Column(Float, nullable=True)  # file size in MB
    created_at = Column(DateTime, default=datetime.utcnow)

class DeviceSyncLog(Base):
    """Log of device syncs and wallpaper updates"""
    __tablename__ = "device_sync_logs"
    
    log_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    device_id = Column(String, nullable=False, index=True)
    org_id = Column(String, nullable=False, index=True)
    event_id = Column(String, nullable=True)
    wallpaper_url = Column(String, nullable=True)
    status = Column(String)  # 'success', 'failed', 'pending'
    error_message = Column(Text, nullable=True)
    sync_timestamp = Column(DateTime, default=datetime.utcnow)
