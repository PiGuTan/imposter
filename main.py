import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os

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
        return
    is_guild_message : bool = bool(message.channel.guild)
    is_ping_message : bool = message.content.startswith(f'<@{bot.user.id}>')
    if  is_guild_message and not is_ping_message:
        return

    content = message.content.split(" ",maxsplit=1)[-1] if is_ping_message else message.content
    logging.debug(f"Received message: {content}")

    pass #process content

    await message.channel.send(content)

    await bot.process_commands(message)

bot.run(token, log_handler=handler, log_level=logging.DEBUG)