import json
import re
import spacy
from thefuzz import process
from random import choice as random_choice

# Load NLP once globally
nlp = spacy.load("en_core_web_sm")

CODE_PATTERN = r"^[A-Z]\d{2}$"


class StaticData:
    def __init__(self):
        self._action_mapping = {}
        self._emotion_mapping = {}
        self._frame_mapping = {}

    def load_all(self):
        """Helper to load all JSON files at once"""
        self.get_action_mapping()
        self.get_emotion_mapping()
        self.get_frame_mapping()

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
        try:
            with open("core/data/action_mapping.json", "r", encoding="utf-8") as f:
                self._action_mapping = json.load(f)
        except FileNotFoundError:
            self._action_mapping = {}

    @property
    def action_mapping(self):
        if not self._action_mapping:
            self.get_action_mapping()
        return self._action_mapping

    def get_emotion_mapping(self):
        try:
            with open("core/data/emotion_mapping.json", "r", encoding="utf-8") as f:
                self._emotion_mapping = json.load(f)
        except FileNotFoundError:
            self._emotion_mapping = {}

    @property
    def emotion_mapping(self):
        if not self._emotion_mapping:
            self.get_emotion_mapping()
        return self._emotion_mapping


# Initialize static data
static_data = StaticData()
static_data.load_all()


def _get_code(user_input, mapping, threshold=75):
    raw_upper = str(user_input).strip().upper()
    clean_lower = raw_upper.lower()

    if not clean_lower:
        return None, f"Input '{user_input}' resulted in empty string"

    # 1. Regex Check (Direct Code)
    if re.match(CODE_PATTERN, raw_upper):
        return [raw_upper], "Matched as direct param code"

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


def _get_single_param_code(input_str, mapping, threshold=75):
    debug_list = []
    choice_list, debug = _get_code(input_str, mapping, threshold)
    debug_list.append(debug)

    if not choice_list:
        return None, debug_list

    choice = random_choice(choice_list)
    debug_list.append(f"Picked {choice} from {choice_list}")
    return choice, debug_list


class Params:
    def __init__(self):
        self.action = None
        self.emotion = None
        self.a_frames = None
        self.e_frames = None
        self.debugs = {}

    @property
    def param_str(self):
        parts = []
        if self.action:
            parts.append(f"action={self.action}.{{a_frame}}")
        if self.emotion:
            parts.append(f"emotion={self.emotion}.{{e_frame}}")
        return "?" + "&".join(parts) if parts else ""


class ParamBuilder:
    def __init__(self):
        self.params = Params()

    def build_action(self, user_input):
        choice, debug = _get_single_param_code(user_input, static_data.action_mapping)
        if choice:
            self.params.action = choice
            # Check frame mapping
            self.params.a_frames = static_data.frame_mapping.get(choice, [0])
        self.params.debugs["action"] = debug
        return self

    def build_emotion(self, user_input):
        choice, debug = _get_single_param_code(user_input, static_data.emotion_mapping)
        if choice:
            self.params.emotion = choice
            self.params.e_frames = static_data.frame_mapping.get(choice, [0])
        self.params.debugs["emotion"] = debug
        return self

    def compile(self):
        return self.params.param_str, self.params.a_frames, self.params.e_frames, self.params.debugs