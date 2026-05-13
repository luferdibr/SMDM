
import logging
import re

from database.connection import (
    get_connection
)

from services.auth_service import (
    gerar_hash,
    validar_hash
)

from services.auditoria_service import (
    registrar_evento
)

from config.settings import (
    ADMIN_CONFIG
)


# ==================================================
# CONFIG
# ==================================================

ROOT_LEVEL = 100

ADMIN_LEVEL = 50

SENHA_PADRAO = ADMIN_CONFIG["password"]

LOGINS_RESERVADOS = {

    "ROOT",

    "SYSTEM",

    "SYS"
}


# ==================================================
# HELPERS
# ==================================================

def retorno(
    sucesso,
    mensagem="",
    dados=None
):

    return {

        "sucesso": bool(sucesso),

        "mensagem": str(mensagem),

        "dados": dados
    }


def auditoria_segura(**kwargs):

    try:

        registrar_evento(**kwargs)

    except Exception:

        logging.exception(
            "AUDITORIA ERROR"
        )


def normalizar_login(login):

    return str(
        login or ""
    ).strip().upper()


def is_root(usuario):

    return bool(
        usuario
        and
        int(
            usuario.get(
                "admin_level",
                0
            )
        ) >= ROOT_LEVEL
    )


def get_admin_level(usuario):

    if not usuario:
        return 0

    return int(
        usuario.get(
            "admin_level",
            0
        )
    )


# ==================================================
# SENHA
# ==================================================

def validar_senha(senha):

    senha = str(
        senha or ""
    ).strip()

    if len(senha) < 9:
        return False

    if senha == SENHA_PADRAO:
        return False

    tem_letra = bool(
        re.search(
            r"[A-Za-z]",
            senha
        )
    )

    tem_numero = bool(
        re.search(
            r"\d",
            senha
        )
    )

    tem_simbolo = bool(
        re.search(
            r"[!@#$%&*()_+=\-]",
            senha
        )
    )

    return bool(
        tem_letra
        and
        tem_numero
        and
        tem_simbolo
    )


# ==================================================
# PERFIL
# ==================================================

def map_perfil(row):

    return {

        "id": row[0],

        "nome": row[1],

        "ativo": bool(row[2]),

        "sistema": bool(row[3]),

        "admin_level": int(row[4] or 0)
    }


def obter_perfil(
    cursor,
    perfil_id
):

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
        return None

    return map_perfil(row)


# ==================================================
# USER
# ==================================================

def map_usuario(row):

    return {

        "id": row[0],

        "login": row[1],

        "nome": row[2],

        "perfil_id": row[3],

        "ativo": bool(row[4]),

        "bloqueado": bool(row[5]),

        "tentativas": int(row[6] or 0),

        "ultimo_login": row[7],

        "sistema": bool(row[8]),

        "admin_level": int(row[9] or 0),

        "perfil_nome": row[10]
    }


def obter_usuario(
    cursor,
    user_id
):

    cursor.execute("""

        SELECT
            u.Id,
            u.Login,
            u.Nome,
            u.PerfilId,
            u.Ativo,
            u.Bloqueado,
            u.TentativasLogin,
            u.DataUltimoLogin,

            p.Sistema,
            p.AdminLevel,
            p.Nome

        FROM Usuarios u

        INNER JOIN Perfis p
            ON p.Id = u.PerfilId

        WHERE u.Id = ?

    """, (user_id,))

    row = cursor.fetchone()

    if not row:
        return None

    return map_usuario(row)


# ==================================================
# SEGURANÇA
# ==================================================

def validar_login(login):

    login = normalizar_login(
        login
    )

    if not login:

        raise Exception(
            "Login obrigatório."
        )

    if len(login) < 3:

        raise Exception(
            "Login muito curto."
        )

    if login in LOGINS_RESERVADOS:

        raise Exception(
            f"Login reservado: {login}"
        )

    return login


def validar_perfil(
    perfil
):

    if not perfil:

        raise Exception(
            "Perfil inválido."
        )

    if not perfil["ativo"]:

        raise Exception(
            "Perfil inativo."
        )


def validar_permissao_perfil(
    usuario_logado,
    perfil
):

    if not usuario_logado:

        raise Exception(
            "Usuário inválido."
        )

    validar_perfil(perfil)

    usuario_level = get_admin_level(
        usuario_logado
    )

    # ==============================================
    # ROOT
    # ==============================================

    if usuario_level >= ROOT_LEVEL:
        return

    # ==============================================
    # PERFIL SISTEMA
    # ==============================================

    if perfil["sistema"]:

        raise Exception(
            "Perfil estrutural protegido."
        )

    # ==============================================
    # NÍVEL
    # ==============================================

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

    # ==============================================
    # ROOT
    # ==============================================

    if usuario_level >= ROOT_LEVEL:
        return

    # ==============================================
    # SISTEMA
    # ==============================================

    if usuario_alvo["sistema"]:

        raise Exception(
            "Usuário estrutural protegido."
        )

    # ==============================================
    # LEVEL
    # ==============================================

    if usuario_alvo["admin_level"] >= usuario_level:

        raise Exception(
            "Sem permissão para este usuário."
        )


# ==================================================
# DUPLICIDADE
# ==================================================

def validar_duplicidade(
    cursor,
    login,
    user_id=None
):

    if user_id:

        cursor.execute("""

            SELECT COUNT(*)

            FROM Usuarios

            WHERE
                UPPER(Login) = ?
                AND Id <> ?

        """, (
            login,
            user_id
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


# ==================================================
# LISTAR PERFIS
# ==================================================

def listar_perfis(usuario_logado):

    conn = None

    try:

        conn = get_connection()

        cursor = conn.cursor()

        usuario_level = get_admin_level(
            usuario_logado
        )

        cursor.execute("""

            SELECT
                Id,
                Nome,
                Sistema,
                AdminLevel

            FROM Perfis

            WHERE Ativo = 1

            ORDER BY
                AdminLevel DESC,
                Nome

        """)

        rows = cursor.fetchall()

        perfis = []

        for r in rows:

            sistema = bool(r[2])

            admin_level = int(r[3] or 0)

            if not is_root(usuario_logado):

                if sistema:
                    continue

                if admin_level >= usuario_level:
                    continue

            perfis.append({

                "id": r[0],

                "nome": r[1],

                "sistema": sistema,

                "admin_level": admin_level
            })

        return retorno(
            True,
            dados=perfis
        )

    except Exception as ex:

        logging.exception(
            "LIST PERFIS ERROR"
        )

        return retorno(
            False,
            str(ex),
            []
        )

    finally:

        try:

            if conn:
                conn.close()

        except Exception:
            pass


# ==================================================
# LISTAR USERS
# ==================================================

def listar_usuarios(usuario_logado):

    conn = None

    try:

        conn = get_connection()

        cursor = conn.cursor()

        usuario_level = get_admin_level(
            usuario_logado
        )

        cursor.execute("""

            SELECT
                u.Id,
                u.Login,
                u.Nome,
                u.Ativo,
                u.Bloqueado,
                u.TentativasLogin,
                u.DataUltimoLogin,

                p.Sistema,
                p.AdminLevel,
                p.Nome

            FROM Usuarios u

            INNER JOIN Perfis p
                ON p.Id = u.PerfilId

            ORDER BY
                p.AdminLevel DESC,
                u.Login

        """)

        rows = cursor.fetchall()

        usuarios = []

        for r in rows:

            sistema = bool(r[7])

            admin_level = int(r[8] or 0)

            if not is_root(usuario_logado):

                if sistema:
                    continue

                if admin_level >= usuario_level:
                    continue

            usuarios.append({

                "id": r[0],

                "login": r[1],

                "nome": r[2],

                "ativo": bool(r[3]),

                "bloqueado": bool(r[4]),

                "tentativas": int(r[5] or 0),

                "ultimo_login": r[6],

                "sistema": sistema,

                "admin_level": admin_level,

                "perfil_nome": r[9]
            })

        return retorno(
            True,
            dados=usuarios
        )

    except Exception as ex:

        logging.exception(
            "USER LIST ERROR"
        )

        return retorno(
            False,
            str(ex),
            []
        )

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
    usuario_logado,
    login,
    nome,
    perfil_id
):

    conn = None

    try:

        login = validar_login(
            login
        )

        nome = str(
            nome or login
        ).strip()

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
            SENHA_PADRAO
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
                SenhaMigrada
            )

            OUTPUT INSERTED.Id

            VALUES
            (
                ?, ?, ?,
                ?,
                1,
                0,
                0,
                1,
                1,
                1
            )

        """, (

            login,
            nome,
            senha_hash,
            perfil_id
        ))

        user_id = cursor.fetchone()[0]

        conn.commit()

        auditoria_segura(

            usuario_id=usuario_logado.get("id"),

            login=usuario_logado.get("login"),

            acao="CRIAR_USUARIO",

            entidade="Usuarios",

            registro_id=user_id,

            detalhes=(
                f"login={login};"
                f"perfil={perfil['nome']}"
            )
        )

        return retorno(
            True,
            "Usuário criado.",
            user_id
        )

    except Exception as ex:

        if conn:
            conn.rollback()

        logging.exception(
            "USER CREATE ERROR"
        )

        return retorno(
            False,
            str(ex)
        )

    finally:

        try:

            if conn:
                conn.close()

        except Exception:
            pass


# ==================================================
# ATUALIZAR
# ==================================================

def atualizar_usuario(
    usuario_logado,
    user_id,
    login,
    nome,
    perfil_id,
    ativo=1,
    bloqueado=0
):

    conn = None

    try:

        if not user_id:

            raise Exception(
                "Usuário inválido."
            )

        login = validar_login(
            login
        )

        nome = str(
            nome or login
        ).strip()

        conn = get_connection()

        cursor = conn.cursor()

        usuario_alvo = obter_usuario(
            cursor,
            user_id
        )

        validar_usuario_alvo(
            usuario_logado,
            usuario_alvo
        )

        perfil = obter_perfil(
            cursor,
            perfil_id
        )

        validar_permissao_perfil(
            usuario_logado,
            perfil
        )

        validar_duplicidade(
            cursor,
            login,
            user_id
        )

        # ==========================================
        # AUTO PROTEÇÃO
        # ==========================================

        if (
            usuario_logado.get("id")
            == user_id
        ):

            ativo = 1

            bloqueado = 0

        # ==========================================
        # ROOT
        # ==========================================

        if usuario_alvo["admin_level"] >= ROOT_LEVEL:

            ativo = 1

            bloqueado = 0

            perfil_id = usuario_alvo[
                "perfil_id"
            ]

        cursor.execute("""

            UPDATE Usuarios

            SET
                Login = ?,
                Nome = ?,
                PerfilId = ?,
                Ativo = ?,
                Bloqueado = ?

            WHERE Id = ?

        """, (

            login,
            nome,
            perfil_id,
            int(bool(ativo)),
            int(bool(bloqueado)),
            user_id
        ))

        conn.commit()

        auditoria_segura(

            usuario_id=usuario_logado.get("id"),

            login=usuario_logado.get("login"),

            acao="ATUALIZAR_USUARIO",

            entidade="Usuarios",

            registro_id=user_id
        )

        return retorno(
            True,
            "Usuário atualizado."
        )

    except Exception as ex:

        if conn:
            conn.rollback()

        logging.exception(
            "USER UPDATE ERROR"
        )

        return retorno(
            False,
            str(ex)
        )

    finally:

        try:

            if conn:
                conn.close()

        except Exception:
            pass


# ==================================================
# DESATIVAR
# ==================================================

def excluir_usuario(
    usuario_logado,
    user_id
):

    conn = None

    try:

        if not user_id:

            raise Exception(
                "Usuário inválido."
            )

        conn = get_connection()

        cursor = conn.cursor()

        usuario_alvo = obter_usuario(
            cursor,
            user_id
        )

        validar_usuario_alvo(
            usuario_logado,
            usuario_alvo
        )

        # ==========================================
        # AUTO
        # ==========================================

        if (
            usuario_logado.get("id")
            == user_id
        ):

            raise Exception(
                "Não é permitido desativar o próprio usuário."
            )

        # ==========================================
        # ROOT
        # ==========================================

        if usuario_alvo["admin_level"] >= ROOT_LEVEL:

            raise Exception(
                "ROOT não pode ser desativado."
            )

        cursor.execute("""

            UPDATE Usuarios

            SET
                Ativo = 0,
                Bloqueado = 1

            WHERE Id = ?

        """, (user_id,))

        conn.commit()

        auditoria_segura(

            usuario_id=usuario_logado.get("id"),

            login=usuario_logado.get("login"),

            acao="DESATIVAR_USUARIO",

            entidade="Usuarios",

            registro_id=user_id
        )

        return retorno(
            True,
            "Usuário desativado."
        )

    except Exception as ex:

        if conn:
            conn.rollback()

        logging.exception(
            "USER DELETE ERROR"
        )

        return retorno(
            False,
            str(ex)
        )

    finally:

        try:

            if conn:
                conn.close()

        except Exception:
            pass


# ==================================================
# RESET SENHA
# ==================================================

def resetar_senha(
    usuario_logado,
    user_id
):

    conn = None

    try:

        conn = get_connection()

        cursor = conn.cursor()

        usuario_alvo = obter_usuario(
            cursor,
            user_id
        )

        validar_usuario_alvo(
            usuario_logado,
            usuario_alvo
        )

        senha_hash = gerar_hash(
            SENHA_PADRAO
        )

        cursor.execute("""

            UPDATE Usuarios

            SET
                SenhaHash = ?,
                DeveTrocarSenha = 1,
                SenhaTemporaria = 1,
                DataUltimaTrocaSenha = NULL,
                TentativasLogin = 0,
                Bloqueado = 0

            WHERE Id = ?

        """, (

            senha_hash,
            user_id
        ))

        conn.commit()

        auditoria_segura(

            usuario_id=usuario_logado.get("id"),

            login=usuario_logado.get("login"),

            acao="RESETAR_SENHA",

            entidade="Usuarios",

            registro_id=user_id
        )

        return retorno(
            True,
            "Senha resetada."
        )

    except Exception as ex:

        if conn:
            conn.rollback()

        logging.exception(
            "RESET PASSWORD ERROR"
        )

        return retorno(
            False,
            str(ex)
        )

    finally:

        try:

            if conn:
                conn.close()

        except Exception:
            pass


# ==================================================
# ALTERAR SENHA
# ==================================================

def alterar_senha(
    user_id,
    nova_senha
):

    nova_senha = str(
        nova_senha or ""
    ).strip()

    if not validar_senha(
        nova_senha
    ):

        return retorno(
            False,
            "Senha fraca."
        )

    conn = None

    try:

        conn = get_connection()

        cursor = conn.cursor()

        cursor.execute("""

            SELECT
                SenhaHash,
                Login

            FROM Usuarios

            WHERE Id = ?

        """, (user_id,))

        row = cursor.fetchone()

        if not row:

            return retorno(
                False,
                "Usuário não encontrado."
            )

        senha_atual_hash = row[0]

        login = row[1]

        if validar_hash(
            nova_senha,
            senha_atual_hash
        )[0]:

            return retorno(
                False,
                "A nova senha deve ser diferente da atual."
            )

        senha_hash = gerar_hash(
            nova_senha
        )

        cursor.execute("""

            UPDATE Usuarios

            SET
                SenhaHash = ?,
                DeveTrocarSenha = 0,
                SenhaTemporaria = 0,
                DataUltimaTrocaSenha = GETDATE(),
                TentativasLogin = 0,
                Bloqueado = 0

            WHERE Id = ?

        """, (

            senha_hash,
            user_id
        ))

        conn.commit()

        auditoria_segura(

            usuario_id=user_id,

            login=login,

            acao="ALTERAR_SENHA",

            entidade="Usuarios",

            registro_id=user_id
        )

        return retorno(
            True,
            "Senha alterada."
        )

    except Exception as ex:

        if conn:
            conn.rollback()

        logging.exception(
            "CHANGE PASSWORD ERROR"
        )

        return retorno(
            False,
            str(ex)
        )

    finally:

        try:

            if conn:
                conn.close()

        except Exception:
            pass