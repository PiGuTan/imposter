import io
import os
from google import genai
from google.genai import types

import util

client = genai.Client(api_key=os.getenv('GEMINI_TOKEN'))
text_model = "gemini-2.5-flash"
image_model = "gemini-2.5-flash-image"

def get_url_metadata(candidates):
    metadata = getattr(candidates, "url_context_metadata", None)

    if metadata and getattr(metadata, "url_metadata", None):
        for item in metadata.url_metadata:
            return f"url={item.retrieved_url},status={item.url_retrieval_status}"
    else:
        return f"url was unused in this response"


class Gemini_agent:
    def __init__(self,require_image = False):
        if require_image:
            self.model = image_model
            self.config = types.GenerateContentConfig(
                response_modalities=["IMAGE"],
                image_config=types.ImageConfig(aspect_ratio="9:16"),
                tools=[types.Tool(url_context=types.UrlContext())]
            )
        else:
            self.model = text_model
            self.config = types.GenerateContentConfig(
                response_modalities=["TEXT"],
                tools=[types.Tool(url_context=types.UrlContext())]
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
            util.bot_logger.error(f"error={e}", result="gemini_error")

    def get_response_data(self):
        if len(self._contents) == 0:
            return "",None
        text_out = ""
        image_bytes = None
        candidates = self.response.candidates[0]
        if candidates.url_context_metadata.url_metadata:
            util.bot_logger.debug(get_url_metadata(candidates),result="gemini_url_context_metadata")
        for part in self.response.candidates[0].content.parts:
            if part.text:
                text_out += part.text
            if part.inline_data:
                image_bytes = io.BytesIO(part.inline_data.data)
        util.bot_logger.info(f"text={text_out},image={bool(image_bytes)}", result="gemini_success")
        return text_out, image_bytes