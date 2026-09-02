"""Health check endpoint."""

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.database.database import db_is_ready

router = APIRouter()


@router.get("/api/health")
async def health_check() -> JSONResponse:
    mysql_ok = db_is_ready()
    return JSONResponse(
        content={
            "status": "success",
            "message": "HireFlow API is running",
            "mysql": "connected" if mysql_ok else "not_connected",
        }
    )
