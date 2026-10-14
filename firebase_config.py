# firebase_config.py - Google Firebase Configuration for TRUTHCHECK
import os

FIREBASE_CONFIG = {
    "apiKey": os.environ.get("FIREBASE_API_KEY", "AIzaSyANUYJoL0qTJNHAfU8kbahQicvoZZ3NXu4"),
    "authDomain": os.environ.get("FIREBASE_AUTH_DOMAIN", "ruthcheck.firebaseapp.com"),
    "projectId": os.environ.get("FIREBASE_PROJECT_ID", "ruthcheck"),
    "storageBucket": os.environ.get("FIREBASE_STORAGE_BUCKET", "ruthcheck.firebasestorage.app"),
    "messagingSenderId": os.environ.get("FIREBASE_MESSAGING_SENDER_ID", "658632059087"),
    "appId": os.environ.get("FIREBASE_APP_ID", "1:658632059087:web:97fd4a42301f830ef52fba"),
    "measurementId": os.environ.get("FIREBASE_MEASUREMENT_ID", "G-Z7Y59HFE59")
}