import client
import asyncio

# TODO: move to another module
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

class Character:
    def __init__(self, character_name:str, date = None):
        self.character_name = character_name
        self.date = date
        self.data_agent = client.Data_Agent(character_name, date=date)
        self._ocid = ""
        self._image_url = ""
        self._image = None # processed image

    @property
    def ocid(self):
        self.get_ocid()
        return self._ocid

    def get_ocid(self):
        if not self._ocid:
            resp_dict = self.data_agent.get_ocid()
            # add logic to check for captitalisation?
            if "ocid" not in resp_dict:
                return

            self._ocid = resp_dict["ocid"]
            self.data_agent.set_ocid(self._ocid)

    def find_ocid(self):
        if self._ocid:
            return

        possible_names:{str} = uppercase_combo(self.character_name)
        tasks = []
        loop = asyncio.get_event_loop()

        for name in possible_names:
            find_name = client.Data_Agent(name, date=self.date)
            task = asyncio.create_task(find_name.get_ocid())
            tasks.append(task)
        asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
        # https://stackoverflow.com/questions/42231161/asyncio-gather-vs-asyncio-wait-vs-asyncio-taskgroup


        print("Get first result:")
        finished, unfinished = loop.run_until_complete(
            asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED))


    @property
    def image_url(self):
        if not self._image_url:
            self.get_ocid()
            if not self._ocid:
                return ""
            resp_dict = self.data_agent.get_basic_info()
            self._image_url = resp_dict["character_image"]
        return self._image_url


