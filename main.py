import discord
import logging
import os
import io
import asyncio

from discord.ext import commands
from dotenv import load_dotenv

from core import Character_Image
from core import content_processorr
from core import Character

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

# logging
bot_logger = logging.getLogger('bot_actions')
bot_logger.setLevel(logging.INFO)
bot_handler = logging.FileHandler(filename='actions.log', encoding='utf-8', mode='w')
bot_formatter = logging.Formatter('%(asctime)s|%(interaction_id)s|%(command)s|%(result)s|%(message)s')
bot_logger.addHandler(bot_handler)
bot_handler.setFormatter(bot_formatter)
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

@client.tree.command(name="hello", description="Say hello and tagging yourself")
async def hello(interaction: discord.Interaction):
    log_extra = {
        "interaction_id": interaction.id,
        "command": "hello",
        "result": "-"
    }
    bot_logger.info(f"{interaction.user.id}",extra={**log_extra})
    await interaction.response.defer(thinking=False)
    user = await client.fetch_user(interaction.user.id)
    try:
        if not user:
            bot_logger.error(f"{interaction.user.id} not logged in",extra={**log_extra, "result":"auth_error"})
            await interaction.followup.send("Are you human?")
        await user.send(f"Hello {interaction.user.name}")

        with open(r"templates/hello_template.txt", 'r') as file:
            for line in file:
                await asyncio.sleep(1)
                await user.send(line.strip())
        await asyncio.sleep(1)
        await interaction.followup.send(f"Hihi {interaction.user.mention}, I have sent you some pms <3")
    except Exception as e:
        bot_logger.error(f"imposter shot circuited with error\n{e}",extra={**log_extra, "result":"error"})

@client.tree.command(name="preview", description="shows what the bot can do")
@discord.app_commands.allowed_installs(guilds=False, users=True)
@discord.app_commands.allowed_contexts(guilds=False, dms=True, private_channels=False)
async def preview(interaction: discord.Interaction):
    log_extra = {
        "interaction_id": interaction.id,
        "command": "preview",
        "result": "-"
    }
    bot_logger.info(f"{interaction.user.id}",extra={**log_extra})
    await interaction.response.send_message(r"https://github.com/PiGuTan/imposter/blob/main/previews/character_param_preview.gif?raw=true")

@client.tree.command(name="copy", description="imitates a users character with an action and expression")
@discord.app_commands.allowed_installs(guilds=True, users=True)
@discord.app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def copy(interaction: discord.Interaction, ign:str,action:str=None,expression:str=None):
    log_extra = {
        "interaction_id": interaction.id,
        "command": "copy",
        "result": "-"
    }
    bot_logger.info(f"ign={ign}, action={action}, expression={expression}",
                    extra={**log_extra,"result":"receive"})
    await interaction.response.defer(thinking=True)

    image_url = Character(ign).image_url
    if not image_url:
        bot_logger.info(f"ign not found ign={ign}",
                        extra={**log_extra, "result": "error"})
        await interaction.followup.send(f"Who is {ign}:question:")
        return

    if not (action or expression):
        bot_logger.info(f"no action or expression found",
                        extra={**log_extra, "result": "success"})
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
        bot_logger.info("",
                        extra={**log_extra, "result": "success"})
        await interaction.followup.send(file=discord.File(io.BytesIO(output_bytes), filename=file_name))
    except Exception as e:
        bot_logger.error(f"error={e}",
                        extra={**log_extra, "result": "error"})
        await interaction.followup.send(f"imposter shot circuited with error\n{e}")

client.run(token, log_handler=handler, log_level=logging.DEBUG)