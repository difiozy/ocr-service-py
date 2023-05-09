FROM ubuntu:latest

ENV DEBIAN_FRONTEND=noninteractive

RUN apt update && apt-get update && apt upgrade
RUN apt install poppler-utils -y
RUN apt install python3.10 -y
RUN apt-get install -y libsm6
RUN apt-get install ffmpeg -y
RUN apt-get install libxext6 -y
RUN apt-get update \
  && apt-get -y install tesseract-ocr-rus \
  && apt-get -y install tesseract-ocr\
  && apt-get install -y python3 python3-distutils python3-pip \
  && cd /usr/local/bin \
  && ln -s /usr/bin/python3 python \
  && pip3 --no-cache-dir install --upgrade pip \
  && rm -rf /var/lib/apt/lists/*

RUN pip3 install pytesseract
RUN pip3 install matplotlib
RUN pip3 install opencv-python
RUN pip3 install pillow

RUN pip3 install pdf2image

COPY requirements.txt req.txt
RUN pip3 install -r req.txt