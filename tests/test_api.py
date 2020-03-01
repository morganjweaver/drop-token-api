from unittest import TestCase
from api import api


class DropTokenTestCase(TestCase):
    def setUp(self):
        api.app.config["TESTING"] = True
        self.api = api.app.test_client()

    def tearDown(self):
        api.app.config["TESTING"] = False

    def test_valid_request(self):
        response = self.api.get("/drop_token")
        self.assertEqual(response.status, 200)
        assert b"2740bbc" in response.data

    def test_invalid_request(self):
        response = self.api.get("/drop_token/meow")
        self.assertEqual(response.status, 404)

