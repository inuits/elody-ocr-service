import os
import app
import pkg_resources
from flask import request, Response
from flask_restful import abort, Resource

class BaseStatus(Resource):
    def __init__(self):
        self.headers = {"Authorization": f'Bearer {os.getenv("STATIC_JWT")}'}


    def get(self):
        # connection = app.rabbit.get_connection()
        # channel = connection.channel()
        # queue = channel.queue_declare(queue="dams.ocr_request", durable=True)
        # size = queue.method.message_count

        tesseract = os.popen("tesseract -v").read().split("\n")[0]
        pytesseract = pkg_resources.working_set.by_key['pytesseract'].version
        output = f"{tesseract} available\npytesseract {pytesseract} available\n"
        return Response(response=str(output), status=200)
