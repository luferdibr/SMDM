
import logging

from database.connection import (
    get_connection
)

from config.settings import (
    APP_CONFIG,
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
# TEST CONNECTION
# ==================================================

def test_connection():

    conn = None

    try:

        logging.info(

            "================================="
        )

        logging.info(

            "TESTE DE CONEXÃO SQL SERVER"
        )

        logging.info(

            "================================="
        )

        logging.info(

            (
                f"Sistema: "
                f"{APP_CONFIG['name']}"
            )
        )

        logging.info(

            (
                f"Servidor: "
                f"{DB_CONFIG['host']}"
            )
        )

        logging.info(

            (
                f"Porta: "
                f"{DB_CONFIG['port']}"
            )
        )

        logging.info(

            (
                f"Banco: "
                f"{DB_CONFIG['database']}"
            )
        )

        logging.info(

            (
                f"Usuário: "
                f"{DB_CONFIG['uid']}"
            )
        )

        conn = get_connection()

        cursor = conn.cursor()

        # ==========================================
        # SQL SERVER VERSION
        # ==========================================

        cursor.execute(

            "SELECT @@VERSION"
        )

        version = cursor.fetchone()

        logging.info(

            "================================="
        )

        logging.info(

            "CONECTADO COM SUCESSO"
        )

        logging.info(

            "================================="
        )

        if version:

            logging.info(

                (
                    f"Versão SQL: "
                    f"{version[0]}"
                )
            )

        # ==========================================
        # DATABASE
        # ==========================================

        cursor.execute(

            "SELECT DB_NAME()"
        )

        db = cursor.fetchone()

        if db:

            logging.info(

                (
                    f"Database ativa: "
                    f"{db[0]}"
                )
            )

        # ==========================================
        # USER
        # ==========================================

        cursor.execute(

            "SELECT SYSTEM_USER"
        )

        user = cursor.fetchone()

        if user:

            logging.info(

                (
                    f"Usuário SQL: "
                    f"{user[0]}"
                )
            )

        logging.info(

            "================================="
        )

        return True

    except Exception as ex:

        logging.exception(

            "ERRO TESTE SQL SERVER"
        )

        logging.error(

            (
                f"Erro: {str(ex)}"
            )
        )

        return False

    finally:

        try:

            if conn:

                conn.close()

                logging.info(

                    "Conexão encerrada."
                )

        except Exception:

            pass


# ==================================================
# MAIN
# ==================================================

if __name__ == "__main__":

    ok = test_connection()

    print()

    if ok:

        print(
            "[OK] SQL Server conectado."
        )

    else:

        print(
            "[ERRO] Falha conexão SQL."
        )

    print()