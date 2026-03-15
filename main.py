import discord
import os
import io
import asyncio

from discord.ext import commands
from dotenv import load_dotenv

import util

from core import Character_Image
from core import content_processorr
from core import Character

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

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

@client.tree.command(name="hello", description="Say hello and tagging yourself")
async def hello(interaction: discord.Interaction):

    util.bot_logger.info(f"{interaction.user.id}",interaction=interaction)

    await interaction.response.defer(thinking=False)
    user = await client.fetch_user(interaction.user.id)
    try:
        if not user:
            util.bot_logger.error(f"{interaction.user.id} not logged in", interaction=interaction, result="auth_error")
            await interaction.followup.send("Is that human?")

        await util.do_line_by_line(user.send,"hello_template.txt")
        if interaction.guild:
            await interaction.followup.send(f"Hihi {interaction.user.mention}, I have sent you some pms <3")
        else:
            await interaction.delete_original_response()
    except Exception as e:
        util.bot_logger.error(f"imposter shot circuited with error\n{e}", interaction=interaction, result="error")

@client.tree.command(name="preview", description="shows what the bot can do")
@discord.app_commands.allowed_installs(guilds=False, users=True)
@discord.app_commands.allowed_contexts(guilds=False, dms=True, private_channels=False)
async def preview(interaction: discord.Interaction):
    util.bot_logger.info(f"{interaction.user.id}", interaction=interaction)
    await interaction.response.send_message(r"https://github.com/PiGuTan/imposter/blob/main/previews/character_param_preview.gif?raw=true")

@client.tree.command(name="copy", description="imitates a users character with an action and expression")
@discord.app_commands.allowed_installs(guilds=True, users=True)
@discord.app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def copy(interaction: discord.Interaction, ign:str,action:str=None,expression:str=None):
    util.bot_logger.info(f"ign={ign}, action={action}, expression={expression}", interaction=interaction, result="receive")
    await interaction.response.defer(thinking=True)

    image_url = Character(ign).image_url
    if not image_url:
        util.bot_logger.info(f"ign not found ign={ign}", interaction=interaction,
                             result="error")
        await interaction.followup.send(f"Who is {ign}:question:")
        return

    if not (action or expression):
        util.bot_logger.info(f"no action or expression found", interaction=interaction,
                             result="success")
        await interaction.followup.send(content=image_url)
        return
    try:
        # TODO: change to handle two strings instead of a list of two strings
        content = [i for i in (action,expression) if i is not None]
        param, a_frames, e_frames = content_processorr.process_split_string(content)
        image = Character_Image(image_url,params=param)
        image.get_images(a_frames=a_frames, e_frames=e_frames) # a_frame, e_frame passed as none
        output_bytes = image.process_image()
        file_name = content_processorr.parse_file_name(content,param)
        util.bot_logger.info("", interaction=interaction,
                             result="success")
        await interaction.followup.send(file=discord.File(io.BytesIO(output_bytes), filename=file_name))
    except Exception as e:
        util.bot_logger.error(f"error={e}", interaction=interaction,
                             result="error")
        await interaction.followup.send(f"imposter shot circuited with error\n{e}")

client.run(token, **util.discord_logging_kwarg)