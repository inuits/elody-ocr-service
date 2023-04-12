import app
import mimetypes
import os
import difflib
import sys

from datetime import datetime
from flask import request, Response
from flask_restful import abort, Resource
from services.collection_api_service import CollectionApiService

ALLOWED_LANGUAGES = ["eng", "nld", "fra"]


class OcrCorrection(Resource):
    def __init__(self):
        self.headers = {"Authorization": f'Bearer {os.getenv("STATIC_JWT")}'}
        self.collection_api_service = CollectionApiService()


    def __is_malformed_message(self, data, fields):
        if not all(x in data for x in fields):
            abort(
                405,
                message=f"Malformed request body. Mandatory fieds: {[field for field in fields]}",
            )
    def __validate_mediafiles(self, mediafile_id):
        if not mediafile_id or mediafile_id == "":
            abort(
                400,
                message="Malformed request body. You cannot give an empty mediafile id",
            )
    def __get_mediafile_and_check_existence(self, mediafile_id):
        try:
            response = self.collection_api_service.get_mediafile(mediafile_id)
        except Exception as ex:  # it doesn't exist
            abort(400, message=str(ex))
        return response.json()


    def post(self):
        txt_file = request.files.getlist('new_text')
        mediafile_id = request.values["mediafile_id"]
        content = {'new_text': txt_file, 'mediafile_id': mediafile_id}

        self.__is_malformed_message(content, ["mediafile_id", "new_text"])
        self.__validate_mediafiles(mediafile_id)
        mediafile_image_data = self.__get_mediafile_and_check_existence(mediafile_id)

        path1 = "/app/api/resources/example.txt"
        path2 = "/app/api/resources/modified_example.txt"

        with open(path1, 'r') as file1, open(path2, 'r') as file2:
            text1 = file1.readlines()
            text2 = file2.readlines()

        diff = difflib.unified_diff(a=text1, b=text2, lineterm="\n")
        return Response(response=diff, status=200)


