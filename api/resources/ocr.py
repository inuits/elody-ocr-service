import app
import os

from elody import Client
from flask import request, Response
from flask_restful import abort, Resource
from inuits_policy_based_auth import RequestContext

ALLOWED_LANGUAGES = ["eng", "nld", "fra"]

collection_api_url = os.getenv("COLLECTION_API_URL")
elody_client = Client(collection_api_url, os.getenv("STATIC_JWT"))


class Ocr(Resource):
    def __init__(self):
        self.headers = {"Authorization": f'Bearer {os.getenv("STATIC_JWT")}'}

    def __get_request_body(self):
        if request_body := request.get_json(silent=True):
            return request_body
        abort(405, message="Invalid input")

    def __is_malformed_message(self, data, fields):
        if not all(x in data for x in fields):
            abort(
                405,
                message=f"Malformed request body. Mandatory fieds: {[field for field in fields]}",
            )

    def __is_wrong_operation(self, operation):
        if operation not in ["txt", "alto", "pdf"]:
            abort(
                405,
                message="Invalid operation. Possible operations are ['txt', 'alto', 'pdf']",
            )

    def __send_message_to_queue_and_terminate_call(self, body, warning):
        try:
            app.logger.info("Going to send message to queue")
            app.rabbit.send(body, routing_key="dams.ocr_request")
        except Exception as ex:
            abort(400, f"Exception at queue: {str(ex)}")
        if warning:
            self.headers["Warning"] = warning
        return Response(
            response=f"Ocr job is put on queue.",
            status=200,
            headers=self.headers,
            mimetype="text/plain",
        )

    def __validate_language(self, lang):
        warning = None
        if not lang or lang not in ALLOWED_LANGUAGES:
            lang = ALLOWED_LANGUAGES[0]  # set default to eng
            warning = '299, "Arbitrary information that should be presented to a user or logged.", "For now the ocr tool used ENG as default language. You can specify the language with the key [lang] and possible values: eng, ned, fra'
        return lang, warning

    def __validate_mediafiles(self, mediafile_ids, operation):
        if not isinstance(mediafile_ids, list):
            abort(
                400, message="Malformed request body. Send the image id(s) in an array"
            )
        if len(mediafile_ids) < 1:
            abort(
                400, message="Malformed request body. You forgot to give a mediafile id"
            )
        if len(mediafile_ids) > 1 and operation != "pdf":
            abort(
                400,
                message=f"You can only send 1 image id for the [{operation}] operation. Images received: {str(len(mediafile_ids))}",
            )
        for id in mediafile_ids:
            if id == "":
                abort(
                    400,
                    message="Malformed request body. You cannot give an empty mediafile id",
                )
        return len(mediafile_ids)

    # @app.policy_factory.authenticate(RequestContext(request))
    def post(self):
        content = self.__get_request_body()
        self.__is_malformed_message(content, ["mediafile_id", "operation"])
        operation = content["operation"]
        mediafile_ids = content["mediafile_id"]
        self.__is_wrong_operation(operation)
        lang, warning = self.__validate_language(request.args.get("lang"))
        self.__validate_mediafiles(mediafile_ids, operation)
        mediafile_image_data = elody_client.get_mediafiles_and_check_existence(
            mediafile_ids
        )

        body = {
            "operation": content["operation"],
            "lang": lang,
            "mediafile_image_data": mediafile_image_data,
        }
        return self.__send_message_to_queue_and_terminate_call(body, warning)
