import requests
import unittest
from common.config import *
from common.common_api import *


class GetAccessTokenCases(unittest.TestCase):


    def setUp(self) ->None:
        self.hosts = config.URL
        self.session = requests.session()

    def tearDown(self)->None:
        pass

    def test_get_access_token_api(self):

        actual_result = get_access_token_api(self.session,
                            'client_credential',
                            'wx91b4a00dbb9f828d'
                            , 'f5d2dc18178fac284c135c9e3df0ec5b',
                                             ''
                            )
        self.assertEqual(actual_result.json()['errcode'],40164)

    def test_get_access_token(self):
        # logger.info('[case1] 正常获取 access_token接口：test_get_access_token')
        get_params = {

        }
        headers = {
            "Content-Type": "application/json"
        }
        post_params = {
            "email": "peter@klaven",
            "password": "cityslicka"
        }
        actual_result = self.session.get(url=self.hosts + '/api/login',
                            json=post_params,
                            headers=headers
                            , params=get_params
                            )
        self.assertEqual(actual_result.status_code,200)


    def test_password_error(self):
        # logger.info('[case1] 正常获取 access_token异常：test_password_error')
        get_params = {

        }
        headers = {
            "Content-Type": "application/json"
        }
        post_params = {
            "email": "peter@klaven",
            "password": "cityslic1ka"
        }
        actual_result = self.session.get(url=self.hosts + '/api/login',
                                     json=post_params,
                                     headers=headers
                                     , params=get_params
                                     )
        self.assertEqual(actual_result.status_code, 300)


if __name__ == '__main__':
    unittest.main()