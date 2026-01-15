import firebase_admin
from firebase_admin import credentials, auth

def init_firebase():
    if firebase_admin._apps:
        return

    cred = credentials.Certificate("veil-tech-firebase-adminsdk-fbsvc-c56e27565b.json")
    firebase_admin.initialize_app(cred)

init_firebase()

def verify_firebase_token(id_token: str):
    return auth.verify_id_token(id_token)
