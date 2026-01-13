from flask_restful import Api
from resources.ocr import Ocr
from resources.ocr_correction import OcrCorrection
from resources.spec import OpenAPISpec
from resources.status import Status


def init_api(app):
    api = Api(app)
    api.add_resource(Ocr, "/ocr")
    api.add_resource(OcrCorrection, "/ocr/correction")
    api.add_resource(Status, "/status")
    api.add_resource(OpenAPISpec, "/spec/inuits-dams-ocr-service.json")