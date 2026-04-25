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
        self._require_image = require_image
        if require_image:
            self.model = image_model
            self.config = types.GenerateContentConfig(
                response_modalities=["IMAGE"],
                image_config=types.ImageConfig(aspect_ratio="9:16"),
                tools=[]
            )
        else:
            self.model = text_model
            self.config = types.GenerateContentConfig(
                response_modalities=["TEXT"],
                tools=[types.Tool(url_context=types.UrlContext())]
            )
        self._contents = []
        self.response = None

    def set_prompt_bytes(self,image_bytes, image_type="image/png"):
        if not self._require_image:
            util.bot_logger.info("attempting to set prompt bytes when image not required", result="set_prompt_bytes_mismatch")
            return
        content = types.Part.from_bytes(
            data=image_bytes,
            mime_type=image_type,
        )
        self.set_prompt(content)

    def set_prompt(self, *prompt):
        if (not prompt) or len(prompt) == 0:
            return
        if len(self._contents) > 0:
            self._contents += prompt
        self._contents = prompt

    async def generate(self):
        if self._contents is None:
            return None
        try:
            self.response = await client.aio.models.generate_content(
                model=self.model,
                contents=self._contents,
                config=self.config
            )
            return None
        except Exception as e:
            util.bot_logger.error(f"error={e}", result="gemini_call_error")
            return e

    def get_response_data(self):
        if len(self._contents) == 0:
            util.bot_logger.error(f"no prompt found", result="gemini_content_error")
            return "",None
        if not self.response:
            util.bot_logger.error(f"no response found", result="gemini_response_error")
            return "",None
        if len(self.response.candidates) == 0:
            util.bot_logger.error(f"empty candidates in response", result="gemini_response_error")
            return "",None
        text_out = ""
        image_bytes = None
        try:
            candidates = self.response.candidates[0]
            if (not self._require_image) and candidates.url_context_metadata.url_metadata:
                util.bot_logger.debug(get_url_metadata(candidates),result="gemini_url_context_metadata")
            for part in self.response.candidates[0].content.parts:
                if part.text:
                    text_out += part.text
                if part.inline_data:
                    image_bytes = io.BytesIO(part.inline_data.data)
            util.bot_logger.info(f"text={text_out},image={bool(image_bytes)}", result="gemini_success")
            return text_out, image_bytes
        except Exception as e:
            util.bot_logger.error(f"error={e}", result="gemini_error")
            return "",None