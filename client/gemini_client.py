import io
import os
from google import genai
from google.genai import types

client = genai.Client(api_key=os.getenv('GEMINI_TOKEN'))
text_model = "gemini-2.5-flash"
image_model = "gemini-2.5-flash-image"

class Gemini_agent:
    def __init__(self,require_image = False):
        if require_image:
            self.model = image_model
            self.config = types.GenerateContentConfig(
                response_modalities=["IMAGE"],
                image_config=types.ImageConfig(aspect_ratio="9:16")
            )
        else:
            self.model = text_model
            self.config = types.GenerateContentConfig(
                response_modalities=["TEXT"],
            )
        self._contents = []
        self.response = None

    def set_prompt(self, *prompt):
        if not prompt:
            return
        self._contents = prompt

    async def generate(self):
        if self._contents is None:
            return
        try:
            self.response = await client.aio.models.generate_content(
                model=self.model,
                contents=self._contents,
                config=self.config
            )
        except Exception as e:
            print(f"Error: {e}")

    def get_response_data(self):
        if len(self._contents) == 0:
            return "",None
        text_out = ""
        image_bytes = None

        for part in self.response.candidates[0].content.parts:
            if part.text:
                text_out += part.text
            if part.inline_data:
                image_bytes = io.BytesIO(part.inline_data.data)

        return text_out, image_bytes