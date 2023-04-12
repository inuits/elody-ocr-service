import services
import unittest

from app import app


class BaseCase(unittest.TestCase):
    path_first_image = "/app/api/tests/testdata/screenshot_loremipsum.png"
    path_second_image = "/app/api/tests/testdata/screenshot_dummytext.png"

    filename_with_metadata = {
        "original_filename": "screenshot_loremipsum.png",
        "filename": "screenshot_loremipsum.png",
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

    alto_md5 = {
        "eng": "227a36e0ac35113f0d8fec6ddb6cb688",
        "nld": "696b7d75a3dac7fc140844f3c0c28e06",
        "fra": "9a65f95ca52660fe199b883764b83e90",
    }
    pdf_md5 = {
        "eng": "7b411852f806cd7f462055584a9f4dce",
        "nld": "ff4aba70304e8a98cb9314858cde2036",
        "fra": "06d2b09abeb5642293975265a87d6800",
    }
    txt_md5 = {
        "eng": "e12db9f1f70a8c4ee1ee83b425b1f220",
        "nld": "3be84f9b72ed00f49eef5b9bf609ba6f",
        "fra": "b8f8c2c1ef22c917cca9725bbadecab8",
    }

    def setUp(self):
        app.testing = True
        self.app = app.test_client()
        self.ocr_service = services.ocr_service.OcrService()
