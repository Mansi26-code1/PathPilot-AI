import os
from dotenv import load_dotenv

load_dotenv()

# =========================
# Application Settings
# =========================

APP_NAME = os.getenv("APP_NAME", "PathPilot AI")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
DEBUG = os.getenv("DEBUG", "False")


# =========================
# AI / LLM Settings
# =========================

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

GROQ_MODEL = os.getenv(
    "GROQ_MODEL",
    "openai/gpt-oss-20b"
)

LLM_TEMPERATURE = float(
    os.getenv("LLM_TEMPERATURE", "0.2")
)