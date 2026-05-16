import logging

from database.connection import (
    get_connection
)

from security.password_service import (
    gerar_hash,
    validar_politica_senha
)

from services.auditoria_service import (
    registrar_evento
)


# ==================================================
# CONFIG
# ==================================================

ROOT_LEVEL = 100

ADMIN_LEVEL = 50

LOGINS_PROTEGIDOS = {

    "ROOT",

    "SYSTEM",

    "SYS"
}


# ==================================================
# LOGGER
# ==================================================

LOGGER = logging.getLogger(
    "MDM_USER_SERVICE"
)


# ==================================================
# HELPERS
# ==================================================


def normalizar_login(login):

    return str(
        login or ""
    ).strip().upper()



def get_admin_level(usuario):

    if not usuario:
        return 0

    return int(
        usuario.get(
            "admin_level",
            0
        )
    )



def is_root(usuario):

    return (
        get_admin_level(usuario)
        >= ROOT_LEVEL
    )



def auditoria_segura(**kwargs):

    try:

        registrar_evento(**kwargs)

    except Exception:

        LOGGER.exception(
            "AUDITORIA ERROR"
        )



def map_usuario(row):

    return {

        "id": row[0],

        "login": row[1],

        "nome": row[2],

        "perfil_id": row[3],

        "ativo": bool(row[4]),

        "bloqueado": bool(row[5]),

        "tentativas": int(row[6] or 0),

        "deve_trocar": bool(row[7]),

        "ultimo_login": row[8],

        "perfil_nome": row[9],

        "admin_level": int(row[10] or 0),

        "sistema": bool(row[11])
    }


# ==================================================
# PERFIL
# ==================================================


def obter_perfil(cursor, perfil_id):

    cursor.execute("""

        SELECT
            Id,
            Nome,
            Ativo,
            Sistema,
            AdminLevel

        FROM Perfis

        WHERE Id = ?

    """, (perfil_id,))

    row = cursor.fetchone()

    if not row:

        raise Exception(
            "Perfil inválido."
        )

    perfil = {

        "id": row[0],

        "nome": row[1],

        "ativo": bool(row[2]),

        "sistema": bool(row[3]),

        "admin_level": int(row[4] or 0)
    }

    if not perfil["ativo"]:

        raise Exception(
            "Perfil inativo."
        )

    return perfil


# ==================================================
# USUÁRIO
# ==================================================


def obter_usuario(cursor, usuario_id):

    cursor.execute("""

        SELECT
            u.Id,
            u.Login,
            u.Nome,
            u.PerfilId,
            u.Ativo,
            u.Bloqueado,
            u.TentativasLogin,
            u.DeveTrocarSenha,
            u.DataUltimoLogin,

            p.Nome,
            p.AdminLevel,
            p.Sistema

        FROM Usuarios u

        INNER JOIN Perfis p
            ON p.Id = u.PerfilId

        WHERE u.Id = ?

    """, (usuario_id,))

    row = cursor.fetchone()

    if not row:
        return None

    return map_usuario(row)


# ==================================================
# VALIDAÇÕES
# ==================================================


def validar_login(login):

    login = normalizar_login(login)

    if not login:

        raise Exception(
            "Login obrigatório."
        )

    if len(login) < 3:

        raise Exception(
            "Login inválido."
        )

    if login in LOGINS_PROTEGIDOS:

        raise Exception(
            f"Login reservado: {login}"
        )

    return login



def validar_duplicidade(
    cursor,
    login,
    usuario_id=None
):

    if usuario_id:

        cursor.execute("""

            SELECT COUNT(*)

            FROM Usuarios

            WHERE
                UPPER(Login) = ?
                AND Id <> ?

        """, (
            login,
            usuario_id
        ))

    else:

        cursor.execute("""

            SELECT COUNT(*)

            FROM Usuarios

            WHERE UPPER(Login) = ?

        """, (login,))

    if cursor.fetchone()[0]:

        raise Exception(
            "Usuário já existe."
        )



def validar_permissao_perfil(
    usuario_logado,
    perfil
):

    usuario_level = get_admin_level(
        usuario_logado
    )

    if usuario_level >= ROOT_LEVEL:
        return

    if perfil["sistema"]:

        raise Exception(
            "Perfil estrutural protegido."
        )

    if perfil["admin_level"] >= usuario_level:

        raise Exception(
            "Sem permissão para este perfil."
        )



def validar_usuario_alvo(
    usuario_logado,
    usuario_alvo
):

    if not usuario_alvo:

        raise Exception(
            "Usuário inválido."
        )

    usuario_level = get_admin_level(
        usuario_logado
    )

    if usuario_level >= ROOT_LEVEL:
        return

    if usuario_alvo["sistema"]:

        raise Exception(
            "Usuário estrutural protegido."
        )

    if (
        usuario_alvo["admin_level"]
        >= usuario_level
    ):

        raise Exception(
            "Sem permissão para este usuário."
        )


# ==================================================
# LISTAR PERFIS
# ==================================================


def listar_perfis():

    conn = None

    try:

        conn = get_connection()

        cursor = conn.cursor()

        cursor.execute("""

            SELECT
                Id,
                Nome,
                AdminLevel,
                Sistema

            FROM Perfis

            WHERE Ativo = 1

            ORDER BY
                AdminLevel DESC,
                Nome

        """)

        rows = cursor.fetchall()

        retorno = []

        for row in rows:

            retorno.append({

                "id": row[0],

                "nome": row[1],

                "admin_level": int(row[2] or 0),

                "sistema": bool(row[3])
            })

        return retorno

    except Exception:

        LOGGER.exception(
            "LIST PERFIS ERROR"
        )

        raise

    finally:

        try:

            if conn:
                conn.close()

        except Exception:
            pass


# ==================================================
# LISTAR USUÁRIOS
# ==================================================


def listar_usuarios(filtro=""):

    conn = None

    try:

        conn = get_connection()

        cursor = conn.cursor()

        filtro = str(
            filtro or ""
        ).strip()

        query = """

            SELECT
                u.Id,
                u.Login,
                u.Nome,
                u.PerfilId,
                u.Ativo,
                u.Bloqueado,
                u.TentativasLogin,
                u.DeveTrocarSenha,
                u.DataUltimoLogin,

                p.Nome,
                p.AdminLevel,
                p.Sistema

            FROM Usuarios u

            INNER JOIN Perfis p
                ON p.Id = u.PerfilId

        """

        params = []

        if filtro:

            query += """

                WHERE
                    u.Login LIKE ?
                    OR
                    u.Nome LIKE ?

            """

            like = f"%{filtro}%"

            params.extend([
                like,
                like
            ])

        query += """

            ORDER BY
                p.AdminLevel DESC,
                u.Login

        """

        cursor.execute(query, params)

        rows = cursor.fetchall()

        retorno = []

        for row in rows:

            retorno.append(
                map_usuario(row)
            )

        return retorno

    except Exception:

        LOGGER.exception(
            "LIST USERS ERROR"
        )

        raise

    finally:

        try:

            if conn:
                conn.close()

        except Exception:
            pass


# ==================================================
# CRIAR
# ==================================================


def criar_usuario(
    dados,
    usuario_logado
):

    conn = None

    try:

        login = validar_login(
            dados.get("login")
        )

        nome = str(
            dados.get("nome") or login
        ).strip()

        senha = str(
            dados.get("senha") or ""
        ).strip()

        perfil_id = int(
            dados.get("perfil_id")
        )

        politica = validar_politica_senha(
            senha
        )

        if not politica["valida"]:

            raise Exception(
                " | ".join(
                    politica["erros"]
                )
            )

        conn = get_connection()

        cursor = conn.cursor()

        validar_duplicidade(
            cursor,
            login
        )

        perfil = obter_perfil(
            cursor,
            perfil_id
        )

        validar_permissao_perfil(
            usuario_logado,
            perfil
        )

        senha_hash = gerar_hash(
            senha
        )

        cursor.execute("""

            INSERT INTO Usuarios
            (
                Login,
                Nome,
                SenhaHash,
                PerfilId,
                Ativo,
                Bloqueado,
                TentativasLogin,
                DeveTrocarSenha,
                SenhaTemporaria,
                DataUltimaTrocaSenha
            )

            VALUES
            (
                ?, ?, ?, ?,
                ?, 0, 0,
                ?, 0,
                GETDATE()
            )

        """, (

            login,

            nome,

            senha_hash,

            perfil_id,

            int(dados.get("ativo", True)),

            int(dados.get("trocar", False))
        ))

        conn.commit()

        auditoria_segura(

            usuario_id=usuario_logado.get("id"),

            login=usuario_logado.get("login"),

            acao="CRIAR_USUARIO",

            entidade="Usuarios",

            detalhes=f"Login={login}"
        )

        return True

    except Exception:

        if conn:
            conn.rollback()

        LOGGER.exception(
            "CREATE USER ERROR"
        )

        raise

    finally:

        try:

            if conn:
                conn.close()

        except Exception:
            pass


# ==================================================
# UPDATE
# ==================================================


def atualizar_usuario(
    usuario_id,
    dados,
    usuario_logado
):

    conn = None

    try:

        conn = get_connection()

        cursor = conn.cursor()

        usuario_alvo = obter_usuario(
            cursor,
            usuario_id
        )

        validar_usuario_alvo(
            usuario_logado,
            usuario_alvo
        )

        perfil = obter_perfil(
            cursor,
            int(dados["perfil_id"])
        )

        validar_permissao_perfil(
            usuario_logado,
            perfil
        )

        senha = str(
            dados.get("senha") or ""
        ).strip()

        # ==========================================
        # COM SENHA
        # ==========================================

        if senha:

            politica = validar_politica_senha(
                senha
            )

            if not politica["valida"]:

                raise Exception(
                    " | ".join(
                        politica["erros"]
                    )
                )

            senha_hash = gerar_hash(
                senha
            )

            cursor.execute("""

                UPDATE Usuarios

                SET
                    Nome = ?,
                    PerfilId = ?,
                    Ativo = ?,
                    DeveTrocarSenha = ?,
                    SenhaHash = ?,
                    DataUltimaTrocaSenha = GETDATE()

                WHERE Id = ?

            """, (

                dados["nome"],

                dados["perfil_id"],

                int(dados["ativo"]),

                int(dados["trocar"]),

                senha_hash,

                usuario_id
            ))

        # ==========================================
        # SEM SENHA
        # ==========================================

        else:

            cursor.execute("""

                UPDATE Usuarios

                SET
                    Nome = ?,
                    PerfilId = ?,
                    Ativo = ?,
                    DeveTrocarSenha = ?

                WHERE Id = ?

            """, (

                dados["nome"],

                dados["perfil_id"],

                int(dados["ativo"]),

                int(dados["trocar"]),

                usuario_id
            ))

        conn.commit()

        auditoria_segura(

            usuario_id=usuario_logado.get("id"),

            login=usuario_logado.get("login"),

            acao="ALTERAR_USUARIO",

            entidade="Usuarios",

            registro_id=usuario_id,

            detalhes=usuario_alvo["login"]
        )

        return True

    except Exception:

        if conn:
            conn.rollback()

        LOGGER.exception(
            "UPDATE USER ERROR"
        )

        raise

    finally:

        try:

            if conn:
                conn.close()

        except Exception:
            pass


# ==================================================
# DELETE
# ==================================================


def excluir_usuario(
    usuario_id,
    usuario_logado
):

    conn = None

    try:

        conn = get_connection()

        cursor = conn.cursor()

        usuario_alvo = obter_usuario(
            cursor,
            usuario_id
        )

        validar_usuario_alvo(
            usuario_logado,
            usuario_alvo
        )

        if usuario_alvo["login"] == "ROOT":

            raise Exception(
                "ROOT não pode ser removido."
            )

        cursor.execute("""

            DELETE FROM Usuarios

            WHERE Id = ?

        """, (usuario_id,))

        conn.commit()

        auditoria_segura(

            usuario_id=usuario_logado.get("id"),

            login=usuario_logado.get("login"),

            acao="EXCLUIR_USUARIO",

            entidade="Usuarios",

            registro_id=usuario_id,

            detalhes=usuario_alvo["login"]
        )

        return True

    except Exception:

        if conn:
            conn.rollback()

        LOGGER.exception(
            "DELETE USER ERROR"
        )

        raise

    finally:

        try:

            if conn:
                conn.close()

        except Exception:
            pass