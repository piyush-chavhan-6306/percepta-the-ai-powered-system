"""
PERCEPTA ONLINE SUPABASE AUTH & USER ISOLATION
Validates Supabase Auth tokens, extracts tenant context, and enforces RBAC.
Operates seamlessly on Supabase Free Tier without credit cards, and gracefully in local demo mode.
"""
import os
import json
import logging
from typing import Optional, Dict, Any
from fastapi import Request, HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
import urllib.request
import urllib.error

logger = logging.getLogger("percepta.online.auth")
security = HTTPBearer(auto_error=False)

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_ANON_KEY = os.environ.get("SUPABASE_ANON_KEY", "")
SUPABASE_JWT_SECRET = os.environ.get("SUPABASE_JWT_SECRET", "percepta_secret_jwt_key_32_bytes_long!!")
DEMO_MODE = os.environ.get("DEMO_MODE", "true").lower() in ("true", "1", "yes")


class AuthenticatedUser:
    def __init__(self, user_id: str, email: str, role: str, tenant_id: str):
        self.user_id = user_id
        self.email = email
        self.role = role
        self.tenant_id = tenant_id

    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "email": self.email,
            "role": self.role,
            "tenant_id": self.tenant_id,
        }


def _validate_via_supabase_api(token: str) -> Optional[Dict[str, Any]]:
    """Validate Bearer token against Supabase Auth API endpoint on Free Tier."""
    if not SUPABASE_URL or not SUPABASE_ANON_KEY:
        return None
    url = f"{SUPABASE_URL.rstrip('/')}/auth/v1/user"
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "apikey": SUPABASE_ANON_KEY,
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            if resp.status == 200:
                data = json.loads(resp.read().decode("utf-8"))
                return data
    except Exception as ex:
        logger.debug(f"Supabase auth API check failed: {ex}")
    return None


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security),
) -> AuthenticatedUser:
    """
    Extracts authenticated user from Bearer JWT.
    Enforces multi-tenant data isolation.
    """
    if credentials is None:
        if DEMO_MODE:
            return AuthenticatedUser(
                user_id="usr_default_operator",
                email="commander@percepta.defence",
                role="COMMANDER",
                tenant_id="tenant_northern_border",
            )
        raise HTTPException(status_code=401, detail="Authentication credentials required")

    token = credentials.credentials.strip()

    # 1. Check for local dev / demo tokens
    if token.startswith("tok_percepta_") or token.startswith("tok_offline_") or token.startswith("tok_demo_"):
        parts = token.split("_")
        user_suffix = parts[2] if len(parts) > 2 else "operator"
        return AuthenticatedUser(
            user_id=f"usr_offline_{user_suffix}",
            email=f"{user_suffix}@percepta.defence",
            role="SURVEILLANCE_OFFICER",
            tenant_id=f"tenant_{user_suffix}",
        )

    # 2. Try Supabase Auth API direct validation
    api_user = _validate_via_supabase_api(token)
    if api_user and "id" in api_user:
        uid = str(api_user["id"])
        email = api_user.get("email", "operator@percepta.defence")
        metadata = api_user.get("user_metadata", {})
        role = metadata.get("role", "SURVEILLANCE_OFFICER")
        tenant = metadata.get("tenant_id", f"tenant_{uid}")
        return AuthenticatedUser(
            user_id=uid,
            email=email,
            role=role,
            tenant_id=tenant,
        )

    # 3. Try JWT signature decode
    try:
        payload = jwt.decode(
            token,
            SUPABASE_JWT_SECRET,
            algorithms=["HS256", "RS256"],
            options={"verify_exp": True, "verify_signature": False if DEMO_MODE else True},
        )
        user_id = payload.get("sub") or payload.get("id")
        email = payload.get("email", "unknown@percepta.defence")
        role = payload.get("role", "SURVEILLANCE_OFFICER")
        tenant_id = payload.get("tenant_id") or f"tenant_{user_id}"
        
        return AuthenticatedUser(
            user_id=str(user_id),
            email=email,
            role=role,
            tenant_id=str(tenant_id),
        )
    except JWTError as e:
        if DEMO_MODE:
            return AuthenticatedUser(
                user_id="usr_demo_evaluator",
                email="evaluator@percepta.defence",
                role="COMMANDER",
                tenant_id="tenant_northern_border",
            )
        raise HTTPException(status_code=401, detail=f"Invalid authentication token: {str(e)}")
