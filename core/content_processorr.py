import json
import copy

import spacy
import re
from thefuzz import process
from random import choice as random_choice

nlp = spacy.load("en_core_web_sm")

CODE_PATTERN = r"^[A-Z]\d{2}$"

class Static_Data:
    def __init__(self):
        self._action_mapping: {str:[str]} = {}
        self._emotion_mapping: {str:[str]} = {}
        self._frame_mapping: {str:[int]} = {}

    def get_frame_mapping(self):
        with open("core/data/frame_data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            f.close()
        self._frame_mapping = data

    @property
    def frame_mapping(self):
        if not self._frame_mapping:
            self.get_frame_mapping()
        return self._frame_mapping

    def get_action_mapping(self):
        with open("core/data/action_mapping.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            f.close()
        self._action_mapping = data

    @property
    def action_mapping(self):
        if not self._action_mapping:
            self.get_action_mapping()
        return self._action_mapping

    def get_emotion_mapping(self):
        with open("core/data/emotion_mapping.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            f.close()
        self._emotion_mapping = data

    @property
    def emotion_mapping(self):
        if not self._emotion_mapping:
            self.get_emotion_mapping()
        return self._emotion_mapping

static_data = Static_Data()
static_data.get_param_code_data()

def pre_process_content(content:str):
    content = content.strip()
    split_string = content.split(" ")
    if len(split_string) == 1:
        return split_string[0], []
    return split_string[0], split_string[1:]

def parse_file_name(content:str,param:str):
    return f"{content}_{param[1:]}.gif"

def _get_code(user_input, mapping, threshold=75) -> ([str],str):
    """
    generic method to get list of param code based on user input
    TO USE the function get_action_code and get_emotion_code instead
    :param user_input:
    :param mapping: one of the static data dictionaries e.g. static_data.action_mapping
    :param threshold:
    :return: list of possible param codes e.g. [A01 , A02] and its debug message
    """
    raw_upper = str(user_input).strip().upper()
    clean_lower = raw_upper.lower()
    try:
        if not clean_lower:
            return None, f"input {user_input} is None after lowercase"

        # Regex Check
        if re.match(CODE_PATTERN, raw_upper): # TODO: remove and put as static data to handle F1 F2 etc
            return [raw_upper], f"matched as param code"

        # Lemmatization (Grammar Check)
        doc = nlp(clean_lower)
        lemma = doc[0].lemma_

        # Direct Lookup
        if lemma in mapping:
            return mapping[lemma], f"matched `{user_input}` with `{mapping[lemma]}` during direct lookup"

        # Fuzzy Lookup
        best_match, score = process.extractOne(lemma, mapping.keys())

        if score >= threshold:
            return mapping[best_match], f"matched `{user_input}` with `{best_match}` during fuzzy lookup"
        return None, f"input `{user_input}` not matched to static data"

    except Exception as e:
        return None, str(e)

def _get_single_param_code(input:str,static_data_mapping:dict,threshold=75):
    debug_list = []
    choice_list,debug = _get_code(input, static_data_mapping,threshold)
    debug_list.append(debug)
    if not choice_list or choice_list == []:
        debug_list.append(f"list is empty")
        return None, debug_list
    choice = random_choice(choice_list)
    debug_list.append(f"picked {choice} from {choice_list}")
    return choice, debug_list


class Params:
    def __init__(self):
        self.params = None
        self.debugs:{str:[str]} = {}

        self.action:str = None
        self.emotion:str = None
        self.a_frames:[int] = None
        self.e_frames:[int] = None

    @property
    def param_str(self) -> str:
        if not (self.action or self.emotion):
            self.debugs["parsing"] = "empty action and emotion"
            return ""
        str_list = []
        if self.action:
            self.debugs["parsing"] = "handle action"
            str_list.append(f"action={self.action}.{{a_frame}}")
        if self.emotion:
            self.debugs["parsing"] = "handle emotion"
            str_list.append(f"emotion={self.emotion}.{{e_frame}}")
        return "?" + "&".join(str_list)

class ParamBuilder:
    def __init__(self):
        self.params:Params = Params()

    def build_action(self,user_input:str):
        choice, debug = _get_single_param_code(user_input, static_data.action_mapping, threshold=75)
        if choice and choice in static_data.frame_mapping:
            self.a_frames = static_data.frame_mapping[choice]
            self.params.action = choice
        else:
            debug.append(f"choice of action {choice} is invalid")
        self.params.debugs["action"] = debug
        return self

    def build_emotion(self,user_input:str):
        choice, debug = _get_single_param_code(user_input, static_data.emotion_mapping, threshold=75)
        if choice and choice in static_data.frame_mapping:
            self.e_frames = static_data.frame_mapping[choice]
            self.params.emotion = choice
        else:
            debug.append(f"choice of emotion {choice} is invalid")
        self.params.debugs["emotion"] = debug
        return self
        # implement other param builder here

    def compile_params(self):
        # returns something like '?action=A13.{a_frame}&emotion=E02.{e_frame}'  [0, 1, 2] [0] with debug
        return self.params.param_str, self.params.a_frames, self.params.e_frames, self.params.debugs

def build_params(user_inputs:{str:str}):
    param = ParamBuilder()
    try:
        if "action" in user_inputs and user_inputs["action"]:
            param = param.build_action(user_inputs["action"])
        if "emotion" in user_inputs and user_inputs["emotion"]:
            param = param.build_emotion(user_inputs["emotion"])
        return param.compile_params()
    except Exception as e:
        param.params.debugs["exception"] = str(e)
        return None,None,None, param.params.debugs