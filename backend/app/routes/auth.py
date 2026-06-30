from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models import Organization
from app.schemas import OrganizationCreate, LoginRequest, LoginResponse, OrganizationResponse
from app.utils import SecurityUtils
from app.database import get_db
from datetime import datetime, timedelta
from jose import JWTError, jwt
from app.config import settings

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/register", response_model=OrganizationResponse)
def register(org_data: OrganizationCreate, db: Session = Depends(get_db)):
    """Register a new organization/admin"""
    
    # Check if email already exists
    existing_org = db.query(Organization).filter(Organization.email == org_data.email).first()
    if existing_org:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash password and create organization
    new_org = Organization(
        admin_name=org_data.admin_name,
        email=org_data.email,
        password_hash=SecurityUtils.hash_password(org_data.password),
        company_name=org_data.company_name
    )
    
    db.add(new_org)
    db.commit()
    db.refresh(new_org)
    
    return OrganizationResponse.from_orm(new_org)

@router.post("/login", response_model=LoginResponse)
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    """Login an admin/organization"""
    
    # Find organization by email
    org = db.query(Organization).filter(Organization.email == credentials.email).first()
    
    if not org or not SecurityUtils.verify_password(credentials.password, org.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    if not org.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Organization account is inactive"
        )
    
    # Generate JWT token
    access_token = create_access_token(
        data={"sub": org.org_id, "email": org.email, "type": "org"}
    )
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=OrganizationResponse.from_orm(org)
    )

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt

def verify_token(token: str):
    """Verify JWT token"""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        org_id: str = payload.get("sub")
        if org_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return org_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
