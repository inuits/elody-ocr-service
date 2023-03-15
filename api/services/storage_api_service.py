import os
import requests

class StorageApiService(object):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(StorageApiService, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        self.storage_api_url = os.getenv("STORAGE_API_URL")
        self.headers = {"Authorization": f'Bearer {os.getenv("STATIC_JWT")}'}


    def download_image(self, image_name):
        req = requests.get(
            f"{self.storage_api_url}//download/{image_name}",
            headers=self.headers
        )
        if req.status_code != 200:
            raise Exception(req.text.strip())
        return req

    def upload_ocr(self, id_mediafile, file_in_bytes, mediafile_name):
        metadata = [{"key": "publication_status", "value": "publiek"}]
        self.headers["Content-Type"] = "application/pdf"
        payload = {"metadata": metadata, "filename": mediafile_name}

        req = requests.post(
            f"{self.storage_api_url}/upload?id={id_mediafile}",
            data={
                "body": file_in_bytes
            },
            json=payload,
            headers=self.headers
        )

        if req.status_code != 200:
            raise Exception(req.text.strip())
        return req
