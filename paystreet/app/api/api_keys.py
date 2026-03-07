# pyright: reportMissingImports=false
"""Admin API key management endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from paystreet.app.database import get_db
from paystreet.app.models.api_key import ApiKey

router = APIRouter()


# --------------------------------------------------------------------------- #
# Request / Response schemas
# --------------------------------------------------------------------------- #


class ApiKeyUpsertRequest(BaseModel):
    provider: str  # "openai" | "elevenlabs"
    key_value: str
    label: str | None = None


class ApiKeyResponse(BaseModel):
    id: str
    provider: str
    label: str | None
    is_active: bool
    # Never return the raw key — mask it
    key_masked: str


def _mask(key: str) -> str:
    """Return sk-...xxxx style masked key."""
    if len(key) <= 8:
        return "****"
    return key[:4] + "****" + key[-4:]


def _to_response(obj: ApiKey) -> dict:
    return {
        "id": str(obj.id),
        "provider": obj.provider,
        "label": obj.label,
        "is_active": obj.is_active,
        "key_masked": _mask(obj.key_value),
    }


# --------------------------------------------------------------------------- #
# Endpoints
# --------------------------------------------------------------------------- #


@router.get("/api-keys")
async def list_api_keys(db: AsyncSession = Depends(get_db)):
    """List all stored API keys (masked)."""
    result = await db.execute(select(ApiKey).order_by(ApiKey.provider))
    keys = result.scalars().all()
    return {"success": True, "data": [_to_response(k) for k in keys], "error": None}


@router.put("/api-keys")
async def upsert_api_key(body: ApiKeyUpsertRequest, db: AsyncSession = Depends(get_db)):
    """Create or update an API key for a given provider."""
    result = await db.execute(select(ApiKey).where(ApiKey.provider == body.provider))
    existing = result.scalar_one_or_none()

    if existing:
        existing.key_value = body.key_value
        existing.is_active = True
        if body.label is not None:
            existing.label = body.label
        await db.commit()
        await db.refresh(existing)
        return {"success": True, "data": _to_response(existing), "error": None}

    new_key = ApiKey(
        provider=body.provider,
        key_value=body.key_value,
        label=body.label,
        is_active=True,
    )
    db.add(new_key)
    await db.commit()
    await db.refresh(new_key)
    return {"success": True, "data": _to_response(new_key), "error": None}


@router.delete("/api-keys/{provider}")
async def delete_api_key(provider: str, db: AsyncSession = Depends(get_db)):
    """Delete the API key for a given provider."""
    result = await db.execute(select(ApiKey).where(ApiKey.provider == provider))
    key = result.scalar_one_or_none()
    if not key:
        raise HTTPException(status_code=404, detail="API key not found")
    await db.delete(key)
    await db.commit()
    return {"success": True, "data": {"provider": provider}, "error": None}


@router.patch("/api-keys/{provider}/toggle")
async def toggle_api_key(provider: str, db: AsyncSession = Depends(get_db)):
    """Toggle active/inactive state of an API key."""
    result = await db.execute(select(ApiKey).where(ApiKey.provider == provider))
    key = result.scalar_one_or_none()
    if not key:
        raise HTTPException(status_code=404, detail="API key not found")
    key.is_active = not key.is_active
    await db.commit()
    await db.refresh(key)
    return {"success": True, "data": _to_response(key), "error": None}
