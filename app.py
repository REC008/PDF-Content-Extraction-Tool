from flask import Flask, render_template, request, redirect, jsonify
from pdf_utils import convert_pdf_to_images, extract_images_from_pdf, extract_text_from_pdf
from config import Config
import os

app = Flask(__name__)
app.config.from_object(Config)

@app.route('/', methods=['GET', 'POST'])
def index():
    page_images = []
    extracted_text = []
    extracted_images = []
    text_from_pdf = []
    pdf_filename = None  # Initialize pdf_filename

    if request.method == 'POST':
        if 'pdf_file' not in request.files:
            return redirect(request.url)

        pdf_file = request.files['pdf_file']
        if pdf_file.filename == '':
            return redirect(request.url)

        if pdf_file:
            try:
                pdf_filename = pdf_file.filename  # Save the filename
                pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], pdf_filename)
                pdf_file.save(pdf_path)

                page_images, extracted_text = convert_pdf_to_images(pdf_path)
                extracted_images = extract_images_from_pdf(pdf_path)
                text_from_pdf, word_positions = extract_text_from_pdf(pdf_path)

            except Exception as e:
                return f"An error occurred while processing the PDF: {e}"

    combined_data = list(zip(page_images, extracted_text))
    return render_template('index.html', combined_data=combined_data, extracted_images=extracted_images,
                           text_from_pdf=text_from_pdf, pdf_filename=pdf_filename)

@app.route('/find_text', methods=['POST'])
def find_text():
    search_text = request.form['text']
    pdf_filename = request.form['pdf_filename']
    pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], pdf_filename)

    # Extract text and word positions from the PDF
    _, word_positions = extract_text_from_pdf(pdf_path)

    all_occurrences = []
    for page_number, words in enumerate(word_positions):
        line_number = 1
        current_line_text = ''
        for word in words:
            current_line_text += word[4] + ' '
            if search_text.lower() in word[4].lower():
                all_occurrences.append({
                    'page': page_number + 1,
                    'line': line_number,
                    'text': word[4],
                    'x': word[0],
                    'y': word[1]
                })
            if word[4].endswith('\n'):
                line_number += 1
                current_line_text = ''  # Reset for the new line

    return jsonify({'results': all_occurrences})

if __name__ == '__main__':
    app.run(debug=True)
