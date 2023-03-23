import app
import json
from services.ocr_service import OcrService
from services.storage_api_service import StorageApiService
from services.collection_api_service import CollectionApiService


def __get_ocr_output(operation, mediafile_image_data, lang, image_name):
    ocr_service = OcrService()
    try:
        return ocr_service.ocr(
            operation, mediafile_image_data, lang, image_name
        )  # ERROR IS HERE
    except Exception as ex:
        app.logger.error(f'"In queues - The ocr function failed with:" {ex}')


def __upload_ocr_output(ocr_output, id_new_mediafile, mediafile_name, content_type):
    storage_api_service = StorageApiService()
    try:
        storage_api_service.upload_ocr(
            ocr_output, id_new_mediafile, mediafile_name, content_type
        )
    except Exception as ex:
        app.logger.error(
            f'"The ocr function failed during uploading the image in the storage api:" {ex}'
        )


# def __get_and_finish_job(body):
#     collection_api_service = CollectionApiService()
#     try:
#         job = collection_api_service.get_job_by_id(body.get("main_job_identifier"))
#     except Exception as ex:
#         app.logger.error(
#             f'"The ocr function failed during fetching the job by id:" {ex}'
#         )
#
#     app.jobs_extension.finish_job(
#         job,
#         f"Successfully OCRed image '{body.get('image_name')}' with id '{body.get('id_new_mediafile')}'",
#     )


@app.rabbit.queue("dams.ocr_request")
def do_ocr(routing_key, body, message_id):
    app.logger.info("Message received:\tKey: {}".format(routing_key))

    ocr_output, mediafile_name, content_type = __get_ocr_output(
        body["operation"],
        body["mediafile_image_data"],
        body["lang"],
        body["image_name"],
    )
    __upload_ocr_output(
        ocr_output, body["id_new_mediafile"], mediafile_name, content_type
    )

    # __get_and_finish_job(body)
    app.logger.info(
        "The ocr job is complete. You can now fetch the image with the given id"
    )
