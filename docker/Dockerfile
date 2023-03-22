### Base stage
FROM python:3.11-slim AS base-stage

ENV FLASK_APP=app.py

RUN apt-get -y update && apt-get -y install libmagic1 tesseract-ocr tesseract-ocr-fra tesseract-ocr-nld && adduser --disabled-password --home /app --shell /bin/bash app
USER app
WORKDIR /app

COPY docker/entrypoint*.sh /
COPY docker/run-tests.sh /
COPY requirements.txt ./

RUN echo "export PATH=${PATH}:/app/.local/bin" >> .bashrc

ENTRYPOINT ["/entrypoint.sh"]

### Development stage
FROM base-stage AS development-stage

ENV APP_ENV=dev

COPY docker/pip.conf /etc

RUN pip install --no-cache-dir -r requirements.txt

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
