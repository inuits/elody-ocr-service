import app
from services.ocr_service import OcrService


def __is_malformed_message(data, fields, mimetypes):
    raise NotImplementedError("not implemented")


@app.rabbit.queue("dams.file_uploaded")
def __do_ocr(body, operation, error_message):
    # eenmalige initialisatie van singleton ocr_service
    data = body["data"]

    try:
        ocr_engine = OcrService(data["mediafile"], data["url"])
        ocr_engine.ocr(operation, data["image_ids"], data["language"])
    except Exception as ex:
        app.logger.error(f'{error_message.format(data["mediafile"]["filename"])} {ex}')
