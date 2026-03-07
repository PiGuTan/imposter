import asyncio
import json
import math

from copy import copy

import requests


def uppercase_combo(check_string:str)-> {str}:
    check_string = check_string.lower()
    all_combo = set()
    for i in range(0,2**len(check_string)):
        all_combo.add(uppercase_single(check_string,i))
    return all_combo

def uppercase_single(check_string:str, position:int)-> str:
    check_string_new = ""
    count = 1
    for i in check_string:
        if count & position:
            check_string_new += i.upper()
        else:
            check_string_new += i
        count *= 2
    return check_string_new

async def get_ocid(name:str):
    url = "https://open.api.nexon.com/maplestorysea/v1/id?character_name=%s" % name

    payload = {}
    headers = {
      'accept': 'application/json',
      'x-nxopen-api-key': 'test_d2adeb5393c349343b87a2a35faaec948fc8cd112c137789874088fe38de859eefe8d04e6d233bd35cf2fabdeb93fb0d'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    resp_dict = json.loads(response.text)
    if "ocid" in resp_dict:
        return resp_dict["ocid"]
    else:
        return None

def run_till_get(function, inputs:list):
    tasks = []
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    for i in inputs:
        task = function(i)
        tasks.append(task)
    finished, unfinished = loop.run_until_complete(
        asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED))
    while len(unfinished) > 0:
        for task in finished:
            if task.result():
                for unfinished_task in unfinished:
                    unfinished_task.cancel()
                return task.result()
        finished, unfinished = loop.run_until_complete(
            asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED))
    return None





if __name__ == "__main__":
    check = "xaih"
    possibilities = uppercase_combo(check)
    output = run_till_get(get_ocid, possibilities)
    print(output)
