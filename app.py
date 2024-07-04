from flask import Flask, request, render_template, jsonify, Response
import os
import fitz
from io import BytesIO
import zipfile
import logging

try:
    from config import API_KEY
except ImportError:
    print("API key not found. Please create a config.py file with API_KEY variable.")
    exit(1)

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def pdftoimage(pdf_file, output_folder, folder_name=None):
    pdf = fitz.open(pdf_file)
    outputimg = []

    if folder_name:
        folder_path = os.path.join(output_folder, folder_name)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
    else:
        folder_path = output_folder

    for page_num in range(pdf.page_count):
        page = pdf[page_num]
        pix = page.get_pixmap()
        output_file = os.path.join(folder_path, f"page_{page_num + 1}.jpeg")
        pix.save(output_file)
        outputimg.append(output_file)

    pdf.close()
    return folder_path, outputimg

@app.route('/', methods=['GET'])
def home():
    return render_template('index.html', api_key=API_KEY)

@app.route('/convert', methods=['POST'])
def convert_pdf():
    api_key = request.headers.get('X-API-Key')
    if api_key != API_KEY:
        return Response(status=401)

    if 'file' not in request.files:
        return Response(status=400)

    file = request.files['file']
    if file.filename == '':
        return Response(status=400)

    if file and file.filename.endswith('.pdf'):
        output_folder = 'temp_output'
        os.makedirs(output_folder, exist_ok=True)

        pdf_path = os.path.join(output_folder, file.filename)
        file.save(pdf_path)

        folder_name = request.form.get('folder_name', '')
        if not folder_name:
            folder_name = os.path.splitext(file.filename)[0]

        folder_path, output_images = pdftoimage(pdf_path, output_folder, folder_name)

        memory_file = BytesIO()
        with zipfile.ZipFile(memory_file, 'w') as zf:
            for img in output_images:
                zf.write(img, os.path.join(folder_name, os.path.basename(img)))
        memory_file.seek(0)

        for img in output_images:
            os.remove(img)
        os.remove(pdf_path)
        zip_filename = f"{folder_name}.zip"

        temp_zip_path = os.path.join(output_folder, zip_filename)
        with open(temp_zip_path, 'wb') as f:
            f.write(memory_file.getvalue())

        return jsonify({"status": "success", "filename": zip_filename})

    return Response(status=400)

@app.route('/download/<filename>')
def download_file(filename):
    return send_file(f"temp_output/{filename}", as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)