import pyodbc
from connection import get_connection

def testar():
    conn = get_connection()

    if not conn:
        print("❌ Falha na conexão")
        return

    print("✅ Conectado!")

    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sys.tables")

    for t in cursor.fetchall():
        print("-", t[0])

    conn.close()

if __name__ == "__main__":
    testar()