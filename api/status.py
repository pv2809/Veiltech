from fastapi import APIRouter, HTTPException, Request, Depends
from datetime import datetime

from core.db import get_db
from core.sessions.session_middleware import require_session

router = APIRouter()

@router.get("/status/{file_id}", tags=["Files"])
def file_status(
    file_id: str,
    request: Request,
    user_id: str = Depends(require_session)
):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    try:
        cursor.execute(
            "SELECT * FROM secure_files WHERE file_id=%s",
            (file_id,)
        )
        record = cursor.fetchone()

        if not record:
            raise HTTPException(status_code=404, detail="FILE_NOT_FOUND")

        # Optional: only owner can view full status
        if record["owner_id"] != user_id:
            raise HTTPException(status_code=403, detail="FORBIDDEN")

        expired = (
            record["expires_at"] is not None
            and datetime.utcnow() > record["expires_at"]
        )

        remaining_attempts = max(
            0,
            record["max_attempts"] - record["attempt_count"]
        )

        return {
            "file_id": file_id,
            "is_locked": bool(record["is_locked"]),
            "is_expired": expired,
            "attempts_used": record["attempt_count"],
            "attempts_left": remaining_attempts,
            "max_attempts": record["max_attempts"],
            "expires_at": (
                record["expires_at"].isoformat()
                if record["expires_at"] else None
            ),
            "created_at": record["created_at"].isoformat()
        }

    finally:
        cursor.close()
        db.close()
