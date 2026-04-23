import client
import asyncio
import json
import util

class Static_data:
    def __init__(self):
        with open("core/data/item_prompt.json") as f:
            data = json.load(f)
            self.item_prompt:str = data["item_description"]
            self.defined_items:list[str] = data["defined_items"]
            self.description_required_items:list[str] = data["description_required_items"]

static_data = Static_data()

class Beauty_item:
    def __init__(self, item_type:str, item_name:str,item_url:str=None):
        self.item_type = item_type
        self.item_name = item_name
        self.item_url = item_url
        self.description = None
        self.colour = None

    @classmethod
    def with_item_equipment(cls, data:dict,is_description_needed:bool=False):
        url = data["item_shape_icon"] if is_description_needed else None
        item = cls(data['item_equipment_slot'],data['item_shape_name'],url)
        return item

    @classmethod
    def with_cash_equipment(cls, data:dict,is_description_needed:bool=False):
        url = data["cash_item_icon"] if is_description_needed else None
        item = cls(data['cash_item_equipment_slot'],data['cash_item_name'],url)
        # what to do with colour
        return item

    @classmethod
    def with_beauty(cls,beauty_type, data:dict):
        item = cls(beauty_type,data[f'{beauty_type}_name'])
        # if data['mix_color']:
        #     mix_amount = data['mix_rate']
        #     base_amount = 100-int(data['mix_rate'])
        #     item.colour = f"{base_amount}% {data['base_color']}, {mix_amount}% {data['mix_color']}"
        # else:
        #     item.colour = data['base_color']
        return item

    @property
    def dict(self):
        return {
            'type': self.item_type,
            'name': self.description if self.description else self.item_name,
        }

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
            if item_data["item_equipment_slot"] not in static_data.defined_items:
                continue
            is_description_needed = item_data["item_equipment_slot"] in static_data.description_required_items
            self._temp_items[item_data["item_equipment_slot"]] = Beauty_item.with_item_equipment(item_data,is_description_needed)

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
            if item_data["cash_item_equipment_slot"] not in static_data.defined_items:
                continue
            is_description_needed = item_data["cash_item_equipment_slot"] in static_data.description_required_items
            self._temp_items[item_data["cash_item_equipment_slot"]] = Beauty_item.with_cash_equipment(item_data,is_description_needed)
            if item_data["cash_item_equipment_part"] == "Overall" and "Bottom" in self._temp_items:
                del self._temp_items["Bottom"]
            self._process_cash_item = True

    def merge_temp_items(self):
        for item in self._temp_items.values():
            self._beauty_items.append(item)

    async def _process_single_item(self, item):
        agent = client.Gemini_agent()
        prompt = static_data.item_prompt.format(item_name=item.item_name)
        agent.set_prompt(item.item_url,prompt)
        try:
            await agent.generate()
            description, _ = agent.get_response_data()
            item.description = description
        except Exception as e:
            #dont need to fail
            item.description = ""
            util.bot_logger.error(f"error={e}", result="process_single_item_error")

    async def post_process_beauty_items(self):
        self._beauty_items = [i for i in self._beauty_items if "Transparent" not in i.item_name]

        tasks = [
            self._process_single_item(item)
            for item in self._beauty_items if item.item_url
        ]

        await asyncio.gather(*tasks)

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
            self.fill_cash_details(cash_data)
            if self._process_cash_item:
                self.merge_temp_items()

            await self.post_process_beauty_items()

            return self._beauty_items
        except Exception as e:
            util.bot_logger.error(f"error={e}", result="get_all_beauty_item_error")
            return self._beauty_items

    @property
    def beauty_items(self):
        # should be used after await get_all_beauty_items
        items = {}
        for item in self._beauty_items:
            items[item.dict["type"]]=item.dict
        return items
