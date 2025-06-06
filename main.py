import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import io
import asyncio

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


bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f"We are ready to go in, {bot.user.name}")

@bot.event
async def on_message(message):
    if message.author.bot:
        await bot.process_commands(message)
        return
    is_guild_message : bool = bool(message.channel.guild)
    is_ping_message : bool = message.content.startswith(f'<@{bot.user.id}>')
    if  is_guild_message and not is_ping_message:
        await bot.process_commands(message)
        return

    content = message.content.split(" ",maxsplit=1)[-1] if is_ping_message else message.content
    logging.debug(f"Received message: {content}")

    if is_guild_message:
        await message.delete()

    content, command = content_processorr.pre_process_content(content)
    output = Character(content).image_url
    if not output:
        await message.channel.send(f"Who is {content}:question:")
        await bot.process_commands(message)
        return
    if not command:
        await message.channel.send(content=output)
        await bot.process_commands(message)
        return
    param, a_frames, e_frames = content_processorr.process_split_string(command)
    image = Character_Image(output,params=param)
    image.get_images(a_frames=a_frames, e_frames=e_frames) # a_frame, e_frame passed as none
    output_bytes = image.process_image()
    file_name = content_processorr.parse_file_name(content,param)
    await message.channel.send(file=discord.File(io.BytesIO(output_bytes), filename=file_name))

    await bot.process_commands(message)

bot.run(token, log_handler=handler, log_level=logging.DEBUG)