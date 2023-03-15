import os
import requests

class CollectionApiService(object):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(CollectionApiService, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        self.collection_api_url = os.getenv("COLLECTION_API_URL")
        self.headers = {"Authorization": f'Bearer {os.getenv("STATIC_JWT")}'}

    def get_mediafile(self, mediafile_id):
        req = requests.get(
            f"{self.collection_api_url}/mediafiles/{mediafile_id}",
            headers=self.headers,
        )
        if req.status_code != 200:
            raise Exception(req.text.strip())
        return req

    def create_mediafile(self, mediafile, operation):
        filename = mediafile[0]["original_filename"].split(".")[0] + f"-ocr.{operation}"
        data = {
            "filename": filename
        }

        req = requests.post(
            f"{self.collection_api_url}/mediafiles",
            json=data,
            headers=self.headers,
        )

        if req.status_code != 201:
            raise Exception(req.text.strip())
        return req

