from __future__ import annotations

import asyncio
from dataclasses import dataclass
from functools import lru_cache

import httpx
import jwt
from fastapi import Depends, HTTPException, Request, status
from jwt import PyJWKClient

from .config import get_settings


@dataclass
class Principal:
    subject: str
    email: str | None
    roles: set[str]


@lru_cache(maxsize=16)
def _jwks_client(url: str) -> PyJWKClient:
    return PyJWKClient(url, cache_keys=True)


async def get_principal(request: Request) -> Principal:
    settings = get_settings()
    if settings.auth_mode == "dev":
        roles = request.headers.get("x-flowrebase-roles", "admin,architect,developer,auditor")
        return Principal(
            subject=request.headers.get("x-flowrebase-user", settings.dev_user_id),
            email=request.headers.get("x-flowrebase-email", settings.dev_user_email),
            roles={r.strip() for r in roles.split(",") if r.strip()},
        )

    auth = request.headers.get("authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="missing bearer token")
    if not settings.oidc_issuer or not settings.oidc_audience:
        raise HTTPException(status_code=500, detail="OIDC issuer/audience not configured")

    token = auth.split(" ", 1)[1]
    issuer = settings.oidc_issuer.rstrip("/")
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            metadata = (await client.get(f"{issuer}/.well-known/openid-configuration")).json()
        jwks_uri = metadata["jwks_uri"]
        key = await asyncio.to_thread(_jwks_client(jwks_uri).get_signing_key_from_jwt, token)
        algorithms = metadata.get("id_token_signing_alg_values_supported") or ["RS256"]
        claims = jwt.decode(token, key.key, algorithms=algorithms, audience=settings.oidc_audience, issuer=settings.oidc_issuer)
    except Exception as exc:
        raise HTTPException(status_code=401, detail="invalid token") from exc
    roles = set(claims.get("roles", [])) | set(claims.get("groups", []))
    return Principal(subject=claims["sub"], email=claims.get("email"), roles=roles)


def require_roles(*required: str):
    async def dependency(principal: Principal = Depends(get_principal)) -> Principal:
        if "admin" in principal.roles or principal.roles.intersection(required):
            return principal
        raise HTTPException(status_code=403, detail=f"requires one of roles: {', '.join(required)}")

    return dependency
