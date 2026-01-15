from fastapi import APIRouter, Form, Depends, HTTPException, Response
from datetime import datetime
import json
import base64

from core.db import get_db
from core.sessions.session_middleware import require_session
from core.core_pipeline import reveal_data

router = APIRouter(prefix="/files", tags=["Files"])


@router.post("/reveal")
async def reveal_file(
    file_id: str = Form(...),
    pin: str = Form(...),
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
            raise HTTPException(404, "FILE_NOT_FOUND")

        if record["is_locked"]:
            raise HTTPException(403, "FILE_LOCKED")

        if record["expires_at"] and datetime.utcnow() > record["expires_at"]:
            raise HTTPException(410, "FILE_EXPIRED")

        if record["attempt_count"] >= record["max_attempts"]:
            cursor.execute(
                "UPDATE secure_files SET is_locked=1 WHERE file_id=%s",
                (file_id,)
            )
            db.commit()
            raise HTTPException(403, "ATTEMPTS_EXCEEDED")

        encrypted_payload = json.loads(record["encrypted_payload"])

        try:
            # 1️⃣ Decrypt (AES-GCM + ML)
            decrypted_b64 = reveal_data(encrypted_payload, pin)

            # 2️⃣ Base64 → raw bytes
            original_bytes = base64.b64decode(decrypted_b64)

        except Exception:
            cursor.execute(
                """
                UPDATE secure_files
                SET attempt_count = attempt_count + 1
                WHERE file_id=%s
                """,
                (file_id,)
            )
            db.commit()

            attempts_left = max(
                record["max_attempts"] - (record["attempt_count"] + 1),
                0
            )

            raise HTTPException(
                status_code=401,
                detail={
                    "error": "INVALID_PIN",
                    "attempts_left": attempts_left
                }
            )

        return Response(
            content=original_bytes,
            media_type=record["file_mime"]
        )

    finally:
        cursor.close()
        db.close()
