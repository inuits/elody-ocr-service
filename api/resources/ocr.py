import app
import os
import mimetypes
from flask import request, Response
from flask_restful import abort, Resource
from services.collection_api_service import CollectionApiService


ALLOWED_LANGUAGES = ["eng", "nld", "fra"]
ALLOWED_MIMETYPES = [
    "image/png",
    "image/jpg",
    "image/jpeg",
    "image/tiff",
    "image/gif",
    "image/webp",
]


class Ocr(Resource):
    def __init__(self):
        self.headers = {"Authorization": f'Bearer {os.getenv("STATIC_JWT")}'}
        self.collection_api_service = CollectionApiService()
        # self.main_job = None

    def __get_request_body(self):
        if request_body := request.get_json(silent=True):
            return request_body
        # app.jobs_extension.fail_job(self.main_job, "Invalid input")
        abort(405, message="Invalid input")

    def __is_malformed_message(self, data, fields):
        if not all(x in data for x in fields):
            # app.jobs_extension.fail_job(self.main_job, "Malformed request body")
            abort(
                405,
                message=f"Malformed request body. Mandatory fieds: {[field for field in fields]}",
            )

    def __is_wrong_operation(self, operation):
        if operation not in ["txt", "alto", "pdf"]:
            # app.jobs_extension.fail_job(self.main_job, "Invalid operation")
            abort(
                405,
                message="Invalid operation. Possible operations are ['txt', 'alto', 'pdf']",
            )

    def __validate_mediafiles(self, mediafile_ids, operation):
        if not isinstance(mediafile_ids, list):
            # app.jobs_extension.fail_job(self.main_job, "Malformed request body. Send the image id(s) in an array")
            abort(
                400, message="Malformed request body. Send the image id(s) in an array"
            )
        if len(mediafile_ids) < 1:
            # app.jobs_extension.fail_job(self.main_job, "Malformed request body. You forgot to give a mediafile id")
            abort(
                400, message="Malformed request body. You forgot to give a mediafile id"
            )
        if len(mediafile_ids) > 1 and operation != "pdf":
            # app.jobs_extension.fail_job(self.main_job, "ou can only send 1 image id for this operation")
            abort(
                400,
                message=f"You can only send 1 image id for the [{operation}] operation. Images received: {str(len(mediafile_ids))}",
            )
        for id in mediafile_ids:
            if id == "":
                # app.jobs_extension.fail_job(self.main_job, "Malformed request body. You cannot give an empty mediafile id")
                abort(
                    400,
                    message="Malformed request body. You cannot give an empty mediafile id",
                )
        return len(mediafile_ids)

    def __validate_language(self, lang):
        warning = None

        if not lang or lang not in ALLOWED_LANGUAGES:
            lang = ALLOWED_LANGUAGES[0]  # set default to eng
            warning = '299, "Arbitrary information that should be presented to a user or logged.", "For now the ocr tool used ENG as default language. You can specify the language with the key [lang] and possible values: eng, ned, fra'

        return lang, warning

    def __is_mimetype_from_filename_valid(self, filename):
        mime = mimetypes.guess_type(filename, False)[0]
        return mime in ALLOWED_MIMETYPES

    def __get_imagename_and_validate(self, mediafile_image_data):
        image_name = mediafile_image_data[0].get("filename")
        if not self.__is_mimetype_from_filename_valid(image_name):
            # app.jobs_extension.fail_job(self.main_job, "Extension is not valid")
            abort(400, message="Extension is not valid")
        return image_name

    def __get_mediafiles_and_check_existence(self, count, mediafile_id):
        try:
            mediafile_image_data = []
            for i in range(count):
                response = self.collection_api_service.get_mediafile(mediafile_id[i])
                mediafile_image_data.append(response.json())
        except Exception as ex:  # it doesn't exist
            # app.jobs_extension.fail_job(self.main_job, str(ex))
            abort(400, message=str(ex))
        return mediafile_image_data

    def __create_mediafile(self, mediafile_image_data, operation):
        try:
            response = self.collection_api_service.create_mediafile(
                mediafile_image_data, operation
            )
        except Exception as ex:
            # app.jobs_extension.fail_job(self.main_job, str(ex))
            abort(400, message=str(ex))
        new_mediafile = response.json()

        id = new_mediafile["_id"]
        if "/" in id:
            id = id.split("/")[1]
        return id

    def __send_message_to_queue_and_terminate_call(
        self, body, id_new_mediafile, warning
    ):
        try:
            app.logger.info("Going to send message to queue")
            # app.jobs_extension.progress_job(self.main_job, mediafile_id=body.get("id_new_mediafile"))
            app.rabbit.send(body, routing_key="dams.ocr_request")
        except Exception as ex:
            # app.jobs_extension.fail_job(self.main_job, str(ex))
            abort(400, f"Exception at queue: {str(ex)}")

        if warning:
            self.headers["Warning"] = warning
        return Response(
            response=f"Ocr job is put on queue. Fetch it later with the mediafile id: [{id_new_mediafile}]",
            status=200,
            headers=self.headers,
            mimetype="text/plain"
        )

    def post(self):
        # self.main_job = app.jobs_extension.create_new_job(
        #     f"Start ocr process of an image",
        #     "dams.ocr_request",
        # )

        content = self.__get_request_body()
        self.__is_malformed_message(content, ["mediafile_id", "operation"])

        operation = content["operation"]
        mediafile_id = content["mediafile_id"]

        self.__is_wrong_operation(operation)
        lang, warning = self.__validate_language(request.args.get("lang"))
        count = self.__validate_mediafiles(mediafile_id, operation)

        mediafile_image_data = self.__get_mediafiles_and_check_existence(
            count, mediafile_id
        )
        image_name = self.__get_imagename_and_validate(mediafile_image_data)
        id_new_mediafile = self.__create_mediafile(mediafile_image_data, operation)

        body = {
            "operation": content["operation"],
            "mediafile_image_data": mediafile_image_data,
            "lang": lang,
            "id_new_mediafile": id_new_mediafile,
            "image_name": image_name,
            # "main_job_identifier": self.main_job.identifiers[0],
        }
        return self.__send_message_to_queue_and_terminate_call(
            body, id_new_mediafile, warning
        )
