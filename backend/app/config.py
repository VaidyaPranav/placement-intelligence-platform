# Global Configuration for Placement Intelligence Platform

from dotenv import load_dotenv
import os

load_dotenv(override=True)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
USE_LLM_ENRICHMENT = os.getenv("USE_LLM_ENRICHMENT", "True").lower() == "true"
ENABLE_AUTOMATIC_FALLBACK = os.getenv("ENABLE_AUTOMATIC_FALLBACK", "True").lower() == "true"

PIPELINE_VERSION = "1.0.0"

if not GOOGLE_API_KEY:
    print("[CONFIG]")
    print("GOOGLE_API_KEY not configured.")
    print("LLM enrichment will automatically fall back.")
