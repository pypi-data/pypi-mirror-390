"""
Simplified configuration for image generation package
"""
import os
from dotenv import load_dotenv

# Try to load .env file if it exists
load_dotenv()


class Config:
    """Configuration for image generation"""

    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    ARK_API_KEY = os.getenv("ARK_API_KEY")  # BytePlus ARK API for Seedream 4.0

    # Supabase Configuration (optional)
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

    # Feature flags
    ENABLE_IMAGE_GENERATION = os.getenv('ENABLE_IMAGE_GENERATION', 'true').lower() == 'true'

    # Logging Configuration
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
