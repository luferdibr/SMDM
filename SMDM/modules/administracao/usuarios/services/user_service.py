import logging

from database.connection import (
    get_connection
)

from security.password_service import (
    gerar_hash,
    validar_politica_senha
)

from config.settings import (
    ADMIN_CONFIG,
)

from services.auditoria_service import (
    registrar_evento
)

from services.identity_service import (
    coluna_eh_identity,
    obter_proximo_id,
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


def is_admin(usuario):

    return (
        get_admin_level(usuario)
        >= ADMIN_LEVEL
    )


def validar_operador_admin(usuario_logado):

    if not is_admin(usuario_logado):

        raise Exception(
            "Acesso restrito à administração."
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

        "email": row[3],

        "perfil_id": row[4],

        "ativo": bool(row[5]),

        "bloqueado": bool(row[6]),

        "tentativas": int(row[7] or 0),

        "deve_trocar": bool(row[8]),

        "ultimo_login": row[9],

        "perfil_nome": row[10],

        "admin_level": int(row[11] or 0),

        "sistema": bool(row[12])
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
            u.Email,
            u.PerfilId,
            u.Ativo,
            u.Bloqueado,
            u.TentativasLogin,
            u.DeveTrocarSenha,
            u.UltimoLogin,

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

    validar_operador_admin(
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

    validar_operador_admin(
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


def contar_admins_ativos(
    cursor,
):

    cursor.execute("""

        SELECT COUNT(*)

        FROM Usuarios u

        INNER JOIN Perfis p
            ON p.Id = u.PerfilId

        WHERE
            u.Ativo = 1
            AND u.Bloqueado = 0
            AND p.AdminLevel >= ?
            AND p.AdminLevel < ?

    """, (
        ADMIN_LEVEL,
        ROOT_LEVEL,
    ))

    return int(
        cursor.fetchone()[0] or 0
    )


def validar_login_imutavel(
    dados,
    usuario_alvo,
):

    login_novo = dados.get(
        "login"
    )

    if login_novo in (
        None,
        "",
    ):

        return

    if normalizar_login(login_novo) != normalizar_login(
        usuario_alvo["login"]
    ):

        raise Exception(
            "Login não pode ser alterado."
        )


def validar_desativacao_admin_unico(
    cursor,
    usuario_logado,
    usuario_alvo,
    novo_ativo,
):

    if novo_ativo:

        return

    if not usuario_alvo.get(
        "ativo"
    ):

        return

    admin_level_alvo = int(
        usuario_alvo.get(
            "admin_level",
            0,
        )
    )

    if not (
        ADMIN_LEVEL <= admin_level_alvo < ROOT_LEVEL
    ):

        return

    if contar_admins_ativos(cursor) > 1:

        return

    if is_root(usuario_logado):

        return

    raise Exception(
        "Somente ROOT pode desabilitar o único ADMIN."
    )


def validar_perfil_root_unico(
    login,
    perfil,
):

    login_root = normalizar_login(
        ADMIN_CONFIG["root_login"]
    )

    login = normalizar_login(
        login
    )

    if int(perfil.get("admin_level", 0)) < ROOT_LEVEL:

        return

    if login == login_root:

        return

    raise Exception(
        "Perfil ROOT é exclusivo do usuário ROOT."
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
                u.Email,
                u.PerfilId,
                u.Ativo,
                u.Bloqueado,
                u.TentativasLogin,
                u.DeveTrocarSenha,
                u.UltimoLogin,

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

        validar_operador_admin(
            usuario_logado
        )

        login = validar_login(
            dados.get("login")
        )

        nome = str(
            dados.get("nome") or login
        ).strip()

        email = str(
            dados.get("email") or ""
        ).strip() or None

        senha = str(
            ADMIN_CONFIG["admin_senha"]
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

        validar_perfil_root_unico(
            login,
            perfil
        )

        validar_permissao_perfil(
            usuario_logado,
            perfil
        )

        senha_hash = gerar_hash(
            senha
        )

        if coluna_eh_identity(
            cursor,
            "Usuarios",
            "Id",
        ):

<<<<<<< HEAD
            INSERT INTO Usuarios
            (
                Login,
                Nome,
                Email,
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
                ?, ?, ?, ?, ?,
                ?, 0, 0,
                1, 1,
                GETDATE()
            )
=======
            cursor.execute("""

                INSERT INTO Usuarios
                (
                    Login,
                    Nome,
                    Email,
                    SenhaHash,
                    PerfilId,
                    Ativo,
                    Bloqueado,
                    TentativasLogin,
                    DeveTrocarSenha,
                    SenhaTemporaria,
                    DataUltimaTrocaSenha
                )
>>>>>>> 25/05/2026 - 12:09

                VALUES
                (
                    ?, ?, ?, ?, ?,
                    ?, 0, 0,
                    1, 1,
                    GETDATE()
                )

            """, (

                login,

<<<<<<< HEAD
            email,

            senha_hash,
=======
                nome,
>>>>>>> 25/05/2026 - 12:09

                email,

<<<<<<< HEAD
            int(dados.get("ativo", True)),
        ))
=======
                senha_hash,

                perfil_id,

                int(dados.get("ativo", True)),
            ))

        else:

            cursor.execute("""

                INSERT INTO Usuarios
                (
                    Id,
                    Login,
                    Nome,
                    Email,
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
                    ?, ?, ?, ?, ?, ?,
                    ?, 0, 0,
                    1, 1,
                    GETDATE()
                )

            """, (

                obter_proximo_id(
                    cursor,
                    "Usuarios",
                    "Id",
                ),

                login,

                nome,

                email,

                senha_hash,

                perfil_id,

                int(dados.get("ativo", True)),
            ))
>>>>>>> 25/05/2026 - 12:09

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

        validar_login_imutavel(
            dados,
            usuario_alvo
        )

        perfil = obter_perfil(
            cursor,
            int(dados["perfil_id"])
        )

        validar_perfil_root_unico(
            usuario_alvo["login"],
            perfil
        )

        validar_permissao_perfil(
            usuario_logado,
            perfil
        )

        senha = str(
            dados.get("senha") or ""
        ).strip()

        ativo = int(
            bool(
                dados.get(
                    "ativo",
                    True,
                )
            )
        )

        deve_trocar = int(
            bool(
                dados.get(
                    "trocar",
                    dados.get(
                        "deve_trocar",
                        False,
                    ),
                )
            )
        )

        senha_temporaria = int(
            bool(
                senha
                and
                deve_trocar
            )
        )

        validar_desativacao_admin_unico(
            cursor,
            usuario_logado,
            usuario_alvo,
            bool(ativo),
        )

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
                    Email = ?,
                    PerfilId = ?,
                    Ativo = ?,
                    DeveTrocarSenha = ?,
                    SenhaTemporaria = ?,
                    SenhaHash = ?,
                    DataUltimaTrocaSenha = GETDATE()

                WHERE Id = ?

            """, (

                dados["nome"],

                str(
                    dados.get("email")
                    or ""
                ).strip() or None,

                dados["perfil_id"],

                ativo,

                deve_trocar,

                senha_temporaria,

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
                    Email = ?,
                    PerfilId = ?,
                    Ativo = ?,
                    DeveTrocarSenha = ?,
                    SenhaTemporaria = ?

                WHERE Id = ?

            """, (

                dados["nome"],

                str(
                    dados.get("email")
                    or ""
                ).strip() or None,

                dados["perfil_id"],

                ativo,

                deve_trocar,

                deve_trocar,

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


# ==================================================
# RESET SENHA
# ==================================================

def resetar_senha_usuario(
    usuario_id,
    usuario_logado,
    nova_senha=None,
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

        senha = str(
            nova_senha
            or ADMIN_CONFIG["admin_senha"]
        ).strip()

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
                SenhaHash = ?,
                DeveTrocarSenha = 1,
                SenhaTemporaria = 1,
                DataUltimaTrocaSenha = GETDATE()

            WHERE Id = ?

        """, (

            senha_hash,

            usuario_id
        ))

        conn.commit()

        auditoria_segura(

            usuario_id=usuario_logado.get("id"),

            login=usuario_logado.get("login"),

            acao="RESETAR_SENHA",

            entidade="Usuarios",

            registro_id=usuario_id,

            detalhes=usuario_alvo["login"]
        )

        return True

    except Exception:

        if conn:
            conn.rollback()

        LOGGER.exception(
            "RESET PASSWORD ERROR"
        )

        raise

    finally:

        try:

            if conn:
                conn.close()

        except Exception:
            pass


# ==================================================
# ALTERAR SENHA PRÓPRIA
# ==================================================

def validar_senha(
    senha,
):

    return validar_politica_senha(
        senha
    )["valida"]


def alterar_senha(
    usuario_id,
    nova_senha,
):

    conn = None

    try:

        senha = str(
            nova_senha or ""
        ).strip()

        politica = validar_politica_senha(
            senha
        )

        if not politica["valida"]:

            return {

                "sucesso": False,

                "mensagem": " | ".join(
                    politica["erros"]
                )
            }

        conn = get_connection()

        cursor = conn.cursor()

        usuario_alvo = obter_usuario(
            cursor,
            usuario_id,
        )

        if not usuario_alvo:

            return {

                "sucesso": False,

                "mensagem": "Usuário inválido."
            }

        senha_hash = gerar_hash(
            senha
        )

        cursor.execute("""

            UPDATE Usuarios

            SET
                SenhaHash = ?,
                DeveTrocarSenha = 0,
                SenhaTemporaria = 0,
                DataUltimaTrocaSenha = GETDATE()

            WHERE Id = ?

        """, (

            senha_hash,

            usuario_id,
        ))

        conn.commit()

        auditoria_segura(

            usuario_id=usuario_id,

            login=usuario_alvo["login"],

            acao="ALTERAR_SENHA",

            entidade="Usuarios",

            registro_id=usuario_id,

            detalhes=usuario_alvo["login"]
        )

        return {

            "sucesso": True,

            "mensagem": "Senha alterada com sucesso."
        }

    except Exception as ex:

        if conn:
            conn.rollback()

        LOGGER.exception(
            "CHANGE OWN PASSWORD ERROR"
        )

        return {

            "sucesso": False,

            "mensagem": str(ex)
        }

    finally:

        try:

            if conn:
                conn.close()

        except Exception:
            pass
