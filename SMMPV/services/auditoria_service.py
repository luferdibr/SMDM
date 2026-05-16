
import logging
import traceback
from datetime import datetime

from database.connection import (
    get_connection
)


# ==================================================
# CONFIG
# ==================================================

MAX_DETALHES = 4000

SEVERIDADE_INFO = "INFO"

SEVERIDADE_WARN = "WARN"

SEVERIDADE_ERROR = "ERROR"


# ==================================================
# LOGGER
# ==================================================

LOGGER = logging.getLogger(
    "MDM_AUDITORIA"
)

if not LOGGER.handlers:

    logging.basicConfig(

        level=logging.INFO,

        format=(
            "%(asctime)s "
            "[%(levelname)s] "
            "%(message)s"
        )
    )


# ==================================================
# HELPERS
# ==================================================

def _safe_str(valor):

    if valor is None:
        return None

    try:

        texto = str(valor).strip()

        if not texto:
            return None

        return texto[:MAX_DETALHES]

    except Exception:

        return None


def _safe_int(valor):

    try:

        if valor is None:
            return None

        return int(valor)

    except Exception:

        return None


def _safe_bool(valor):

    try:
        return bool(valor)

    except Exception:
        return False


def gerar_detalhes_erro(ex):

    try:

        return (

            f"{type(ex).__name__}: "
            f"{str(ex)}\n\n"
            f"{traceback.format_exc()}"
        )[:MAX_DETALHES]

    except Exception:

        return "Erro ao gerar traceback."


# ==================================================
# REGISTRO BASE
# ==================================================

def registrar_evento(

    acao,

    entidade=None,

    registro_id=None,

    detalhes=None,

    usuario_id=None,

    login=None,

    severidade=SEVERIDADE_INFO,

    sucesso=True
):

    conn = None

    try:

        acao = _safe_str(acao)

        if not acao:

            return False

        conn = get_connection()

        cursor = conn.cursor()

        # ==========================================
        # INSERT
        # ==========================================

        cursor.execute("""

            INSERT INTO Auditoria
            (
                UsuarioId,
                LoginUsuario,
                Acao,
                Entidade,
                RegistroId,
                Detalhes,
                Severidade,
                Sucesso,
                DataEvento
            )

            VALUES
            (
                ?, ?, ?, ?, ?,
                ?, ?, ?, GETDATE()
            )

        """, (

            _safe_int(usuario_id),

            _safe_str(login),

            acao,

            _safe_str(entidade),

            _safe_int(registro_id),

            _safe_str(detalhes),

            _safe_str(severidade),

            int(_safe_bool(sucesso))
        ))

        conn.commit()

        LOGGER.info(

            (
                f"[AUDITORIA] "
                f"{acao} | "
                f"{login or '-'}"
            )
        )

        return True

    except Exception:

        LOGGER.exception(
            "AUDITORIA ERROR"
        )

        return False

    finally:

        try:

            if conn:
                conn.close()

        except Exception:
            pass


# ==================================================
# LOGIN
# ==================================================

def registrar_login(

    login,

    sucesso=True,

    detalhes=None,

    usuario_id=None
):

    return registrar_evento(

        usuario_id=usuario_id,

        login=login,

        acao=(
            "LOGIN_SUCESSO"
            if sucesso
            else
            "LOGIN_FALHA"
        ),

        entidade="LOGIN",

        detalhes=detalhes,

        severidade=(

            SEVERIDADE_INFO

            if sucesso

            else

            SEVERIDADE_WARN
        ),

        sucesso=sucesso
    )


# ==================================================
# LOGOUT
# ==================================================

def registrar_logout(

    login,

    usuario_id=None,

    detalhes=None
):

    return registrar_evento(

        usuario_id=usuario_id,

        login=login,

        acao="LOGOUT",

        entidade="LOGIN",

        detalhes=detalhes,

        severidade=SEVERIDADE_INFO,

        sucesso=True
    )


# ==================================================
# ERRO
# ==================================================

def registrar_erro(

    erro,

    modulo=None,

    login=None,

    usuario_id=None
):

    detalhes = (

        gerar_detalhes_erro(erro)

        if isinstance(erro, Exception)

        else

        _safe_str(erro)
    )

    return registrar_evento(

        usuario_id=usuario_id,

        login=login,

        acao="ERRO",

        entidade=_safe_str(modulo),

        detalhes=detalhes,

        severidade=SEVERIDADE_ERROR,

        sucesso=False
    )


# ==================================================
# CRUD HELPERS
# ==================================================

def registrar_criacao(

    entidade,

    registro_id=None,

    detalhes=None,

    usuario_id=None,

    login=None
):

    return registrar_evento(

        usuario_id=usuario_id,

        login=login,

        acao="CRIACAO",

        entidade=entidade,

        registro_id=registro_id,

        detalhes=detalhes
    )


def registrar_alteracao(

    entidade,

    registro_id=None,

    detalhes=None,

    usuario_id=None,

    login=None
):

    return registrar_evento(

        usuario_id=usuario_id,

        login=login,

        acao="ALTERACAO",

        entidade=entidade,

        registro_id=registro_id,

        detalhes=detalhes
    )


def registrar_exclusao(

    entidade,

    registro_id=None,

    detalhes=None,

    usuario_id=None,

    login=None
):

    return registrar_evento(

        usuario_id=usuario_id,

        login=login,

        acao="EXCLUSAO",

        entidade=entidade,

        registro_id=registro_id,

        detalhes=detalhes,

        severidade=SEVERIDADE_WARN
    )


# ==================================================
# EVENTOS SISTEMA
# ==================================================

def registrar_evento_sistema(

    acao,

    detalhes=None
):

    return registrar_evento(

        login="SYSTEM",

        acao=acao,

        entidade="SISTEMA",

        detalhes=detalhes,

        severidade=SEVERIDADE_INFO
    )


# ==================================================
# SEGURANÇA
# ==================================================

def registrar_evento_seguranca(

    acao,

    detalhes=None,

    login=None,

    usuario_id=None
):

    return registrar_evento(

        usuario_id=usuario_id,

        login=login,

        acao=acao,

        entidade="SEGURANCA",

        detalhes=detalhes,

        severidade=SEVERIDADE_WARN,

        sucesso=False
    )