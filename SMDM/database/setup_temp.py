from config.settings import ADMIN_CONFIG
from database.connection import get_connection
from security.password_service import gerar_hash


def atualizar_senha_usuario_sistema(
    login,
    senha,
    deve_trocar,
    senha_temporaria,
):

    senha_hash = gerar_hash(senha)

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE Usuarios
        SET SenhaHash = ?,
            DeveTrocarSenha = ?,
            SenhaTemporaria = ?,
            DataUltimaTrocaSenha = GETDATE()
        WHERE Login = ?
    """, (
        senha_hash,
        1 if deve_trocar else 0,
        1 if senha_temporaria else 0,
        login,
    ))

    conn.commit()
    conn.close()

    print(f"Senha atualizada: {login}")


def atualizar_admin():

    atualizar_senha_usuario_sistema(
        login=ADMIN_CONFIG["admin_login"],
        senha=ADMIN_CONFIG["admin_senha"],
        deve_trocar=True,
        senha_temporaria=True,
    )


def recuperar_root():

    atualizar_senha_usuario_sistema(
        login=ADMIN_CONFIG["root_login"],
        senha=ADMIN_CONFIG["root_senha"],
        deve_trocar=False,
        senha_temporaria=False,
    )
