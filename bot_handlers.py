# bot_handlers.py
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from translator import Translator
from utils import detect_language

logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("فارسی → انگلیسی", callback_data='fa_en')],
        [InlineKeyboardButton("انگلیسی → فارسی", callback_data='en_fa')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "سلام! من ربات ترجمه هستم 😎\n"
        "می‌تونی متن یا عکس برام بفرستی تا برات ترجمه کنم.\n"
        "ابتدا زبان ترجمه مورد نظر خودت را انتخاب کن:",
        reply_markup=reply_markup
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data['translation_mode'] = query.data
    await query.edit_message_text(
        text=f"✅ حالت ترجمه انتخاب شد: {query.data.replace('_', ' → ')}\nحالا متن یا عکس خود را ارسال کنید."
    )

async def translate_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if not text:
        await update.message.reply_text("متن خالی دریافت شد!")
        return

    mode = context.user_data.get('translation_mode')
    if mode:
        src, tgt = mode.split('_')
    else:
        src = detect_language(text)
        tgt = 'fa' if src == 'en' else 'en'

    try:
        translator = Translator(source=src, target=tgt)
        translated = await translator.translate(text)
        await update.message.reply_text(f"🌐 ترجمه ({src} → {tgt}):\n{translated}")
    except Exception as e:
        logger.error(f"Failed to translate text for update {update.update_id}: {e}", exc_info=True)
        await update.message.reply_text("An unexpected error occurred during translation.")

async def translate_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ در حال پردازش تصویر...")
    photo_file = await update.message.photo[-1].get_file()
    photo_path = Translator.save_temp_photo(photo_file)

    mode = context.user_data.get('translation_mode')
    if mode:
        src, tgt = mode.split('_')
    else:
        src, tgt = 'auto', 'auto'

    try:
        translator = Translator(source=src, target=tgt)
        extracted_text, translated_text = await translator.translate_image(photo_path)

        if "Error:" in extracted_text or not translated_text:
            await update.message.reply_text(extracted_text)
        elif not extracted_text:
            await update.message.reply_text("متنی در تصویر پیدا نشد!")
        else:
            await update.message.reply_text(f"🌐 متن استخراج شده ({translator.source} → {translator.target}):\n{translated_text}")
    except Exception as e:
        logger.error(f"Failed to process image for update {update.update_id}: {e}", exc_info=True)
        await update.message.reply_text("An unexpected error occurred during image processing.")

async def translate_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ Processing audio...")
    audio_file = await update.message.audio.get_file()
    audio_path = Translator.save_temp_audio(audio_file)

    mode = context.user_data.get('translation_mode')
    if mode:
        src, tgt = mode.split('_')
    else:
        src, tgt = 'auto', 'auto'

    try:
        translator = Translator(source=src, target=tgt)
        extracted_text, translated_text = await translator.translate_audio(audio_path)

        if "Error:" in extracted_text or not translated_text:
            await update.message.reply_text(extracted_text)
        elif not extracted_text:
            await update.message.reply_text("No text found in the audio.")
        else:
            await update.message.reply_text(f"🎤 Extracted text ({translator.source} → {translator.target}):\n{translated_text}")
    except Exception as e:
        logger.error(f"Failed to process audio for update {update.update_id}: {e}", exc_info=True)
        await update.message.reply_text("An unexpected error occurred during audio processing.")
