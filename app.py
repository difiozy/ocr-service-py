from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
from pdf2image import convert_from_path

import numpy as np
import os
import sys
from PIL import Image
import pytesseract
import argparse
import cv2
import time
import matplotlib.pyplot as plt

hsv_min = np.array((2, 28, 65), np.uint8)
hsv_max = np.array((26, 238, 255), np.uint8)
app = Flask(__name__)
UPLOAD_FOLDER = './static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route('/uploader', methods=['GET', 'POST'])
def upload_file():
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
            coordinates = []

            im1 = cv2.imread(path, 0)
            im = cv2.imread(path)
            h, w = im1.shape
            size_image = h * w

            ret, thresh_value = cv2.threshold(im1, 180, 255, cv2.THRESH_BINARY_INV)

            kernel = np.ones((5, 5), np.uint8)
            dilated_value = cv2.dilate(thresh_value, kernel, iterations=1)

            contours, hierarchy = cv2.findContours(dilated_value, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            cordinates = []
            for cnt in contours:
                x, y, w, h = cv2.boundingRect(cnt)
                cordinates.append((x, y, w, h))
                # bounding the images
                if 0.150 >= (w * h) / size_image >= 0.001:
                    cv2.rectangle(im, (x, y), (x + w, y + h), (0, 0, 255), 1)
            # plt.imshow(im)
            # cv2.namedWindow('detecttable', cv2.WINDOW_NORMAL)
            cv2.imwrite('detecttable.jpg', im)
            # cap = round(max(image.shape[0], image.shape[1]) * 0.005)

            cordinates = sorted(cordinates, key=lambda coord: coord[1])
            cur_list = []
            lastY = 0
            result_table = []
            for rect in cordinates:
                x, y, w, h = rect
                cur_img_by_rect = im[y:y + h, x:x + w]

                line_parse = pytesseract.image_to_string(cur_img_by_rect, lang='rus')
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
            f.write(str(result_file))
        return render_template("uploaded.html", displaytext=result_file, fname=filename)


if __name__ == '__main__':
    port = 5000
    app.run(debug=True, host='0.0.0.0', port=port)
    # app.run(host="0.0.0.0", port=5000, debug=True)
