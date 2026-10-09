import os
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).parent
load_dotenv(ROOT / ".env")

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
CLAUDE_MODEL = "claude-sonnet-5"

IDLE_CHECKIN_S = 15 #* 60
IDLE_CHECKIN_MAX_S = 2 * 60 * 60

VISION_ENABLED = True
VISION_CAMERA_INDEX = 0
VISION_POLL_INTERVAL_S = 0.5
VISION_DIFF_RESIZE = (160, 120)
VISION_CHANGE_THRESHOLD = 0.06
VISION_COOLDOWN_S = 45
VISION_SEND_WIDTH = 768

GREETING_COOLDOWN_S = 10 * 60

# Détection d'émotion en continu
EMOTION_POLL_INTERVAL_S = 5
MOOD_CHANGE_COOLDOWN_S = 60

if not ANTHROPIC_API_KEY:
    raise SystemExit("ANTHROPIC_API_KEY maquant dans .env")
