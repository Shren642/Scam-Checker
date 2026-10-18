import os
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "scam-check-elderly-safe-secret-key-2026")
    
    # Gemini API
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
    GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
    
    # WhatsApp Cloud API (Meta Graph API)
    WHATSAPP_TOKEN = os.environ.get("WHATSAPP_TOKEN", "")
    WHATSAPP_PHONE_NUMBER_ID = os.environ.get("WHATSAPP_PHONE_NUMBER_ID", "")
    WHATSAPP_VERIFY_TOKEN = os.environ.get("WHATSAPP_VERIFY_TOKEN", "scam_check_verify_token_123")
    
    # Twilio WhatsApp fallback / alternative
    TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID", "")
    TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN", "")
    TWILIO_PHONE_NUMBER = os.environ.get("TWILIO_PHONE_NUMBER", "")
    
    # Upload settings (Use /tmp on Vercel and serverless environments)
    if os.environ.get("VERCEL"):
        UPLOAD_FOLDER = "/tmp/uploads"
    else:
        UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "gif", "wav", "mp3", "ogg", "m4a", "webm"}
    
    # Supported languages
    SUPPORTED_LANGUAGES = {
        "en": "English",
        "pa": "ਪੰਜਾਬੀ (Punjabi)",
        "pl": "Polski (Polish)",
        "ro": "Română (Romanian)",
        "pt": "Português (Portuguese)"
    }
    DEFAULT_LANGUAGE = "en"
