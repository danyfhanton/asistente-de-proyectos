import secrets
from typing import Optional
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

SESSION_COOKIE_NAME = "asistente_session_id"
_SERVER_SESSIONS: dict[str, dict] = {}


class SessionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        session_id = request.cookies.get(SESSION_COOKIE_NAME)
        if not session_id or session_id not in _SERVER_SESSIONS:
            session_id = secrets.token_urlsafe(32)
            _SERVER_SESSIONS[session_id] = {}

        request.scope["session"] = _SERVER_SESSIONS[session_id]
        response: Response = await call_next(request)
        response.set_cookie(
            key=SESSION_COOKIE_NAME,
            value=session_id,
            httponly=True,
            samesite="lax",
        )
        return response


def get_current_user(request: Request) -> Optional[dict]:
    session = getattr(request, "session", {})
    return session.get("user")

