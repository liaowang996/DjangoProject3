import requests
import unittest
from common import config



class TestCreateTag(unittest.TestCase):


    def setUp(self):
        self.hosts = config.URL
        self.session = requests.session()
    def tearDown(self):
        pass

    def test_api_register(self):
        get_params = {

        }
        headers = {
            "Content-Type": "application/json"
        }
        post_params = {
            "email": "peter@klaven",
            "password": "cityslicka"
        }
        actual_result = self.session.get(url=self.hosts + '/api/register',
                                     json=post_params,
                                     headers=headers
                                     , params=get_params
                                     )
        self.assertEqual(actual_result.status_code, 200)

    def test_api_register(self):
        get_params = {

        }
        headers = {
            "Content-Type": "application/json"
        }
        post_params = {
            "email": "peter@klaven",
            "password": "cityslicka"
        }
        actual_result = requests.get(url=self.hosts + '/api/register',
                                     json=post_params,
                                     headers=headers
                                     , params=get_params
                                     )
        self.assertEqual(actual_result.status_code, 200)

if __name__ == '__main__':
    unittest.main()