from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Device, Organization
from app.schemas import DeviceSyncRequest, DeviceSyncResponse, WallpaperGenerationRequest, WallpaperGenerationResponse
from app.services import DeviceSyncService, AIWallpaperService
from app.routes.auth import verify_token
from datetime import datetime
from typing import Optional

router = APIRouter(prefix="/api/sync", tags=["sync"])

def get_current_device(authorization: str = Header(None), db: Session = Depends(get_db)):
    """Extract device info from device token"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid auth scheme")
        
        device = db.query(Device).filter(Device.device_token == token).first()
        if not device:
            raise HTTPException(status_code=401, detail="Invalid device token")
        
        if not device.is_active:
            raise HTTPException(status_code=403, detail="Device is inactive")
        
        if device.status == "revoked":
            raise HTTPException(status_code=403, detail="Device has been revoked")
        
        return device
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid token format")

@router.post("/device", response_model=DeviceSyncResponse)
def device_sync(
    sync_request: DeviceSyncRequest,
    device: Device = Depends(get_current_device),
    db: Session = Depends(get_db)
):
    """Sync device with active events and wallpapers"""
    
    # Get active events for organization
    active_events = DeviceSyncService.get_active_events_for_device(
        db, device.org_id, device.device_id
    )
    
    if not active_events:
        DeviceSyncService.update_device_sync_status(db, device.device_id, "success")
        return {
            "active_events": [],
            "next_sync_time": 3600,  # 1 hour default
            "timestamp": datetime.utcnow()
        }
    
    # Prepare response
    response = DeviceSyncService.prepare_sync_response(
        active_events,
        active_events[0].rotation_interval if active_events else 60
    )
    
    # Update device sync status
    DeviceSyncService.update_device_sync_status(db, device.device_id, "success")
    
    return response

@router.post("/wallpaper/generate", response_model=WallpaperGenerationResponse)
async def generate_wallpaper(
    request: WallpaperGenerationRequest,
    device: Device = Depends(get_current_device),
    db: Session = Depends(get_db)
):
    """Generate AI wallpaper for event"""
    
    try:
        # Generate wallpaper
        image_url = await AIWallpaperService.generate_wallpaper(
            prompt=request.prompt,
            model=request.model,
            width=request.width,
            height=request.height
        )
        
        # Cache the wallpaper
        from app.models import WallpaperCache
        
        wallpaper = WallpaperCache(
            org_id=device.org_id,
            image_url=image_url,
            prompt=request.prompt,
            ai_model=request.model
        )
        db.add(wallpaper)
        db.commit()
        db.refresh(wallpaper)
        
        return WallpaperGenerationResponse(
            wallpaper_id=wallpaper.wallpaper_id,
            image_url=image_url,
            prompt=request.prompt,
            model=request.model,
            created_at=wallpaper.created_at
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Wallpaper generation failed: {str(e)}"
        )

@router.get("/device/status")
def device_status(
    device: Device = Depends(get_current_device),
    db: Session = Depends(get_db)
):
    """Get device status"""
    return {
        "device_id": device.device_id,
        "device_name": device.device_name,
        "os_type": device.os_type,
        "status": device.status,
        "last_sync": device.last_sync,
        "is_active": device.is_active
    }

@router.post("/device/ping")
def device_ping(
    device: Device = Depends(get_current_device),
    db: Session = Depends(get_db)
):
    """Device heartbeat/ping endpoint"""
    from datetime import datetime
    
    device.last_sync = datetime.utcnow()
    device.status = "online"
    db.commit()
    
    return {"status": "ok", "timestamp": datetime.utcnow()}
