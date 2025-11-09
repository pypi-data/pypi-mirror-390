import os
MODEL_NAME = os.getenv("MODEL_NAME", "")
TEMPERATURE=0.7
MAX_TOKENS=1024

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

KEY_PATTERNS = {
    "google": (
        "GOOGLE_API_KEY",os.getenv("GEMINI_MODEL", "models/gemini-2.5-flash"),"AIza",  
    ),
    "openai": (
        "OPENAI_API_KEY", os.getenv("OPENAI_MODEL", "gpt-4o-mini"),"sk-", 
    ),
}