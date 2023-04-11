import hashlib

from services.ocr_service import OcrService
from tests.base_case import BaseCase
from unittest.mock import patch, MagicMock


class OcrMethodsTest(BaseCase):
    # test cases for txt operation
    def test_upload_one_image_ENG_receive_txt_should_succeed(self):
        ocr_service = OcrService()
        ocr_service.__add_txt_to_metadata = MagicMock()
        ocr_service.collection_api_service.delete_mediafile = MagicMock()
        with open(self.path_first_image, "rb") as file:
            ocr_service.storage_api_service.download_image = MagicMock(
                return_value=file.read()
            )

        data, mediafile_name, mimetype = ocr_service.ocr(
            "txt", [self.filename_with_metadata], "eng", "image", "6789"
        )
        self.assertEqual("text/plain", mimetype)
        actual_md5 = hashlib.md5(data).hexdigest()
        self.assertEqual(self.txt_md5.get("eng"), actual_md5)

    def test_upload_one_image_NLD_receive_txt_should_succeed(self):
        ocr_service = OcrService()
        ocr_service.__add_txt_to_metadata = MagicMock()
        ocr_service.collection_api_service.delete_mediafile = MagicMock()
        with open(self.path_first_image, "rb") as file:
            ocr_service.storage_api_service.download_image = MagicMock(
                return_value=file.read()
            )

        data, mediafile_name, mimetype = ocr_service.ocr(
            "txt", [self.filename_with_metadata], "nld", "image", "6789"
        )
        self.assertEqual("text/plain", mimetype)
        actual_md5 = hashlib.md5(data).hexdigest()
        self.assertEqual(self.txt_md5.get("nld"), actual_md5)

    def test_upload_one_image_FRA_receive_txt_should_succeed(self):
        ocr_service = OcrService()
        ocr_service.__add_txt_to_metadata = MagicMock()
        ocr_service.collection_api_service.delete_mediafile = MagicMock()
        with open(self.path_first_image, "rb") as file:
            ocr_service.storage_api_service.download_image = MagicMock(
                return_value=file.read()
            )

        data, mediafile_name, mimetype = ocr_service.ocr(
            "txt", [self.filename_with_metadata], "fra", "image", "6789"
        )
        self.assertEqual("text/plain", mimetype)
        actual_md5 = hashlib.md5(data).hexdigest()
        self.assertEqual(self.txt_md5.get("fra"), actual_md5)

    # test cases for alto operation
    def test_upload_one_image_ENG_receive_alto_should_succeed(self):
        ocr_service = OcrService()
        ocr_service.__add_txt_to_metadata = MagicMock()
        ocr_service.collection_api_service.delete_mediafile = MagicMock()
        with open(self.path_first_image, "rb") as file:
            ocr_service.storage_api_service.download_image = MagicMock(
                return_value=file.read()
            )

        data, mediafile_name, mimetype = ocr_service.ocr(
            "alto", [self.filename_with_metadata], "eng", "image", "6789"
        )
        self.assertEqual("application/xml", mimetype)
        actual_md5 = hashlib.md5(data).hexdigest()
        self.assertEqual(self.alto_md5.get("eng"), actual_md5)

    def test_upload_one_image_NLD_receive_alto_should_succeed(self):
        ocr_service = OcrService()
        ocr_service.__add_txt_to_metadata = MagicMock()
        ocr_service.collection_api_service.delete_mediafile = MagicMock()
        with open(self.path_first_image, "rb") as file:
            ocr_service.storage_api_service.download_image = MagicMock(
                return_value=file.read()
            )

        data, mediafile_name, mimetype = ocr_service.ocr(
            "alto", [self.filename_with_metadata], "nld", "image", "6789"
        )
        self.assertEqual("application/xml", mimetype)
        actual_md5 = hashlib.md5(data).hexdigest()
        self.assertEqual(self.alto_md5.get("nld"), actual_md5)

    def test_upload_one_image_FRA_receive_alto_should_succeed(self):
        ocr_service = OcrService()
        ocr_service.__add_txt_to_metadata = MagicMock()
        ocr_service.collection_api_service.delete_mediafile = MagicMock()
        with open(self.path_first_image, "rb") as file:
            ocr_service.storage_api_service.download_image = MagicMock(
                return_value=file.read()
            )

        data, mediafile_name, mimetype = ocr_service.ocr(
            "alto", [self.filename_with_metadata], "fra", "image", "6789"
        )
        self.assertEqual("application/xml", mimetype)
        actual_md5 = hashlib.md5(data).hexdigest()
        self.assertEqual(self.alto_md5.get("fra"), actual_md5)

    # test cases for pdf operation
    def test_upload_one_image_ENG_receive_pdf_should_succeed(self):
        ocr_service = OcrService()
        ocr_service.__add_txt_to_metadata = MagicMock()
        ocr_service.collection_api_service.delete_mediafile = MagicMock()
        with open(self.path_first_image, "rb") as file:
            ocr_service.storage_api_service.download_image = MagicMock(
                return_value=file.read()
            )

        data, mediafile_name, mimetype = ocr_service.ocr(
            "pdf", [self.filename_with_metadata], "eng", "image", "6789"
        )
        self.assertEqual("application/pdf", mimetype)
        actual_md5 = hashlib.md5(data.read()).hexdigest()
        self.assertEqual(self.pdf_md5.get("eng"), actual_md5)

    def test_upload_one_image_NLD_receive_pdf_should_succeed(self):
        ocr_service = OcrService()
        ocr_service.__add_txt_to_metadata = MagicMock()
        ocr_service.collection_api_service.delete_mediafile = MagicMock()
        with open(self.path_first_image, "rb") as file:
            ocr_service.storage_api_service.download_image = MagicMock(
                return_value=file.read()
            )

        data, mediafile_name, mimetype = ocr_service.ocr(
            "pdf", [self.filename_with_metadata], "nld", "image", "6789"
        )
        self.assertEqual("application/pdf", mimetype)
        actual_md5 = hashlib.md5(data.read()).hexdigest()
        self.assertEqual(self.pdf_md5.get("nld"), actual_md5)

    def test_upload_one_image_FRA_receive_pdf_should_succeed(self):
        ocr_service = OcrService()
        ocr_service.__add_txt_to_metadata = MagicMock()
        ocr_service.collection_api_service.delete_mediafile = MagicMock()
        with open(self.path_first_image, "rb") as file:
            ocr_service.storage_api_service.download_image = MagicMock(
                return_value=file.read()
            )

        data, mediafile_name, mimetype = ocr_service.ocr(
            "pdf", [self.filename_with_metadata], "fra", "image", "6789"
        )
        self.assertEqual("application/pdf", mimetype)
        actual_md5 = hashlib.md5(data.read()).hexdigest()
        self.assertEqual(self.pdf_md5.get("fra"), actual_md5)
