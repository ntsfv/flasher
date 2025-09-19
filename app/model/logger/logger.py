import logging
import os
import sys
from utils.singleton import Singleton

class Logger(metaclass=Singleton):
    formatter = logging.Formatter("%(levelname)s: %(message)s")

    def __init__(self):
        self.is_debug = False

        log_file = os.getenv("LOG_FILE")
        log_level = os.getenv("LOG_LEVEL")
        log_console = os.getenv("LOG_CONSOLE")

        logging.basicConfig()

        logging.addLevelName(logging.DEBUG, "[DBG]")
        logging.addLevelName(logging.INFO, "[INFO]")
        logging.addLevelName(logging.WARNING, "[WARN]")
        logging.addLevelName(logging.ERROR, "[ERR]")
        logging.addLevelName(logging.CRITICAL, "[CRIT]")

        self.logger = logging.getLogger(__name__)

        match log_level:
            case "DEBUG":
                self.is_debug = True
                self.logger.setLevel(logging.DEBUG)
            case "INFO":
                self.logger.setLevel(logging.INFO)
            case "WARNING":
                self.logger.setLevel(logging.WARNING)
            case "ERROR":
                self.logger.setLevel(logging.ERROR)
            case "CRITICAL":
                self.logger.setLevel(logging.CRITICAL)
            case _:
                self.logger.setLevel(logging.INFO)

        if log_file:
            file_handler = logging.FileHandler(log_file, 'w')
            file_handler.setFormatter(self.formatter)
            self.logger.addHandler(file_handler)

        def formatter_message(message, use_color=True):
            if use_color:
                message = message.replace("$RESET", ColoredFormatter.RESET_SEQ).replace("$BOLD", ColoredFormatter.BOLD_SEQ)
            else:
                message = message.replace("$RESET", "").replace("$BOLD", "")
            return message

        if log_console:
            fmt = "$BOLD%(levelname)s$RESET: %(message)s"
            color_format = formatter_message(fmt, True)
            console_handler = logging.StreamHandler(sys.stdout)
            if sys.platform.startswith('win'):
                console_handler.setFormatter(self.formatter)
            else:
                console_handler.setFormatter(ColoredFormatter(color_format))
            self.logger.addHandler(console_handler)

    def debug(self, message: str):
        if self.is_debug:
            self.logger.debug(message)

    def info(self, message: str):
        self.logger.info(message)

    def warning(self, message: str):
        self.logger.warning(message)

    def error(self, message: str):
        self.logger.error(message)

    def critical(self, message):
        self.logger.critical(message)

    def add_handler(self, handler: logging.Handler, formatter=formatter):
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)



class ColoredFormatter(logging.Formatter):
    RESET_SEQ = "\033[0m"
    COLOR_SEQ = "\033[1;%dm"
    BOLD_SEQ = "\033[1m"

    BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

    COLORS = {
        '[WARN]': YELLOW,
        '[INFO]': BLUE,
        '[DBG]': GREEN,
        '[CRIT]': MAGENTA,
        '[ERR]': RED
    }

    def __init__(self, msg, use_color=True):
        logging.Formatter.__init__(self, msg)
        self.use_color = use_color

    def format(self, record):
        levelname = record.levelname
        if self.use_color and levelname in self.COLORS:
            levelname_color = self.COLOR_SEQ % (30 + self.COLORS[levelname]) + levelname + self.RESET_SEQ
            record.levelname = levelname_color
        return logging.Formatter.format(self, record)