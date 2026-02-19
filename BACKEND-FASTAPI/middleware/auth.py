"""
JWT Authentication Middleware & Dependency

Validates Bearer tokens on protected endpoints.
"""

import os
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt  # type: ignore

JWT_SECRET = os.getenv("JWT_SECRET", "insecure-dev-secret-change-me")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token", auto_error=False)


def get_current_user(token: Optional[str] = Depends(oauth2_scheme)) -> Optional[dict]:
    """
    Decode and validate a JWT Bearer token.

    Returns the token payload or raises 401.
    In development mode (no secret configured) returns a stub user.
    """
    if not token:
        return None  # Allow unauthenticated access in non-protected routes

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def require_user(current_user: Optional[dict] = Depends(get_current_user)) -> dict:
    """Dependency that requires an authenticated user."""
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return current_user
