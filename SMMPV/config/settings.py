import logging
import os

from pathlib import Path

from dotenv import load_dotenv


# ==================================================
# BASE
# ==================================================

BASE_DIR = Path(__file__).resolve().parent.parent


# ==================================================
# LOAD ENV
# ==================================================

load_dotenv()


# ==================================================
# LOGGER
# ==================================================

LOGGER = logging.getLogger(
    "MDM_SETTINGS"
)

if not LOGGER.handlers:

    logging.basicConfig(

        level=logging.INFO,

        format=(
            "%(asctime)s "
            "[%(levelname)s] "
            "%(message)s"
        )
    )


# ==================================================
# HELPERS
# ==================================================


def get_env(chave, default=None):

    valor = os.getenv(
        chave,
        default
    )

    if isinstance(valor, str):
        valor = valor.strip()

    return valor



def get_bool(chave, default=False):

    valor = str(
        get_env(chave, default)
    ).strip().lower()

    return valor in (
        "1",
        "true",
        "yes",
        "sim",
        "on"
    )



def get_int(chave, default=0):

    try:

        return int(
            get_env(chave, default)
        )

    except Exception:

        return default


# ==================================================
# APP
# ==================================================

APP_CONFIG = {

    "name": get_env(
        "APP_NAME",
        "MDM ERP"
    ),

    "company": get_env(
        "APP_COMPANY",
        "Mundo de Magia"
    ),

    "version": get_env(
        "APP_VERSION",
        "1.0.0"
    ),

    "environment": get_env(
        "APP_ENV",
        "development"
    ),

    "debug": get_bool(
        "APP_DEBUG",
        True
    ),

    "timezone": get_env(
        "APP_TIMEZONE",
        "America/Sao_Paulo"
    ),

    "language": get_env(
        "APP_LANGUAGE",
        "pt-BR"
    ),

    "theme": get_env(
        "APP_THEME",
        "light"
    ),

    "assets_dir": get_env(
        "APP_ASSETS_DIR",
        "assets"
    )
}


# ==================================================
# DATABASE
# ==================================================

DB_CONFIG = {

    "driver": get_env(
        "DB_DRIVER",
        "ODBC Driver 17 for SQL Server"
    ),

    "server": get_env(
        "DB_SERVER",
        "localhost"
    ),

    "port": get_env(
        "DB_PORT",
        "1433"
    ),

    "database": get_env(
        "DB_NAME",
        "MMPV"
    ),

    "user": get_env(
        "DB_USER",
        "sa"
    ),

    "password": get_env(
        "DB_PASSWORD",
        ""
    ),

    "encrypt": get_bool(
        "DB_ENCRYPT",
        False
    ),

    "trust_cert": get_bool(
        "DB_TRUST_CERT",
        True
    ),

    "timeout": get_int(
        "DB_TIMEOUT",
        30
    ),

    "app_name": get_env(
        "APP_NAME",
        "MDM ERP"
    )
}


# ==================================================
# SECURITY
# ==================================================

SECURITY_CONFIG = {

    "bcrypt_rounds": get_int(
        "SECURITY_BCRYPT_ROUNDS",
        12
    ),

    "session_timeout": get_int(
        "SECURITY_SESSION_TIMEOUT",
        60
    ),

    "max_login_attempts": get_int(
        "SECURITY_MAX_LOGIN_ATTEMPTS",
        5
    ),

    "password_min_length": get_int(
        "SECURITY_PASSWORD_MIN_LENGTH",
        8
    ),

    "require_upper": get_bool(
        "SECURITY_REQUIRE_UPPER",
        True
    ),

    "require_lower": get_bool(
        "SECURITY_REQUIRE_LOWER",
        True
    ),

    "require_number": get_bool(
        "SECURITY_REQUIRE_NUMBER",
        True
    ),

    "require_special": get_bool(
        "SECURITY_REQUIRE_SPECIAL",
        True
    )
}


# ==================================================
# ADMIN
# ==================================================

ADMIN_CONFIG = {

    "root_login": get_env(
        "ADMIN_ROOT_LOGIN",
        "ROOT"
    ),

    "root_nome": get_env(
        "ADMIN_ROOT_NOME",
        "Administrador ROOT"
    ),

    "root_senha": get_env(
        "ADMIN_ROOT_PASSWORD",
        "Root@123"
    ),

    "admin_login": get_env(
        "ADMIN_LOGIN",
        "ADMIN"
    ),

    "admin_nome": get_env(
        "ADMIN_NOME",
        "Administrador"
    ),

    "admin_senha": get_env(
        "ADMIN_PASSWORD",
        "Admin@123"
    )
}


# ==================================================
# AUDITORIA
# ==================================================

AUDITORIA_CONFIG = {

    "enabled": get_bool(
        "AUDITORIA_ENABLED",
        True
    ),

    "max_detalhes": get_int(
        "AUDITORIA_MAX_DETALHES",
        4000
    )
}


# ==================================================
# FLET
# ==================================================

FLET_CONFIG = {

    "window_width": get_int(
        "FLET_WINDOW_WIDTH",
        1440
    ),

    "window_height": get_int(
        "FLET_WINDOW_HEIGHT",
        900
    ),

    "window_min_width": get_int(
        "FLET_WINDOW_MIN_WIDTH",
        1200
    ),

    "window_min_height": get_int(
        "FLET_WINDOW_MIN_HEIGHT",
        700
    )
}


# ==================================================
# API
# ==================================================

API_CONFIG = {

    "host": get_env(
        "API_HOST",
        "0.0.0.0"
    ),

    "port": get_int(
        "API_PORT",
        8000
    )
}


# ==================================================
# WEBSOCKET
# ==================================================

WS_CONFIG = {

    "host": get_env(
        "WS_HOST",
        "0.0.0.0"
    ),

    "port": get_int(
        "WS_PORT",
        8765
    )
}


# ==================================================
# FEATURE FLAGS
# ==================================================

FEATURE_FLAGS = {

    "realtime": get_bool(
        "ENABLE_REALTIME",
        False
    ),

    "event_stream": get_bool(
        "ENABLE_EVENT_STREAM",
        False
    ),

    "mobile_api": get_bool(
        "ENABLE_MOBILE_API",
        False
    ),

    "distributed_runtime": get_bool(
        "ENABLE_DISTRIBUTED_RUNTIME",
        False
    )
}


# ==================================================
# PATHS
# ==================================================

LOG_DIR = BASE_DIR / "logs"

TEMP_DIR = BASE_DIR / "temp"

BACKUP_DIR = BASE_DIR / "backup"

EXPORT_DIR = BASE_DIR / "export"


# ==================================================
# CREATE DIRS
# ==================================================

for path in [

    LOG_DIR,

    TEMP_DIR,

    BACKUP_DIR,

    EXPORT_DIR
]:

    try:

        path.mkdir(

            parents=True,

            exist_ok=True
        )

    except Exception:

        LOGGER.exception(
            "Erro criando diretório: %s",
            path
        )


# ==================================================
# ENVIRONMENT
# ==================================================

ENVIRONMENT = APP_CONFIG[
    "environment"
]

IS_DEVELOPMENT = (
    ENVIRONMENT == "development"
)

IS_PRODUCTION = (
    ENVIRONMENT == "production"
)


# ==================================================
# LOG STARTUP
# ==================================================

LOGGER.info(
    f"Ambiente: {ENVIRONMENT}"
)

LOGGER.info(
    f"Aplicação: {APP_CONFIG['name']}"
)

LOGGER.info(
    f"SQL Server: {DB_CONFIG['server']}"
)