import json
import unittest

from app import app


class BaseCase(unittest.TestCase):
    entity = json.dumps(
        {
            "identifiers": ["12345", "abcde"],
            "type": "entity",
            "metadata": [
                {"key": "title", "value": "Een schilderij", "lang": "nl"},
                {"key": "title", "value": "A painting", "lang": "en"},
                {
                    "key": "description",
                    "value": "Beschrijving van een schilderij",
                    "lang": "nl",
                },
                {
                    "key": "description",
                    "value": "Description of a painting",
                    "lang": "en",
                },
            ],
        }
    )

    invalid_entity = json.dumps(
        {
            "identifiers": "123",
            "metadata": "title",
            "data": "test",
        }
    )

    mediafile = json.dumps(
        {
            "identifiers": ["12345", "abcde"],
            "filename": "test.jpg",
            "original_file_location": "http://dams-storage.inuits.io/download/test.jpg",
        }
    )

    invalid_mediafile = json.dumps(
        {
            "identifiers": "12345",
            "original_file_location": [
                "http://dams-storage.inuits.io/download/test.jpg"
            ],
        }
    )

    filename = json.dumps(
        {
            "filename": "test.jpg",
        }
    )

    filename_with_metadata = json.dumps(
        {
            "filename": "test.jpg",
            "metadata": [
                {
                    "key": "rights",
                    "value": "CC-BY-4.0",
                    "lang": "en",
                },
                {
                    "key": "copyright",
                    "value": "Inuits",
                    "lang": "en",
                },
            ],
        }
    )

    def setUp(self):
        app.testing = True
        self.app = app.test_client()

