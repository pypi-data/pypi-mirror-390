"""
Proxy Registration Endpoints
This module provides proxy registration endpoints for testing.
Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional
import time
import uuid

# In-memory registry for testing
_registry: Dict[str, Dict] = {}
router = APIRouter(prefix="/proxy", tags=["proxy"])


class ServerRegistration(BaseModel):
    """Server registration request model."""

    server_id: str
    server_url: str
    server_name: str
    description: Optional[str] = None
    version: Optional[str] = "1.0.0"
    capabilities: Optional[List[str]] = None
    endpoints: Optional[Dict[str, str]] = None
    auth_method: Optional[str] = "none"
    security_enabled: Optional[bool] = False


class ServerUnregistration(BaseModel):
    """Server unregistration request model."""

    server_key: str  # Use server_key directly


class HeartbeatData(BaseModel):
    """Heartbeat data model."""

    server_id: str
    server_key: str
    timestamp: Optional[int] = None
    status: Optional[str] = "healthy"


class RegistrationResponse(BaseModel):
    """Registration response model."""

    success: bool
    server_key: str
    message: str
    copy_number: int


class DiscoveryResponse(BaseModel):
    """Discovery response model."""

    success: bool
    servers: List[Dict]
    total: int
    active: int


@router.post("/register", response_model=RegistrationResponse)


@router.post("/unregister")


@router.post("/heartbeat")


@router.get("/discover", response_model=DiscoveryResponse)


@router.get("/status")


@router.delete("/clear")
