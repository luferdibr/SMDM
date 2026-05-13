
import os
import logging

from pathlib import Path

from dotenv import load_dotenv


# ==================================================
# BASE PATH
# ==================================================

BASE_DIR = Path(
    __file__
).resolve().parent.parent


# ==================================================
# LOAD ENV
# ==================================================

load_dotenv(
    BASE_DIR / ".env"
)


# ==================================================
# HELPERS
# ==================================================

def get_env(
    key,
    default=None
):

    value = os.getenv(
        key,
        default
    )

    if isinstance(value, str):

        value = value.strip()

    return value


def get_bool(
    key,
    default=False
):

    value = str(

        get_env(
            key,
            str(default)
        )

    ).strip().lower()

    return value in (

        "1",
        "true",
        "yes",
        "y",
        "on"
    )


def get_int(
    key,
    default=0
):

    try:

        return int(
            get_env(
                key,
                default
            )
        )

    except Exception:

        logging.warning(
            "ENV inválida: %s",
            key
        )

        return default


# ==================================================
# APP
# ==================================================

APP_NAME = get_env(
    "APP_NAME",
    "SMMPV ERP"
)

APP_VERSION = get_env(
    "APP_VERSION",
    "1.0.0"
)

APP_ENV = get_env(
    "APP_ENV",
    "DEV"
).upper()

SECRET_KEY = get_env(
    "SECRET_KEY",
    "SMMPV_DEV_SECRET"
)


# ==================================================
# RBAC
# ==================================================

ROOT_LEVEL = get_int(
    "ROOT_LEVEL",
    100
)

ADMIN_LEVEL = get_int(
    "ADMIN_LEVEL",
    50
)


# ==================================================
# SESSION
# ==================================================

SESSION_TIMEOUT_MINUTES = get_int(
    "SESSION_TIMEOUT_MINUTES",
    60
)


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

        logging.exception(
            "Erro criando diretório: %s",
            path
        )


# ==================================================
# LOGGING
# ==================================================

LOG_LEVEL = get_env(
    "LOG_LEVEL",
    "INFO"
).upper()

LOG_TO_FILE = get_bool(
    "LOG_TO_FILE",
    False
)

logging.basicConfig(

    level=getattr(
        logging,
        LOG_LEVEL,
        logging.INFO
    ),

    format=(
        "%(asctime)s "
        "[%(levelname)s] "
        "%(message)s"
    )
)


# ==================================================
# DATABASE
# ==================================================

DB_CONFIG = {

    # ==============================================
    # SQL SERVER
    # ==============================================

    "driver": get_env(
        "DB_DRIVER",
        "{SQL Server}"
    ),

    "server": get_env(
        "DB_SERVER",
        "localhost"
    ),

    "database": get_env(
        "DB_NAME",
        "SMMPV"
    ),

    # ==============================================
    # LOGIN
    # ==============================================

    "uid": get_env(
        "DB_USER",
        "sa"
    ),

    "pwd": get_env(
        "DB_PASSWORD",
        ""
    ),

    # ==============================================
    # SEGURANÇA
    # ==============================================

    "encrypt": get_env(
        "DB_ENCRYPT",
        "no"
    ).lower(),

    "trust_cert": get_env(
        "DB_TRUST_CERT",
        "yes"
    ).lower(),

    # ==============================================
    # TIMEOUT
    # ==============================================

    "timeout": get_int(
        "DB_TIMEOUT",
        30
    )
}


# ==================================================
# ADMIN PADRÃO
# ==================================================

ADMIN_CONFIG = {

    "login": get_env(
        "ADMIN_LOGIN",
        "ROOT"
    ).upper(),

    "password": get_env(
        "ADMIN_PASSWORD",
        "RootAdmin@2026"
    ),

    "force_change": get_bool(
        "ADMIN_FORCE_CHANGE",
        True
    )
}


# ==================================================
# SECURITY
# ==================================================

SECURITY = {

    # ==============================================
    # LOGIN
    # ==============================================

    "max_login_attempts": get_int(
        "MAX_LOGIN_ATTEMPTS",
        5
    ),

    # ==============================================
    # SENHA
    # ==============================================

    "password_min_length": get_int(
        "PASSWORD_MIN_LENGTH",
        9
    ),

    "password_expire_days": get_int(
        "PASSWORD_EXPIRE_DAYS",
        90
    ),

    # ==============================================
    # HASH
    # ==============================================

    "bcrypt_rounds": get_int(
        "BCRYPT_ROUNDS",
        12
    )
}


# ==================================================
# AUDITORIA
# ==================================================

AUDITORIA = {

    "enabled": get_bool(
        "AUDITORIA_ENABLED",
        True
    ),

    "log_login": get_bool(
        "AUDITORIA_LOGIN",
        True
    ),

    "log_admin": get_bool(
        "AUDITORIA_ADMIN",
        True
    )
}


# ==================================================
# HELPERS APP
# ==================================================

def is_dev():

    return APP_ENV == "DEV"


def is_prod():

    return APP_ENV == "PROD"


def is_test():

    return APP_ENV == "TEST"


# ==================================================
# VALIDAR CONFIG
# ==================================================

def validar_config():

    erros = []

    # ==============================================
    # DATABASE
    # ==============================================

    if not DB_CONFIG["server"]:

        erros.append(
            "DB_SERVER não configurado."
        )

    if not DB_CONFIG["database"]:

        erros.append(
            "DB_NAME não configurado."
        )

    # ==============================================
    # PRODUÇÃO
    # ==============================================

    if is_prod():

        if not SECRET_KEY:

            erros.append(
                "SECRET_KEY obrigatória em PROD."
            )

        if len(
            ADMIN_CONFIG["password"]
        ) < SECURITY["password_min_length"]:

            erros.append(
                "ADMIN_PASSWORD insegura."
            )

        if SECURITY["bcrypt_rounds"] < 10:

            erros.append(
                "BCRYPT_ROUNDS inseguro."
            )

        if DB_CONFIG["encrypt"] != "yes":

            erros.append(
                "DB_ENCRYPT obrigatório em PROD."
            )

    # ==============================================
    # RESULTADO
    # ==============================================

    if erros:

        for erro in erros:

            logging.error(erro)

        raise Exception(
            "Configuração inválida."
        )

    logging.info(
        "Configurações carregadas."
    )


# ==================================================
# STARTUP
# ==================================================

validar_config()
