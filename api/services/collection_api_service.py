import app
import requests
import os
import random

from elody import Client
from singleton import Singleton
from time import sleep

collection_api_url = os.getenv("COLLECTION_API_URL")
elody_client = Client(collection_api_url, os.getenv("STATIC_JWT"))

CONFLICT_RETRY_ATTEMPTS = 4
CONFLICT_RETRY_DELAYS = (0.25, 0.5, 1.0)
CONFLICT_RETRY_JITTER = 0.1
OPTIMISTIC_CONCURRENCY_MESSAGE = "Optimistic concurrency failure"


def send_with_conflict_retry(method, url, **kwargs):
    """Send a request to the collection-api, retrying on optimistic concurrency conflicts.

    Only a 409 whose body reports an optimistic concurrency failure is retried;
    other 409s are semantic and returned as-is. Returns the last response
    without raising, so every caller keeps its own error handling.
    """
    response = None
    for attempt in range(1, CONFLICT_RETRY_ATTEMPTS + 1):
        response = requests.request(method, url, **kwargs)
        if (
            response.status_code != 409
            or OPTIMISTIC_CONCURRENCY_MESSAGE not in response.text
            or attempt == CONFLICT_RETRY_ATTEMPTS
        ):
            return response
        app.logger.warning(
            f"Concurrency conflict on {method} {url}, retrying (attempt {attempt}/{CONFLICT_RETRY_ATTEMPTS})"
        )
        sleep(
            CONFLICT_RETRY_DELAYS[attempt - 1]
            + random.uniform(0, CONFLICT_RETRY_JITTER)
        )
    return response


class CollectionApiService(metaclass=Singleton):
    def __init__(self):
        self.collection_api_url = os.getenv("COLLECTION_API_URL")
        self.headers = {"Authorization": f'Bearer {os.getenv("STATIC_JWT")}'}

    def add_ocr_output_to_metadata(self, mediafile_id, metadata):
        app.logger.info(
            "Storing the OCR txt output in the metadata of the original image file"
        )
        req = send_with_conflict_retry(
            "PATCH",
            f"{self.collection_api_url}/mediafiles/{mediafile_id}",
            json=metadata,
            headers=self.headers,
        )
        if req.status_code != 200:
            raise Exception(req.text.strip())
        return req

    def add_ocr_output_to_parent_entities(
        self, original_mediafile_id, ocr_mediafile_id, operation, lang
    ):
        original_mediafile = elody_client.get_object(
            "mediafiles", original_mediafile_id
        )
        unique_entities = list()
        payload = [
            {
                "key": ocr_mediafile_id,
                "label": "hasMediafile",
                "type": "hasMediafile",
                "is_ocr": True,
                "operation": operation,
                "lang": lang,
            }
        ]
        for relation in original_mediafile.get("relations", list()):
            entity_id = relation.get("key")
            if (
                relation.get("type") == "belongsTo"
                and entity_id not in unique_entities
                and "is_ocr" not in relation
                and self.get_entity_type(entity_id) == "asset"
            ):
                url = f"{self.collection_api_url}/entities/{entity_id}/relations"
                req = send_with_conflict_retry(
                    "PATCH", url, json=payload, headers=self.headers
                )
                if req.status_code != 200:
                    raise Exception(req.text.strip())
                unique_entities.append(entity_id)
        url = f"{self.collection_api_url}/mediafiles/{original_mediafile_id}/relations"
        req = send_with_conflict_retry(
            "PATCH", url, json=payload, headers=self.headers
        )
        if req.status_code != 200:
            raise Exception(req.text.strip())

    def get_entity_type(self, entity_id):
        return (
            requests.get(
                f"{self.collection_api_url}/entities/{entity_id}",
                headers=self.headers,
            )
            .json()
            .get("type")
        )

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
