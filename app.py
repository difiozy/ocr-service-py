from flask import Flask, render_template, request
from werkzeug import secure_filename
from pdf2image import convert_from_path
import numpy as np
import os
import sys
from PIL import Image
import pytesseract
import argparse
import cv2
import time

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
        images = convert_from_path(filepath, 300)
        res_paths = []
        for i in range(len(images)):
            cur_path = os.path.join(app.config['UPLOAD_FOLDER'], str(int(cur_time)) + str(i) + filename + '.png')
            images[i].save(cur_path)
            res_paths.append(cur_path)

        result_file = []
        for path in res_paths:
            coordinates = []
            image = cv2.imread(path)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
            ret, thresh = cv2.threshold(gray, 75, 255, cv2.THRESH_BINARY_INV)
            obr_img = cv2.erode(thresh, np.ones((2, 2), np.uint8), iterations=1)
            obr_img = cv2.GaussianBlur(obr_img, (3, 3), 0)
            contours, hierarchy = cv2.cvStartFindContours_Impl(obr_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_TC89_L1)
            cap = round(max(image.shape[0], image.shape[1]) * 0.005)
            for i in range(0, len(contours)):
                x, y, w, h = cv2.boundingRect(contours[i])
                if h > 50 and w > 50 and h * w > cap:
                    coordinates.append((x, y, w, h))
            coordinates = sorted(coordinates, key=lambda coord: coord.y)
            cur_list = []
            lastY = 0
            result_table = []
            for rect in coordinates:
                x, y, w, h = rect
                line_parse = pytesseract.image_to_string(gray[y:y+h, x:x+w])
                line_parse = line_parse.strip().replaceAll('\n', ' ')
                if abs(lastY - y) < 0.1:
                    cur_list.append(line_parse)
                else:
                    lastY = y
                    if len(cur_list) > 0:
                        result_table.append(cur_list.copy())
                    cur_list = []
                    cur_list.append(line_parse)
            result_table.append(cur_list)
            result_file.append(result_table)

        return render_template("uploaded.html", displaytext=result_file, fname=filename)


if __name__ == '__main__':
    port = 5000
    app.run(debug=True, host='0.0.0.0', port=port)
    # app.run(host="0.0.0.0", port=5000, debug=True)
