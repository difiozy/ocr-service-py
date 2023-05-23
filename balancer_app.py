from flask import Flask, render_template, request, make_response
from werkzeug.utils import secure_filename
from concurrent.futures import ThreadPoolExecutor
from PyPDF2 import PdfWriter, PdfReader

import os, shutil
import requests
import time
import concurrent

app = Flask(__name__)
UPLOAD_FOLDER = './static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024
max_threads = int(os.environ['THREAD_BY_REQUEST'])
ocr_proxy = os.environ['OCR_PROXY_HOST']


@app.route("/")
def index():
    return render_template("index.html")


@app.route('/uploader', methods=['POST'])
def upload_file():
    res_paths = []
    try:
        if request.method == 'POST':
            f = request.files['file']

            filename = secure_filename(f.filename)
            filename = os.path.splitext(filename)[0]

            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            f.save(filepath)
            cur_time = time.time()
            inputpdf = PdfReader(open(filepath, "rb"))

            for i in range(len(inputpdf.pages)):
                cur_path = os.path.join(app.config['UPLOAD_FOLDER'], str(int(cur_time)) + str(i) + filename + '.png')
                output = PdfWriter()
                output.add_page(inputpdf.pages[i])
                with open(cur_path, "wb") as outputStream:
                    output.write(outputStream)
                res_paths.append(cur_path)

            result_file = []
            nginx_path = ocr_proxy + '/uploader'
            with ThreadPoolExecutor(max_workers=max_threads*3) as executor:
                processes = {executor.submit(recognize_file, nginx_path, query) for query in res_paths}
                for result in concurrent.futures.as_completed(processes):
                    result_file.append(result.result())

            return make_response(str(result_file).replace('\\\'', '\''))
    finally:
        for filename in os.listdir(app.config['UPLOAD_FOLDER']):
            if filename not in res_paths:
                continue
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))


def recognize_file(endpoint: str, filename: str) -> str:
    headers = {"enctype": "multipart/form-data",
               'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    with requests.post(endpoint, files={'file': open(filename, 'rb'), }, headers=headers) as response:
        with open('res.txt', 'w') as f:
            f.write(str(response.text))
        return str(response.text)


if __name__ == '__main__':
    port = 5500
    app.run(debug=True, host='0.0.0.0', port=port)
