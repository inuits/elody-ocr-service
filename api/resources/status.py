import os
import pkg_resources
from flask import request, Response
from flask_restful import abort, Resource

class Status(Resource):
    def __init__(self):
        self.headers = {"Authorization": f'Bearer {os.getenv("STATIC_JWT")}'}


    def get(self):
        tesseract = os.popen("tesseract -v").read().split("\n")[0]
        pytesseract = pkg_resources.working_set.by_key['pytesseract'].version
        output = f"{tesseract} available\npytesseract {pytesseract} available\n"
        return Response(response=output, status=200)
