"""
Configuration module for the Student Dashboard application.
Handles all path configurations and settings.
"""
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent

# Database configuration
DATABASE_PATH = BASE_DIR / 'database' / 'students.db'

# Excel file paths
EXCEL_INPUT_DIR = BASE_DIR / 'excel_input'
EXCEL_OUTPUT_DIR = BASE_DIR / 'excel_output'

# Ensure output directory exists
EXCEL_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Default input file
EXCEL_PATH_INPUT = EXCEL_INPUT_DIR / 'students_500.xlsx'

# Flask secret key (should be environment variable in production)
SECRET_KEY = os.environ.get('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')

# Database settings
DB_TIMEOUT = 30  # seconds