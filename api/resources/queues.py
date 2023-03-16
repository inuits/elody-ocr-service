import app
from flask_restful import abort
from services.ocr_service import OcrService
from services.storage_api_service import StorageApiService


@app.rabbit.queue("dams.ocr_request")
def do_ocr(routing_key, body, message_id):
    app.logger.info('Message received:')
    app.logger.info('\tKey: {}'.format(routing_key))

    ocr_service = OcrService()
    storage_api_service = StorageApiService()

    # run ocr job
    try:
        ocr_output, mediafile_name, content_type = ocr_service.ocr(body["operation"], body["mediafile_image_data"],
                                                                   body["lang"], body["image_name"])
    except Exception as ex:
        app.logger.error(f'"In queues - The ocr function failed with:" {ex}')

    # ocr job finished -> save ocr_image in storage api
    try:
        storage_api_service.upload_ocr(ocr_output, body["id_new_mediafile"], mediafile_name, content_type)
    except Exception as ex:
        app.logger.error(f'"The ocr function failed during uploading the image in the storage api:" {ex}')

    app.logger.info("The ocr job is complete. You can now fetch the image with the given id")
