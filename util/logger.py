import logging
import contextvars
import uuid
import sys
import traceback

discord_logging_kwarg = {
    "log_handler": logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w'),
    "log_level":logging.DEBUG
}

request_id_var = contextvars.ContextVar("request_id", default="N/A")

class LevelFormatter(logging.Formatter):
    STANDARD = '%(asctime)s|%(request_id)s|%(funcName)s|%(result)s|%(message)s'

    FORMATS = {
        logging.DEBUG: f'{STANDARD}',
        logging.INFO: f'{STANDARD}',
        logging.ERROR: f'{STANDARD} (%(trace_name)s:%(trace_line)d)',
    }

    def format(self, record):
        # Use a specific format if defined, otherwise use your standard one
        log_fmt = self.FORMATS.get(record.levelno, self.STANDARD)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


class RequestIdFilter(logging.Filter):
    def filter(self, record):
        record.request_id = request_id_var.get()
        return True

class Logger:
    """
    optional interaction_id - generate a new request_id
    required result
    """

    def __init__(self):
        self.bot_logger = logging.getLogger('bot_actions')
        # Ensure log level is low enough to catch DEBUG if needed
        self.bot_logger.setLevel(logging.DEBUG)

        if not self.bot_logger.handlers:
            self.bot_handler = logging.FileHandler(filename='actions.log', encoding='utf-8', mode='w')
            self.bot_handler.addFilter(RequestIdFilter())

            self.bot_handler.setFormatter(LevelFormatter())

            self.bot_logger.addHandler(self.bot_handler)

    def _process_context(self, kwargs):
        if "interaction_id" in kwargs:
            new_id = f"REQ-{kwargs["interaction_id"]}-{str(uuid.uuid4())[:8]}"
            request_id_var.set(new_id)
            kwargs.pop("interaction_id",None)

    def _log(self, level, message, result="-", **kwargs):
        self._process_context(kwargs)
        extra = {"result": result, **kwargs}
        self.bot_logger.log(level, message, extra=extra, stacklevel=3)

    def info(self, message, result="-", **kwargs):
        self._log(logging.INFO, message, result, **kwargs)

    def debug(self, message, result="-", **kwargs):
        self._log(logging.DEBUG, message, result, **kwargs)

    def error(self, message, result="-",**kwargs):
        try:
            frame = traceback.extract_tb(sys.exc_info()[2])[-2]
        except:
            frame = None
        kwargs['trace_name'] = frame.filename if frame else "unknown file"
        kwargs['trace_line'] = frame.lineno if frame else -1
        self._log(logging.ERROR, message, result, **kwargs)