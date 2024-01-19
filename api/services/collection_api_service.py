import app
import requests
import os

from singleton import Singleton


class CollectionApiService(metaclass=Singleton):
    def __init__(self):
        self.collection_api_url = os.getenv("COLLECTION_API_URL")
        self.headers = {"Authorization": f'Bearer {os.getenv("STATIC_JWT")}'}

    def add_ocr_output_to_metadata(self, mediafile_id, metadata):
        app.logger.info(
            "Storing the OCR txt output in the metadata of the original image file"
        )
        req = requests.patch(
            f"{self.collection_api_url}/mediafiles/{mediafile_id}",
            json=metadata,
            headers=self.headers,
        )
        if req.status_code != 201:
            raise Exception(req.text.strip())
        return req

    def add_ocr_output_to_parent_entities(
        self, original_mediafile_id, ocr_mediafile_id, operation, lang
    ):
        original_mediafile = self.get_mediafile(original_mediafile_id).json()
        unique_entities = list()
        for relation in original_mediafile.get("relations", list()):
            entity_id = relation.get("key")
            if (
                relation.get("type") == "belongsTo"
                and entity_id not in unique_entities
                and "is_ocr" not in relation
            ):
                payload = [
                    {
                        "key": ocr_mediafile_id,
                        "label": "hasMediafile",
                        "type": "belongsTo",
                        "is_ocr": True,
                        "operation": operation,
                        "lang": lang,
                    }
                ]
                url = f"{self.collection_api_url}/entities/{entity_id}/relations"
                req = requests.patch(url, json=payload, headers=self.headers)
                if req.status_code != 201:
                    raise Exception(req.text.strip())
                url = f"{self.collection_api_url}/mediafiles/{original_mediafile_id}/relations"
                req = requests.patch(url, json=payload, headers=self.headers)
                if req.status_code != 201:
                    raise Exception(req.text.strip())

    def create_mediafile(self, mediafile, operation):
        filename = mediafile[0]["original_filename"].split(".")[0] + f"-ocr.{operation}"
        data = {"filename": filename}
        req = requests.post(
            f"{self.collection_api_url}/mediafiles",
            json=data,
            headers=self.headers,
        )
        if req.status_code != 201:
            raise Exception(req.text.strip())
        return req

    def create_ticket(self, mediafile_name):
        req = requests.post(
            f"{self.collection_api_url}/tickets",
            json={"filename": mediafile_name},
            headers=self.headers,
        )
        if req.status_code != 201:
            raise Exception(req.text.strip())
        return req.text.strip().replace('"', "")

    def delete_mediafile(self, mediafile_id):
        req = requests.delete(
            f"{self.collection_api_url}/mediafiles/{mediafile_id}", headers=self.headers
        )
        if req.status_code != 204:
            raise Exception(req.text.strip())
        return req

    def get_mediafile(self, mediafile_id):
        req = requests.get(
            f"{self.collection_api_url}/mediafiles/{mediafile_id}",
            headers=self.headers,
        )
        if req.status_code != 200:
            raise Exception(req.text.strip())
        return req
