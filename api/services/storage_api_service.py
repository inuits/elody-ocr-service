import os
import requests

from singleton import Singleton


class StorageApiService(metaclass=Singleton):
    def __init__(self):
        self.storage_api_url = os.getenv("STORAGE_API_URL")
        self.headers = {"Authorization": f'Bearer {os.getenv("STATIC_JWT")}'}

    def download_image(self, image_name):
        req = requests.get(
            f"{self.storage_api_url}//download/{image_name}", headers=self.headers
        )
        if req.status_code != 200:
            raise Exception(req.text.strip())
        return req.content

    def upload_ocr(self, ocr_output, id_mediafile, mediafile_name, content_type):
        self.headers["Content-Type"] = content_type
        req = requests.post(
            f"{self.storage_api_url}/upload/{mediafile_name}?id={id_mediafile}",
            data=ocr_output,
            headers=self.headers,
        )
        if req.status_code != 201:
            raise Exception(req.text.strip())
        return req
