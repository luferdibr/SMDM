import pyodbc
from config.settings import DB_CONFIG


def get_connection():
    try:
        return pyodbc.connect(
            f"SERVER={DB_CONFIG['server']};"
            f"DATABASE={DB_CONFIG['database']};"
            f"UID={DB_CONFIG['user']};"
            f"PWD={DB_CONFIG['password']};"
        )
    except Exception as e:
        print("Erro:", e)
        return None