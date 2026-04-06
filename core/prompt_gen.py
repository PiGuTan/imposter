import json
from contextlib import suppress

class StaticData:
    def __init__(self):
        with open("core/data/prompt_template.json") as f:
            templates = json.load(f)
        self.user_instruction_header:str = templates["user_instruction_header"]
        self.user_instruction:str = templates["user_instruction"]
        self.task_header:str = templates["task_header"]
        self.task:str = templates["task"]
        self.metadata_header:str = templates["metadata_header"]
        self.other_instruction_header:str = templates["other_instruction_header"]

static_data = StaticData()

class Prompt:
    def __init__(self):
        self.user_instruction_prompt:str = ""
        self.task_prompt:str = ""
        self.metadata_prompt:str = ""
        self.other_instructions: list[str] = []

        self.prompt_detail = []

    @property
    def full_prompt(self):

        return "\n".join(self.prompt_detail)


class PromptBuilder:
    def __init__(self):
        self.prompt:Prompt = Prompt()

    def build_user_instruction_prompt(self) -> "PromptBuilder":
        self.prompt.user_instruction_prompt = static_data.user_instruction
        self.prompt.prompt_detail += [static_data.user_instruction_header, self.prompt.user_instruction_prompt]
        return self
    def build_task_prompt(self, style, proportions) -> "PromptBuilder":
        self.prompt.task_prompt = static_data.task.format(style=style, proportions=proportions)
        self.prompt.prompt_detail += [static_data.task_header, self.prompt.task_prompt]
        return self
    def build_metadata_prompt(self, beauty_items) -> "PromptBuilder":

        pass #how am I supposed to do this?
        metadata = ""
        self.prompt.prompt_detail += [static_data.metadata_header, metadata]
        return self
    def build_other_instruction_prompt(self,other_instructions:str) -> "PromptBuilder":
        if not other_instructions:
            return self
        self.prompt.other_instructions = other_instructions.split(";")
        self.prompt.prompt_detail += [static_data.other_instruction_header,*self.prompt.other_instructions]
        return self


def build_prompt(style,proportions,beauty_items,other_instructions) -> str:
    prompt_builder = PromptBuilder()
    with suppress(KeyError):
        prompt_builder.build_user_instruction_prompt()
        prompt_builder.build_task_prompt(style,proportions)
        prompt_builder.build_metadata_prompt(beauty_items)
        prompt_builder.build_other_instruction_prompt(other_instructions)
    return prompt_builder.prompt.full_prompt

