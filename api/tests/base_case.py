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
        "eng": "f5d5e55a5041ef1435a0adc3a12d2263",
        "nld": "a44a1e5d0c23d1493e57fd93c66683d3",
        "fra": "6e3a4c2dd873cb84c2cea40db4a5d97e",
    }
    pdfs_md5 = {
        "eng": "03daba6ed1850964f2e372f63a7d1438",
        "nld": "ffff70fa984fc789fbd42881b9550fe1",
        "fra": "622f358887cfbab7023e74501c6c7348",
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
