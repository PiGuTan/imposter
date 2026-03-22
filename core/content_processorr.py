import json
import spacy
from thefuzz import process
from random import choice as random_choice
from dataclasses import dataclass, field
from typing import List, Optional, Dict

# Load NLP once globally
nlp = spacy.load("en_core_web_sm")

CODE_PATTERN = r"^[A-Z]\d{2}$"

@dataclass
class Special_mapping:
    action: dict
    emotion: dict

class StaticData:
    def __init__(self):
        self._action_mapping: {str:[str]} = {}
        self._emotion_mapping: {str:[str]} = {}
        self._frame_mapping: {str:[int]} = {}

        self._special_mapping: Special_mapping | None = None

    def load_all(self):
        """Helper to load all JSON files at once"""
        self.get_action_mapping()
        self.get_emotion_mapping()
        self.get_frame_mapping()
        self.get_special_mapping()

    def get_frame_mapping(self):
        try:
            with open("core/data/frame_data.json", "r", encoding="utf-8") as f:
                self._frame_mapping = json.load(f)
        except FileNotFoundError:
            self._frame_mapping = {}

    @property
    def frame_mapping(self):
        if not self._frame_mapping:
            self.get_frame_mapping()
        return self._frame_mapping

    def get_action_mapping(self):
        with open("core/data/action_mapping.json", "r", encoding="utf-8") as f:
            self._action_mapping = json.load(f)

    @property
    def action_mapping(self):
        if not self._action_mapping:
            self.get_action_mapping()
        return self._action_mapping

    def get_emotion_mapping(self):
        with open("core/data/emotion_mapping.json", "r", encoding="utf-8") as f:
            self._emotion_mapping = json.load(f)

    @property
    def emotion_mapping(self):
        if not self._emotion_mapping:
            self.get_emotion_mapping()
        return self._emotion_mapping

    def get_special_mapping(self):
        try:
            with open("core/data/special_mapping.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                self._special_mapping = Special_mapping(data["actions"], data["emotions"])
        except FileNotFoundError:
            self._special_mapping = {}

    def special_mapping(self):
        if not self._special_mapping:
            self.get_special_mapping()
        return self._special_mapping


static_data = StaticData()
static_data.load_all()


def _get_code(user_input, mapping, special_map, threshold=75):
    raw_upper = str(user_input).strip().upper()
    clean_lower = raw_upper.lower()

    if not clean_lower:
        return None, f"Input '{user_input}' resulted in empty string"

    # 1. Regex Check (Direct Code)
    if clean_lower in special_map:
        mapped_code = special_map[clean_lower]
        return mapped_code, f"Matched {clean_lower} to {mapped_code} as direct param code"

    # 2. Lemmatization
    doc = nlp(clean_lower)
    lemma = doc[0].lemma_

    # 3. Direct Lookup
    if lemma in mapping:
        return mapping[lemma], f"Direct match: '{lemma}'"

    # 4. Fuzzy Lookup
    best_match, score = process.extractOne(lemma, mapping.keys())
    if score >= threshold:
        return mapping[best_match], f"Fuzzy match: '{best_match}' (score: {score})"

    return None, f"No match found for '{user_input}'"


def _get_single_param_code(input_str, mapping, special_map, threshold=75):
    debug_list = []
    choice_list, debug = _get_code(input_str, mapping, special_map, threshold)
    debug_list.append(debug)

    if not choice_list:
        return None, debug_list

    choice = random_choice(choice_list)
    debug_list.append(f"Picked {choice} from {choice_list}")
    return choice, debug_list


@dataclass
class Params:
    # Basic attributes with types
    action: Optional[str] = None
    emotion: Optional[str] = None

    # Lists require a default_factory to avoid mutable default errors
    a_frames: List[int] = field(default_factory=list)
    e_frames: List[int] = field(default_factory=list)

    # Dictionary for debugging logs
    debugs: Dict[str, List[str]] = field(default_factory=dict)

    @property
    def param_str(self) -> str:
        str_list = []
        if self.action:
            str_list.append(f"action={self.action}.{{a_frame}}")
        if self.emotion:
            str_list.append(f"emotion={self.emotion}.{{e_frame}}")

        return "?" + "&".join(str_list) if str_list else ""


class ParamBuilder:
    def __init__(self):
        self.params: Params = Params()

    def build_action(self, user_input: str) -> "ParamBuilder":
        choice, debug = _get_single_param_code(user_input, static_data.action_mapping, static_data.special_mapping.action)

        if choice:
            self.params.action = choice
            # Using .get() ensures we don't crash if the code is missing in frame_data
            self.params.a_frames = static_data.frame_mapping.get(choice, [])

        self.params.debugs["action"] = debug
        return self

    def build_emotion(self, user_input: str) -> "ParamBuilder":
        choice, debug = _get_single_param_code(user_input, static_data.emotion_mapping)

        if choice:
            self.params.emotion = choice
            self.params.e_frames = static_data.frame_mapping.get(choice, [])

        self.params.debugs["emotion"] = debug
        return self

    def compile_params(self):
        # Returns the final state for the API or Controller
        return (
            self.params.param_str,
            self.params.a_frames,
            self.params.e_frames,
            self.params.debugs
        )

def build_params(action=None, emotion=None):
    builder = ParamBuilder()

    query_string, a_frames, e_frames, debugs = (
        builder
        .build_action(action)
        .build_emotion(emotion)
        .compile_params()
    )
    return query_string, a_frames, e_frames, debugs

def parse_file_name(content:str,param:str):
    return f"{content}_{param[1:]}.gif"