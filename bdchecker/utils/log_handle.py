import logging
import logging.handlers
import os
import sys


class UnixConsoleColorFormatter(logging.Formatter):
    def __init__(self, formatter):
        grey = "\x1b[38;20m"
        yellow = "\x1b[33;20m"
        red = "\x1b[31;20m"
        bold_red = "\x1b[31;1m"
        reset = "\x1b[0m"

        self.FORMATS = {
            logging.DEBUG: grey + formatter + reset,
            logging.INFO: grey + formatter + reset,
            logging.WARNING: yellow + formatter + reset,
            logging.ERROR: red + formatter + reset,
            logging.CRITICAL: bold_red + formatter + reset
        }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


class LogHandle(object):
    """simple log init"""

    @staticmethod
    def init_log(
            filename,
            console_level=logging.WARNING,
            file_level=logging.DEBUG,
            use_rotate=False,
            mode="a"):
        """
        initialize log
        :param filename: log output filepath
        :param console_level: console filter level
        :param file_level: file filter level
        :param use_rotate: is use rotate
        :param mode: open mode
        :return:
        """
        # create output dir
        folder = os.path.dirname(filename)
        if len(folder) > 0 and (not os.path.exists(folder)):
            os.makedirs(folder, exist_ok=True)

        # log handler
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)

        ch = LogHandle.get_console_handler(console_level)
        ch.setFormatter(LogHandle.get_console_formatter())
        logger.addHandler(ch)

        if file_level != -1:
            if use_rotate is True:
                fh = LogHandle.get_rotating_handler(
                    level=file_level, filename=filename, mode=mode)
            else:
                fh = LogHandle.get_file_handler(
                    level=file_level, filename=filename, mode=mode)
            fh.setFormatter(LogHandle.get_formatter())
            logger.addHandler(fh)

    @staticmethod
    def get_formatter():
        """
        log format
        """
        return logging.Formatter(
            "%(asctime)s|%(levelname)s|%(filename)s:%(lineno)s - "
            "%(message)s")

    @staticmethod
    def get_console_formatter():
        """
        console formatter
        """
        if sys.platform.startswith("win32"):
            return LogHandle.get_formatter()
        else:
            return UnixConsoleColorFormatter(
                "%(asctime)s|%(levelname)s|%(filename)s:%(lineno)s - "
                "%(message)s")

    @staticmethod
    def get_console_handler(level):
        """
        get console log handler
        :param level: log filter level
        :return: log handler
        """
        handler = logging.StreamHandler()
        handler.setLevel(level)
        return handler

    @staticmethod
    def get_file_handler(level, filename, mode="a"):
        """
        get file log handler
        :param level: log filter level
        :param filename: output filepath
        :param mode: open mode
        :return: log handler
        """
        handler = logging.FileHandler(filename=filename, mode=mode)
        handler.setLevel(level)
        return handler

    @staticmethod
    def get_rotating_handler(
            level, filename, mode="a",
            maxBytes=20 * 1024 * 1024, backupCount=10):
        """
        get rotating log handler
        :param level: log filter level
        :param filename: output filepath
        :param mode: open mode
        :param maxBytes: max bytes
        :param backupCount: backup file count
        :return: log handler
        """
        handler = logging.handlers.RotatingFileHandler(
            filename=filename, mode=mode, maxBytes=maxBytes,
            backupCount=backupCount)
        handler.setLevel(level)
        return handler

    @staticmethod
    def log_level(str_level: str):
        """
        convert string to log level enum
        :param str_level: log level string
        :return: log level enum
        """
        if str_level.lower() == "debug":
            return logging.DEBUG
        elif str_level.lower() == "info":
            return logging.INFO
        elif str_level.lower() == "warning":
            return logging.WARNING
        elif str_level.lower() == "error":
            return logging.ERROR
        elif str_level.lower() == "fatal":
            return logging.FATAL
        else:
            return logging.INFO
