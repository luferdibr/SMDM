# =========================================================
# services/auditoria_service.py
# =========================================================

import logging
import traceback

from database.connection import (
    get_connection,
)

from services.identity_service import (
    coluna_eh_identity,
    obter_proximo_id,
)

from core.state.state import (
    get_user,
    get_current_view,
    get_selected_module,
)

# =========================================================
# LOGGER
# =========================================================

LOGGER = logging.getLogger(
    "SMDM_AUDITORIA"
)

# =========================================================
# LEVELS
# =========================================================

LEVEL_INFO = "INFO"

LEVEL_WARNING = "WARNING"

LEVEL_ERROR = "ERROR"

LEVEL_CRITICAL = "CRITICAL"

# =========================================================
# EVENTS
# =========================================================

EVENT_LOGIN = "LOGIN"

EVENT_LOGOUT = "LOGOUT"

EVENT_INSERT = "INSERT"

EVENT_UPDATE = "UPDATE"

EVENT_DELETE = "DELETE"

EVENT_ACCESS = "ACCESS"

EVENT_SECURITY = "SECURITY"

EVENT_ERROR = "ERROR"

EVENT_SYSTEM = "SYSTEM"

# =========================================================
# USER DATA
# =========================================================

def get_user_data():

    try:

        usuario = get_user()

        if not usuario:

            return {

                "id": None,

                "login": "SYSTEM",

                "perfil": None,

                "admin_level": 0,
            }

        return {

            "id": usuario.get("id"),

            "login": usuario.get(
                "login",
                "SYSTEM",
            ),

            "perfil": usuario.get(
                "perfil_nome"
            ),

            "admin_level": usuario.get(
                "admin_level",
                0,
            ),
        }

    except Exception:

        return {

            "id": None,

            "login": "SYSTEM",

            "perfil": None,

            "admin_level": 0,
        }

# =========================================================
# BASE EVENT
# =========================================================

def registrar_evento(

    evento=None,

    descricao=None,

    level=LEVEL_INFO,

    referencia=None,

    dados=None,

    **kwargs,
):

    conn = None

    cursor = None

    try:

        # =================================================
        # LEGACY COMPATIBILITY
        # =================================================

        if not evento:

            evento = kwargs.get(
                "acao",
                kwargs.get(
                    "tipo",
                    EVENT_SYSTEM,
                ),
            )

        if not descricao:

            descricao = kwargs.get(
                "detalhes",
                kwargs.get(
                    "mensagem",
                    "",
                ),
            )

        login_legacy = kwargs.get(
            "login"
        )

        usuario_id_legacy = kwargs.get(
            "usuario_id"
        )

        entidade = kwargs.get(
            "entidade"
        )

        registro_id = (
            kwargs.get("registro_id")
            or
            referencia
        )

        sucesso = bool(
            kwargs.get(
                "sucesso",
                True,
            )
        )

        usuario = get_user_data()

        if login_legacy:

            usuario["login"] = (
                login_legacy
            )

        if usuario_id_legacy is not None:

            usuario["id"] = (
                usuario_id_legacy
            )

        try:

            view = (
                get_current_view()
            )

        except Exception:

            view = None

        try:

            modulo = (
                get_selected_module()
            )

        except Exception:

            modulo = None

        LOGGER.info(

            "[AUDITORIA] "

            f"{evento} "

            f"| {usuario['login']} "

            f"| {descricao}"
        )

        conn = get_connection()

        if not conn:

            LOGGER.warning(
                "Sem conexão auditoria."
            )

            return

        cursor = conn.cursor()

        detalhes = descricao

        if dados:

            detalhes = (
                f"{descricao} | {dados}"
                if descricao
                else
                str(dados)
            )

        id_identity = coluna_eh_identity(
            cursor,
            "Auditoria",
            "Id",
        )

        if id_identity:

            sql = """

            INSERT INTO Auditoria (

                UsuarioId,

                Login,

                Acao,

                Entidade,

                RegistroId,

                Detalhes,

                Severidade,

                Sucesso,

                CriadoEm

            )

            VALUES (

                ?, ?, ?, ?, ?, ?, ?, ?, GETDATE()

            )

            """

            params = (

                usuario["id"],

                usuario["login"],

                evento,

                entidade or modulo,

                registro_id,

                detalhes,

                level,

                int(sucesso),
            )

        else:

            sql = """

            INSERT INTO Auditoria (

                Id,

                UsuarioId,

                Login,

                Acao,

                Entidade,

                RegistroId,

                Detalhes,

                Severidade,

                Sucesso,

                CriadoEm

            )

            VALUES (

                ?, ?, ?, ?, ?, ?, ?, ?, ?, GETDATE()

            )

            """

            params = (

                obter_proximo_id(
                    cursor,
                    "Auditoria",
                    "Id",
                ),

                usuario["id"],

                usuario["login"],

                evento,

                entidade or modulo,

                registro_id,

                detalhes,

                level,

                int(sucesso),
            )

        cursor.execute(

            sql,

            params,
        )

        conn.commit()

    except Exception:

        LOGGER.exception(
            "Erro auditoria."
        )

    finally:

        try:

            if cursor:

                cursor.close()

        except Exception:

            pass

        try:

            if conn:

                conn.close()

        except Exception:

            pass

# =========================================================
# LOGIN
# =========================================================

def auditoria_login(
    login,
):

    registrar_evento(

        evento=EVENT_LOGIN,

        descricao=(
            f"Login realizado: "
            f"{login}"
        ),
    )

# =========================================================
# LOGOUT
# =========================================================

def auditoria_logout(
    login,
):

    registrar_evento(

        evento=EVENT_LOGOUT,

        descricao=(
            f"Logout realizado: "
            f"{login}"
        ),
    )

# =========================================================
# INSERT
# =========================================================

def auditoria_insert(

    entidade,

    referencia=None,

    dados=None,
):

    registrar_evento(

        evento=EVENT_INSERT,

        descricao=(
            f"Inclusão em "
            f"{entidade}"
        ),

        referencia=referencia,

        dados=dados,
    )

# =========================================================
# UPDATE
# =========================================================

def auditoria_update(

    entidade,

    referencia=None,

    dados=None,
):

    registrar_evento(

        evento=EVENT_UPDATE,

        descricao=(
            f"Alteração em "
            f"{entidade}"
        ),

        referencia=referencia,

        dados=dados,
    )

# =========================================================
# DELETE
# =========================================================

def auditoria_delete(

    entidade,

    referencia=None,

    dados=None,
):

    registrar_evento(

        evento=EVENT_DELETE,

        descricao=(
            f"Exclusão em "
            f"{entidade}"
        ),

        level=LEVEL_WARNING,

        referencia=referencia,

        dados=dados,
    )

# =========================================================
# ACCESS
# =========================================================

def auditoria_access(
    tela,
):

    registrar_evento(

        evento=EVENT_ACCESS,

        descricao=(
            f"Acesso à tela "
            f"{tela}"
        ),
    )

# =========================================================
# SECURITY
# =========================================================

def auditoria_security(

    descricao,

    dados=None,
):

    registrar_evento(

        evento=EVENT_SECURITY,

        descricao=descricao,

        level=LEVEL_CRITICAL,

        dados=dados,
    )

# =========================================================
# ERROR
# =========================================================

def auditoria_error(

    descricao,

    exception=None,
):

    detalhes = None

    try:

        if exception:

            detalhes = (
                traceback.format_exc()
            )

    except Exception:

        detalhes = str(exception)

    registrar_evento(

        evento=EVENT_ERROR,

        descricao=descricao,

        level=LEVEL_ERROR,

        dados=detalhes,
    )


def registrar_erro(

    exception,

    usuario=None,

    modulo=None,
):

    descricao = str(
        exception
        or "Erro não informado."
    )

    dados = None

    try:

        dados = traceback.format_exc()

    except Exception:

        dados = descricao

    registrar_evento(

        evento=EVENT_ERROR,

        descricao=descricao,

        level=LEVEL_ERROR,

        dados=dados,

        entidade=modulo,

        usuario_id=(
            usuario.get("id")
            if isinstance(usuario, dict)
            else None
        ),

        login=(
            usuario.get("login")
            if isinstance(usuario, dict)
            else None
        ),
    )

# =========================================================
# SYSTEM
# =========================================================

def auditoria_system(

    descricao,

    detalhes=None,
):

    if detalhes:

        descricao = (

            f"{descricao} | "

            f"{detalhes}"
        )

    registrar_evento(

        evento=EVENT_SYSTEM,

        descricao=descricao,
    )

# =========================================================
# CRUD HELPERS
# =========================================================

def auditoria_save(

    entidade,

    referencia=None,
):

    auditoria_insert(

        entidade=entidade,

        referencia=referencia,
    )

def auditoria_edit(

    entidade,

    referencia=None,
):

    auditoria_update(

        entidade=entidade,

        referencia=referencia,
    )

def auditoria_remove(

    entidade,

    referencia=None,
):

    auditoria_delete(

        entidade=entidade,

        referencia=referencia,
    )

# =========================================================
# STARTUP
# =========================================================

def auditoria_startup():

    auditoria_system(
        "Sistema iniciado."
    )

# =========================================================
# SHUTDOWN
# =========================================================

def auditoria_shutdown():

    auditoria_system(
        "Sistema encerrado."
    )

# =========================================================
# LEGACY COMPATIBILITY
# =========================================================

registrar_evento_sistema = (
    auditoria_system
)

registrar_evento_login = (
    auditoria_login
)

registrar_evento_logout = (
    auditoria_logout
)

registrar_evento_erro = (
    auditoria_error
)

registrar_evento_seguranca = (
    auditoria_security
)
