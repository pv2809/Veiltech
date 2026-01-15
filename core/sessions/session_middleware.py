from fastapi import Request, HTTPException
from core.sessions.session_manager import validate_session


def require_session(request: Request) -> int:
    session_id = request.headers.get("X-Session-ID")

    if not session_id:
        raise HTTPException(
            status_code=401,
            detail="Session missing"
        )

    user_id = validate_session(session_id)

    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Session expired or invalid"
        )

    return user_id
