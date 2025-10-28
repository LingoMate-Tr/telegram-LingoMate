# translator.py
import logging
import os
import uuid
import asyncio
from PIL import Image
import pytesseract
from deep_translator import GoogleTranslator
import whisper
import fitz
from pydub import AudioSegment
from config import TESSERACT_CMD, TEMP_DIR, WHISPER_MODEL_SIZE
from utils import detect_language

logger = logging.getLogger(__name__)
pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD

# Load the Whisper model once at startup
WHISPER_MODEL = whisper.load_model(WHISPER_MODEL_SIZE)
logger.info(f"Whisper model '{WHISPER_MODEL_SIZE}' loaded.")

class Translator:
    def __init__(self, source: str = 'auto', target: str = 'en'):
        self.source = source
        self.target = target

    async def translate(self, text: str) -> str:
        if not text:
            return ""
        try:
            return await asyncio.to_thread(
                GoogleTranslator(source=self.source, target=self.target).translate, text
            )
        except Exception as e:
            logger.error(f"Error translating text: {e}", exc_info=True)
            return "Error: Could not translate text."

    async def translate_image(self, file_path: str) -> (str, str):
        try:
            loop = asyncio.get_running_loop()
            img = await loop.run_in_executor(None, Image.open, file_path)
            img = await loop.run_in_executor(None, img.convert, "L")
            extracted_text = await loop.run_in_executor(None, pytesseract.image_to_string, img, 'fas+eng')
            extracted_text = extracted_text.strip()
            if not extracted_text:
                return "No text found in the image.", ""

            if self.source == 'auto' or self.target == 'auto':
                lang = detect_language(extracted_text)
                self.source = lang
                self.target = 'fa' if lang == 'en' else 'en'

            translated_text = await self.translate(extracted_text)
            return extracted_text, translated_text
        except Exception as e:
            logger.error(f"Error processing image: {e}", exc_info=True)
            return "Error: Could not process image.", ""
        finally:
            if os.path.exists(file_path):
                os.remove(file_path)

    async def translate_audio(self, file_path: str) -> (str, str):
        temp_wav_path = os.path.join(TEMP_DIR, f"temp_{uuid.uuid4().hex}.wav")
        try:
            loop = asyncio.get_running_loop()
            audio = await loop.run_in_executor(None, AudioSegment.from_file, file_path)
            await loop.run_in_executor(None, audio.export, temp_wav_path, "wav")

            result = await loop.run_in_executor(None, WHISPER_MODEL.transcribe, temp_wav_path)
            extracted_text = result["text"]

            if not extracted_text:
                return "No text found in the audio.", ""

            lang = detect_language(extracted_text)
            self.source = lang
            self.target = 'fa' if lang == 'en' else 'en'

            translated_text = await self.translate(extracted_text)
            return extracted_text, translated_text
        except Exception as e:
            logger.error(f"Error processing audio: {e}", exc_info=True)
            return "Error: Could not process audio.", ""
        finally:
            if os.path.exists(temp_wav_path):
                os.remove(temp_wav_path)
            if os.path.exists(file_path):
                os.remove(file_path)

    @staticmethod
    def save_temp_audio(audio_file) -> str:
        file_path = audio_file.file_path
        file_ext = os.path.splitext(file_path)[1] if '.' in file_path else '.ogg'
        temp_file_path = os.path.join(TEMP_DIR, f"temp_{uuid.uuid4().hex}{file_ext}")
        audio_file.download_to_drive(temp_file_path)
        return temp_file_path

    async def translate_document(self, file_path: str) -> (str, str):
        try:
            doc = await asyncio.to_thread(fitz.open, file_path)
            extracted_text = ""
            for page in doc:
                extracted_text += page.get_text()

            if not extracted_text:
                return "No text found in the document.", ""

            lang = detect_language(extracted_text)
            self.source = lang
            self.target = 'fa' if lang == 'en' else 'en'

            translated_text = await self.translate(extracted_text)
            return extracted_text, translated_text
        except Exception as e:
            logger.error(f"Error processing document: {e}", exc_info=True)
            return "Error: Could not process document.", ""
        finally:
            if os.path.exists(file_path):
                os.remove(file_path)

    @staticmethod
    def save_temp_document(document_file) -> str:
        file_path = document_file.file_name
        file_ext = os.path.splitext(file_path)[1] if '.' in file_path else '.pdf'
        temp_file_path = os.path.join(TEMP_DIR, f"temp_{uuid.uuid4().hex}{file_ext}")
        document_file.download_to_drive(temp_file_path)
        return temp_file_path

    @staticmethod
    def save_temp_photo(photo_file) -> str:
        temp_file_path = os.path.join(TEMP_DIR, f"temp_{uuid.uuid4().hex}.jpg")
        photo_file.download_to_drive(temp_file_path)
        return temp_file_path
