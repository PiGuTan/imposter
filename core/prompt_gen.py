import json
from contextlib import suppress

class StaticData:
    def __init__(self):
        with open("core/data/prompt_template.txt", 'r', encoding='utf-8') as f:
            self.template = f.read()
        with open("core/data/prompt_template.json") as f:
            data = json.load(f)
        self.pose_and_action_header = data["pose_and_action_header"]
        self.equipment_manifest_header = data["equipment_manifest_header"]

static_data = StaticData()

class Prompt:
    def __init__(self):
        self.template = static_data.template

        self.pose_and_action_header = static_data.pose_and_action_header
        self.pose_and_action:str = ""
        self.equipment_manifest_header = static_data.equipment_manifest_header
        self.equipment_manifest:str = ""

        self.prompt_detail = [self.template]

    @property
    def full_prompt(self):
        prompt_detail = "\n\n".join(self.prompt_detail)
        return f"```\n{prompt_detail}\n```"


class PromptBuilder:
    def __init__(self):
        self.prompt:Prompt = Prompt()
        self.beauty_list:list = []

    def build_pose_and_action(self,action:str=None,expression:str=None):
        if not (action or expression):
            return self
        pose_and_action_list = [self.prompt.pose_and_action_header]
        if action:
            action = f"Action: {action}"
            pose_and_action_list.append(action)
        if expression:
            expression = f"Expression: {expression}"
            pose_and_action_list.append(expression)
        self.prompt.pose_and_action = "\n1. ".join(pose_and_action_list)
        self.prompt.prompt_detail.append(self.prompt.pose_and_action)
        return self

    def build_face_hair(self,beauty_items:dict=None):
        """part of build equipent manifest"""
        if "hair" in beauty_items:
            hair = beauty_items["hair"]["name"]
            color = beauty_items["hair"]["color"]
            self.beauty_list.append(f"Hair: {hair} with {color}")
        if "face" in beauty_items:
            face = beauty_items["face"]["name"]
            color = beauty_items["face"]["color"]
            self.beauty_list.append(f"Face: {face} with {color}")

    def build_hat(self,beauty_items:dict=None):
        """part of build equipment manifest"""
        if "Hat" in beauty_items:
            hat = beauty_items["Hat"]["name"]
            self.beauty_list.append(f"Headwear: {hat}")

    def build_outfit(self,beauty_items:dict=None):
        """part of build equipment manifest"""
        outfit = []
        if "Top" in beauty_items:
            top = beauty_items["Top"]["name"]
            outfit.append(top)
        if "Bottom" in beauty_items:
            bottom = beauty_items["Bottom"]["name"]
            outfit.append(bottom)
        if "Cape" in beauty_items:
            cape = beauty_items["Cape"]["name"]
            outfit.append(cape)
        if "Glove" in beauty_items:
            glove = beauty_items["Glove"]["name"]
            outfit.append(glove)
        if outfit and len(outfit) > 0:
            self.beauty_list.append(f"Outfit: {",".join(outfit)}")

    def build_accessories(self,beauty_items:dict=None):
        """part of build equipment manifest"""
        accessories = []
        if "Face Acc." in beauty_items:
            face = beauty_items["Face Acc."]["name"]
            accessories.append(face)
        if "Eye Acc." in beauty_items:
            eye = beauty_items["Eye Acc."]["name"]
            accessories.append(eye)
        if "Earring" in beauty_items:
            earring = beauty_items["Earring"]["name"]
            accessories.append(earring)
        if accessories and len(accessories)>0:
            self.beauty_list.append(f"Accessories: {",".join(accessories)}")

    def build_footwear(self,beauty_items:dict=None):
        """part of build equipment manifest"""
        if "Shoes" in beauty_items:
            shoes = beauty_items["Shoes"]["name"]
            self.beauty_list.append(f"Footwear: {shoes}")

    def build_weapon(self,beauty_items:dict=None):
        """part of build equipment manifest"""
        if "Weapon" in beauty_items:
            weapon = beauty_items["Weapon"]["name"]
            self.beauty_list.append(f"Weapon: {weapon}")

    def build_equipment_manifest(self,beauty_items:dict=None):
        if not beauty_items or beauty_items == {}:
            return self
        self.beauty_list = [self.prompt.equipment_manifest_header]

        self.build_face_hair(beauty_items)
        self.build_hat(beauty_items)
        self.build_outfit(beauty_items)
        self.build_accessories(beauty_items)
        self.build_footwear(beauty_items)
        self.build_weapon(beauty_items)

        self.prompt.equipment_manifest = "\n".join(self.beauty_list)
        self.prompt.prompt_detail.append(self.prompt.equipment_manifest)
        return self


def build_prompt(beauty_items,a_param="A00",e_param="E00") -> str:
    prompt_builder = PromptBuilder()
    with suppress(KeyError):
        prompt_builder.build_pose_and_action(action = a_param, expression = e_param)
        prompt_builder.build_equipment_manifest(beauty_items)
    return prompt_builder.prompt.full_prompt

