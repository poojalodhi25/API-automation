"""Analytics API."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import db_is_ready, get_db
from app.services.analytics import build_analytics

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("")
def analytics(db: Session = Depends(get_db)):
    if not db_is_ready():
        raise HTTPException(status_code=503, detail="MySQL is not connected")
    stats = build_analytics(db)
    stats.pop("recent", None)
    return {"status": "success", "stats": stats}
