# bot_handlers.py
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from translator import Translator
from utils import detect_language
from database import set_user_preference, get_user_preference

logger = logging.getLogger(__name__)

async def get_translation_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mode = context.user_data.get('translation_mode')
    if not mode:
        user_id = update.effective_user.id
        mode = get_user_preference(user_id)
        if mode:
            context.user_data['translation_mode'] = mode
    return mode

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
    user_id = query.from_user.id
    translation_mode = query.data
    set_user_preference(user_id, translation_mode)
    context.user_data['translation_mode'] = translation_mode
    await query.edit_message_text(
        text=f"✅ حالت ترجمه انتخاب شد: {query.data.replace('_', ' → ')}\nحالا متن یا عکس خود را ارسال کنید."
    )

async def translate_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if not text:
        await update.message.reply_text("متن خالی دریافت شد!")
        return

    mode = await get_translation_mode(update, context)
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
        await update.message.reply_text("مشکلی در ترجمه متن پیش آمد!")

async def translate_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ در حال پردازش تصویر...")
    photo_file = await update.message.photo[-1].get_file()
    photo_path = Translator.save_temp_photo(photo_file)

    mode = await get_translation_mode(update, context)
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
        await update.message.reply_text("مشکلی در پردازش تصویر پیش آمد!")

async def translate_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ Processing audio...")
    audio_file = await update.message.audio.get_file()
    audio_path = Translator.save_temp_audio(audio_file)

    mode = await get_translation_mode(update, context)
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
        await update.message.reply_text("مشکلی در پردازش صوت پیش آمد!")

async def translate_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ Processing document...")
    document_file = await update.message.document.get_file()
    document_path = Translator.save_temp_document(document_file)

    mode = await get_translation_mode(update, context)
    if mode:
        src, tgt = mode.split('_')
    else:
        src, tgt = 'auto', 'auto'

    try:
        translator = Translator(source=src, target=tgt)
        extracted_text, translated_text = await translator.translate_document(document_path)

        if "Error:" in extracted_text or not translated_text:
            await update.message.reply_text(extracted_text)
        elif not extracted_text:
            await update.message.reply_text("No text found in the document.")
        else:
            await update.message.reply_text(f"📄 Extracted text ({translator.source} → {translator.target}):\n{translated_text}")
    except Exception as e:
        logger.error(f"Failed to process document for update {update.update_id}: {e}", exc_info=True)
        await update.message.reply_text("مشکلی در پردازش سند پیش آمد!")
