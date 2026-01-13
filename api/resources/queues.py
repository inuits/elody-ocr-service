import mimetypes
import os

import app
import requests
from elody import Client
from elody.exceptions import InvalidExtensionException
from elody.job import finish_job, start_job
from rabbit import get_rabbit
from services.ocr_service import OcrService
from services.storage_api_service import StorageApiService
from os import getenv

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


def __argument_wrapper(*, queue_name, routing_key):
    arguments = {"routing_key": routing_key}
    queue_type = getenv("QUEUE_TYPE", "classic")
    if getenv("AMQP_MANAGER", "amqpstorm_flask") == "amqpstorm_flask":
        arguments["queue_name"] = queue_name
        if queue_type:
            arguments["queue_arguments"] = {"x-queue-type": queue_type}
    return arguments


def __get_ocr_output(
    operation,
    mediafile_image_data,
    lang,
    image_name,
    id_new_mediafile,
    main_job_id=None,
    user_email=None,
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
            user_email,
        )
    except Exception as ex:
        app.logger.error(f'"In queues - The ocr function failed with:" {ex}')


def __upload_ocr_output(
    ocr_output,
    id_new_mediafile,
    mediafile_name,
    content_type,
    user_email,
    parent_job_id=None,
):
    storage_api_service = StorageApiService()
    try:
        storage_api_service.upload_ocr(
            ocr_output,
            id_new_mediafile,
            mediafile_name,
            content_type,
            user_email=user_email,
            parent_job_id=parent_job_id,
        )
    except Exception as ex:
        app.logger.error(
            f'"The ocr function failed during uploading the image in the storage api:" {ex}'
        )


def __resolve_user_from_parent_job(main_job_id):
    try:
        headers = {"Authorization": f'Bearer {os.getenv("STATIC_JWT")}'}
        r = requests.get(
            f"{collection_api_url}/jobs/{main_job_id}", headers=headers, timeout=5
        )
        if r.status_code == 200:
            job = r.json()
            return job.get("created_by") or job.get("last_editor") or None
    except Exception:
        pass
    return None


@get_rabbit().queue(
    **__argument_wrapper(queue_name="dams.ocr_request", routing_key="dams.ocr_request")
)
def do_ocr(routing_key, body, message_id):
    app.logger.info("Message received:\tKey: {}".format(routing_key))
    user_email = body["user_email"]
    main_job_id = body.get("main_job_id")

    auth_header = body.get("auth_header")

    if (not user_email) and main_job_id:
        user_from_parent = __resolve_user_from_parent_job(main_job_id)
        if user_from_parent:
            user_email = user_from_parent

    start_job(main_job_id, get_rabbit=get_rabbit)
    if body["operation"] in ["txt", "alto"]:
        for image in body["mediafile_image_data"]:
            image_name = __get_imagename_and_validate(image, body["operation"])
            id_new_mediafile = __create_mediafile(
                image, body["operation"], body["lang"], user_email, auth_header
            )
            ocr_output, mediafile_name, content_type = __get_ocr_output(
                body["operation"],
                [image],
                body["lang"],
                image_name,
                id_new_mediafile,
                main_job_id,
                user_email,
            )
            __upload_ocr_output(
                ocr_output,
                id_new_mediafile,
                mediafile_name,
                content_type,
                user_email=user_email,
                parent_job_id=main_job_id,
            )
            app.logger.info(
                f"The ocr job is complete. You can now fetch the image with the given id: {id_new_mediafile}"
            )
    if body["operation"] == "pdf":
        image_name = "asset-pdf"
        id_new_mediafile = __create_mediafile(
            body["mediafile_image_data"][0],
            body["operation"],
            body["lang"],
            user_email,
            auth_header,
        )
        ocr_output, mediafile_name, content_type = __get_ocr_output(
            body["operation"],
            body["mediafile_image_data"],
            body["lang"],
            image_name,
            id_new_mediafile,
            main_job_id,
            user_email,
        )
        __upload_ocr_output(
            ocr_output,
            id_new_mediafile,
            mediafile_name,
            content_type,
            user_email=user_email,
        )
        app.logger.info(
            f"The ocr job is complete. You can now fetch the image with the given id: {id_new_mediafile}"
        )
    finish_job(main_job_id, get_rabbit=get_rabbit)


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


def __create_mediafile(
    mediafile_image, operation, lang, user_email=None, auth_header=None
):
    try:
        filename = mediafile_image["original_filename"].split(".")[0] + f".{operation}"

        auth_token = auth_header or os.getenv("STATIC_JWT")
        headers = {"Authorization": f"Bearer {auth_token}"}
        if user_email:
            headers["X-User-Email"] = user_email

        if operation == "pdf":
            asset_id = [
                relation["key"]
                for relation in mediafile_image["relations"]
                if relation["type"] == "isMediafileFor"
            ][0]
            response = requests.post(
                f"{collection_api_url}/entities/{asset_id}/mediafiles",
                json={
                    "filename": filename,
                    "relation_properties": {"lang": lang, "operation": operation},
                    "technical_origin": "ocr",
                    "type": "mediafile",
                },
                headers=headers,
            )
        else:
            response = requests.post(
                f"{collection_api_url}/mediafiles/{mediafile_image['_id']}/derivatives",
                json={
                    "filename": filename,
                    "relation_properties": {"lang": lang, "operation": operation},
                    "technical_origin": "ocr",
                    "type": "mediafile",
                },
                headers=headers,
            )
        if not response.ok:
            raise Exception(response.json())
        new_mediafile = response.json()
        if isinstance(new_mediafile, dict):
            return new_mediafile.get("_key") or new_mediafile.get("_id")
        return new_mediafile
    except Exception as ex:
        raise Exception(str(ex))