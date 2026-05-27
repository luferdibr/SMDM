
import logging
import pyodbc

from config.settings import (
    DB_CONFIG
)


# ==================================================
# LOGGER
# ==================================================

LOGGER = logging.getLogger(
    "MDM_DATABASE"
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
# CONFIG
# ==================================================

pyodbc.pooling = True


# ==================================================
# HELPERS
# ==================================================

def bool_to_sqlserver(valor):

    return "yes" if valor else "no"


def validar_config():

    obrigatorios = [

        "driver",

        "server",

        "database",

        "user",

        "password"
    ]

    for chave in obrigatorios:

        valor = DB_CONFIG.get(chave)

        if not valor:

            raise Exception(
                f"DB_CONFIG inválido: {chave}"
            )


def build_connection_string(

    database=None
):

    validar_config()

    driver = DB_CONFIG["driver"]

    server = DB_CONFIG["server"]

    db_name = database or DB_CONFIG["database"]

    user = DB_CONFIG["user"]

    password = DB_CONFIG["password"]

    encrypt = bool_to_sqlserver(
        DB_CONFIG.get(
            "encrypt",
            False
        )
    )

    trust_cert = bool_to_sqlserver(
        DB_CONFIG.get(
            "trust_cert",
            True
        )
    )

    timeout = int(
        DB_CONFIG.get(
            "timeout",
            30
        )
    )

    app_name = DB_CONFIG.get(
        "app_name",
        "MDM"
    )

    return (

        f"DRIVER={{{driver}}};"

        f"SERVER={server};"

        f"DATABASE={db_name};"

        f"UID={user};"

        f"PWD={password};"

        f"Encrypt={encrypt};"

        f"TrustServerCertificate={trust_cert};"

        f"Connection Timeout={timeout};"

        f"APP={app_name};"

        f"MARS_Connection=yes;"
    )


# ==================================================
# CONNECTION
# ==================================================

def get_connection():

    try:

        conn_string = build_connection_string()

        conn = pyodbc.connect(

            conn_string,

            autocommit=False
        )

        LOGGER.info(

            (
                f"Conexão SQL aberta "
                f"[{DB_CONFIG['server']}]"
            )
        )

        return conn

    except Exception as ex:

        LOGGER.exception(
            "DATABASE CONNECTION ERROR"
        )

        raise Exception(

            (
                "Erro ao conectar "
                "ao SQL Server.\n\n"
                f"{str(ex)}"
            )
        )


# ==================================================
# MASTER CONNECTION
# ==================================================

def get_master_connection():

    try:

        conn_string = build_connection_string(
            database="master"
        )

        conn = pyodbc.connect(

            conn_string,

            autocommit=False
        )

        LOGGER.info(

            (
                f"Conexão MASTER aberta "
                f"[{DB_CONFIG['server']}]"
            )
        )

        return conn

    except Exception as ex:

        LOGGER.exception(
            "MASTER CONNECTION ERROR"
        )

        raise Exception(

            (
                "Erro ao conectar "
                "na base MASTER.\n\n"
                f"{str(ex)}"
            )
        )


# ==================================================
# TEST CONNECTION
# ==================================================

def testar_conexao():

    conn = None

    try:

        conn = get_connection()

        cursor = conn.cursor()

        cursor.execute(
            "SELECT @@VERSION"
        )

        versao = cursor.fetchone()[0]

        LOGGER.info(
            "Conexão validada."
        )

        return {

            "ok": True,

            "versao": versao
        }

    except Exception as ex:

        LOGGER.exception(
            "TEST CONNECTION ERROR"
        )

        return {

            "ok": False,

            "erro": str(ex)
        }

    finally:

        try:

            if conn:
                conn.close()

        except Exception:
            pass


# ==================================================
# EXECUTE
# ==================================================

def execute_scalar(

    query,

    params=None
):

    conn = None

    try:

        conn = get_connection()

        cursor = conn.cursor()

        cursor.execute(

            query,

            params or []
        )

        row = cursor.fetchone()

        conn.commit()

        if not row:
            return None

        return row[0]

    except Exception:

        if conn:
            conn.rollback()

        LOGGER.exception(
            "EXECUTE SCALAR ERROR"
        )

        raise

    finally:

        try:

            if conn:
                conn.close()

        except Exception:
            pass


def execute_non_query(

    query,

    params=None
):

    conn = None

    try:

        conn = get_connection()

        cursor = conn.cursor()

        cursor.execute(

            query,

            params or []
        )

        conn.commit()

        return True

    except Exception:

        if conn:
            conn.rollback()

        LOGGER.exception(
            "EXECUTE NON QUERY ERROR"
        )

        raise

    finally:

        try:

            if conn:
                conn.close()

        except Exception:
            pass


def execute_query(

    query,

    params=None
):

    conn = None

    try:

        conn = get_connection()

        cursor = conn.cursor()

        cursor.execute(

            query,

            params or []
        )

        columns = [

            column[0]

            for column in cursor.description
        ]

        rows = cursor.fetchall()

        retorno = []

        for row in rows:

            retorno.append(

                dict(
                    zip(columns, row)
                )
            )

        return retorno

    except Exception:

        LOGGER.exception(
            "EXECUTE QUERY ERROR"
        )

        raise

    finally:

        try:

            if conn:
                conn.close()

        except Exception:
            pass