# routers/audit_logs.py

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session
from models.audit_log import AuditLog
from auth.auth import get_db, write_permission
from models.user import User

router = APIRouter(
    prefix="/audit-logs",
    tags=["audit_logs"],
)

@router.get("/", response_model=List[dict])
def get_audit_logs(
    db: Session = Depends(get_db),
    current_user: User = Depends(write_permission),
):
    try:
        logs = db.query(AuditLog).all()
        return [
            {
                "id": log.id,
                "user_id": log.user_id,
                "action": log.action,
                "timestamp": log.timestamp,
                "details": log.details
            }
            for log in logs
        ]
    except:
        raise HTTPException(status_code=500, detail="Internal Server Error")
