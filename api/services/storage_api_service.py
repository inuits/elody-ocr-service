import os
import requests

from elody import Client
from singleton import Singleton

collection_api_url = os.getenv("COLLECTION_API_URL")
elody_client = Client(collection_api_url, os.getenv("STATIC_JWT"))


class StorageApiService(metaclass=Singleton):
    def __init__(self):
        self.storage_api_url = os.getenv("STORAGE_API_URL")
        self.headers = {"Authorization": f'Bearer {os.getenv("STATIC_JWT")}'}

    def download_image(self, image_name):
        req = requests.get(
            f"{self.storage_api_url}/download/{image_name}", headers=self.headers
        )
        if req.status_code != 200:
            raise Exception(req.text.strip())
        return req.content

    def upload_ocr(
        self, ocr_output, id_mediafile, mediafile_name, content_type, user_email
    ):
        self.headers["Content-Type"] = content_type
        ticket_id = elody_client.create_ticket(mediafile_name)
        req = requests.post(
            f"{self.storage_api_url}/upload-with-ticket/{mediafile_name}?id={id_mediafile}&ticket_id={ticket_id}&user_email={user_email}",
            data=ocr_output,
        )
        if req.status_code != 201:
            raise Exception(req.text.strip())
        return req
