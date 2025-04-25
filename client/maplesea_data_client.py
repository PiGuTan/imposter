import requests
import json
import os
import logging

host = "https://open.api.nexon.com/"

headers = {
  "x-nxopen-api-key": os.getenv('OPENAPI_TOKEN'),
}

handler = logging.FileHandler(filename='client.log', encoding='utf-8', mode='w')

class Data_Agent:
  def __init__(self, character_name:str, date:str=None):
      self.character_name = character_name
      self.resp_dict = {}
      self.resp_headers = {}

      self.call_stack = {}

      # uncommon params
      self.date = date

  def _call_openapi(self, endpoint:str=None,params=None):
    url = host + endpoint
    if not params:
      logging.error(f"params is empty %s",self.call_stack)
      return {}
    if not endpoint:
      logging.error(f"endpoint is empty %s",self.call_stack)
      return {}
    response = requests.request("GET", url, headers=headers, data={}, params=params)

    pass #handle for non 200 code

    self.resp_headers = response.headers
    self.call_stack[endpoint] = self.resp_headers["x-request-id"]
    if self.resp_headers.get('content-type') != 'application/json':
      self.resp_dict = {}
    else:
      self.resp_dict = json.loads(response.text)
    return self.resp_dict


