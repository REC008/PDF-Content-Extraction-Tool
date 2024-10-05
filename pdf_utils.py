import os
from PIL import Image
from pdf2image import convert_from_path
import pytesseract
import fitz  # PyMuPDF
from config import Config
from flask import url_for, jsonify


def convert_pdf_to_images(pdf_path, dpi=100, max_width=500):
    pdf_filename = os.path.splitext(os.path.basename(pdf_path))[0]
    pdf_dir = os.path.join(Config.UPLOAD_FOLDER, pdf_filename)

    if not os.path.exists(pdf_dir):
        os.makedirs(pdf_dir)

    pages = convert_from_path(pdf_path, dpi=dpi, poppler_path=Config.POPPLER_PATH)

    page_images = []
    extracted_text = []

    for page_number, page in enumerate(pages):
        width_percent = (max_width / float(page.size[0]))
        new_height = int((float(page.size[1]) * float(width_percent)))
        resized_image = page.resize((max_width, new_height), Image.LANCZOS)

        image_filename = f"page_{page_number + 1}.png"
        image_path = os.path.join(pdf_dir, image_filename)
        resized_image.save(image_path, 'PNG')
        page_images.append(url_for('static', filename=f'pdf_images/{pdf_filename}/{image_filename}'))

        text = pytesseract.image_to_string(resized_image)
        extracted_text.append(text)

    # Save the extracted text as a file
    text_filename = f"{pdf_filename}_text.txt"
    text_path = os.path.join(pdf_dir, text_filename)
    with open(text_path, 'w', encoding='utf-8') as text_file:
        text_file.write("\n\n".join(extracted_text))

    return page_images, extracted_text


def extract_images_from_pdf(pdf_path):
    pdf_filename = os.path.splitext(os.path.basename(pdf_path))[0]
    pdf_dir = os.path.join(Config.UPLOAD_FOLDER, pdf_filename)

    if not os.path.exists(pdf_dir):
        os.makedirs(pdf_dir)

    pdf_document = fitz.open(pdf_path)
    extracted_images = []

    for page_number in range(len(pdf_document)):
        page = pdf_document.load_page(page_number)
        image_list = page.get_images(full=True)

        for img_index, image in enumerate(image_list):
            xref = image[0]
            base_image = pdf_document.extract_image(xref)
            image_bytes = base_image["image"]
            image_filename = f"page_{page_number + 1}_image_{img_index + 1}.png"
            image_path = os.path.join(pdf_dir, image_filename)
            with open(image_path, "wb") as img_file:
                img_file.write(image_bytes)
            extracted_images.append(url_for('static', filename=f'pdf_images/{pdf_filename}/{image_filename}'))

    return extracted_images


def extract_text_from_pdf(pdf_path):
    pdf_filename = os.path.splitext(os.path.basename(pdf_path))[0]
    pdf_dir = os.path.join(Config.UPLOAD_FOLDER, pdf_filename)

    if not os.path.exists(pdf_dir):
        os.makedirs(pdf_dir)

    pdf_document = fitz.open(pdf_path)
    text_from_pdf = []
    word_positions = []

    for page_number in range(len(pdf_document)):
        page = pdf_document.load_page(page_number)
        text = page.get_text("text")
        text_from_pdf.append(text)

        # Get word positions
        words = page.get_text("words")  # Returns a list of words with their positions
        word_positions.append(words)

    # Save the extracted text as a file
    text_filename = f"{pdf_filename}_layout_text.txt"
    text_path = os.path.join(pdf_dir, text_filename)
    with open(text_path, 'w', encoding='utf-8') as text_file:
        text_file.write("\n\n".join(text_from_pdf))

    return text_from_pdf, word_positions