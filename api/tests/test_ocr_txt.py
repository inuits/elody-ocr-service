import json
from tests.base_case import BaseCase
from unittest.mock import patch, MagicMock


@patch("app.rabbit", new=MagicMock())
class OcrTxtTest(BaseCase):
    raise NotImplementedError()
