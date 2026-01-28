"""RBAC middleware for tenant isolation."""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from typing import Optional
from uuid import UUID

from app.auth.utils import decode_token


class TenantMiddleware(BaseHTTPMiddleware):
    """Middleware to extract tenant_id from JWT token and set it in request.state."""
    
    async def dispatch(self, request: Request, call_next):
        """Extract tenant_id from JWT token and set it in request.state."""
        request.state.tenant_id = None
        
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            try:
                payload = decode_token(token)
                tenant_id_str = payload.get("tenant_id")
                if tenant_id_str:
                    request.state.tenant_id = UUID(tenant_id_str)
            except (ValueError, TypeError, AttributeError):
                # Invalid token or missing tenant_id - continue without tenant context
                pass
        
        response = await call_next(request)
        return response
