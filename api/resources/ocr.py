import importlib

import app
import sys
from flask import request, Response
from flask_restful import abort, Resource
from services.ocr_service import OcrService


class BaseOcr(Resource):
    def __get_request_body(self):
        raise NotImplementedError("not implemented")


    def __is_malformed_message(self, data, fields, mimetypes):
        raise NotImplementedError("not implemented")

    def get(self):
        return Response(response="It works!", status=400)

    def post(self):
        # verwijzen  naar queueu
        data = self.__get_request_body()

        try:
            ocr_engine = OcrService(data["mediafile"], data["url"])
            ocr_engine.ocr(data["operation"], data["image_ids"], data["language"])
        except Exception as ex:
            return str(ex), 400



