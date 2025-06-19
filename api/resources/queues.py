import app
import mimetypes
import os
import requests

from elody import Client
from elody.exceptions import InvalidExtensionException
from elody.job import start_job, finish_job
from services.ocr_service import OcrService
from services.storage_api_service import StorageApiService

ALLOWED_MIMETYPES = [
    "image/png",
    "image/jpg",
    "image/jpeg",
    "image/tiff",
    "image/gif",
    "image/webp",
    "application/pdf",
]

collection_api_url = os.getenv("COLLECTION_API_URL")
elody_client = Client(collection_api_url, os.getenv("STATIC_JWT"))


def __get_ocr_output(
    operation,
    mediafile_image_data,
    lang,
    image_name,
    id_new_mediafile,
    main_job_id=None,
):
    ocr_service = OcrService()
    try:
        return ocr_service.ocr(
            operation,
            mediafile_image_data,
            lang,
            image_name,
            id_new_mediafile,
            main_job_id,
        )
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


@app.rabbit.queue("dams.ocr_request")
def do_ocr(routing_key, body, message_id):
    app.logger.info("Message received:\tKey: {}".format(routing_key))
    main_job_id = body.get("main_job_id")
    start_job(main_job_id, get_rabbit=lambda: app.rabbit)
    if body["operation"] in ["txt", "alto"]:
        for image in body["mediafile_image_data"]:
            image_name = __get_imagename_and_validate(image, body["operation"])
            id_new_mediafile = __create_mediafile(
                image, body["operation"], body["lang"]
            )
            ocr_output, mediafile_name, content_type = __get_ocr_output(
                body["operation"],
                [image],
                body["lang"],
                image_name,
                id_new_mediafile,
                main_job_id,
            )
            __upload_ocr_output(
                ocr_output, id_new_mediafile, mediafile_name, content_type
            )
            app.logger.info(
                f"The ocr job is complete. You can now fetch the image with the given id: {id_new_mediafile}"
            )
    if body["operation"] == "pdf":
        image_name = "asset-pdf"
        id_new_mediafile = __create_mediafile(
            body["mediafile_image_data"][0], body["operation"], body["lang"]
        )
        ocr_output, mediafile_name, content_type = __get_ocr_output(
            body["operation"],
            body["mediafile_image_data"],
            body["lang"],
            image_name,
            id_new_mediafile,
            main_job_id,
        )
        __upload_ocr_output(ocr_output, id_new_mediafile, mediafile_name, content_type)
        app.logger.info(
            f"The ocr job is complete. You can now fetch the image with the given id: {id_new_mediafile}"
        )
    finish_job(main_job_id, get_rabbit=lambda: app.rabbit)


def __get_imagename_and_validate(mediafile_image, operation):
    image_name = mediafile_image.get("filename")
    if not __is_mimetype_from_filename_valid(image_name, operation):
        raise InvalidExtensionException("Extension is not valid")
    return image_name


def __is_mimetype_from_filename_valid(filename, operation):
    mime = mimetypes.guess_type(filename, False)[0]
    if mime == "application/pdf" and operation != "pdf":
        return False
    return mime in ALLOWED_MIMETYPES


def __create_mediafile(mediafile_image, operation, lang):
    try:
        filename = (
            mediafile_image["original_filename"].split(".")[0] + f"-ocr.{operation}"
        )
        response = requests.post(
            f"{collection_api_url}/mediafiles",
            json={
                "filename": filename,
                "relations": [
                    {
                        "key": mediafile_image["_id"],
                        "lang": lang,
                        "operation": operation,
                        "type": "isOcrFor",
                    }
                ],
                "technical_origin": "ocr",
                "type": "mediafile",
            },
            headers={"Authorization": f'Bearer {os.getenv("STATIC_JWT")}'},
        )
        new_mediafile = response.json()
        return new_mediafile.get("_key", new_mediafile["_id"])
    except Exception as ex:
        raise Exception(str(ex))
