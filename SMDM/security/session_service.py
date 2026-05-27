# =========================================================
# security/session_service.py
# =========================================================

import logging
from datetime import datetime

from core.state.state import (
    clear_user,
    set_user,
)

# =========================================================
# LOGGER
# =========================================================

LOGGER = logging.getLogger(
    "SESSION_SERVICE"
)

# =========================================================
# SESSION STORAGE
# =========================================================

_SESSION = {

    "authenticated": False,

    "user": None,

    "started_at": None,
}

# =========================================================
# START SESSION
# =========================================================

def iniciar_sessao(
    usuario: dict,
):

    global _SESSION

    _SESSION = {

        "authenticated": True,

        "user": usuario,

        "started_at": datetime.now(),
    }

    set_user(
        usuario
    )

    LOGGER.info(

        f"Sessão iniciada: "
        f"{usuario.get('login')}"
    )

# =========================================================
# END SESSION
# =========================================================

def encerrar_sessao():

    global _SESSION

    usuario = (
        _SESSION.get("user")
        or {}
    )

    LOGGER.info(

        f"Sessão encerrada: "
        f"{usuario.get('login')}"
    )

    _SESSION = {

        "authenticated": False,

        "user": None,

        "started_at": None,
    }

    clear_user()

# =========================================================
# GET SESSION
# =========================================================

def obter_sessao():

    return _SESSION

# =========================================================
# GET USER
# =========================================================

def obter_usuario():

    return (
        _SESSION.get("user")
    )

# =========================================================
# AUTH CHECK
# =========================================================

def usuario_autenticado():

    return bool(

        _SESSION.get(
            "authenticated"
        )
    )

# =========================================================
# ADMIN CHECK
# =========================================================

def usuario_admin():

    usuario = (
        obter_usuario()
        or {}
    )

    return bool(
        usuario.get("admin")
    )

# =========================================================
# ADMIN LEVEL
# =========================================================

def admin_level():

    usuario = (
        obter_usuario()
        or {}
    )

    return int(

        usuario.get(
            "admin_level",
            0,
        )
    )

# =========================================================
# LOGIN
# =========================================================

def usuario_login():

    usuario = (
        obter_usuario()
        or {}
    )

    return usuario.get(
        "login"
    )

# =========================================================
# USER ID
# =========================================================

def usuario_id():

    usuario = (
        obter_usuario()
        or {}
    )

    return usuario.get(
        "id"
    )

# =========================================================
# PROFILE
# =========================================================

def usuario_perfil():

    usuario = (
        obter_usuario()
        or {}
    )

    return usuario.get(
        "perfil_id"
    )

# =========================================================
# ROOT CHECK
# =========================================================

def usuario_root():

    usuario = (
        obter_usuario()
        or {}
    )

    return (
        usuario.get("login")
        == "ROOT"
    )

# =========================================================
# SESSION INFO
# =========================================================

def resumo_sessao():

    usuario = (
        obter_usuario()
        or {}
    )

    return {

        "authenticated": (
            usuario_autenticado()
        ),

        "login": usuario.get(
            "login"
        ),

        "admin": usuario.get(
            "admin"
        ),

        "admin_level": usuario.get(
            "admin_level"
        ),

        "started_at": (
            _SESSION.get(
                "started_at"
            )
        ),
    }
