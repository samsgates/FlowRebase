from __future__ import annotations

import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from .db import SessionLocal
from .models import AuditEvent


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
        response = await call_next(request)
        response.headers["x-request-id"] = request_id
        if request.method in {"POST", "PUT", "PATCH", "DELETE"}:
            actor = request.headers.get("x-flowrebase-user") or ("oidc-bearer" if request.headers.get("authorization") else "anonymous")
            try:
                async with SessionLocal() as db:
                    db.add(
                        AuditEvent(
                            actor=actor,
                            action=request.method,
                            resource=request.url.path,
                            request_id=request_id,
                            status_code=response.status_code,
                            details={"query": str(request.url.query)[:1000]},
                        )
                    )
                    await db.commit()
            except Exception:
                # Audit persistence failure is observable but must not corrupt an already completed response.
                pass
        return response
