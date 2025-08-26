# Use a lightweight Python base image
FROM python:3.11-slim

# Install Tesseract OCR and Persian language support
RUN apt-get update && apt-get install -y tesseract-ocr tesseract-ocr-fas

# Set working directory in the container
WORKDIR /app

# Copy all project files to the container
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Command to run the bot
CMD ["python", "bot.py"]
