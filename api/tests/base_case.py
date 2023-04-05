import unittest

from app import app


class BaseCase(unittest.TestCase):
    path_first_image = "/app/api/tests/testdata/screenshot_loremipsum.png"
    path_second_image = "/app/api/tests/testdata/screenshot_dummytext.png"

    txt_md5 = {
        "eng": "17d482e4437ae14fefd9992d721e4cb3",
        "nld": "e599b7f46027e8ec966a87e84f123aad",
        "fra": "b098f3c27a6cb3cf97e6122cb1445baa",
    }
    alto_md5 = {
        "eng": "00fa00688eb377f28adf841a119e942c",
        "nld": "4729e74e013673cf2979533621f7c37f",
        "fra": "bea4de68fd227cda4fa04be104c2f018"
    }
    pdf_md5 = {
        "eng": "f5d5e55a5041ef1435a0adc3a12d2263",
        "nld": "a44a1e5d0c23d1493e57fd93c66683d3",
        "fra": "6e3a4c2dd873cb84c2cea40db4a5d97e"
    }
    pdfs_md5 = {
        "eng": "03daba6ed1850964f2e372f63a7d1438",
        "nld": "ffff70fa984fc789fbd42881b9550fe1",
        "fra": "622f358887cfbab7023e74501c6c7348"
    }

    filename_with_metadata =  {
        "original_filename": "screenshot_loremipsum.png",
        "filename": "screenshot_loremipsum.png",
        "metadata": [
            {
                "key": "rights",
                "value": "CC-BY-4.0",
                "lang": "en",
            },
            {
                "key": "copyright",
                "value": "Inuits",
                "lang": "en",
            },
        ],
    }


    def setUp(self):
        app.testing = True
        self.app = app.test_client()
