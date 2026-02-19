"""Admin router – user management and system statistics."""

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from passlib.context import CryptContext  # type: ignore
from sqlalchemy.orm import Session

from dependencies import get_db
from models.user import User
from schemas.user import UserCreate, UserResponse

router = APIRouter(prefix="/api/admin", tags=["Admin"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.post("/users", response_model=UserResponse, status_code=201)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Create a new system user."""
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=409, detail="Email already registered")
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=409, detail="Username already taken")

    db_user = User(
        id=str(uuid.uuid4()),
        email=user.email,
        username=user.username,
        hashed_password=pwd_context.hash(user.password),
        full_name=user.full_name,
        role=user.role,
        preferred_language=user.preferred_language,
        created_at=datetime.utcnow(),
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/stats")
def system_stats(db: Session = Depends(get_db)):
    """Return high-level system statistics."""
    from models.audit_log import AuditLog
    from models.mrp_run import MRPRun
    from models.risk_record import RiskRecord

    return {
        "total_risk_records": db.query(RiskRecord).count(),
        "total_audit_logs": db.query(AuditLog).count(),
        "total_mrp_runs": db.query(MRPRun).count(),
        "total_users": db.query(User).count(),
        "quantum_safe": True,
    }
