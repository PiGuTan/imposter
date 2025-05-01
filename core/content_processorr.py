import json
import copy

A_FLAG = 1
E_FLAG = 2
W_FLAG = 4

class Param_code:
    def __init__(self,name:str,param_code:str,data:dict):
        self.name = name
        self.param_code = param_code
        self.frames = data["frames"] if "frames" in data else []
        self.flag = (A_FLAG*(param_code[0] == "A")
                     + E_FLAG*(param_code[0] == "E")
                     + W_FLAG*(param_code[0] == "W"))

    def reset_name(self,name:str):
        self.name = name

    @property
    def parsed_param(self):
        match self.flag:
            case 1: #for some reason IDE throw warning if use A_FLAG
                return f"action={self.param_code}"+".{a_frame}" if len(self.frames) else ""
            case 2:
                return f"emotion={self.param_code}"+".{e_frame}" if len(self.frames) else ""
            case 4:
                return f"wmotion={self.param_code}"+""
            case _:
                return f"{self.name}={self.param_code}" # anyhow implement


class Static_Data:
    def __init__(self):
        self._param_codes: {str:Param_code} = {}
        self._custom_flag = {}
    def get_param_code_data(self):
        with open("core/data/param_code.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            f.close()

        for param_code in data.keys():
            value = data[param_code]
            for used_name in value["used_names"]:
                if used_name in self._param_codes:
                    continue
                self._param_codes[used_name.lower()] = Param_code(used_name,param_code,value)

    @property
    def param_codes(self) -> {str:Param_code}:
        if not self._param_codes:
            self.get_param_code_data()
        return self._param_codes

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

def process_split_string(split_strings: list[str]):
    a_frames = None
    e_frames = None
    found_flags = 0
    unused_strings: list[str] = [] # will I use this?
    used_params:list[Param_code] = []
    for split_string in split_strings:
        if split_string.lower() in static_data.param_codes:
            used_param=copy.deepcopy(static_data.param_codes[split_string.lower()])
            if not (found_flags & used_param.flag):
                found_flags |= used_param.flag
                used_param.reset_name(split_string)
                match used_param.flag:
                    case 1:
                        a_frames = used_param.frames
                    case 2:
                        e_frames = used_param.frames
                    case _:
                        pass
                used_params.append(used_param)
                continue
        unused_strings.append(split_string)
    """
    implemtnat other flags
    """

    return "?"+"&".join([s.parsed_param for s in used_params]), a_frames, e_frames #," ".join(unused_strings)











