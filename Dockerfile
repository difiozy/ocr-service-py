FROM ubuntu:18.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
  && apt-get -y install tesseract-ocr-rus \
  && apt-get install -y python3 python3-distutils python3-pip \
  && cd /usr/local/bin \
  && ln -s /usr/bin/python3 python \
  && pip3 --no-cache-dir install --upgrade pip \
  && rm -rf /var/lib/apt/lists/*

RUN apt update && apt-get update
RUN apt-get install ffmpeg -y
RUN apt-get install libsm6 -y
RUN apt-get install libxext6 -y

RUN pip3 install pytesseract
RUN pip3 install opencv-python
RUN pip3 install pillow

RUN pip3 install pdf2image
RUN apt-get install poppler-utils -y