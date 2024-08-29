import app
import mimetypes
import os

from elody import Client
from elody.exceptions import InvalidExtensionException
from services.collection_api_service import CollectionApiService
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
    operation, mediafile_image_data, lang, image_name, id_new_mediafile
):
    ocr_service = OcrService()
    try:
        return ocr_service.ocr(
            operation, mediafile_image_data, lang, image_name, id_new_mediafile
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
    collection_api_service = CollectionApiService()
    original_mediafile = body["mediafile_image_data"][0]
    institution_id = ""
    for original_mediafile_relation in original_mediafile.get("relations", []):
        if original_mediafile_relation.get("type") == "belongsTo":
            if not institution_id:
                institution_id = collection_api_service.get_institution_from_asset(
                    original_mediafile_relation.get("key")
                )
    image_name = __get_imagename_and_validate(
        body["mediafile_image_data"], body["operation"]
    )
    id_new_mediafile = __create_mediafile(
        body["mediafile_image_data"], body["operation"], institution_id
    )
    collection_api_service.add_ocr_output_to_parent_entities(
        body["mediafile_image_data"][0]["_id"],
        id_new_mediafile,
        body["operation"],
        body["lang"],
    )
    ocr_output, mediafile_name, content_type = __get_ocr_output(
        body["operation"],
        body["mediafile_image_data"],
        body["lang"],
        image_name,
        id_new_mediafile,
    )
    __upload_ocr_output(ocr_output, id_new_mediafile, mediafile_name, content_type)
    app.logger.info(
        f"The ocr job is complete. You can now fetch the image with the given id: {id_new_mediafile}"
    )


def __get_imagename_and_validate(mediafile_image_data, operation):
    image_name = mediafile_image_data[0].get("filename")
    if not __is_mimetype_from_filename_valid(image_name, operation):
        raise InvalidExtensionException("Extension is not valid")
    return image_name


def __is_mimetype_from_filename_valid(filename, operation):
    mime = mimetypes.guess_type(filename, False)[0]
    if mime == "application/pdf" and operation != "pdf":
        return False
    return mime in ALLOWED_MIMETYPES


def __create_mediafile(mediafile_image_data, operation, institution_id):
    try:
        filename = (
            mediafile_image_data[0]["original_filename"].split(".")[0]
            + f"-ocr.{operation}"
        )
        response = elody_client.create_mediafile_with_filename(filename, institution_id)
    except Exception as ex:
        raise Exception(str(ex))
    new_mediafile = response.json()
    return new_mediafile.get("_key", new_mediafile["_id"])
