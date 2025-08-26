import logging
import os
import uuid
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler,
    ContextTypes, filters
)
from deep_translator import GoogleTranslator
from PIL import Image
import pytesseract

# ---------- تنظیمات ----------
TOKEN = os.environ.get("TOKEN")
pytesseract.pytesseract.tesseract_cmd = "tesseract"

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ---------- توابع کمکی ----------
def detect_language(text: str) -> str:
    try:
        lang = GoogleTranslator(source='auto', target='en').detect(text)
        if lang.startswith('fa'):
            return 'fa'
        else:
            return 'en'
    except Exception as e:
        logger.warning(f"Language detection failed: {e}")
        return 'en'

# ---------- دستورات ----------
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

    try:
        mode = context.user_data.get('translation_mode')
        if mode:
            src, tgt = mode.split('_')
        else:
            src = detect_language(text)
            tgt = 'fa' if src == 'en' else 'en'

        translated = GoogleTranslator(source=src, target=tgt).translate(text)
        await update.message.reply_text(f"🌐 ترجمه ({src} → {tgt}):\n{translated}")
    except Exception as e:
        logger.error(f"Error translating text: {e}")
        await update.message.reply_text("مشکلی در ترجمه متن پیش آمد!")

async def translate_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo_path = f"/tmp/temp_{uuid.uuid4().hex}.jpg"
    try:
        await update.message.reply_text("⏳ در حال پردازش تصویر...")
        photo_file = await update.message.photo[-1].get_file()
        await photo_file.download_to_drive(photo_path)

        img = Image.open(photo_path).convert("L")
        text = pytesseract.image_to_string(img, lang='fas+eng').strip()

        if not text:
            await update.message.reply_text("متنی در تصویر پیدا نشد!")
            return

        mode = context.user_data.get('translation_mode')
        if mode:
            src, tgt = mode.split('_')
        else:
            src = detect_language(text)
            tgt = 'fa' if src == 'en' else 'en'

        translated = GoogleTranslator(source=src, target=tgt).translate(text)
        await update.message.reply_text(f"🌐 متن استخراج شده ({src} → {tgt}):\n{translated}")
    except Exception as e:
        logger.error(f"Error processing image: {e}")
        await update.message.reply_text("مشکلی در پردازش تصویر پیش آمد!")
    finally:
        if os.path.exists(photo_path):
            os.remove(photo_path)

# ---------- اجرای ربات ----------
if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, translate_text))
    app.add_handler(MessageHandler(filters.PHOTO, translate_image))

    logger.info("ربات در حال اجراست...")
    app.run_polling()