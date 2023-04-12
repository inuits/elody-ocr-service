import hashlib

from pypdf import PdfReader
from tests.base_case import BaseCase
from unittest.mock import patch, MagicMock


class OcrMethodsTest(BaseCase):
    # test cases for txt operation
    def test_upload_one_image_ENG_receive_txt_should_succeed(self):
        self.ocr_service.__add_txt_to_metadata = MagicMock()
        self.ocr_service.collection_api_service.delete_mediafile = MagicMock()
        with open(self.path_first_image, "rb") as file:
            self.ocr_service.storage_api_service.download_image = MagicMock(
                return_value=file.read()
            )

        data, mediafile_name, mimetype = self.ocr_service.ocr(
            "txt", [self.filename_with_metadata], "eng", "image", "6789"
        )
        self.assertEqual("text/plain", mimetype)
        self.assertEqual("screenshot_loremipsum.txt", mediafile_name)
        actual_md5 = hashlib.md5(data).hexdigest()
        self.assertEqual(self.txt_md5.get("eng"), actual_md5)

    def test_upload_one_image_NLD_receive_txt_should_succeed(self):
        self.ocr_service.__add_txt_to_metadata = MagicMock()
        self.ocr_service.collection_api_service.delete_mediafile = MagicMock()
        with open(self.path_first_image, "rb") as file:
            self.ocr_service.storage_api_service.download_image = MagicMock(
                return_value=file.read()
            )

        data, mediafile_name, mimetype = self.ocr_service.ocr(
            "txt", [self.filename_with_metadata], "nld", "image", "6789"
        )
        self.assertEqual("text/plain", mimetype)
        self.assertEqual("screenshot_loremipsum.txt", mediafile_name)
        actual_md5 = hashlib.md5(data).hexdigest()
        self.assertEqual(self.txt_md5.get("nld"), actual_md5)

    def test_upload_one_image_FRA_receive_txt_should_succeed(self):
        self.ocr_service.__add_txt_to_metadata = MagicMock()
        self.ocr_service.collection_api_service.delete_mediafile = MagicMock()
        with open(self.path_first_image, "rb") as file:
            self.ocr_service.storage_api_service.download_image = MagicMock(
                return_value=file.read()
            )

        data, mediafile_name, mimetype = self.ocr_service.ocr(
            "txt", [self.filename_with_metadata], "fra", "image", "6789"
        )
        self.assertEqual("text/plain", mimetype)
        self.assertEqual("screenshot_loremipsum.txt", mediafile_name)
        actual_md5 = hashlib.md5(data).hexdigest()
        self.assertEqual(self.txt_md5.get("fra"), actual_md5)

    # test cases for alto operation
    def test_upload_one_image_ENG_receive_alto_should_succeed(self):
        self.ocr_service.__add_txt_to_metadata = MagicMock()
        self.ocr_service.collection_api_service.delete_mediafile = MagicMock()
        with open(self.path_first_image, "rb") as file:
            self.ocr_service.storage_api_service.download_image = MagicMock(
                return_value=file.read()
            )

        data, mediafile_name, mimetype = self.ocr_service.ocr(
            "alto", [self.filename_with_metadata], "eng", "image", "6789"
        )
        self.assertEqual("application/xml", mimetype)
        self.assertEqual("screenshot_loremipsum.xml", mediafile_name)
        actual_md5 = hashlib.md5(data).hexdigest()
        self.assertEqual(self.alto_md5.get("eng"), actual_md5)

    def test_upload_one_image_NLD_receive_alto_should_succeed(self):
        self.ocr_service.__add_txt_to_metadata = MagicMock()
        self.ocr_service.collection_api_service.delete_mediafile = MagicMock()
        with open(self.path_first_image, "rb") as file:
            self.ocr_service.storage_api_service.download_image = MagicMock(
                return_value=file.read()
            )

        data, mediafile_name, mimetype = self.ocr_service.ocr(
            "alto", [self.filename_with_metadata], "nld", "image", "6789"
        )
        self.assertEqual("application/xml", mimetype)
        self.assertEqual("screenshot_loremipsum.xml", mediafile_name)
        actual_md5 = hashlib.md5(data).hexdigest()
        self.assertEqual(self.alto_md5.get("nld"), actual_md5)

    def test_upload_one_image_FRA_receive_alto_should_succeed(self):
        self.ocr_service.__add_txt_to_metadata = MagicMock()
        self.ocr_service.collection_api_service.delete_mediafile = MagicMock()
        with open(self.path_first_image, "rb") as file:
            self.ocr_service.storage_api_service.download_image = MagicMock(
                return_value=file.read()
            )

        data, mediafile_name, mimetype = self.ocr_service.ocr(
            "alto", [self.filename_with_metadata], "fra", "image", "6789"
        )
        self.assertEqual("application/xml", mimetype)
        self.assertEqual("screenshot_loremipsum.xml", mediafile_name)
        actual_md5 = hashlib.md5(data).hexdigest()
        self.assertEqual(self.alto_md5.get("fra"), actual_md5)

    # test cases for pdf operation
    def test_upload_one_image_ENG_receive_pdf_should_succeed(self):
        self.ocr_service.__add_txt_to_metadata = MagicMock()
        self.ocr_service.collection_api_service.delete_mediafile = MagicMock()
        with open(self.path_second_image, "rb") as file:
            self.ocr_service.storage_api_service.download_image = MagicMock(
                return_value=file.read()
            )

        data, mediafile_name, mimetype = self.ocr_service.ocr(
            "pdf", [self.filename_with_metadata], "eng", "image", "6789"
        )
        reader = PdfReader(data)
        text_output = ""
        for i in range(len(reader.pages)):
            page = reader.pages[0]
            text_output += page.extract_text()

        self.assertEqual("application/pdf", mimetype)
        self.assertEqual("screenshot_loremipsum.pdf", mediafile_name)
        actual_md5 = hashlib.md5(text_output.encode('utf-8')).hexdigest()
        self.assertEqual(self.pdf_md5.get("eng"), actual_md5)

    def test_upload_one_image_NLD_receive_pdf_should_succeed(self):
        self.ocr_service.__add_txt_to_metadata = MagicMock()
        self.ocr_service.collection_api_service.delete_mediafile = MagicMock()
        with open(self.path_second_image, "rb") as file:
            self.ocr_service.storage_api_service.download_image = MagicMock(
                return_value=file.read()
            )

        data, mediafile_name, mimetype = self.ocr_service.ocr(
            "pdf", [self.filename_with_metadata], "nld", "image", "6789"
        )
        reader = PdfReader(data)
        text_output = ""
        for i in range(len(reader.pages)):
            page = reader.pages[0]
            text_output += page.extract_text()

        self.assertEqual("application/pdf", mimetype)
        self.assertEqual("screenshot_loremipsum.pdf", mediafile_name)
        actual_md5 = hashlib.md5(text_output.encode('utf-8')).hexdigest()
        self.assertEqual(self.pdf_md5.get("nld"), actual_md5)


    def test_upload_one_image_FRA_receive_pdf_should_succeed(self):
        self.ocr_service.__add_txt_to_metadata = MagicMock()
        self.ocr_service.collection_api_service.delete_mediafile = MagicMock()
        with open(self.path_second_image, "rb") as file:
            self.ocr_service.storage_api_service.download_image = MagicMock(
                return_value=file.read()
            )

        data, mediafile_name, mimetype = self.ocr_service.ocr(
            "pdf", [self.filename_with_metadata], "fra", "image", "6789"
        )
        reader = PdfReader(data)
        text_output = ""
        for i in range(len(reader.pages)):
            page = reader.pages[0]
            text_output += page.extract_text()

        self.assertEqual("application/pdf", mimetype)
        self.assertEqual("screenshot_loremipsum.pdf", mediafile_name)
        actual_md5 = hashlib.md5(text_output.encode('utf-8')).hexdigest()
        self.assertEqual(self.pdf_md5.get("fra"), actual_md5)
