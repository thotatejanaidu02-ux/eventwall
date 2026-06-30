import firebase_admin
from firebase_admin import credentials, firestore, storage, auth as firebase_auth
from app.config import settings
import os

# Initialize Firebase
def initialize_firebase():
    """Initialize Firebase Admin SDK"""
    if not firebase_admin._apps:
        creds_path = settings.FIREBASE_CREDENTIALS_PATH
        
        if os.path.exists(creds_path):
            cred = credentials.Certificate(creds_path)
        else:
            # Use environment variable if file doesn't exist
            cred = credentials.ApplicationDefault()
        
        firebase_admin.initialize_app(cred, {
            'projectId': settings.FIREBASE_PROJECT_ID,
        })

def get_firestore_client():
    """Get Firestore client"""
    initialize_firebase()
    return firestore.client()

def get_storage_bucket():
    """Get Firebase Storage bucket"""
    initialize_firebase()
    return storage.bucket()

def get_firebase_auth():
    """Get Firebase Auth"""
    initialize_firebase()
    return firebase_auth
