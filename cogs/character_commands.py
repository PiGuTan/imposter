from discord.ext import commands
import discord
from discord import app_commands

import io
import sys
import traceback

import util
from core import Character, Character_Image, content_processor
from core import generate_maple_art,generate_maple_art_with_url
from services.character_service import get_character, get_image_io, get_prompt_with_context


class CharacterCommands(commands.Cog):
    def __init__(self, client):
        self.client = client

    @app_commands.command(name="hello", description="Say hello and tagging yourself")
    async def hello(self,interaction: discord.Interaction):

        util.bot_logger.info(f"{interaction.user.id}",result="incoming", interaction_id=interaction.id)

        await interaction.response.defer(thinking=False)
        user = await self.client.fetch_user(interaction.user.id)
        try:
            if not user:
                util.bot_logger.error(f"{interaction.user.id} not logged in", result="auth_error")
                await interaction.followup.send("Is that human?")

            await util.do_line_by_line(user.send, "hello_template.txt")
            if interaction.guild:
                await interaction.followup.send(f"Hihi {interaction.user.mention}, I have sent you some pms <3")
            else:
                await interaction.delete_original_response()
        except Exception as e:
            util.bot_logger.error(f"error={e}, traceback={traceback.extract_tb(sys.exc_info()[2])[-1].lineno}", result="error")
            await interaction.followup.send(f"imposter shot circuited with error\n{e}")

    @app_commands.command(name="preview", description="shows what the bot can do")
    @app_commands.allowed_installs(guilds=False, users=True)
    @app_commands.allowed_contexts(guilds=False, dms=True, private_channels=False)
    async def preview(self, interaction: discord.Interaction):
        util.bot_logger.info(f"{interaction.user.id}",result="incoming", interaction_id=interaction.id)
        await interaction.response.send_message(
            r"https://github.com/PiGuTan/imposter/blob/main/previews/character_param_preview.gif?raw=true")

    @app_commands.command(name="copy", description="imitates a users character with an action and expression")
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def copy(self, interaction: discord.Interaction, ign: str, action: str = None, expression: str = None):
        util.bot_logger.info(f"ign={ign}, action={action}, expression={expression}", interaction_id=interaction.id,
                             result="receive")
        await interaction.response.defer(thinking=True)

        character = get_character(ign)
        if not character:
            await interaction.followup.send(f"Who is {ign}:question:")
            return
        try:
            gif_bytes, extension = get_image_io(character.image_url,action=action,expression=expression)
            await interaction.followup.send(file=discord.File(io.BytesIO(gif_bytes), filename=f"{ign}.{extension}"))
        except Exception as e:
            util.bot_logger.error(f"error={e}, traceback={traceback.extract_tb(sys.exc_info()[2])[-1].lineno}", result="error")
            await interaction.followup.send(f"imposter shot circuited with error\n{e}")

    @app_commands.command(name="draw", description="draws out the character with action and expression")
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def draw(self, interaction: discord.Interaction, ign: str, action: str = None, expression: str = None):
        util.bot_logger.info(f"ign={ign}, action={action}, expression={expression}", interaction_id=interaction.id,
                             result="receive")
        await interaction.response.defer(thinking=True)

        character = Character(ign)
        if not character:
            util.bot_logger.info(f"ign not found ign={ign}", result="error")
            await interaction.followup.send(f"Who is {ign}:question:")
            return

        try:
            await character.get_all_beauty_items()
            image_url, prompt, beauty_details = get_prompt_with_context(character, action, expression)
            # await interaction.followup.send(content=image_url)
            if prompt:
                file = discord.File(io.StringIO(prompt), filename=f"{ign}_prompt.md")
                await interaction.followup.send(file=file)
        except Exception as e:
            util.bot_logger.error(f"error={e}, traceback={traceback.extract_tb(sys.exc_info()[2])[-1].lineno}",
                                  result="error")
            await interaction.followup.send(f"imposter shot circuited with error\n{e}")
        try:
            # prompt + image_url = artwork?
            pass
        except Exception as e:
            util.bot_logger.error(f"error={e}, traceback={traceback.extract_tb(sys.exc_info()[2])[-1].lineno}",
                                  result="artwork_gen_error")
            # return prompt?

    @app_commands.command(name="create_prompt", description="imitates a users character with an action and expression")
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def create_prompt(self, interaction: discord.Interaction, ign: str, action: str = None, expression: str = None,
                            style: str = "photo realistic", proportions:str = "adult", other_instructions: str = None):
        util.bot_logger.info(f"ign={ign}, action={action}, expression={expression}", interaction_id=interaction.id,
                             result="receive")
        await interaction.response.defer(thinking=True)

        character = Character(ign)
        if not character:
            util.bot_logger.info(f"ign not found ign={ign}",result="error")
            await interaction.followup.send(f"Who is {ign}:question:")
            return

        try:
            await character.get_all_beauty_items()
            image_url,prompt,beauty_details = get_prompt_with_context(character, action, expression)
            await interaction.followup.send(content=image_url)
            if prompt:
                file = discord.File(io.StringIO(prompt), filename=f"{ign}_prompt.md")
                await interaction.followup.send(file=file)
            # await interaction.followup.send(content=beauty_details)
        except Exception as e:
            util.bot_logger.error(f"error={e}, traceback={traceback.extract_tb(sys.exc_info()[2])[-1].lineno}", result="error")
            await interaction.followup.send(f"imposter shot circuited with error\n{e}")

async def setup(bot):
    await bot.add_cog(CharacterCommands(bot))