from fastapi import APIRouter, Request, Depends, HTTPException, UploadFile, File, Form
from datetime import datetime, timedelta
import uuid
import json
import base64

from core.db import get_db
from core.sessions.session_middleware import require_session
from core.core_pipeline import protect_data
from core.file_policy import validate_file_policy

router = APIRouter(prefix="/files", tags=["Files"])


@router.post("/register")
async def register_file(
    request: Request,

    file: UploadFile = File(...),
    pin: str = Form(...),

    max_attempts: int = Form(3),
    expiry_minutes: int = Form(10),

    user_id: str = Depends(require_session)
):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    try:
        # 1️⃣ Read file bytes (async safe)
        file_bytes = await file.read()
        file_size = len(file_bytes)
        file_mime = file.content_type

        if not file_bytes:
            raise HTTPException(400, "EMPTY_FILE")

        # 2️⃣ Enforce file policy
        try:
            validate_file_policy(file_mime, file_size)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        # 3️⃣ Generate file_id
        file_id = str(uuid.uuid4())

        # 4️⃣ Encrypt (base64 → ML → AES-GCM)
        encrypted_payload = protect_data(
            plain_text=base64.b64encode(file_bytes).decode("utf-8"),
            pin=pin
        )

        expires_at = datetime.utcnow() + timedelta(minutes=expiry_minutes)

        # 5️⃣ Store securely
        cursor.execute(
            """
            INSERT INTO secure_files (
                file_id,
                owner_id,
                file_mime,
                file_size,
                max_attempts,
                attempt_count,
                is_locked,
                expires_at,
                encrypted_payload
            )
            VALUES (%s, %s, %s, %s, %s, 0, 0, %s, %s)
            """,
            (
                file_id,
                user_id,
                file_mime,
                file_size,
                max_attempts,
                expires_at,
                json.dumps(encrypted_payload),
            )
        )
        db.commit()

        return {
            "status": "FILE_REGISTERED",
            "file_id": file_id,
            "expires_at": expires_at.isoformat(),
        }

    finally:
        cursor.close()
        db.close()
