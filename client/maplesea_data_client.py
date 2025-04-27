import requests
import json
import os
import logging
from dotenv import load_dotenv

host = "https://open.api.nexon.com/"

load_dotenv()
headers = {
    "x-nxopen-api-key": os.getenv('OPENAPI_TOKEN'),
}

class Data_Agent:
    def __init__(self, character_name: str, date: str = None):
        self.character_name = character_name
        self.resp_dict = {}
        self.resp_headers = {}
        self.ocid = ""

        self.call_stack = {}

        # uncommon params
        self.date = date

    def _call_openapi(self, endpoint: str = None, params=None):
        url = host + endpoint
        if not params:
            logging.error(f"params is empty %s", self.call_stack)
            return {}
        if not endpoint:
            logging.error(f"endpoint is empty %s", self.call_stack)
            return {}


        response = requests.request("GET", url, headers=headers, data={}, params=params)

        if response.status_code != 200:
            logging.error(response.status_code)
            return {}

        self.resp_headers = response.headers
        self.call_stack[endpoint] = self.resp_headers["x-request-id"]
        if not self.resp_headers.get('Content-Type').__contains__('application/json'):
            self.resp_dict = {}
        else:
            self.resp_dict = json.loads(response.text)
        return self.resp_dict

    def set_ocid(self, ocid):
        self.ocid = ocid

    def get_ocid(self):
        param = {
            "character_name": self.character_name,
        }
        return self._call_openapi(endpoint="maplestorysea/v1/id", params=param)

    def get_basic_info(self):
        param = {
            "ocid": self.ocid,
        }
        if self.date:
            param["date"] = self.date
        return self._call_openapi(endpoint="maplestorysea/v1/character/basic", params=param)
