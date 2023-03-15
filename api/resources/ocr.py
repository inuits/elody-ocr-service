import app
import os
from flask import request, Response
from flask_restful import abort, Resource
from services.ocr_service import OcrService
from services.collection_api_service import CollectionApiService
from services.storage_api_service import StorageApiService

ALLOWED_LANGUAGES = ["eng", "nld", "fra"]

class BaseOcr(Resource):

    def __init__(self):
        self.headers = {"Authorization": f'Bearer {os.getenv("STATIC_JWT")}'}


    def __get_request_body(self):
        if request_body := request.get_json(silent=True):
            return request_body
        abort(405, message="Invalid input")

    def __is_malformed_message(self, data, fields):
        if not all(x in data for x in fields):
            abort(405, message=f"Malformed request body. Mandatory fieds: {[field for field in fields]}")

    def __validate_number_of_ids(self, data, operation):
        if len(data) < 1:
            abort(400, message="Malformed request body. You forgot to give a mediafile id")
        if len(data) > 1 and operation != "pdf":
            abort(400, message=f"You can only send 1 image for txt of alto. Images received: {str(len(data))}")
        for id in data:
            if id  == "":
                abort(400, message="Malformed request body. You cannot give an empty mediafile id")
        return len(data)

    def __validate_language(self, lang):
        warning = None

        if not lang or lang not in ALLOWED_LANGUAGES:
            lang = ALLOWED_LANGUAGES[0] # set default to eng
            warning = '299, "Arbitrary information that should be presented to a user or logged.", "For now the ocr tool used ENG as default language. You can specify the language with the key [lang] and possible values: eng, ned, fra'

        return lang, warning


    def post(self):
        # get content and validate
        content = self.__get_request_body()
        self.__is_malformed_message(content, ["mediafile_id", "operation"])

        # validate language
        lang, warning = self.__validate_language(request.args.get("lang"))

        # validate count
        operation = content["operation"]
        mediafile_id = content["mediafile_id"]
        count = self.__validate_number_of_ids(mediafile_id, operation)

        # initialize api's
        collection_api_service = CollectionApiService()
        storage_api_service = StorageApiService()
        ocr_service = OcrService()


        # get mediafile and see if it exists
        try:
            mediafile_image_data = []
            for i in range(count):
                response = collection_api_service.get_mediafile(mediafile_id[i])
                mediafile_image_data.append(response.json())
        except Exception as ex: # it doesn't exist
            return Response(response=str(ex), status=400)


        # it exists -> create new mediafile for ocr image
        try:
            response = collection_api_service.create_mediafile(mediafile_image_data, operation)
        except Exception as ex:
            return Response(response=str(ex), status=401)
        new_mediafile = response.json()



        # THIS CODE SHOULD RUN IN / MOVE TO THE QUEUE
        # new mediafile succesfully created -> run ocr job
        try:
            ocr_output, mediafile_name, content_type = ocr_service.ocr(operation, mediafile_image_data, lang)
        except Exception as ex:
            return Response(response=str(ex), status=400)


        # ocr job finished -> save ocr_image in storage api
        id_new_mediafile = new_mediafile["_id"].split("/")[1]
        try:
            storage_api_service.upload_ocr(ocr_output, id_new_mediafile, mediafile_name, content_type)
        except Exception as ex:
            return Response(response=str(ex), status=400)


        # finally return the mediafile_id so user can fetch it themself
        if warning:
            self.headers["Warning"] = warning
        return Response(response=f"Ocr job finished. The mediafile_ID is: [{id_new_mediafile}]", status=200, headers=self.headers)

