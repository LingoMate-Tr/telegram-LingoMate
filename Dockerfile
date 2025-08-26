RUN pip uninstall -y python-telegram-bot \
    && pip install --no-cache-dir -r requirements.txt
# استفاده از Python 3.13 slim برای کانتینر سبک
FROM python:3.13-slim

# نصب tesseract و زبان فارسی
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-fas \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# ایجاد دایرکتوری کاری
WORKDIR /app

# کپی کردن فایل‌ها به کانتینر
COPY . .

# نصب کتابخانه‌های پایتون
RUN pip install --no-cache-dir -r requirements.txt

# فرمان اجرای ربات
CMD ["python", "bot.py"]

