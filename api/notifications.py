from fastapi import APIRouter, Form, Depends, Request
from firebase_admin import messaging

from core.db import get_db
from core.sessions.session_middleware import require_session

router = APIRouter(prefix="/notifications", tags=["Notifications"])


# -------------------------------------------------
# Register / update FCM token
# -------------------------------------------------
@router.post("/register-fcm")
def register_fcm_token(
    request: Request,
    fcm_token: str = Form(...),
    user_id: str = Depends(require_session)
):
    db = get_db()
    cursor = db.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO user_devices (user_id, fcm_token)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE
                fcm_token=%s
            """,
            (user_id, fcm_token, fcm_token)
        )
        db.commit()
        return {"status": "FCM_REGISTERED"}

    finally:
        cursor.close()
        db.close()


# -------------------------------------------------
# INTERNAL: Send FCM to a user (utility function)
# -------------------------------------------------
def send_fcm_to_user(
    user_id: str,
    title: str,
    body: str,
    data: dict | None = None
):
    """
    Send notification to all devices of a user.
    (Internal use only)
    """
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        "SELECT fcm_token FROM user_devices WHERE user_id=%s",
        (user_id,)
    )
    tokens = [row["fcm_token"] for row in cursor.fetchall()]

    cursor.close()
    db.close()

    if not tokens:
        return

    message = messaging.MulticastMessage(
        notification=messaging.Notification(
            title=title,
            body=body,
        ),
        data=data or {},
        tokens=tokens,
    )

    messaging.send_multicast(message)
