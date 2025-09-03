"""
Configuration file for ETL pipeline
"""
import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
LOGS_DIR = DATA_DIR / "logs"
DEAD_LETTER_DIR = LOGS_DIR / "dead_letter"

# File paths
XML_INPUT_PATH = RAW_DIR / "momo.xml"
DASHBOARD_JSON_PATH = PROCESSED_DIR / "dashboard.json"
DATABASE_PATH = DATA_DIR / "db.sqlite3"
ETL_LOG_PATH = LOGS_DIR / "etl.log"

# ETL Configuration
BATCH_SIZE = 1000
MAX_RETRIES = 3
LOG_LEVEL = "INFO"

# Database Configuration
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# Transaction Categories
TRANSACTION_CATEGORIES = {
    "payment": ["payment", "pay", "bill", "utility"],
    "transfer": ["transfer", "send", "money", "cash"],
    "withdrawal": ["withdraw", "withdrawal", "atm", "cashout"],
    "deposit": ["deposit", "topup", "recharge", "add"]
}

# Amount thresholds for categorization
AMOUNT_THRESHOLDS = {
    "small": 1000,
    "medium": 5000,
    "large": 10000
}

# Phone number patterns (Ghana)
PHONE_PATTERNS = [
    r"\+233\d{9}",  # +233XXXXXXXXX
    r"0\d{9}",      # 0XXXXXXXXX
    r"233\d{9}"     # 233XXXXXXXXX
]

# Date formats to try
DATE_FORMATS = [
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%dT%H:%M:%S",
    "%d/%m/%Y %H:%M",
    "%d-%m-%Y %H:%M",
    "%Y-%m-%d"
]

# Ensure directories exist
def ensure_directories():
    """Create necessary directories if they don't exist"""
    directories = [RAW_DIR, PROCESSED_DIR, LOGS_DIR, DEAD_LETTER_DIR]
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

# Initialize directories
ensure_directories()
