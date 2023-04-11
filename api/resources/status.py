import flask
import os
import pkg_resources

from flask_restful import abort, Resource


class Status(Resource):
    def __init__(self):
        self.headers = {"Authorization": f'Bearer {os.getenv("STATIC_JWT")}'}

    def get(self):
        try:
            tesseract = os.popen("tesseract -v").read().split("\n")[0]
            pytesseract = pkg_resources.working_set.by_key["pytesseract"].version
            output = f"{tesseract} available\npytesseract {pytesseract} available"
            return flask.Response(response=output, status=200, mimetype="text/plain")
        except Exception as ex:
            abort(status=400, message=str(ex))
