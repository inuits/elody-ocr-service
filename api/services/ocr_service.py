
import os
from PIL import ExifTags, Image, ImageOps, TiffImagePlugin

Image.MAX_IMAGE_PIXELS = None

# moet een SINGLETON zijn
class OcrService:
    def __init__(self, mediafile, url):
        self.collection_api_url = os.getenv("COLLECTION_API_URL")
        self.headers = {"Authorization": f'Bearer {os.getenv("STATIC_JWT")}'}
        self.mediafile = mediafile
        self.storage_api_url = os.getenv("STORAGE_API_URL")
        self.url = url

    def __get_exif_for_mediafile(self, mediafile):
        raise NotImplementedError("not implemented")

    def __get_file(self, output):
        raise NotImplementedError("not implemented")

    def __get_item_metadata_value(self, item, key):
        raise NotImplementedError("not implemented")


    def __get_raw_id(self, item):
        raise NotImplementedError("not implemented")


    def __patch_mediafile(self, payload):
        raise NotImplementedError("not implemented")


    def __upload_ocr(self, file_name, file_bytes):
        raise NotImplementedError("not implemented")


    def ocr(self, operation, image_ids, language):
        operations = {
            "txt": self.ocr_to_txt,
            "alto": self.ocr_to_alto,
            "pdf": self.ocr_to_pdf,
        }
        func = operations.get(operation)
        if not func:
            raise Exception(f"Operation {operation} not supported")

        func(image_ids, language)


    def ocr_to_txt(self, image_id, language):
        raise NotImplementedError("not implemented")

    def ocr_to_alto(self, image_id, language):
        raise NotImplementedError("not implemented")

    def ocr_to_pdf(self, image_id, language):
        raise NotImplementedError("not implemented")