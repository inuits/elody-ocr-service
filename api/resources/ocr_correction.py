import app
import difflib
import os

from datetime import datetime
from elody import Client
from flask import request, Response
from flask_restful import abort, Resource
from inuits_policy_based_auth import RequestContext
from policy_factory import authenticate
from services.collection_api_service import CollectionApiService
from services.storage_api_service import StorageApiService


collection_api_url = os.getenv("COLLECTION_API_URL")
elody_client = Client(collection_api_url, os.getenv("STATIC_JWT"))


class OcrCorrection(Resource):
    def __init__(self):
        self.headers = {"Authorization": f'Bearer {os.getenv("STATIC_JWT")}'}
        self.collection_api_service = CollectionApiService()
        self.storage_api_service = StorageApiService()

    def __add_txt_to_metadata(self, metadata, diff, mediafile_image_data):
        new_metadata = {
            "key": "updated_text_from_ocr",
            "value": [
                {"key": "date", "value": str(datetime.now())},
                {"key": "updated_text", "value": diff},
            ],
        }
        metadata.append(new_metadata)
        try:
            self.collection_api_service.add_ocr_output_to_metadata(
                mediafile_image_data.get("_key"),
                {"metadata": mediafile_image_data.get("metadata")},
            )
        except Exception as ex:
            app.logger.error(
                f'"The ocr function failed during update of metadata:" {ex}'
            )

    def __get_diff(self, original_text, updated_text):
        original_text = original_text.splitlines(1)
        updated_text = updated_text.splitlines(1)
        diff = difflib.unified_diff(a=original_text, b=updated_text, n=0, lineterm="\n")
        return "".join(diff)

    def __get_mediafile_and_check_existence(self, mediafile_id):
        try:
            response = elody_client.get_object("mediafiles", mediafile_id)
        except Exception as ex:  # it doesn't exist
            abort(400, message=str(ex))
        return response.json()

    def __get_original_text_and_check_existence(self, metadata):
        original_text = next(
            (item for item in metadata if item["key"] == "text_from_ocr"), None
        )
        if not original_text:
            abort(
                400,
                message="The original mediafile has no OCR data in the metadata. First run a txt OCR job to generate the metadata.",
            )
        return original_text.get("value")

    def __validate_mediafiles(self, mediafile_id):
        if not mediafile_id or mediafile_id == "":
            abort(
                400,
                message="Malformed request body. You cannot give an empty mediafile id",
            )

    @authenticate(RequestContext(request))
    def post(self):
        try:
            updated_text = request.values["updated_text"]
            mediafile_id = request.values["mediafile_id"]
        except Exception as ex:
            app.logger.error(f"Wrong body: {ex}")
            abort(
                400,
                message="Give the correct body. [updated_text] and [mediafile_id] are required",
            )
        self.__validate_mediafiles(mediafile_id)
        mediafile_image_data = self.__get_mediafile_and_check_existence(mediafile_id)
        metadata = mediafile_image_data.get("metadata")
        original_text = self.__get_original_text_and_check_existence(metadata)
        diff = self.__get_diff(original_text, updated_text)
        self.__add_txt_to_metadata(metadata, diff, mediafile_image_data)
        return Response(
            response="A diff file is created based on the original txt output and saved in the metadata of the mediafile",
            status=201,
        )
