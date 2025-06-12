import firebase_admin
from firebase_admin import credentials, firestore

# Point to your service‑account JSON:
cred = credentials.Certificate("firebase_key.json")
firebase_admin.initialize_app(cred)

# Export the Firestore client for other modules to import:
firestore_db = firestore.client()
