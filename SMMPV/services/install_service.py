
import logging
import pyodbc
import hashlib

from config.settings import DB_CONFIG


# ==================================================
# CONFIG
# ==================================================

DATABASE_NAME = DB_CONFIG["database"]

SCHEMA_VERSION = 1

ROOT_LEVEL = 100

ADMIN_LEVEL = 50


# ==================================================
# HELPERS
# ==================================================

def ok(
    mensagem="OK",
    dados=None
):

    return {

        "sucesso": True,

        "mensagem": mensagem,

        "dados": dados
    }


def erro(
    mensagem,
    dados=None
):

    return {

        "sucesso": False,

        "mensagem": str(mensagem),

        "dados": dados
    }


# ==================================================
# CONNECTION STRING
# ==================================================

def build_conn_str(database=None):

    conn = (

        f"DRIVER={DB_CONFIG['driver']};"
        f"SERVER={DB_CONFIG['server']};"
        f"UID={DB_CONFIG['uid']};"
        f"PWD={DB_CONFIG['pwd']};"
        f"Encrypt={DB_CONFIG['encrypt']};"
        f"TrustServerCertificate={DB_CONFIG['trust_cert']};"
        "MARS_Connection=yes;"
    )

    if database:

        conn += f"DATABASE={database};"

    return conn


# ==================================================
# ENCODING
# ==================================================

def configurar_encoding(conn):

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


# ==================================================
# CONNECTIONS