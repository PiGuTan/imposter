import client
import asyncio

DEFINED_ITEMS = ["Face Acc.","Eye Acc.","Earring","Weapon","Hat","Top","Bottom","Cape","Glove","Shoes"]

class Beauty_item:
    def __init__(self, item_type:str, item_name:str):
        self.item_type = item_type
        self.item_name = item_name
        self.colour = None

    @classmethod
    def with_item_equipment(cls, data:dict):
        item = cls(data['item_equipment_slot'],data['item_shape_name'])
        return item

    @classmethod
    def with_cash_equipment(cls, data:dict):
        item = cls(data['cash_item_equipment_slot'],data['cash_item_name'])
        # what to do with colour
        return item

    @classmethod
    def with_beauty(cls,beauty_type, data:dict):
        item = cls(beauty_type,data[f'{beauty_type}_name'])
        if data['mix_color']:
            mix_amount = data['mix_rate']
            base_amount = 100-int(data['mix_rate'])
            item.colour = f"{base_amount}% {data['base_color']}, {mix_amount}% {data['mix_color']}"
        else:
            item.colour = data['base_color']
        return item

    @property
    def dict(self):
        return {
            'type': self.item_type,
            'name': self.item_name,
            **({'color': self.colour} if self.colour else {})
        }

    def __str__(self):
        print_items = [self.item_type, self.item_name]
        if self.colour:
            print_items.append(self.colour)
        return "|".join(print_items)

class Character:
    def __init__(self, character_name:str, date = None):
        self.character_name = character_name
        self.date = date
        self.data_agent = client.Data_Agent(character_name, date=date)
        self._ocid = ""
        self._image_url = ""
        self._image = None # processed image

        self._beauty_items: list[Beauty_item] = []
        self._temp_items = {}
        # flags for calling openapi will be true if they are successfully called
        self._beauty_call = False
        self._equip_call = False
        self._cash_call = False
        self._process_cash_item = False

    @property
    def ocid(self):
        self.get_ocid()
        return self._ocid

    def get_ocid(self):
        self._ocid = self.data_agent.ocid

    @property
    def image_url(self):
        if not self._image_url:
            self.get_ocid()
            if not self._ocid:
                return ""
            resp_dict = self.data_agent.get_basic_info()
            self._image_url = resp_dict["character_image"]
        return self._image_url

    def fill_beauty_details(self,data:dict):
        if not data or data == {}:
            return
        hair = data["additional_character_hair"] if data["additional_character_hair"] else data["character_hair"]
        hair_item = Beauty_item.with_beauty("hair", hair)
        self._beauty_items.append(hair_item)
        face = data["additional_character_face"] if data["additional_character_face"] else data["character_face"]
        face_item = Beauty_item.with_beauty("face", face)
        self._beauty_items.append(face_item)

    def fill_temp_item_details(self,data:dict):
        if not data or data == {}:
            return
        if data["preset_no"]:
            preset = data["preset_no"]
            items = data[f"item_equipment_preset_{preset}"]
        else:
            items = data["item_equipment"]
        for item_data in items:
            if item_data["item_equipment_slot"] not in DEFINED_ITEMS:
                continue
            self._temp_items[item_data["item_equipment_slot"]] = Beauty_item.with_item_equipment(item_data)

    def fill_cash_details(self,data:dict):
        if not data or data == {}:
            return
        if int(data["character_look_mode"]) == 1: # ab handling
            prefix = "additional_"
        else:
            prefix = ""

        items = data[f"{prefix}cash_item_equipment_base"]
        if data["preset_no"]:
            preset = data["preset_no"]
            # only zero (beta) uses additional preset
            items += data[f"cash_item_equipment_preset_{preset}"]

        for item_data in items:
            if item_data["cash_item_equipment_slot"] not in DEFINED_ITEMS:
                continue

            self._temp_items[item_data["cash_item_equipment_slot"]] = Beauty_item.with_cash_equipment(item_data)
            if item_data["cash_item_equipment_part"] == "Overall" and "Bottom" in self._temp_items:
                del self._temp_items["Bottom"]
            self._process_cash_item = True

    def merge_temp_items(self):
        # print(self._temp_items)
        for item in self._temp_items.values():
            self._beauty_items.append(item)

    @property
    def temp_items_debug(self):
        if not self._temp_items or self._temp_items == {}:
            return {}
        debug_dict = {}
        for key, value in self._temp_items.items():
            debug_dict[key] = str(value)
        return debug_dict

    async def get_all_beauty_items(self):
        # Unpack the results from the gather call
        results = await asyncio.gather(
            self.data_agent.get_beauty(),
            self.data_agent.get_item(),
            self.data_agent.get_cash_item(),
            return_exceptions=True
        )

        beauty_data, item_data, cash_data = results

        try:
            self.fill_beauty_details(beauty_data)

            self.fill_temp_item_details(item_data)
            # print(self.temp_items_debug)
            self.fill_cash_details(cash_data)
            # print(self.temp_items_debug)
            if self._process_cash_item:
                self.merge_temp_items()
            return self._beauty_items
        except Exception as e:
            return self._beauty_items

    @property
    def beauty_items(self):
        # should be used after await get_all_beauty_items
        items = []
        for item in self._beauty_items:
            items.append(item.dict)
        return items
