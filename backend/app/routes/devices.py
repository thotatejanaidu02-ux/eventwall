from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from app.models import Device, JoinCode, Organization
from app.schemas import DeviceCreate, DeviceResponse, JoinCodeResponse, JoinCodeValidate, DeviceJoinResponse
from app.database import get_db
from app.routes.auth import verify_token
from app.utils import SecurityUtils
from datetime import datetime
from typing import List

router = APIRouter(prefix="/api/devices", tags=["devices"])

def get_current_org(authorization: str = Header(None), db: Session = Depends(get_db)):
    """Extract organization ID from JWT token"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid auth scheme")
        org_id = verify_token(token)
        
        org = db.query(Organization).filter(Organization.org_id == org_id).first()
        if not org or not org.is_active:
            raise HTTPException(status_code=403, detail="Organization not found")
        
        return org_id
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid token format")

@router.post("/generate-join-code", response_model=JoinCodeResponse)
def generate_join_code(
    device_name: str,
    org_id: str = Depends(get_current_org),
    db: Session = Depends(get_db)
):
    """Generate a unique join code for device onboarding"""
    
    # Generate unique code
    while True:
        code = SecurityUtils.generate_join_code()
        existing = db.query(JoinCode).filter(JoinCode.code == code).first()
        if not existing:
            break
    
    # Create join code
    join_code = JoinCode(
        code=code,
        org_id=org_id,
        device_name=device_name,
        expires_at=SecurityUtils.get_join_code_expiration()
    )
    
    db.add(join_code)
    db.commit()
    
    return JoinCodeResponse(
        code=code,
        expires_at=join_code.expires_at
    )

@router.post("/join", response_model=DeviceJoinResponse)
def device_join(
    join_data: JoinCodeValidate,
    db: Session = Depends(get_db)
):
    """Validate join code and register device"""
    
    # Find and validate join code
    join_code_record = db.query(JoinCode).filter(
        JoinCode.code == join_data.code
    ).first()
    
    if not join_code_record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid join code"
        )
    
    # Check if expired
    if join_code_record.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Join code expired"
        )
    
    # Check if already used
    if join_code_record.is_used:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Join code already used"
        )
    
    # Create device
    device_token = SecurityUtils.generate_device_token()
    new_device = Device(
        org_id=join_code_record.org_id,
        device_name=join_data.device_name,
        os_type=join_data.os_type,
        os_version=join_data.os_version,
        device_token=device_token,
        is_active=True,
        status="online"
    )
    
    db.add(new_device)
    
    # Mark join code as used
    join_code_record.is_used = True
    join_code_record.used_by_device_id = new_device.device_id
    join_code_record.used_at = datetime.utcnow()
    
    db.commit()
    db.refresh(new_device)
    
    return DeviceJoinResponse(
        device_id=new_device.device_id,
        device_token=device_token,
        org_id=new_device.org_id,
        status=new_device.status
    )

@router.get("/", response_model=List[DeviceResponse])
def list_devices(
    org_id: str = Depends(get_current_org),
    db: Session = Depends(get_db)
):
    """List all devices for organization"""
    devices = db.query(Device).filter(Device.org_id == org_id).all()
    return [DeviceResponse.from_orm(d) for d in devices]

@router.get("/{device_id}", response_model=DeviceResponse)
def get_device(
    device_id: str,
    org_id: str = Depends(get_current_org),
    db: Session = Depends(get_db)
):
    """Get device details"""
    device = db.query(Device).filter(
        Device.device_id == device_id,
        Device.org_id == org_id
    ).first()
    
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    return DeviceResponse.from_orm(device)

@router.delete("/{device_id}")
def revoke_device(
    device_id: str,
    org_id: str = Depends(get_current_org),
    db: Session = Depends(get_db)
):
    """Revoke/delete a device"""
    device = db.query(Device).filter(
        Device.device_id == device_id,
        Device.org_id == org_id
    ).first()
    
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    device.status = "revoked"
    device.is_active = False
    db.commit()
    
    return {"message": "Device revoked successfully"}
