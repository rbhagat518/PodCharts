"""Authentication and authorization utilities."""
from __future__ import annotations

import os
from typing import Annotated
from uuid import UUID

from dotenv import load_dotenv
from fastapi import Depends, HTTPException, Header, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

load_dotenv()

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY")  # For server-side operations

security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Security(security),
    api_key: str | None = Header(None, alias="X-API-Key"),
) -> dict | None:
    """Get current user from JWT token or API key."""
    if api_key:
        # API key authentication
        return await get_user_by_api_key(api_key)
    
    if credentials:
        # JWT token authentication
        token = credentials.credentials
        if SUPABASE_AVAILABLE and SUPABASE_URL and SUPABASE_SERVICE_KEY:
            try:
                supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
                user = supabase.auth.get_user(token)
                return {"id": user.user.id, "email": user.user.email}
            except Exception:
                pass
    
    return None


async def get_user_by_api_key(api_key: str) -> dict | None:
    """Get user by API key."""
    from app.db import get_connection
    from psycopg.rows import dict_row
    
    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                """
                SELECT id, email, subscription_tier, api_quota_monthly, api_calls_used, api_reset_date
                FROM users
                WHERE api_key = %s
                """,
                (api_key,),
            )
            user = cursor.fetchone()
            if user:
                # Check if quota reset needed
                from datetime import date
                if user["api_reset_date"] < date.today():
                    # Reset quota
                    cursor.execute(
                        """
                        UPDATE users
                        SET api_calls_used = 0, api_reset_date = CURRENT_DATE
                        WHERE id = %s
                        """,
                        (user["id"],),
                    )
                    conn.commit()
                    user["api_calls_used"] = 0
                
                return user
    return None


async def require_auth(user: dict | None = Depends(get_current_user)) -> dict:
    """Require authentication."""
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    return user


async def require_pro(user: dict = Depends(require_auth)) -> dict:
    """Require Pro subscription."""
    if user.get("subscription_tier") not in ("pro", "enterprise"):
        raise HTTPException(
            status_code=403,
            detail="Pro subscription required. Upgrade at /pricing",
        )
    return user


def check_api_quota(user: dict) -> bool:
    """Check if user has API quota remaining."""
    quota = user.get("api_quota_monthly", 1000)
    used = user.get("api_calls_used", 0)
    return used < quota


async def record_api_usage(user_id: UUID | None, api_key: str | None, endpoint: str) -> None:
    """Record API usage for rate limiting."""
    from app.db import get_connection
    
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO api_usage (api_key, endpoint, user_id)
                VALUES (%s, %s, %s)
                """,
                (api_key, endpoint, user_id),
            )
            if user_id:
                cursor.execute(
                    """
                    UPDATE users
                    SET api_calls_used = api_calls_used + 1
                    WHERE id = %s
                    """,
                    (user_id,),
                )
            conn.commit()

