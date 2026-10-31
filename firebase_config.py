# firebase_config.py - Google Firebase Configuration for TRUTHCHECK
# ⚠️  All secrets are loaded from environment variables ONLY.
#     Run with a .env file (never commit .env to Git).
import os

def _require(key: str) -> str:
    """Raise a clear error at startup if a required env var is missing."""
    value = os.environ.get(key)
    if not value:
        raise EnvironmentError(
            f"[TRUTHCHECK] Missing required environment variable: {key}\n"
            "Add it to your .env file and restart the app."
        )
    return value

FIREBASE_CONFIG = {
    "apiKey":            _require("FIREBASE_API_KEY"),
    "authDomain":        os.environ.get("FIREBASE_AUTH_DOMAIN", ""),
    "projectId":         os.environ.get("FIREBASE_PROJECT_ID", ""),
    "storageBucket":     os.environ.get("FIREBASE_STORAGE_BUCKET", ""),
    "messagingSenderId": os.environ.get("FIREBASE_MESSAGING_SENDER_ID", ""),
    "appId":             os.environ.get("FIREBASE_APP_ID", ""),
    "measurementId":     os.environ.get("FIREBASE_MEASUREMENT_ID", ""),
}