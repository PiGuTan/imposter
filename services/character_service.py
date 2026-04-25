from core import Character, Character_Image
from PIL import Image
from core import content_processor,build_prompt
from client import Gemini_agent
import util

def get_character(ign) -> Character | None:
    """Returns Character if valid, None if not found."""
    return Character(ign)

def get_image_io(image_url, action, expression) -> (bytes, str):
    """Returns image in io bytes together with its format"""
    try:
        param, a_frames, e_frames, _, _, debug = content_processor.build_params(action=action, emotion=expression)
        util.bot_logger.info(f"{debug}",result="process_params")
        image = Character_Image(image_url,params=param)
        output_bytes, extension = image.process_image(a_frames=a_frames, e_frames=e_frames)
        return output_bytes, extension
    except Exception as e:
        util.bot_logger.error(f"error={e}", result="error")
        # return something?

def get_single_image(image_url, action, expression) -> Image:
    """Returns a PIL image for /draw."""

def get_image_url(image_url, action, expression) -> str:
    """Returns a composed image URL for /create_prompt."""

def get_params(action, expression) -> tuple | None:
    """Returns (param, a_frames, e_frames, debug) or None."""

def get_prompt_with_context(character:Character,action, expression) -> (str,str,str):
    """generates an image + prompt + """
    try:
        param, a_frames, e_frames, a_param, e_param, debug = content_processor.build_params(action=action, emotion=expression)
        image = Character_Image(character.image_url, params=param)
        image = image.get_single_image(a_frames, e_frames)

        full_prompt = build_prompt(character.beauty_items,a_param=a_param,e_param=e_param)

        return image, full_prompt, character.beauty_items
    except Exception as e:
        util.bot_logger.error(f"error={e}", result="error")
        return None

async def generate_artwork(image, prompt):
    """Generates an artwork image."""
    gemini_agent = Gemini_agent(require_image=True)
    gemini_agent.set_prompt(image)
    gemini_agent.set_prompt(prompt)
    error = await gemini_agent.generate()
    if error and error.code == 429:
        raise util.RateLimitError("Owner is broke and does not have enough money to fund project. Kindly donate")
    elif error:
        util.bot_logger.error(f"error={error}", result="generate_error")
        raise error
    _, gen_image = gemini_agent.get_response_data()
    return gen_image