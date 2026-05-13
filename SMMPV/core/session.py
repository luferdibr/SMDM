
from core.logger import get_logger

from core.cache import (

    set_cache,

    get_cache,

    delete_cache,

    invalidate_session_cache,

    clear_user_menu_cache
)

from core.security import (
    sanitize_payload
)

from core.responses import (
    ok,
    erro
)


# ==================================================
# LOGGER
# ==================================================

logger = get_logger("session")


# ==================================================
# CONFIG
# ==================================================

SESSION_NAMESPACE = "session"

ROOT_LEVEL = 100

ADMIN_LEVEL = 50


# ==================================================
# HELPERS
# ==================================================

def _has_attr(page, attr):

    try:

        return hasattr(page, attr)

    except Exception:

        return False


def _safe_get(page, attr, default=None):

    try:

        return getattr(
            page,
            attr,
            default
        )

    except Exception:

        return default


def _safe_set(page, attr, value):

    try:

        setattr(
            page,
            attr,
            value
        )

        return True

    except Exception:

        return False


# ==================================================
# USER
# ==================================================

def set_user(

    page,

    usuario
):

    try:

        if not usuario:

            return erro(
                "Usuário inválido."
            )

        usuario = sanitize_payload(
            usuario
        )

        # ==========================================
        # PAGE
        # ==========================================

        _safe_set(
            page,
            "usuario_logado",
            usuario
        )

        _safe_set(
            page,
            "user",
            usuario
        )

        # ==========================================
        # CACHE
        # ==========================================

        user_id = usuario.get("id")

        if user_id:

            set_cache(

                key=f"user:{user_id}",

                value=usuario,

                ttl=3600,

                namespace=SESSION_NAMESPACE
            )

        logger.info(

            (
                f"SESSION USER "
                f"{usuario.get('login')}"
            )
        )

        return ok(
            "Sessão iniciada."
        )

    except Exception as ex:

        logger.exception(
            "SET USER ERROR"
        )

        return erro(str(ex))


# ==================================================
# GET USER
# ==================================================

def get_user(page):

    try:

        # ==========================================
        # MODERNO
        # ==========================================

        usuario = _safe_get(
            page,
            "usuario_logado"
        )

        if (
            isinstance(usuario, dict)
            and
            usuario.get("id")
        ):

            return usuario

        # ==========================================
        # LEGADO
        # ==========================================

        usuario = _safe_get(
            page,
            "user"
        )

        if (
            isinstance(usuario, dict)
            and
            usuario.get("id")
        ):

            return usuario

        return None

    except Exception:

        logger.exception(
            "GET USER ERROR"
        )

        return None


# ==================================================
# USER ID
# ==================================================

def get_user_id(page):

    usuario = get_user(page)

    if not usuario:

        return None

    try:

        return int(
            usuario.get("id")
        )

    except Exception:

        return None


# ==================================================
# LOGIN
# ==================================================

def is_logged(page):

    usuario = get_user(page)

    return bool(

        usuario

        and

        usuario.get("id")
    )


# ==================================================
# ROOT
# ==================================================

def is_root(page):

    usuario = get_user(page)

    if not usuario:

        return False

    try:

        return int(

            usuario.get(
                "admin_level",
                0
            )

        ) >= ROOT_LEVEL

    except Exception:

        return False


# ==================================================
# ADMIN
# ==================================================

def is_admin(page):

    usuario = get_user(page)

    if not usuario:

        return False

    try:

        return int(

            usuario.get(
                "admin_level",
                0
            )

        ) >= ADMIN_LEVEL

    except Exception:

        return False


# ==================================================
# LEVEL
# ==================================================

def has_level(

    page,

    level
):

    usuario = get_user(page)

    if not usuario:

        return False

    try:

        return int(

            usuario.get(
                "admin_level",
                0
            )

        ) >= int(level)

    except Exception:

        return False


# ==================================================
# PROFILE
# ==================================================

def get_profile_id(page):

    usuario = get_user(page)

    if not usuario:

        return None

    try:

        return int(
            usuario.get("perfil_id")
        )

    except Exception:

        return None


# ==================================================
# ROUTE
# ==================================================

def set_route(

    page,

    rota
):

    try:

        _safe_set(
            page,
            "rota_atual",
            rota
        )

        return True

    except Exception:

        logger.exception(
            "SET ROUTE ERROR"
        )

        return False


def get_route(page):

    return _safe_get(
        page,
        "rota_atual"
    )


# ==================================================
# CONTENT
# ==================================================

def set_content(

    page,

    conteudo
):

    return _safe_set(
        page,
        "conteudo",
        conteudo
    )


def get_content(page):

    return _safe_get(
        page,
        "conteudo"
    )


# ==================================================
# CACHE
# ==================================================

def clear_session_cache(page):

    try:

        user_id = get_user_id(page)

        if user_id:

            delete_cache(

                key=f"user:{user_id}",

                namespace=SESSION_NAMESPACE
            )

            clear_user_menu_cache(
                user_id
            )

        invalidate_session_cache()

    except Exception:

        logger.exception(
            "CLEAR SESSION CACHE ERROR"
        )


# ==================================================
# CLEAR USER
# ==================================================

def clear_user(page):

    try:

        clear_session_cache(page)

        _safe_set(
            page,
            "usuario_logado",
            None
        )

        _safe_set(
            page,
            "user",
            None
        )

        _safe_set(
            page,
            "conteudo",
            None
        )

        _safe_set(
            page,
            "rota_atual",
            None
        )

        logger.info(
            "Sessão limpa."
        )

        return ok(
            "Sessão encerrada."
        )

    except Exception as ex:

        logger.exception(
            "CLEAR USER ERROR"
        )

        return erro(str(ex))


# ==================================================
# LOGOUT
# ==================================================

def logout(

    page,

    redirect=True
):

    try:

        clear_user(page)

        # ==========================================
        # LIMPAR UI
        # ==========================================

        try:

            page.clean()

        except Exception:
            pass

        # ==========================================
        # LOGIN VIEW
        # ==========================================

        if redirect:

            from ui.login import login_view

            page.add(
                login_view(page)
            )

            page.update()

        logger.info(
            "Logout realizado."
        )

        return ok(
            "Logout realizado."
        )

    except Exception as ex:

        logger.exception(
            "LOGOUT ERROR"
        )

        return erro(str(ex))


# ==================================================
# STATE
# ==================================================

def init_page_state(page):

    try:

        if not _has_attr(
            page,
            "usuario_logado"
        ):

            page.usuario_logado = None

        if not _has_attr(
            page,
            "conteudo"
        ):

            page.conteudo = None

        if not _has_attr(
            page,
            "rota_atual"
        ):

            page.rota_atual = None

        if not _has_attr(
            page,
            "menu_cache"
        ):

            page.menu_cache = None

        return ok(
            "Estado inicializado."
        )

    except Exception as ex:

        logger.exception(
            "INIT PAGE STATE ERROR"
        )

        return erro(str(ex))


# ==================================================
# SESSION INFO
# ==================================================

def get_session_info(page):

    usuario = get_user(page)

    return {

        "logado": bool(usuario),

        "usuario_id": (
            usuario.get("id")
            if usuario
            else None
        ),

        "login": (
            usuario.get("login")
            if usuario
            else None
        ),

        "perfil_id": (
            usuario.get("perfil_id")
            if usuario
            else None
        ),

        "admin_level": (
            usuario.get("admin_level")
            if usuario
            else 0
        ),

        "root": is_root(page),

        "admin": is_admin(page),

        "rota": get_route(page)
    }


# ==================================================
# STARTUP
# ==================================================

logger.info(
    "Session manager inicializado."
)