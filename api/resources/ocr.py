import json
import importlib
import app
import sys
from io import BytesIO
from flask import request, Response
from flask_restful import abort, Resource
from services.ocr_service import OcrService
from services.collection_api_service import CollectionApiService
from services.storage_api_service import StorageApiService

class BaseOcr(Resource):
    def __get_request_body(self):
        if request_body := request.get_json(silent=True):
            return request_body
        abort(405, message="Invalid input")

    def __is_malformed_message(self, data, fields):
        if not all(x in data for x in fields):
            abort(405, message=f"Malformed request body. Mandatory fieds: {[field for field in fields]}")


    def get(self):
        # get content and validate
        content = self.__get_request_body()
        self.__is_malformed_message(content, ["mediafile_id", "operation"])

        # initialize api's
        collection_api_service = CollectionApiService()
        storage_api_service = StorageApiService()
        ocr_service = OcrService()


        # get mediafile and see if it exists
        try:
            response = collection_api_service.get_mediafile(content["mediafile_id"])
        except Exception as ex: # it doesn't exist
            return Response(response=str(ex), status=400)
        mediafile_image_data = response.json()


        # it exists -> create new mediafile for ocr image
        try:
            response = collection_api_service.create_mediafile(mediafile_image_data, content["operation"])
        except Exception as ex:
            return Response(response=str(ex), status=401)
        new_mediafile = response.json()


        # new mediafile succesfully created -> run ocr job
        lang = content.get("lang")
        if not lang:
            lang = None

        try:
            file_in_bytes = ocr_service.ocr(content["operation"], [mediafile_image_data], lang)
        except Exception as ex:
            return Response(response=str(ex), status=400)


        # ocr job finished -> save ocr_image in storage api
        id_mediafile = new_mediafile["_id"].split("/")[1]
        mediafile_name = mediafile_image_data.get("original_filename")
        try:
            response = storage_api_service.upload_ocr(id_mediafile, file_in_bytes, mediafile_name)
        except Exception as ex:
            return Response(response=str(ex), status=402)


        # finally return the mediafile_id so user can fetch it themself
        return Response(response=f"Ocr job finished. The mediafile is: [{id_mediafile}]/n {response}")

