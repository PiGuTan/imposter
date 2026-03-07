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


client.run(token)