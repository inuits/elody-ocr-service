import app
import os
from flask import request, Response
from flask_restful import abort, Resource
from services.ocr_service import OcrService
from services.collection_api_service import CollectionApiService
from services.storage_api_service import StorageApiService

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


    def post(self):
        # get content and validate
        lang = request.args.get("lang")
        if not lang:
            lang = None
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



        # HERE YOU HAVE TO SEND A MESSAGE TO THE QUEUE
        # body = {
        #     "operation": content["operation"],
        #     "mediafile_image_data": [mediafile_image_data],
        #     "lang": lang
        # }
        # app.rabbit.send(body, routing_key="dams.ocr_request")




        # THIS CODE SHOULD RUN IN / MOVE TO THE QUEUE
        # new mediafile succesfully created -> run ocr job
        try:
            ocr_output, mediafile_name, content_type, warning = ocr_service.ocr(content["operation"], [mediafile_image_data], lang)
        except Exception as ex:
            return Response(response=str(ex), status=400)

        # ocr job finished -> save ocr_image in storage api
        id_mediafile = new_mediafile["_id"].split("/")[1]
        try:
            storage_api_service.upload_ocr(ocr_output, id_mediafile, mediafile_name, content_type)
        except Exception as ex:
            return Response(response=str(ex), status=400)

        # finally return the mediafile_id so user can fetch it themself
        if warning:
            self.headers["Warning"] = warning
        return Response(response=f"Ocr job finished. The mediafile_ID is: [{id_mediafile}]", status=200, headers=self.headers)

