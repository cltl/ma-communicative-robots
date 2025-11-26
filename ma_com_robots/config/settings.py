# Configuration settings
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # OpenAI
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    USE_OPENAI = os.getenv("USE_OPENAI", "False").lower() == "true"

    # AI2Thor
    GRID_SIZE = 0.25
    VISIBILITY_DISTANCE = 2.0
    SCENE_WIDTH = 750
    SCENE_HEIGHT = 750

    # Search thresholds
    ROOM_SIMILARITY_THRESHOLD = 0.75
    TEXT_SIMILARITY_THRESHOLD = 0.70
    MAX_SEARCH_TIME = 20 * 60  # 20 minutes
    MIN_CANDIDATES = 4

    # Exploration
    POSITION_SAMPLE_RATE = 5  # Visit every 5th position
    MAX_EXPLORATION_POSITIONS = 50
    WALL_DETECTION_RADIUS = 3.0  # meters

    # Paths
    EMISSOR_DATA_PATH = "./data/emissor"

    # Models
    BLIP_MODEL = "Salesforce/blip-image-captioning-large"
    SENTENCE_MODEL = "sentence-transformers/roberta-large-nli-stsb-mean-tokens"
