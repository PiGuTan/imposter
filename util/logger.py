import logging
from discord import Interaction

discord_logging_kwarg = {
    "log_handler": logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w'),
    "log_level":logging.DEBUG
}
class Logger:
    def __init__(self):
        self.bot_logger = logging.getLogger('bot_actions')
        self.bot_logger.setLevel(logging.INFO)
        self.bot_handler = logging.FileHandler(filename='actions.log', encoding='utf-8', mode='w')
        self.bot_formatter = logging.Formatter('%(asctime)s|%(interaction_id)s|%(funcName)s|%(result)s|%(message)s')
        self.bot_logger.addHandler(self.bot_handler)
        self.bot_handler.setFormatter(self.bot_formatter)

    def log_extra(self,interaction:Interaction,result:str="-",**kwargs):
        return {
            "interaction_id": interaction.id,
            "result": result,
            **kwargs
        }

    def info(self, message,interaction:Interaction,result:str="-",**kwargs):
        log_extra = self.log_extra(interaction=interaction,result=result,**kwargs)
        self.bot_logger.info(message,extra=log_extra,stacklevel=2)

    def debug(self, message,interaction:Interaction,result:str="-",**kwargs):
        log_extra = self.log_extra(interaction=interaction,result=result,**kwargs)
        self.bot_logger.debug(message,extra=log_extra,stacklevel=2)

    def error(self, message,interaction:Interaction,result:str="-",**kwargs):
        log_extra = self.log_extra(interaction=interaction,result=result,**kwargs)
        self.bot_logger.error(message,extra=log_extra,stacklevel=2)