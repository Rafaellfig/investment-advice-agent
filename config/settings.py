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

# Output file paths
OUTPUT_FILE = OUTPUT_DIR / "output_letter.txt"
OUTPUT_DOCX_FILE = OUTPUT_DIR / "Relatorio_Investimento_Mensal.docx"

# Document configuration
LOGO_FILE = INPUT_DIR / "xp-investimentos_logo.png"
DEFAULT_CITY = "São Paulo"
DEFAULT_SUBJECT = "Relatório Mensal de Investimentos"
DEFAULT_CLOSING_LINE = "Atenciosamente,"
DEFAULT_ADVISOR_TITLE = "Assessor de Investimentos"
DEFAULT_GREETING_PREFIX = "Prezado(a)"
FINAL_PARAGRAPH_TEXT = (
    "Estamos à disposição para discutir mais detalhadamente os resultados e as recomendações, "
    "bem como para esclarecer quaisquer dúvidas que você possa ter. Agradecemos pela confiança "
    "depositada em nossos serviços e seguimos comprometidos em ajudá-lo a alcançar seus objetivos financeiros."
)

# Document margins (in millimeters)
DEFAULT_TOP_MARGIN = 25
DEFAULT_BOTTOM_MARGIN = 25
DEFAULT_LEFT_MARGIN = 22
DEFAULT_RIGHT_MARGIN = 22

# Preview settings
PREVIEW_LENGTH = 500
