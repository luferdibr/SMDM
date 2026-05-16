
import logging

from datetime import datetime
from typing import Optional

from database.connection import (
    get_connection
)

from security.password_service import (
    verificar_senha,
    gerar_hash
)

from services.auditoria_service import (
    registrar_evento
)

from services.security_service import (
    usuario_bloqueado,
    registrar_falha_login,
    registrar_login_sucesso
)


# ==================================================
# CONFIG
# ==================================================

ROOT_LEVEL = 100

ADMIN_LEVEL = 90


# ==================================================
# LOGGER
# ==================================================

LOGGER = logging.getLogger(
    "MDM_AUTH"
)


# ==================================================
# HELPERS
# ==================================================

def auditoria_segura(**kwargs):

    try:

        registrar_evento(**kwargs)

    except Exception:

        LOGGER.exception(
            "AUDITORIA ERROR"
        )


def auth_fail(
    mensagem="Usuário ou senha inválidos.",
    bloqueado=False
):

    return {

        "autenticado": False,

        "bloqueado": bloqueado,

        "mensagem": mensagem
    }


def map_usuario(row):

    return {

        "id": row[0],

        "login": row[1],

        "nome": row[2],

        "senha_hash": row[3],

        "perfil_id": row[4],

        "ativo": bool(row[5]),

        "bloqueado": bool(row[6]),

        "tentativas": int(row[7] or 0),

        "deve_trocar": bool(row[8]),

        "senha_temporaria": bool(row[9]),

        "ultimo_login": row[10],

        "ultimo_troca": row[11],

        "perfil_nome": row[12],

        "admin_level": int(row[13] or 0),

        "perfil_sistema": bool(row[14]),

        "validade_senha": row[15],

        "bloqueado_ate": row[16],

        "nivel_bloqueio": int(row[17] or 0),

        "bloqueio_total": bool(row[18])
    }


def obter_usuario(
    cursor,
    login
) -> Optional[dict]:

    cursor.execute("""

        SELECT

            u.Id,
            u.Login,
            u.Nome,
            u.SenhaHash,
            u.PerfilId,
            u.Ativo,
            u.Bloqueado,
            u.TentativasLogin,
            u.DeveTrocarSenha,
            u.SenhaTemporaria,
            u.UltimoLogin,
            u.DataUltimaTrocaSenha,

            p.Nome,
            p.AdminLevel,
            p.Sistema,
            p.ValidadeSenhaDias,

            u.BloqueadoAte,
            u.NivelBloqueio,
            u.BloqueioTotal

        FROM Usuarios u

        INNER JOIN Perfis p
            ON p.Id = u.PerfilId

        WHERE UPPER(u.Login) = ?

    """, (

        str(login).strip().upper(),

    ))

    row = cursor.fetchone()

    if not row:
        return None

    return map_usuario(row)


def senha_expirada(usuario):

    validade = usuario.get(
        "validade_senha"
    )

    if not validade:
        return False

    ultima_troca = usuario.get(
        "ultimo_troca"
    )

    if not ultima_troca:
        return True

    dias = (

        datetime.now()

        - ultima_troca

    ).days

    return dias >= int(validade)


def is_root(usuario):

    return int(

        usuario.get(
            "admin_level",
            0
        )

    ) >= ROOT_LEVEL


def is_admin(usuario):

    return int(

        usuario.get(
            "admin_level",
            0
        )

    ) >= ADMIN_LEVEL


# ==================================================
# LOGIN
# ==================================================

def autenticar(
    login,
    senha
):

    conn = None

    try:

        login = str(
            login or ""
        ).strip().upper()

        senha = str(
            senha or ""
        ).strip()

        LOGGER.info(
            f"Autenticando usuário {login}"
        )

        # ==========================================
        # VALIDACOES
        # ==========================================

        if not login:

            return auth_fail(
                "Usuário obrigatório."
            )

        if not senha:

            return auth_fail(
                "Senha obrigatória."
            )

        conn = get_connection()

        cursor = conn.cursor()

        usuario = obter_usuario(
            cursor,
            login
        )

        # ==========================================
        # USUARIO NAO EXISTE
        # ==========================================

        if not usuario:

            auditoria_segura(

                login=login,

                acao="LOGIN_INVALIDO",

                entidade="LOGIN",

                detalhes="Usuário inexistente"
            )

            return auth_fail()

        # ==========================================
        # USUARIO SEM HASH
        # ==========================================

        if not usuario.get(
            "senha_hash"
        ):

            LOGGER.error(
                f"Usuário sem hash: {login}"
            )

            return auth_fail()

        # ==========================================
        # INATIVO
        # ==========================================

        if not usuario["ativo"]:

            auditoria_segura(

                usuario_id=usuario["id"],

                login=usuario["login"],

                acao="LOGIN_INATIVO",

                entidade="LOGIN"
            )

            return auth_fail(
                "Usuário inativo."
            )

        # ==========================================
        # SEGURANCA
        # ==========================================

        status = usuario_bloqueado(
            usuario
        )

        if status["bloqueado"]:

            auditoria_segura(

                usuario_id=usuario["id"],

                login=usuario["login"],

                acao="LOGIN_BLOQUEADO",

                entidade="LOGIN",

                detalhes=status[
                    "motivo"
                ]
            )

            return auth_fail(

                status["motivo"],

                True
            )

        # ==========================================
        # BCRYPT
        # ==========================================

        senha_ok = verificar_senha(

            senha,

            usuario["senha_hash"]
        )

        # ==========================================
        # SENHA INVALIDA
        # ==========================================

        if not senha_ok:

            seguranca = registrar_falha_login(

                cursor,

                usuario
            )

            conn.commit()

            auditoria_segura(

                usuario_id=usuario["id"],

                login=usuario["login"],

                acao="LOGIN_INVALIDO",

                entidade="LOGIN",

                registro_id=usuario["id"],

                detalhes=(
                    f"Tentativas="
                    f"{usuario['tentativas'] + 1}"
                )
            )

            if seguranca["temporario"]:

                auditoria_segura(

                    usuario_id=usuario["id"],

                    login=usuario["login"],

                    acao="LOGIN_TEMP_BLOCK",

                    entidade="LOGIN",

                    detalhes=(
                        f"Bloqueado por "
                        f"{seguranca['minutos']} minutos"
                    )
                )

            if seguranca["total"]:

                auditoria_segura(

                    usuario_id=usuario["id"],

                    login=usuario["login"],

                    acao="LOGIN_TOTAL_BLOCK",

                    entidade="LOGIN"
                )

            return auth_fail()

        # ==========================================
        # LOGIN SUCESSO
        # ==========================================

        registrar_login_sucesso(

            cursor,

            usuario["id"]
        )

        conn.commit()

        usuario = obter_usuario(
            cursor,
            login
        )

        expirada = senha_expirada(
            usuario
        )

        auditoria_segura(

            usuario_id=usuario["id"],

            login=usuario["login"],

            acao="LOGIN_SUCESSO",

            entidade="LOGIN"
        )

        LOGGER.info(
            f"Login sucesso {usuario['login']}"
        )

        return {

            "autenticado": True,

            "usuario": usuario,

            "bloqueado": False,

            "senha_expirada": expirada,

            "trocar_senha": (

                usuario["deve_trocar"]

                or

                usuario["senha_temporaria"]
            ),

            "is_root": is_root(usuario),

            "is_admin": is_admin(usuario)
        }

    except Exception:

        if conn:
            conn.rollback()

        LOGGER.exception(
            "AUTH ERROR"
        )

        raise

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

    usuario_id,

    nova_senha
):

    conn = None

    try:

        nova_senha = str(
            nova_senha or ""
        ).strip()

        if not nova_senha:

            return False

        conn = get_connection()

        cursor = conn.cursor()

        novo_hash = gerar_hash(
            nova_senha
        )

        cursor.execute("""

            UPDATE Usuarios

            SET

                SenhaHash = ?,

                DeveTrocarSenha = 0,

                SenhaTemporaria = 0,

                TentativasLogin = 0,

                Bloqueado = 0,

                BloqueadoAte = NULL,

                NivelBloqueio = 0,

                BloqueioTotal = 0,

                DataUltimaTrocaSenha = GETDATE()

            WHERE Id = ?

        """, (

            novo_hash,

            usuario_id
        ))

        conn.commit()

        auditoria_segura(

            usuario_id=usuario_id,

            acao="ALTERAR_SENHA",

            entidade="Usuarios",

            registro_id=usuario_id
        )

        return True

    except Exception:

        if conn:
            conn.rollback()

        LOGGER.exception(
            "ALTER PASSWORD ERROR"
        )

        return False

    finally:

        try:

            if conn:
                conn.close()

        except Exception:
            pass
