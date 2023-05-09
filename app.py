from flask import Flask, render_template, request, make_response
from werkzeug.utils import secure_filename
from pdf2image import convert_from_path

import json
import numpy as np
import os, shutil
import pytesseract
import cv2
import time

hsv_min = np.array((2, 28, 65), np.uint8)
hsv_max = np.array((26, 238, 255), np.uint8)
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
            for path in res_paths:

                im1 = cv2.imread(path, 0)
                im = cv2.imread(path)
                high, wid = im1.shape
                size_image = high * wid

                ret, thresh_value = cv2.threshold(im1, 180, 255, cv2.THRESH_BINARY_INV)

                kernel = np.ones((5, 5), np.uint8)
                dilated_value = cv2.dilate(thresh_value, kernel, iterations=1)

                contours, hierarchy = cv2.findContours(dilated_value, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                coordinates = []
                for cnt in contours:
                    x, y, w, h = cv2.boundingRect(cnt)
                    # bounding the images
                    if (0.150 > (w * h) / size_image) and ((w * h) / size_image >= 0.001):
                        coordinates.append((x, y, w, h))
                        cv2.rectangle(im, (x, y), (x + w, y + h), (0, 0, 255), 1)

                # cv2.imwrite('detectable.jpg', im)

                coordinates = sorted(coordinates, key=lambda coord: (coord[1], coord[0]))
                cur_list = []
                lastY = 0
                result_table = []
                for rect in coordinates:
                    x, y, w, h = rect
                    cur_img_by_rect = im[y:y + h, x:x + w]

                    line_parse = pytesseract.image_to_string(cur_img_by_rect, lang='rus+eng')
                    line_parse = line_parse.strip().replace('\n', ' ')
                    if abs(lastY - y) < 0.1:
                        cur_list.append(line_parse)
                    else:
                        lastY = y
                        if len(cur_list) > 0:
                            result_table.append(cur_list.copy())
                        cur_list = [line_parse]
                result_table.append(cur_list)
                result_file.append(result_table)
            with open('result_value.txt', 'w') as f:
                for el in result_file:
                    for ell in el:
                        f.write(str(ell))
                        f.write('\n')
                    f.write('\n')
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


if __name__ == '__main__':
    port = 5000
    app.run(debug=True, host='0.0.0.0', port=port)
