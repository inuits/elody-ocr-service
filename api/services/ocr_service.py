import app
import ghostscript
import os
import pytesseract

from io import BytesIO
from pathlib import Path
from PIL import Image
from singleton import Singleton
from services.collection_api_service import CollectionApiService
from services.storage_api_service import StorageApiService


CLIENT_PDF_FILENAME = str(os.getenv("CLIENT_PDF_FILENAME", False))
CLIENT_IMAGE_PATH = str(os.getenv("CLIENT_IMAGE_PATH", False))
CLIENT_PDF_PATH = str(os.getenv("CLIENT_PDF_PATH", False))


class OcrService(metaclass=Singleton):
    def __init__(self):
        self.headers = {"Authorization": f'Bearer {os.getenv("STATIC_JWT")}'}
        self.storage_api_service = StorageApiService()
        self.collection_api_service = CollectionApiService()

    def __add_txt_to_metadata(self, mediafile_image_data, ocr_output):
        try:
            metadata = {"key": "text_from_ocr", "value": ocr_output}
            mediafile_image_data.get("metadata").append(metadata)
            self.collection_api_service.add_ocr_output_to_metadata(
                mediafile_image_data.get("_key"),
                {"metadata": mediafile_image_data.get("metadata")},
            )
        except Exception as ex:
            app.logger.error(
                f'"The ocr function failed during update of metadata:" {ex}'
            )

    def __run_tesseract(self, method, path, image_data, lang):
        with open(path, "wb") as handler:
            handler.write(image_data)
        data = method(Image.open(path), lang=lang)
        Path(path).unlink()
        return data

    def convert_image_to_data(
        self,
        method,
        ext,
        mimetype,
        mediafile_image_data,
        lang,
        image_name,
        id_new_mediafile,
    ):
        try:
            img_data = self.storage_api_service.download_image(image_name)
        except Exception as ex:
            self.collection_api_service.delete_mediafile(id_new_mediafile)
            app.logger.info("The created mediafile is deleted due to an error:")
            app.logger.error(
                f'"The ocr function failed during downloading the image in the storage api:" {ex}'
            )
        try:
            data = self.__run_tesseract(method, CLIENT_IMAGE_PATH, img_data, lang)
            mediafile_name = (
                mediafile_image_data[0].get("original_filename").split(".")[0] + ext
            )
        except Exception as ex:
            self.collection_api_service.delete_mediafile(id_new_mediafile)
            app.logger.info("The created mediafile is deleted due to an error:")
            app.logger.error(
                f"The ocr function failed during running tesseract en getting the filename: {ex}"
            )
        if ext == ".txt":
            self.__add_txt_to_metadata(mediafile_image_data[0], data)
            data = data.encode("utf-8")
        return data, mediafile_name, mimetype

    def create_pdf_with_ghostscript(self, images, lang, id_new_mediafile):
        pdfs = self.create_searchable_pdfs(images, id_new_mediafile)
        args = [
            "pdfocr8",
            "-dNOPAUSE",
            "-dBATCH",
            "-dSAFER",
            "-sDEVICE=pdfocr8",
            f"-sOCRLanguage={lang}",
            f"-sOutputFile={CLIENT_PDF_FILENAME}",
        ]
        for pdf in pdfs:
            args.append("-f")
            args.append(pdf)
        ghostscript.Ghostscript(*args)
        for pdf in pdfs:
            Path(pdf).unlink()

    def create_searchable_pdfs(self, images, id_new_mediafile):
        pdfs = []
        not_valid_counter = 0
        for i in range(len(images)):
            if not images[i]:
                not_valid_counter += 1
                continue
            try:
                img_data = self.storage_api_service.download_image(images[i])
            except Exception as ex:
                self.collection_api_service.delete_mediafile(id_new_mediafile)
                app.logger.info("The created mediafile is deleted due to an error:")
                app.logger.error(
                    f'"The ocr function failed during downloading the image in the storage api:" {ex}'
                )
            pdfname = CLIENT_PDF_FILENAME + str(i) + ".pdf"
            if not images[i].endswith(".pdf"):
                img = Image.open(BytesIO(img_data))
                pdf = img.convert("RGB")
                pdf.save(pdfname)
            else:
                with open(pdfname, "wb") as handler:
                    handler.write(img_data)
            pdfs.append(pdfname)
        return pdfs

    def ocr(self, operation, mediafile_image_data, lang, image_name, id_new_mediafile):
        operations = {
            "txt": self.ocr_to_txt,
            "alto": self.ocr_to_alto,
            "pdf": self.ocr_to_pdf,
        }
        func = operations.get(operation)
        return func(mediafile_image_data, lang, image_name, id_new_mediafile)

    def ocr_to_alto(self, mediafile_image_data, lang, image_name, id_new_mediafile):
        response = self.convert_image_to_data(
            method=pytesseract.image_to_alto_xml,
            ext=".xml",
            mimetype="application/xml",
            mediafile_image_data=mediafile_image_data,
            lang=lang,
            image_name=image_name,
            id_new_mediafile=id_new_mediafile,
        )
        return response

    def ocr_to_txt(self, mediafile_image_data, lang, image_name, id_new_mediafile):
        response = self.convert_image_to_data(
            method=pytesseract.image_to_string,
            ext=".txt",
            mimetype="text/plain",
            mediafile_image_data=mediafile_image_data,
            lang=lang,
            image_name=image_name,
            id_new_mediafile=id_new_mediafile,
        )
        return response

    def ocr_to_pdf(self, mediafile_image_data, lang, image_name, id_new_mediafile):
        images = []
        for i in range(len(mediafile_image_data)):
            images.append(mediafile_image_data[i].get("filename"))
        try:
            self.create_pdf_with_ghostscript(images, lang, id_new_mediafile)
        except Exception as ex:
            self.collection_api_service.delete_mediafile(id_new_mediafile)
            app.logger.info("The created mediafile is deleted due to an error:")
            app.logger.error(f"Ghostscript failed: {ex}")
        try:
            mediafile_name = (
                mediafile_image_data[0].get("original_filename").split(".")[0] + ".pdf"
            )
            return open(CLIENT_PDF_FILENAME, "rb"), mediafile_name, "application/pdf"
        except Exception as ex:
            self.collection_api_service.delete_mediafile(id_new_mediafile)
            app.logger.info("The created mediafile is deleted due to an error:")
            app.logger.error(f'"In ocr_service - The ocr function failed with:" {ex}')
        finally:
            Path(CLIENT_PDF_FILENAME).unlink()
