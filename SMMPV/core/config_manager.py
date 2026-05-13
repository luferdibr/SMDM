
import os
from copy import deepcopy

from dotenv import load_dotenv

from core.logger import get_logger

from core.cache import (

    get_cache,

    set_cache,

    invalidate_config_cache
)

from core.exceptions import (
    ConfigError
)


# ==================================================
# LOGGER
# ==================================================

logger = get_logger("config")


# ==================================================
# CACHE
# ==================================================

CONFIG_NAMESPACE = "config"

CONFIG_CACHE_KEY = "settings"


# ==================================================
# DEFAULTS
# ==================================================

DEFAULT_CONFIG = {

    # ==============================================
    # APP
    # ==============================================

    "app": {

        "name": "SMMPV",

        "version": "1.0.0",

        "environment": "production",

        "debug": False
    },

    # ==============================================
    # DATABASE
    # ==============================================

    "db": {

        "driver": (
            "ODBC Driver 17 "
            "for SQL Server"
        ),

        "server": "localhost",

        "database": "SMMPV",

        "uid": "sa",

        "pwd": "",

        "encrypt": "no",

        "trust_cert": "yes"
    },

    # ==============================================
    # AUTH
    # ==============================================

    "auth": {

        "session_timeout": 3600,

        "password_min_length": 6,

        "root_level": 100,

        "admin_level": 50
    },

    # ==============================================
    # CACHE
    # ==============================================

    "cache": {

        "enabled": True,

        "default_ttl": 300
    },

    # ==============================================
    # LOGGING
    # ==============================================

    "logging": {

        "level": "INFO",

        "file": None
    }
}


# ==================================================
# INTERNAL
# ==================================================

_CONFIG = deepcopy(
    DEFAULT_CONFIG
)


# ==================================================
# HELPERS
# ==================================================

def _env(

    key,

    default=None
):

    return os.getenv(
        key,
        default
    )


def _to_bool(valor):

    if valor in (
        True,
        1,
        "1",
        "true",
        "TRUE",
        "yes",
        "YES",
        "sim",
        "SIM"
    ):

        return True

    return False


def _to_int(

    valor,

    default=0
):

    try:

        return int(valor)

    except Exception:

        return default


# ==================================================
# LOAD ENV
# ==================================================

def load_environment():

    try:

        load_dotenv()

        logger.info(
            "ENV carregado."
        )

    except Exception as ex:

        logger.exception(
            "LOAD ENV ERROR"
        )

        raise ConfigError(
            str(ex)
        )


# ==================================================
# LOAD CONFIG
# ==================================================

def load_config():

    global _CONFIG

    try:

        load_environment()

        cfg = deepcopy(
            DEFAULT_CONFIG
        )

        # ==========================================
        # APP
        # ==========================================

        cfg["app"]["name"] = _env(
            "APP_NAME",
            cfg["app"]["name"]
        )

        cfg["app"]["version"] = _env(
            "APP_VERSION",
            cfg["app"]["version"]
        )

        cfg["app"]["environment"] = _env(
            "APP_ENV",
            cfg["app"]["environment"]
        )

        cfg["app"]["debug"] = _to_bool(
            _env(
                "APP_DEBUG",
                cfg["app"]["debug"]
            )
        )

        # ==========================================
        # DB
        # ==========================================

        cfg["db"]["driver"] = _env(
            "DB_DRIVER",
            cfg["db"]["driver"]
        )

        cfg["db"]["server"] = _env(
            "DB_SERVER",
            cfg["db"]["server"]
        )

        cfg["db"]["database"] = _env(
            "DB_DATABASE",
            cfg["db"]["database"]
        )

        cfg["db"]["uid"] = _env(
            "DB_UID",
            cfg["db"]["uid"]
        )

        cfg["db"]["pwd"] = _env(
            "DB_PWD",
            cfg["db"]["pwd"]
        )

        cfg["db"]["encrypt"] = _env(
            "DB_ENCRYPT",
            cfg["db"]["encrypt"]
        )

        cfg["db"]["trust_cert"] = _env(
            "DB_TRUST_CERT",
            cfg["db"]["trust_cert"]
        )

        # ==========================================
        # AUTH
        # ==========================================

        cfg["auth"][
            "session_timeout"
        ] = _to_int(

            _env(
                "SESSION_TIMEOUT",
                3600
            ),

            3600
        )

        cfg["auth"][
            "password_min_length"
        ] = _to_int(

            _env(
                "PASSWORD_MIN_LENGTH",
                6
            ),

            6
        )

        # ==========================================
        # CACHE
        # ==========================================

        cfg["cache"]["enabled"] = (
            _to_bool(

                _env(
                    "CACHE_ENABLED",
                    True
                )
            )
        )

        cfg["cache"][
            "default_ttl"
        ] = _to_int(

            _env(
                "CACHE_DEFAULT_TTL",
                300
            ),

            300
        )

        # ==========================================
        # LOGGING
        # ==========================================

        cfg["logging"]["level"] = _env(
            "LOG_LEVEL",
            "INFO"
        )

        cfg["logging"]["file"] = _env(
            "LOG_FILE",
            None
        )

        validate_config(cfg)

        _CONFIG = cfg

        set_cache(

            CONFIG_CACHE_KEY,

            cfg,

            ttl=3600,

            namespace=CONFIG_NAMESPACE
        )

        logger.info(
            "Config carregada."
        )

        return cfg

    except Exception as ex:

        logger.exception(
            "LOAD CONFIG ERROR"
        )

        raise ConfigError(
            str(ex)
        )


# ==================================================
# VALIDATE
# ==================================================

def validate_config(cfg=None):

    if cfg is None:

        cfg = _CONFIG

    # ==============================================
    # APP
    # ==============================================

    if not cfg["app"]["name"]:

        raise ConfigError(
            "APP_NAME inválido."
        )

    # ==============================================
    # DB
    # ==============================================

    if not cfg["db"]["server"]:

        raise ConfigError(
            "DB_SERVER inválido."
        )

    if not cfg["db"]["database"]:

        raise ConfigError(
            "DB_DATABASE inválido."
        )

    if not cfg["db"]["uid"]:

        raise ConfigError(
            "DB_UID inválido."
        )

    # ==============================================
    # AUTH
    # ==============================================

    if (

        cfg["auth"][
            "password_min_length"
        ] < 4

    ):

        raise ConfigError(
            "PASSWORD_MIN_LENGTH inválido."
        )

    return True


# ==================================================
# GET CONFIG
# ==================================================

def get_config():

    cache = get_cache(

        CONFIG_CACHE_KEY,

        namespace=CONFIG_NAMESPACE
    )

    if cache:

        return cache

    return load_config()


# ==================================================
# SECTION
# ==================================================

def get_section(

    section,

    default=None
):

    cfg = get_config()

    return cfg.get(
        section,
        default or {}
    )


# ==================================================
# GET VALUE
# ==================================================

def get_value(

    section,

    key,

    default=None
):

    section_data = get_section(
        section
    )

    return section_data.get(
        key,
        default
    )


# ==================================================
# STRING
# ==================================================

def get_str(

    section,

    key,

    default=""
):

    valor = get_value(

        section,

        key,

        default
    )

    return str(valor)


# ==================================================
# INTEGER
# ==================================================

def get_int(

    section,

    key,

    default=0
):

    valor = get_value(

        section,

        key,

        default
    )

    return _to_int(
        valor,
        default
    )


# ==================================================
# BOOLEAN
# ==================================================

def get_bool(

    section,

    key,

    default=False
):

    valor = get_value(

        section,

        key,

        default
    )

    return _to_bool(valor)


# ==================================================
# RELOAD
# ==================================================

def reload_config():

    invalidate_config_cache()

    logger.warning(
        "Reload config."
    )

    return load_config()


# ==================================================
# DB CONNECTION STRING
# ==================================================

def build_connection_string():

    db = get_section("db")

    return (

        f"DRIVER={db['driver']};"

        f"SERVER={db['server']};"

        f"DATABASE={db['database']};"

        f"UID={db['uid']};"

        f"PWD={db['pwd']};"

        f"Encrypt={db['encrypt']};"

        f"TrustServerCertificate="
        f"{db['trust_cert']};"

        "MARS_Connection=yes;"
    )


# ==================================================
# DEBUG
# ==================================================

def dump_config():

    cfg = deepcopy(
        get_config()
    )

    try:

        cfg["db"]["pwd"] = (
            "[PROTEGIDO]"
        )

    except Exception:
        pass

    return cfg


# ==================================================
# STARTUP
# ==================================================

load_config()

logger.info(
    "Config manager inicializado."
)
