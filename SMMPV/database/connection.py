import logging

import pyodbc

from config.settings import (
    DB_CONFIG
)


# ==================================================
# LOGGING
# ==================================================

logging.basicConfig(

    level=logging.INFO,

    format=(
        "%(asctime)s "
        "[%(levelname)s] "
        "%(message)s"
    )
)


# ==================================================
# CONNECTION STRING
# ==================================================

CONNECTION_STRING = (

    f"DRIVER={DB_CONFIG['driver']};"

    f"SERVER={DB_CONFIG['server']};"

    f"DATABASE={DB_CONFIG['database']};"

    f"UID={DB_CONFIG['uid']};"

    f"PWD={DB_CONFIG['pwd']};"

    f"Encrypt={DB_CONFIG['encrypt']};"

    f"TrustServerCertificate={DB_CONFIG['trust_cert']};"

    "MARS_Connection=yes;"
)


# ==================================================
# CONNECTION
# ==================================================

def get_connection():

    try:

        conn = pyodbc.connect(

            CONNECTION_STRING,

            timeout=DB_CONFIG.get(

                "timeout",

                30
            )
        )

        # ==========================================
        # LATIN1 / SQL SERVER LEGADO
        # ==========================================

        conn.setdecoding(

            pyodbc.SQL_CHAR,

            encoding="latin1"
        )

        conn.setdecoding(

            pyodbc.SQL_WCHAR,

            encoding="utf-16le"
        )

        conn.setencoding(

            encoding="latin1"
        )

        logging.info(

            "Conexão SQL aberta."
        )

        return conn

    except Exception:

        logging.exception(

            "Erro conexão SQL"
        )

        raise