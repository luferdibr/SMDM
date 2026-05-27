import sys

from pathlib import Path


APP_DIR = Path(__file__).resolve().parent.parent

if str(APP_DIR) not in sys.path:

    sys.path.insert(
        0,
        str(APP_DIR),
    )


from config.settings import ADMIN_CONFIG
from database.setup_temp import atualizar_senha_usuario_sistema


CONFIRMACAO = "RECUPERAR ROOT"


def recuperar_root():

    login_root = ADMIN_CONFIG["root_login"]

    print(
        "Recuperação local do ROOT"
    )

    print(
        "Esta rotina deve ser executada apenas no servidor "
        "ou estação técnica autorizada."
    )

    print(
        "A senha será restaurada a partir de ADMIN_ROOT_PASSWORD "
        "configurado no ambiente."
    )

    confirmacao = input(
        f"Digite '{CONFIRMACAO}' para continuar: "
    ).strip().upper()

    if confirmacao != CONFIRMACAO:

        print(
            "Operação cancelada."
        )

        return False

    atualizar_senha_usuario_sistema(
        login=login_root,
        senha=ADMIN_CONFIG["root_senha"],
        deve_trocar=False,
        senha_temporaria=False,
    )

    print(
        "ROOT recuperado. A senha não foi exibida."
    )

    return True


if __name__ == "__main__":

    recuperar_root()
