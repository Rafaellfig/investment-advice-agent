"""Project configuration and constants."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# OpenAI API configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = "gpt-4o-mini"
TEMPERATURE = 0.5
MAX_TOKENS = 1024

# Directory paths
BASE_DIR = Path(__file__).parent.parent
INPUT_DIR = BASE_DIR / "Input"
OUTPUT_DIR = BASE_DIR / "Output"
OUTPUT_DIR.mkdir(exist_ok=True)

# Input file paths
PORTFOLIO_FILE = INPUT_DIR / "XP - Albert_s portfolio.txt"
RISK_PROFILE_FILE = INPUT_DIR / "XP - Albert_s risk profile.txt"
MACRO_ANALYSIS_FILE = INPUT_DIR / "XP - Macro analysis.txt"

# Output file path
OUTPUT_FILE = OUTPUT_DIR / "output_letter.txt"
