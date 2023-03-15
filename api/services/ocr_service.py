from pathlib import Path
from fpdf import FPDF
from pypdf import PdfMerger
from PIL import Image
from humanfriendly import parse_size
from flask import Response, make_response, send_file
from flask_restful import Headers, abort
import urllib.request
import os
import pytesseract
import mimetypes
import magic
from services.storage_api_service import StorageApiService



CLIENT_PDF_FILENAME = "ocr-pdf"
CLIENT_IMAGE_PATH = "/app/api/ocr-image"
CLIENT_PDF_PATH = "/app/api/ocr-pdf"

ALLOWED_MIMETYPES = ['image/png', 'image/jpg', 'image/jpeg', 'image/tiff', 'image/gif', 'image/webp']
ALLOWED_LANGUAGES = ["eng", "nld", "fra"]


class OcrService(object):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(OcrService, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        self.headers = {"Authorization": f'Bearer {os.getenv("STATIC_JWT")}'}
        self.storage_api_service = StorageApiService()



    def ocr(self, operation, mediafile_image_data, language):
        operations = {
            "txt": self.ocr_to_txt,
            "alto": self.ocr_to_alto,
            "pdf": self.ocr_to_pdf,
        }
        func = operations.get(operation)
        if not func:
            raise Exception(f"Operation {operation} not supported")

        return func(mediafile_image_data, language)


    def ocr_to_txt(self, mediafile_image_data, lang):
        response = self.convert_image_to_data(method=pytesseract.image_to_string, ext=".txt", mimetype="text/plain", mediafile_image_data=mediafile_image_data, lang=lang)
        return response


    def ocr_to_alto(self, mediafile_image_data, lang):
        response = self.convert_image_to_data(method=pytesseract.image_to_alto_xml, ext=".xml", mimetype="application/xml", mediafile_image_data=mediafile_image_data, lang=lang)
        return response


    def ocr_to_pdf(self, mediafile_image_data, lang):
        # get the diverted images if it exists, otherwise the originals
        images = []
        for i in range(len(mediafile_image_data)):
            images.append(mediafile_image_data[i].get("filename"))

        # merging
        self.merge_searchable_pdfs(images, lang)

        # returning the pdf file
        mediafile_name = mediafile_image_data[0].get("original_filename").split(".")[0] + ".pdf"
        try:
            return open(CLIENT_PDF_PATH, "rb"), mediafile_name, "application/pdf"
        except Exception as ex:
            abort(400, message=str(ex))
        finally:
            Path(CLIENT_PDF_PATH).unlink()



    # helper method for text/alto
    def convert_image_to_data(self, method, ext, mimetype, mediafile_image_data, lang):
        # there should only be one image
        if len(mediafile_image_data) > 1:
            abort(400, message="You can only send 1 image. Images received: " + str(len(mediafile_image_data)))

        # get the diverted image if it exists, otherwise the original
        image_name = mediafile_image_data[0].get("filename")

        # validate extension
        if not self.is_mimetype_from_filename_valid(image_name):
            abort(400, message="Extension is not valid")

        # download image
        try:
            img_data = self.storage_api_service.download_image(image_name)
        except Exception as ex:
            abort(400, message=str(ex))

        # save image on disk, run tesseract & delete image
        with open(CLIENT_IMAGE_PATH, 'wb') as handler:
            handler.write(img_data.content)
        data = method(Image.open(CLIENT_IMAGE_PATH), lang=lang)
        Path(CLIENT_IMAGE_PATH).unlink()

        mediafile_name = mediafile_image_data[0].get("original_filename").split(".")[0] + ext
        if ext == ".txt":
            data = data.encode("utf-8")
        return data, mediafile_name, mimetype


    def create_searchable_pdfs(self, images, language):
        pdfs = []
        not_valid_counter = 0

        for i in range(len(images)):
            # check if the image isn't a none type
            if not images[i]:
                not_valid_counter += 1
                continue

            # check the extension of the image
            if not self.is_mimetype_from_filename_valid(images[i]):
                not_valid_counter += 1
                continue

            # download images
            try:
                img_data = self.storage_api_service.download_image(images[i])
            except Exception as ex:
                abort(400, message=str(ex))

            # save image on disk, run tesseract & delete image
            with open(CLIENT_IMAGE_PATH, 'wb') as handler:
                handler.write(img_data.content)

            # create the pdf
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("helvetica", size=12)
            pdf.output(CLIENT_PDF_FILENAME + str(i))

            # add reference to list of pdfs
            pdfs.append(CLIENT_PDF_PATH + str(i))
            # create output and delete image
            output = pytesseract.image_to_pdf_or_hocr(Image.open(CLIENT_IMAGE_PATH), lang=language, extension="pdf")
            Path(CLIENT_IMAGE_PATH).unlink()
            # add output to created pdf
            with open(pdfs[i - not_valid_counter], "wb") as binary_pdf:
                binary_pdf.write(output)

        return pdfs


    def merge_searchable_pdfs(self, images, language):
        # create seperate pdfs with references in list
        pdfs = self.create_searchable_pdfs(images, language)
        if len(pdfs) == 0:
            abort(400, message="Extensions are not valid or file not found")

        # create final pdf
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("helvetica", size=12)
        pdf.output(CLIENT_PDF_FILENAME)

        # merge seperate pdfs into final pdf
        pdf_merger = PdfMerger()
        for pdfUrl in pdfs:
            pdf_merger.append(pdfUrl)
        with Path(CLIENT_PDF_PATH).open(mode="wb") as output_file:
            pdf_merger.write(output_file)

        # cleanup: delete separate pdf's
        for pdf in pdfs:
            Path(pdf).unlink()



    def get_file_mimetype(self, file):
        file.seek(0)
        mime = magic.Magic(mime=True).from_buffer(file.read(parse_size("8 KiB")))
        return mime in ALLOWED_MIMETYPES


    def is_mimetype_from_filename_valid(self, filename):
        mime = mimetypes.guess_type(filename, False)[0]
        return mime in ALLOWED_MIMETYPES

