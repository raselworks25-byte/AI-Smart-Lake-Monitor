import os


def _bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in ("true", "1", "yes", "on")


class Config:
    """Production configuration - all secrets must be set via environment variables."""

    # --- Core secrets (required in production) ---
    SECRET_KEY = os.getenv("SECRET_KEY", "38b595f34f47d0d9c676247a0f91869c2930393da36b6629857e34decac3faf1")
    if not SECRET_KEY:
        raise ValueError("CRITICAL: SECRET_KEY environment variable must be set")

    INGEST_API_KEY = os.getenv("INGEST_API_KEY", "5e579ff0da792cb6361a385a08b3167ce0fe5c8ff04cbeda")
    if not INGEST_API_KEY:
        raise ValueError("CRITICAL: INGEST_API_KEY environment variable must be set")

    # --- Firebase (optional persistence) ---
    FIREBASE_DATABASE_URL = os.getenv("FIREBASE_DATABASE_URL", "https://autonomous-boat-906cf-default-rtdb.asia-southeast1.firebasedatabase.app")
    FIREBASE_STORAGE_BUCKET = os.getenv("FIREBASE_STORAGE_BUCKET", "autonomous-boat-906cf.appspot.com")
    FIREBASE_CREDENTIALS_PATH = os.getenv(
        "FIREBASE_CREDENTIALS_PATH", os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "D:\\Claude\\secret\\autonomous-boat-906cf-firebase-adminsdk-fbsvc-5769add472.json")
    )

    # --- App ---
    APP_NAME = os.getenv("APP_NAME", "Smart AI Lake Monitoring")
    ENVIRONMENT = os.getenv("FLASK_ENV", "production")
    DEBUG = _bool(os.getenv("FLASK_DEBUG"), False)

    # --- Session cookie hardening ---
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    # Secure cookies require HTTPS. Auto-on in production, off in debug so local
    # HTTP testing still works. Override with SESSION_COOKIE_SECURE=true/false.
    SESSION_COOKIE_SECURE = _bool(os.getenv("SESSION_COOKIE_SECURE"), not DEBUG)

    # --- Login accounts (override via env; never hardcode real passwords) ---
    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@lakewatch.local")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")
    RESEARCHER_EMAIL = os.getenv("RESEARCHER_EMAIL", "researcher@lakewatch.local")
    RESEARCHER_PASSWORD = os.getenv("RESEARCHER_PASSWORD", "research123")
    VIEWER_EMAIL = os.getenv("VIEWER_EMAIL", "viewer@lakewatch.local")
    VIEWER_PASSWORD = os.getenv("VIEWER_PASSWORD", "viewer123")

    # Login brute-force limit: max attempts per IP within the window (seconds).
    LOGIN_RATE_LIMIT = int(os.getenv("LOGIN_RATE_LIMIT", "10"))
    LOGIN_RATE_WINDOW = int(os.getenv("LOGIN_RATE_WINDOW", "300"))
