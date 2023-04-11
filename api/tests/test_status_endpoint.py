from tests.base_case import BaseCase


class StatusEndpointTest(BaseCase):
    def test_status_endpoint_get(self):
        response = self.app.get(
            f"/status", headers={"content-type": "multipart/form-data"}
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual("text/plain", response.mimetype)
        self.assertEqual(
            "tesseract 4.1.1 available\npytesseract 0.3.10 available",
            response.get_data(as_text=True),
        )
