from pathlib import Path
from fpdf import FPDF
from pypdf import PdfMerger
from PIL import Image
from humanfriendly import parse_size
import app
from flask_restful import abort
import os
import pytesseract
import magic
from services.storage_api_service import StorageApiService
from services.collection_api_service import CollectionApiService


CLIENT_PDF_FILENAME = "ocr-pdf"
CLIENT_IMAGE_PATH = "/app/api/ocr-image"
CLIENT_PDF_PATH = "/app/api/ocr-pdf"


class OcrService(object):
    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(OcrService, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        self.headers = {"Authorization": f'Bearer {os.getenv("STATIC_JWT")}'}
        self.storage_api_service = StorageApiService()
        self.collection_api_service = CollectionApiService()

    def __run_tesseract(self, method, path, image_data, lang):
        with open(path, "wb") as handler:
            handler.write(image_data.content)
        data = method(Image.open(path), lang=lang)
        Path(path).unlink()
        return data

    def __create_pdf(self, i):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("helvetica", size=12)
        if i != -1:
            pdf.output(CLIENT_PDF_FILENAME + str(i))
        else:
            pdf.output(CLIENT_PDF_FILENAME)

    def __add_txt_to_metadata(self, mediafile_image_data, ocr_output):
        try:
            metadata = {
                "key": "text_from_ocr",
                "value": ocr_output
            }

            mediafile_image_data.get("metadata").append(metadata)
            self.collection_api_service.add_ocr_output_to_metadata(mediafile_image_data.get("_key"),
                                                                   mediafile_image_data)
        except Exception as ex:
            app.logger.error(
                f'"The ocr function failed during update of metadata:" {ex}'
            )

    def ocr(self, operation, mediafile_image_data, lang, image_name):
        operations = {
            "txt": self.ocr_to_txt,
            "alto": self.ocr_to_alto,
            "pdf": self.ocr_to_pdf,
        }
        func = operations.get(operation)
        if not func:
            raise Exception(f"Operation {operation} not supported")

        return func(mediafile_image_data, lang, image_name)

    def ocr_to_txt(self, mediafile_image_data, lang, image_name):
        response = self.convert_image_to_data(
            method=pytesseract.image_to_string,
            ext=".txt",
            mimetype="text/plain",
            mediafile_image_data=mediafile_image_data,
            lang=lang,
            image_name=image_name,
        )
        return response

    def ocr_to_alto(self, mediafile_image_data, lang, image_name):
        response = self.convert_image_to_data(
            method=pytesseract.image_to_alto_xml,
            ext=".xml",
            mimetype="application/xml",
            mediafile_image_data=mediafile_image_data,
            lang=lang,
            image_name=image_name,
        )
        return response

    def ocr_to_pdf(self, mediafile_image_data, lang, image_name):
        images = []
        for i in range(len(mediafile_image_data)):
            images.append(mediafile_image_data[i].get("filename"))
        self.merge_searchable_pdfs(images, lang)
        mediafile_name = (
            mediafile_image_data[0].get("original_filename").split(".")[0] + ".pdf"
        )

        try:
            return open(CLIENT_PDF_PATH, "rb"), mediafile_name, "application/pdf"
        except Exception as ex:
            app.logger.error(f'"In ocr_service - The ocr function failed with:" {ex}')
        finally:
            Path(CLIENT_PDF_PATH).unlink()

    def convert_image_to_data(
        self, method, ext, mimetype, mediafile_image_data, lang, image_name
    ):
        try:
            img_data = self.storage_api_service.download_image(image_name)
        except Exception as ex:
            app.logger.error(
                f'"The ocr function failed during downloading the image in the storage api:" {ex}'
            )
        data = self.__run_tesseract(method, CLIENT_IMAGE_PATH, img_data, lang)
        mediafile_name = (
            mediafile_image_data[0].get("original_filename").split(".")[0] + ext
        )

        if ext == ".txt":
            self.__add_txt_to_metadata(mediafile_image_data[0], data)
            data = data.encode("utf-8")
        return data, mediafile_name, mimetype

    def create_searchable_pdfs(self, images, lang):
        pdfs = []
        not_valid_counter = 0
        for i in range(len(images)):
            if not images[i]:
                not_valid_counter += 1
                continue
            try:
                img_data = self.storage_api_service.download_image(images[i])
            except Exception as ex:
                app.logger.error(
                    f'"The ocr function failed during downloading the image in the storage api:" {ex}'
                )

            self.__create_pdf(i)
            pdfs.append(CLIENT_PDF_PATH + str(i))
            output = self.__run_tesseract(
                pytesseract.image_to_pdf_or_hocr, CLIENT_IMAGE_PATH, img_data, lang
            )
            with open(pdfs[i - not_valid_counter], "wb") as binary_pdf:
                binary_pdf.write(output)
        return pdfs

    def merge_searchable_pdfs(self, images, lang):
        pdfs = self.create_searchable_pdfs(images, lang)
        if len(pdfs) == 0:
            app.logger.error("The ocr function failed because: File not found")

        self.__create_pdf(-1)
        pdf_merger = PdfMerger()
        for pdfUrl in pdfs:
            pdf_merger.append(pdfUrl)
        with Path(CLIENT_PDF_PATH).open(mode="wb") as output_file:
            pdf_merger.write(output_file)

        for pdf in pdfs:
            Path(pdf).unlink()
