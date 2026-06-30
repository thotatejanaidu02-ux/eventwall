from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from datetime import datetime
from app.models import Event, Organization, Device
from app.schemas import EventCreate, EventUpdate, EventResponse
from app.database import get_db
from app.routes.auth import verify_token
from typing import List

router = APIRouter(prefix="/api/events", tags=["events"])

def get_current_org(authorization: str = Header(None), db: Session = Depends(get_db)):
    """Extract organization ID from JWT token"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid auth scheme")
        org_id = verify_token(token)
        
        # Verify organization exists and is active
        org = db.query(Organization).filter(Organization.org_id == org_id).first()
        if not org or not org.is_active:
            raise HTTPException(status_code=403, detail="Organization not found or inactive")
        
        return org_id
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid token format")

@router.post("/", response_model=EventResponse)
def create_event(
    event_data: EventCreate,
    org_id: str = Depends(get_current_org),
    db: Session = Depends(get_db)
):
    """Create a new wallpaper event"""
    
    # Validate dates
    if event_data.start_date >= event_data.end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="start_date must be before end_date"
        )
    
    # Create event
    new_event = Event(
        org_id=org_id,
        title=event_data.title,
        description=event_data.description,
        ai_prompt=event_data.ai_prompt,
        wallpaper_urls=event_data.wallpaper_urls,
        rotation_interval=event_data.rotation_interval,
        start_date=event_data.start_date,
        end_date=event_data.end_date
    )
    
    db.add(new_event)
    db.commit()
    db.refresh(new_event)
    
    return EventResponse.from_orm(new_event)

@router.get("/", response_model=List[EventResponse])
def list_events(
    org_id: str = Depends(get_current_org),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 50
):
    """List all events for organization"""
    events = db.query(Event).filter(Event.org_id == org_id).offset(skip).limit(limit).all()
    return [EventResponse.from_orm(e) for e in events]

@router.get("/{event_id}", response_model=EventResponse)
def get_event(
    event_id: str,
    org_id: str = Depends(get_current_org),
    db: Session = Depends(get_db)
):
    """Get a specific event"""
    event = db.query(Event).filter(
        Event.event_id == event_id,
        Event.org_id == org_id
    ).first()
    
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    return EventResponse.from_orm(event)

@router.put("/{event_id}", response_model=EventResponse)
def update_event(
    event_id: str,
    event_update: EventUpdate,
    org_id: str = Depends(get_current_org),
    db: Session = Depends(get_db)
):
    """Update an event"""
    event = db.query(Event).filter(
        Event.event_id == event_id,
        Event.org_id == org_id
    ).first()
    
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Update fields
    update_data = event_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(event, field, value)
    
    event.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(event)
    
    return EventResponse.from_orm(event)

@router.delete("/{event_id}")
def delete_event(
    event_id: str,
    org_id: str = Depends(get_current_org),
    db: Session = Depends(get_db)
):
    """Delete an event"""
    event = db.query(Event).filter(
        Event.event_id == event_id,
        Event.org_id == org_id
    ).first()
    
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    db.delete(event)
    db.commit()
    
    return {"message": "Event deleted successfully"}
