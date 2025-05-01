import client

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
            if "ocid" not in resp_dict:
                return
            self._ocid = resp_dict["ocid"]
            self.data_agent.set_ocid(self._ocid)


    @property
    def image_url(self):
        if not self._image_url:
            self.get_ocid()
            if not self._ocid:
                return ""
            resp_dict = self.data_agent.get_basic_info()
            self._image_url = resp_dict["character_image"]
        return self._image_url


