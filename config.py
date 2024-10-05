import os

class Config:
    UPLOAD_FOLDER = 'static/pdf_images/'
    POPPLER_PATH = 'C:\\Program Files\\poppler\\poppler-24.07.0\\Library\\bin'
    TESSERACT_CMD = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

# Ensure the upload folder exists
if not os.path.exists(Config.UPLOAD_FOLDER):
    os.makedirs(Config.UPLOAD_FOLDER)
