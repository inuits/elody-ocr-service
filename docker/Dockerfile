### Base stage
FROM python:3.11-slim AS base-stage

ENV FLASK_APP=app.py

RUN apt-get update && apt-get install -y --no-install-recommends \
    autoconf \
    automake \
    build-essential \
    gcc \
    libmagic1 \
    libtool \
    pkg-config \
    tesseract-ocr \
    tesseract-ocr-fra \
    tesseract-ocr-nld \
    wget \
    && rm -rf /var/lib/apt/lists/*

RUN wget https://github.com/ArtifexSoftware/ghostpdl-downloads/releases/download/gs10011/ghostscript-10.01.1.tar.gz && \
    tar -zxf ghostscript-10.01.1.tar.gz && \
    cd ghostscript-10.01.1/ && \
    ./configure --prefix=/usr && \
    make so -j9 && \
    make soinstall && \
    cd / && \
    rm -rf ghostscript-10.01.1.tar.gz ghostscript-10.01.1/

RUN mkdir -p /usr/lib/tessdata/script && \
    wget https://raw.githubusercontent.com/tesseract-ocr/tessdata_best/main/script/Latin.traineddata -O /usr/lib/tessdata/script/Latin.traineddata && \
    wget https://raw.githubusercontent.com/tesseract-ocr/tessdata_best/main/nld.traineddata -O /usr/lib/tessdata/nld.traineddata && \
    wget https://raw.githubusercontent.com/tesseract-ocr/tessdata_best/main/eng.traineddata -O /usr/lib/tessdata/eng.traineddata && \
    wget https://raw.githubusercontent.com/tesseract-ocr/tessdata_best/main/fra.traineddata -O /usr/lib/tessdata/fra.traineddata

RUN apt-get -y purge \
    autoconf \
    automake \
    build-essential \
    gcc \
    libtool \
    pkg-config \
    wget

RUN adduser --disabled-password --home /app --shell /bin/bash app

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
