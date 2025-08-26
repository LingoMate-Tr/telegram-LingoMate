
# ---------- تنظیمات اولیه ----------
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler
from deep_translator import GoogleTranslator
from PIL import Image
import pytesseract
import os
import uuid

# ---------- تنظیمات اولیه ----------
TOKEN = os.environ.get("TOKEN")  # از Environment Variable استفاده کن

# مسیر Tesseract مناسب Render
pytesseract.pytesseract.tesseract_cmd = "tesseract"

# راه‌اندازی logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# ---------- دستور start ----------
def start(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("فارسی → انگلیسی", callback_data='fa_en')],
        [InlineKeyboardButton("انگلیسی → فارسی", callback_data='en_fa')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        "سلام! من ربات ترجمه هستم 😎\n"
        "می‌تونی متن یا عکس حاوی متن برام بفرستی تا برات ترجمه کنم.\n"
        "ابتدا زبان ترجمه مورد نظر خودت را انتخاب کن:",
        reply_markup=reply_markup
    )

# ---------- مدیریت انتخاب زبان ----------
def button(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    context.user_data['translation_mode'] = query.data
    query.edit_message_text(text=f"✅ حالت ترجمه انتخاب شد: {query.data.replace('_', ' → ')}\n"
                                 "حالا متن یا عکس خود را ارسال کنید.")

# ---------- ترجمه متن ----------
def translate_text(update: Update, context: CallbackContext):
    try:
        text = update.message.text
        if not text.strip():
            update.message.reply_text("متن خالی دریافت شد!")
            return

        # استفاده از حالت انتخابی کاربر یا شناسایی خودکار
        mode = context.user_data.get('translation_mode')
        if mode:
            src, tgt = mode.split('_')
        else:
            # تشخیص خودکار زبان
            detected_lang = GoogleTranslator(source='auto', target='en').detect(text)
            src = detected_lang
            tgt = 'fa' if detected_lang == 'en' else 'en'

        translated = GoogleTranslator(source=src, target=tgt).translate(text)
        update.message.reply_text(f"🌐 ترجمه ({src} → {tgt}):\n{translated}")

    except Exception as e:
        logger.error(f"Error translating text: {e}")
        update.message.reply_text("مشکلی در ترجمه متن پیش آمد!")

# ---------- ترجمه متن داخل عکس ----------
def translate_image(update: Update, context: CallbackContext):
    try:
        update.message.reply_text("⏳ در حال پردازش تصویر...")

        photo_file = update.message.photo[-1].get_file()
        photo_path = f"/tmp/temp_{uuid.uuid4().hex}.jpg"
        photo_file.download(photo_path)

        # باز کردن تصویر و تبدیل به grayscale
        img = Image.open(photo_path).convert("L")
        text = pytesseract.image_to_string(img, lang='fas+eng')

        if not text.strip():
            update.message.reply_text("متنی در تصویر پیدا نشد!")
            os.remove(photo_path)
            return

        # استفاده از حالت انتخابی کاربر یا شناسایی خودکار
        mode = context.user_data.get('translation_mode')
        if mode:
            src, tgt = mode.split('_')
        else:
            detected_lang = GoogleTranslator(source='auto', target='en').detect(text)
            src = detected_lang
            tgt = 'fa' if detected_lang == 'en' else 'en'

        translated = GoogleTranslator(source=src, target=tgt).translate(text)
        update.message.reply_text(f"🌐 متن استخراج شده ({src} → {tgt}):\n{translated}")

        os.remove(photo_path)

    except Exception as e:
        logger.error(f"Error processing image: {e}")
        update.message.reply_text("مشکلی در پردازش تصویر پیش آمد!")

# ---------- ثبت هندلرها ----------
def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(button))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, translate_text))
    dp.add_handler(MessageHandler(Filters.photo, translate_image))

    updater.start_polling()
    logger.info("ربات در حال اجراست...")
    updater.idle()

if __name__ == '__main__':
    main()
