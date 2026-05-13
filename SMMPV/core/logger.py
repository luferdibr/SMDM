
import logging
import sys
from logging.handlers import RotatingFileHandler

from config.settings import LOGGING


# ==================================================
# CONFIG
# ==================================================

LOGGER_NAME = "SMMPV"

DEFAULT_LEVEL = "INFO"

DEFAULT_FORMAT = (

    "%(asctime)s "
    "[%(levelname)s] "
    "[%(name)s] "
    "%(message)s"
)

MAX_BYTES = 5 * 1024 * 1024

BACKUP_COUNT = 5


# ==================================================
# LEVEL
# ==================================================

def get_log_level():

    try:

        level = str(

            LOGGING.get(
                "level",
                DEFAULT_LEVEL
            )

        ).upper()

        return getattr(
            logging,
            level,
            logging.INFO
        )

    except Exception:

        return logging.INFO


# ==================================================
# FORMATTER
# ==================================================

def build_formatter():

    return logging.Formatter(

        DEFAULT_FORMAT
    )


# ==================================================
# CONSOLE HANDLER
# ==================================================

def build_console_handler():

    handler = logging.StreamHandler(
        sys.stdout
    )

    handler.setLevel(
        get_log_level()
    )

    handler.setFormatter(
        build_formatter()
    )

    return handler


# ==================================================
# FILE HANDLER
# ==================================================

def build_file_handler():

    try:

        arquivo = LOGGING.get(
            "file"
        )

        if not arquivo:
            return None

        handler = RotatingFileHandler(

            arquivo,

            maxBytes=MAX_BYTES,

            backupCount=BACKUP_COUNT,

            encoding="utf-8"
        )

        handler.setLevel(
            get_log_level()
        )

        handler.setFormatter(
            build_formatter()
        )

        return handler

    except Exception:

        return None


# ==================================================
# LOGGER
# ==================================================

def build_logger():

    logger = logging.getLogger(
        LOGGER_NAME
    )

    # ==============================================
    # DUPLICATE HANDLERS
    # ==============================================

    if logger.handlers:

        return logger

    logger.setLevel(
        get_log_level()
    )

    logger.propagate = False

    # ==============================================
    # CONSOLE
    # ==============================================

    logger.addHandler(
        build_console_handler()
    )

    # ==============================================
    # FILE
    # ==============================================

    file_handler = build_file_handler()

    if file_handler:

        logger.addHandler(
            file_handler
        )

    # ==============================================
    # NULL HANDLER
    # ==============================================

    if not logger.handlers:

        logger.addHandler(
            logging.NullHandler()
        )

    return logger


# ==================================================
# LOGGER SINGLETON
# ==================================================

logger = build_logger()


# ==================================================
# FACTORY
# ==================================================

def get_logger(nome=None):

    if not nome:

        return logger

    child = logger.getChild(
        str(nome)
    )

    return child


# ==================================================
# SAFE HELPERS
# ==================================================

def info(msg):

    try:

        logger.info(msg)

    except Exception:
        pass


def warning(msg):

    try:

        logger.warning(msg)

    except Exception:
        pass


def error(msg):

    try:

        logger.error(msg)

    except Exception:
        pass


def exception(msg):

    try:

        logger.exception(msg)

    except Exception:
        pass


# ==================================================
# STARTUP
# ==================================================

try:

    logger.info(
        "Logger central inicializado."
    )

except Exception:
    pass