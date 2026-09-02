"""Gmail OAuth connect routes."""

import os

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import RedirectResponse

from app.services import gmail_client

os.environ.setdefault("OAUTHLIB_INSECURE_TRANSPORT", "1")

router = APIRouter(prefix="/api/gmail", tags=["gmail"])


@router.get("/connect")
def connect():
    try:
        return RedirectResponse(gmail_client.build_auth_url())
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/callback")
def callback(code: str = Query(...)):
    try:
        gmail_client.exchange_code(code)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return RedirectResponse("/settings")
