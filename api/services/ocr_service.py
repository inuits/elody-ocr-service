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


CLIENT_PDF_FILENAME = "ocr-pdf"
CLIENT_IMAGE_PATH = "/app/api/ocr-image"
CLIENT_PDF_PATH = "/app/api/ocr-pdf"


class OcrService(object):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(OcrService, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        self.headers = {"Authorization": f'Bearer {os.getenv("STATIC_JWT")}'}
        self.storage_api_service = StorageApiService()



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
        response = self.convert_image_to_data(method=pytesseract.image_to_string, ext=".txt", mimetype="text/plain", mediafile_image_data=mediafile_image_data, lang=lang, image_name=image_name)
        return response


    def ocr_to_alto(self, mediafile_image_data, lang, image_name):
        response = self.convert_image_to_data(method=pytesseract.image_to_alto_xml, ext=".xml", mimetype="application/xml", mediafile_image_data=mediafile_image_data, lang=lang, image_name=image_name)
        return response


    def ocr_to_pdf(self, mediafile_image_data, lang, image_name):
        # get the diverted images if it exists, otherwise the originals
        images = []
        for i in range(len(mediafile_image_data)):
            images.append(mediafile_image_data[i].get("filename"))

        self.merge_searchable_pdfs(images, lang)

        # returning the pdf file
        mediafile_name = mediafile_image_data[0].get("original_filename").split(".")[0] + ".pdf"
        try:
            return open(CLIENT_PDF_PATH, "rb"), mediafile_name, "application/pdf"
        except Exception as ex:
            app.logger.error(f'"In ocr_service - The ocr function failed with:" {ex}')
        finally:
            Path(CLIENT_PDF_PATH).unlink()


    # helper method for text/alto
    def convert_image_to_data(self, method, ext, mimetype, mediafile_image_data, lang, image_name):
        try:
            img_data = self.storage_api_service.download_image(image_name)
        except Exception as ex:
            app.logger.error(f'"The ocr function failed during downloading the image in the storage api:" {ex}')

        # save image on disk, run tesseract & delete image
        with open(CLIENT_IMAGE_PATH, 'wb') as handler:
            handler.write(img_data.content)
        data = method(Image.open(CLIENT_IMAGE_PATH), lang=lang)
        Path(CLIENT_IMAGE_PATH).unlink()

        mediafile_name = mediafile_image_data[0].get("original_filename").split(".")[0] + ext
        if ext == ".txt":
            data = data.encode("utf-8")
        return data, mediafile_name, mimetype


    def create_searchable_pdfs(self, images, lang):
        pdfs = []
        not_valid_counter = 0

        for i in range(len(images)):
            # check if the image isn't a none type
            if not images[i]:
                not_valid_counter += 1
                continue

            # download images
            try:
                img_data = self.storage_api_service.download_image(images[i])
            except Exception as ex:
                app.logger.error(f'"The ocr function failed during downloading the image in the storage api:" {ex}')

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
            output = pytesseract.image_to_pdf_or_hocr(Image.open(CLIENT_IMAGE_PATH), lang=lang, extension="pdf")
            Path(CLIENT_IMAGE_PATH).unlink()
            # add output to created pdf
            with open(pdfs[i - not_valid_counter], "wb") as binary_pdf:
                binary_pdf.write(output)

        return pdfs


    def merge_searchable_pdfs(self, images, lang):
        # create seperate pdfs with references in list
        pdfs = self.create_searchable_pdfs(images, lang)
        if len(pdfs) == 0:
            app.logger.error("The ocr function failed because: File not found")

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
