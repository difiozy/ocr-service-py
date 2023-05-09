from flask import Flask, render_template, request, make_response
from requests import Response
from werkzeug.utils import secure_filename
from pdf2image import convert_from_path
from concurrent.futures import ThreadPoolExecutor

from os import environ
import os, shutil
import requests
import time
import concurrent

app = Flask(__name__)
UPLOAD_FOLDER = './static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024


@app.route("/")
def index():
    return render_template("index.html")


@app.route('/uploader', methods=['POST'])
def upload_file():
    try:
        if request.method == 'POST':
            f = request.files['file']
            # create a secure filename
            filename = secure_filename(f.filename)
            filename = os.path.splitext(filename)[0]

            # save file to /static/uploads
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            f.save(filepath)
            cur_time = time.time()
            images = convert_from_path(filepath, 900)
            res_paths = []
            for i in range(len(images)):
                cur_path = os.path.join(app.config['UPLOAD_FOLDER'], str(int(cur_time)) + str(i) + filename + '.png')
                images[i].save(cur_path)
                res_paths.append(cur_path)

            result_file = []
            nginx_path = os.environ['NGINX_HOST'] + '/uploader'
            with ThreadPoolExecutor(max_workers=2) as executor:
                processes = {executor.submit(recognize_file, nginx_path, query) for query in res_paths}
                for result in concurrent.futures.as_completed(processes):
                    result_file.append(result.result())
                    print(result.result())

            return make_response(str(result_file))
    finally:
        for filename in os.listdir(app.config['UPLOAD_FOLDER']):
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))


def recognize_file(host: str, filename: str) -> Response:
    files = {'media': open(filename, 'rb')}
    return requests.post(host, files=files)


if __name__ == '__main__':
    port = 5500
    app.run(debug=True, host='0.0.0.0', port=port)
