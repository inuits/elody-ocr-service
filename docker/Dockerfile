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

RUN wget https://github.com/tesseract-ocr/tessdata_best/archive/refs/tags/4.1.0.tar.gz && \
    tar -zxf 4.1.0.tar.gz && \
    cp -r tessdata_best-4.1.0/ /usr/lib/ && \
    rm -rf 4.1.0.tar.gz tessdata_best-4.1.0/

RUN apt-get -y remove \
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
