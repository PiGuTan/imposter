import io
import requests
from google import genai
from google.genai import types
from PIL import Image
import os
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv('GEMINI_TOKEN'))

def generate_maple_art_with_url(nexon_img_url, user_prompt_style):
    response = requests.get(nexon_img_url)
    char_image = Image.open(io.BytesIO(response.content))
    return generate_maple_art(char_image, user_prompt_style)

def generate_maple_art(image, user_prompt_style:str="photo realistic"):
    # response = requests.get(nexon_img_url)
    # char_image = Image.open(io.BytesIO(response.content))


    # 3. Construct the "Internal" prompt to ensure quality
    full_prompt = (
        f"Transform this MapleStory character into a {user_prompt_style} style. "
        "Maintain the character's core identity, hair color, and outfit, "
        "but render it with realistic cinematic lighting and textures."
    )

    # 4. Generate using Gemini 2.5 Flash Image

    # 5. Extract the generated image bytes for Discord
    try:
        result = client.models.generate_content(
            model="gemini-2.5-flash-image",
            contents=[full_prompt, image],
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE"]
            )
        )

        for part in result.candidates[0].content.parts:
            if part.inline_data:
                return io.BytesIO(part.inline_data.data), None
    except Exception as e:
        return None, e

if __name__ == "__main__":
    buffer = generate_maple_art("https://images-ext-1.discordapp.net/external/Gf5QcNSTBfpk2Mtm1eMy2u2c1Hxp_7Ppw6qcG9n2pIw/https/open.api.nexon.com/static/maplestorysea/character/look/JHGIIEOHNKPIGJBAJHEMKCNBBHJHCACIGGJFAHOFCCNGMPBFGDIDLLAKMNLHKAAGBCJBBOEGHFIDDEDNOAKGACCLAPEIPMFAIGDLOEPMMJJAFJKOBGOJOJKBPPNJDACBEEJLBMMDLICKJJLIDCDONKMBFCELNEGFIMIIMBHNIFCGMGIGJKGBDFJIKPMFOMBNIKANFPLELNCBCEEDFDDOHLHFPDLBDMFBBFBJPGMBLCNMPLAJKAAAJKNIPACIKJJP?format=webp",
                               "anime")

    with open("output_file.png", "wb") as f:
        f.write(buffer.getvalue())