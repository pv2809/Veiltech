from fastapi import FastAPI, Form, HTTPException, Depends, Request
from pydantic import BaseModel

from core.db import get_db
from core.firebase import verify_firebase_token
from core.sessions.session_manager import create_session
from core.sessions.session_middleware import require_session

from api.reveal import router as reveal_router
from api.register import router as register_router
from api.status import router as status_router
from api.notifications import router as notifications_router

app = FastAPI(title="VeilTech API", version="1.0.0")

# --------------------
# Health
# --------------------
@app.get("/", tags=["Health"])
def root():
    return {"status": "alive"}

@app.get("/ping", tags=["Health"])
def ping():
    return {"status": "ok"}

# --------------------
# Auth (OTP-FREE)
# --------------------
@app.post("/auth/session", tags=["Auth"])
def auth_session(id_token: str = Form(...)):
    decoded = verify_firebase_token(id_token)
    firebase_uid = decoded.get("uid")

    if not firebase_uid:
        raise HTTPException(400, "Firebase UID missing")

    db = get_db()
    cursor = db.cursor(dictionary=True)

    try:
        cursor.execute(
            "SELECT user_id FROM users WHERE user_id=%s",
            (firebase_uid,)
        )
        user = cursor.fetchone()

        if not user:
            cursor.execute(
                "INSERT INTO users (user_id) VALUES (%s)",
                (firebase_uid,)
            )
            db.commit()

        session_token = create_session(firebase_uid)

        return {
            "message": "session created",
            "session_token": session_token,
            "is_new_user": not bool(user),
            "expires_in": 180
        }

    finally:
        cursor.close()
        db.close()

# --------------------
# Session check
# --------------------
@app.get("/me", tags=["Protected"])
def me(user_id: str = Depends(require_session)):
    return {"status": "authenticated", "user_id": user_id}

# --------------------
# Routers
# --------------------
app.include_router(register_router)
app.include_router(reveal_router)
app.include_router(status_router)
app.include_router(notifications_router)
