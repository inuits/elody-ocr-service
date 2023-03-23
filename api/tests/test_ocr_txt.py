import json
import pytest
from tests.base_case import BaseCase
from unittest.mock import patch, MagicMock


path = "./tests/testdata/screenshot_loremipsum.png"
endpoint = "/ocr/txt"

txt_md5 = {
    "eng": "17d482e4437ae14fefd9992d721e4cb3",
    "nld": "e599b7f46027e8ec966a87e84f123aad",
    "fra": "b098f3c27a6cb3cf97e6122cb1445baa"
}

# for wrong testcases
path_txtfile = "./tests/testdata/txtfile"
path_second_image = "./tests/testdata/screenshot_dummytext.png"



@patch("app.rabbit", new=MagicMock())
class OcrTxtTest(BaseCase):

    # STATUS ENDPOINT
    def test_status_endpoint_get(self):
        response = self.app.get(
            f"/status",
            headers={"content-type": "multipart/form-data"}
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual("text/plain", response.mimetype)
        self.assertEqual("tesseract 4.1.1 available\npytesseract 0.3.10 available", response.get_data(as_text=True))



    # OCR ENDPOINT -> operation TXT
    # FAIL TESTCASES
    def test_without_operation_post(self):
        response = self.app.post(
            f"/ocr",
            json={"mediafile_id": ["12345"]},
            headers={"content-type": "application/json"},
        )
        self.assertEqual(405, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertIn("Malformed request body. Mandatory fieds: ['mediafile_id', 'operation']", response.get_data(as_text=True))

    def test_without_mediafile_post(self):
        response = self.app.post(
            f"/ocr",
            json={"operation": "txt"},
            headers={"content-type": "application/json"},
        )
        self.assertEqual(405, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertIn("Malformed request body. Mandatory fieds: ['mediafile_id', 'operation']", response.get_data(as_text=True))

    def test_with_wrong_operation_post(self):
        response = self.app.post(
            f"/ocr",
            json={"mediafile_id": ["12345"], "operation": "txtt"},
            headers={"content-type": "application/json"},
        )
        self.assertEqual(405, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertIn("Invalid operation. Possible operations are ['txt', 'alto', 'pdf']", response.get_data(as_text=True))

    def test_with_invalid_mediafile1_post(self):
        response = self.app.post(
            f"/ocr",
            json={"mediafile_id": "12345", "operation": "txt"},
            headers={"content-type": "application/json"},
        )
        self.assertEqual(400, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertIn("Malformed request body. Send the image id(s) in an array", response.get_data(as_text=True))

    def test_with_invalid_mediafile2_post(self):
        response = self.app.post(
            f"/ocr",
            json={"mediafile_id": [], "operation": "txt"},
            headers={"content-type": "application/json"},
        )
        self.assertEqual(400, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertIn("Malformed request body. You forgot to give a mediafile id", response.get_data(as_text=True))

    def test_with_invalid_mediafile3_post(self):
        response = self.app.post(
            f"/ocr",
            json={"mediafile_id": [""], "operation": "txt"},
            headers={"content-type": "application/json"},
        )
        self.assertEqual(400, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertIn("Malformed request body. You cannot give an empty mediafile id", response.get_data(as_text=True))

    def test_with_multiple_mediafiles_with_txt_post(self):
        response = self.app.post(
            f"/ocr",
            json={"mediafile_id": ['12345', '12345'], "operation": "txt"},
            headers={"content-type": "application/json"},
        )
        self.assertEqual(400, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertIn("You can only send 1 image id for the [txt] operation. Images received: 2", response.get_data(as_text=True))