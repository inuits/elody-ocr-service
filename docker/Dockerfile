### Base stage
FROM python:3.11-slim AS base-stage

ENV FLASK_APP=app.py

RUN apt-get -y update && apt-get -y install git libmagic1 tesseract-ocr tesseract-ocr-fra tesseract-ocr-nld pkg-config autoconf gcc build-essential automake libtool && \
    adduser --disabled-password --home /app --shell /bin/bash app

RUN wget https://github.com/ArtifexSoftware/ghostpdl-downloads/releases/download/gs10011/ghostscript-10.01.1.tar.gz && \
    tar -zxf /ghostscript-10.01.1.tar.gz && \
    cd ghostscript-10.01.1/ && \
    ./configure --prefix=/usr && \
    make so -j9 && \
    make soinstall && \
    rm ghostscript-10.01.1.tar.gz

RUN git clone https://github.com/tesseract-ocr/tessdata_best.git  && \
    cp -r tessdata_best /ghostscript-10.01.1/tesseract/tessdata/tessdata_best/ && \
    rm -rf tessdata_best

USER app
WORKDIR /app

COPY docker/entrypoint*.sh /
COPY docker/run-tests.sh /
COPY docker/test-coverage.sh /
COPY requirements.txt ./
COPY requirements_dev.txt ./

RUN echo "export PATH=${PATH}:/app/.local/bin" >> .bashrc

ENTRYPOINT ["/entrypoint.sh"]

### Development stage
FROM base-stage AS development-stage

ENV APP_ENV=dev

COPY docker/pip.conf /etc

RUN pip install --no-cache-dir -r requirements.txt -r requirements_dev.txt

EXPOSE 5000

### Build stage
FROM base-stage AS build-stage

COPY docker/pip.conf /etc
COPY api ./api

RUN pip install --no-cache-dir -r requirements.txt

### Production stage
FROM base-stage AS production-stage

ENV APP_ENV=prod

COPY --from=build-stage /app /app

ENV GUNICORN_CMD_ARGS="--workers=3"

EXPOSE 8000
