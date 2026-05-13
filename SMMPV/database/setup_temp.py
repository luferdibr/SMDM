import hashlib
from database.connection import get_connection


def atualizar_admin():

    senha = "AdmA1234!"
    senha_hash = hashlib.sha256(senha.encode()).hexdigest()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE Usuarios
        SET SenhaHash = ?,
            DeveTrocarSenha = 0,
            SenhaTemporaria = 0,
            DataUltimaTrocaSenha = GETDATE()
        WHERE Login = 'admin'
    """, (senha_hash,))

    conn.commit()
    conn.close()

    print("✔ Admin atualizado")
