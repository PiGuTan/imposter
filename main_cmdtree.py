import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import io

import ctypes
from discord.ext import commands
from dotenv import load_dotenv

from core import Character_Image
from core import content_processorr
from core import Character

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.members = True
intents.messages = True
intents.message_content = True

client = commands.Bot(command_prefix="!", intents=intents)
client.remove_command("help")

@client.event
async def on_ready():
    try:
        synced = await client.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)

    activity = discord.Activity(type=discord.ActivityType.watching, name="/hello")
    await client.change_presence(status=discord.Status.online, activity=activity)

@client.tree.command(name="hello", description="Say hello and tagging user")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message(f"Hello {interaction.user.mention}!")

@client.tree.command(name="copy", description="imitates a users character with an action and expression")
async def copy(interaction: discord.Interaction, ign:str,action:str=None,expression:str=None):
    logging.debug(f"command_receive|ign={ign}, action={action}, expression={expression}")
    await interaction.response.defer(thinking=True)

    image_url = Character(ign).image_url
    if not image_url:
        await interaction.followup.send(f"Who is {ign}:question:")
        return

    if not (action or expression):
        await interaction.followup.send(content=image_url)
        return
    try:
        content = [i for i in (action,expression) if i is not None]
        param, a_frames, e_frames = content_processorr.process_split_string(content)
        image = Character_Image(image_url,params=param)
        image.get_images(a_frames=a_frames, e_frames=e_frames) # a_frame, e_frame passed as none
        output_bytes = image.process_image()
        file_name = content_processorr.parse_file_name(content,param)
        await interaction.followup.send(file=discord.File(io.BytesIO(output_bytes), filename=file_name))
    except Exception as e:
        await interaction.followup.send(f"imposter shot curcuited with error{e}")

client.run(token, log_handler=handler, log_level=logging.DEBUG)