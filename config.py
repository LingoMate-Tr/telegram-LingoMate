# config.py
import os

TOKEN = os.environ.get("TOKEN")
TESSERACT_CMD = "tesseract"
TEMP_DIR = "/tmp"
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_LEVEL = "INFO"
TRANSLATOR_LANGUAGES = {
    'fa_en': ('fa', 'en'),
    'en_fa': ('en', 'fa'),
}
DEFAULT_TRANSLATOR_TARGET = "en"
DEFAULT_TRANSLATOR_SOURCE = "auto"
