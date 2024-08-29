import app
import requests
import os

from elody import Client
from singleton import Singleton

collection_api_url = os.getenv("COLLECTION_API_URL")
elody_client = Client(collection_api_url, os.getenv("STATIC_JWT"))


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
        original_mediafile = elody_client.get_object(
            "mediafiles", original_mediafile_id
        )
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

    def get_mediafiles_from_entity(self, entity_id):
        url = f"{self.collection_api_url}/entities/{entity_id}/mediafiles"
        req = requests.get(url, headers=self.headers)
        if req.status_code != 200:
            raise Exception(req.text.strip())
        content = req.json()
        return content["results"]

    def get_institution_from_asset(self, asset_id):
        req = requests.get(
            f"{self.collection_api_url}/entities/{asset_id}",
            headers=self.headers,
        )

        asset = req.json()
        institution_id = ""
        for relation in asset.get("relations", []):
            if relation.get("type") == "hasInstitution":
                institution_id = relation.get("key")
                
        return institution_id
