# utils.py
import logging
from deep_translator import GoogleTranslator
from config import DEFAULT_TRANSLATOR_SOURCE, DEFAULT_TRANSLATOR_TARGET

logger = logging.getLogger(__name__)

def detect_language(text: str) -> str:
    try:
        lang = GoogleTranslator(source=DEFAULT_TRANSLATOR_SOURCE, target=DEFAULT_TRANSLATOR_TARGET).detect(text)
        return 'fa' if lang and lang.startswith('fa') else 'en'
    except Exception as e:
        logger.warning(f"Language detection failed: {e}")
        return 'en'
