from tests.base_case import BaseCase


class OcrValidationRulesTest(BaseCase):
    def test_without_operation_post(self):
        response = self.app.post(
            f"/ocr",
            json={"mediafile_id": ["12345"]},
            headers={"content-type": "application/json"},
        )
        self.assertEqual(405, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertIn(
            "Malformed request body. Mandatory fieds: ['mediafile_id', 'operation']",
            response.get_data(as_text=True),
        )

    def test_without_mediafile_post(self):
        response = self.app.post(
            f"/ocr",
            json={"operation": "txt"},
            headers={"content-type": "application/json"},
        )
        self.assertEqual(405, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertIn(
            "Malformed request body. Mandatory fieds: ['mediafile_id', 'operation']",
            response.get_data(as_text=True),
        )

    def test_with_wrong_operation_post(self):
        response = self.app.post(
            f"/ocr",
            json={"mediafile_id": ["12345"], "operation": "txtt"},
            headers={"content-type": "application/json"},
        )
        self.assertEqual(405, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertIn(
            "Invalid operation. Possible operations are ['txt', 'alto', 'pdf']",
            response.get_data(as_text=True),
        )

    def test_with_invalid_mediafile1_post(self):
        response = self.app.post(
            f"/ocr",
            json={"mediafile_id": "12345", "operation": "txt"},
            headers={"content-type": "application/json"},
        )
        self.assertEqual(400, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertIn(
            "Malformed request body. Send the image id(s) in an array",
            response.get_data(as_text=True),
        )

    def test_with_invalid_mediafile2_post(self):
        response = self.app.post(
            f"/ocr",
            json={"mediafile_id": [], "operation": "txt"},
            headers={"content-type": "application/json"},
        )
        self.assertEqual(400, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertIn(
            "Malformed request body. You forgot to give a mediafile id",
            response.get_data(as_text=True),
        )

    def test_with_invalid_mediafile3_post(self):
        response = self.app.post(
            f"/ocr",
            json={"mediafile_id": [""], "operation": "txt"},
            headers={"content-type": "application/json"},
        )
        self.assertEqual(400, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertIn(
            "Malformed request body. You cannot give an empty mediafile id",
            response.get_data(as_text=True),
        )

    def test_with_multiple_mediafiles_with_txt_post(self):
        response = self.app.post(
            f"/ocr",
            json={"mediafile_id": ["12345", "12345"], "operation": "txt"},
            headers={"content-type": "application/json"},
        )
        self.assertEqual(400, response.status_code)
        self.assertEqual("application/json", response.mimetype)
        self.assertIn(
            "You can only send 1 image id for the [txt] operation. Images received: 2",
            response.get_data(as_text=True),
        )
