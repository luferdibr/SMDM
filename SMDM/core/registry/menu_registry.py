# =========================================================
# core/registry/menu_registry.py
# =========================================================

import logging
import threading

from datetime import datetime

# =========================================================
# LOGGER
# =========================================================

LOGGER = logging.getLogger(
    "MENU_REGISTRY"
)

# =========================================================
# LOCK
# =========================================================

_registry_lock = threading.Lock()

# =========================================================
# REGISTRY
# =========================================================

_MENU_REGISTRY = {

    # =============================================
    # INVALIDAÇÃO
    # =============================================

    "dirty": True,

    # =============================================
    # CONTROLE
    # =============================================

    "loading": False,

    "version": 0,

    # =============================================
    # METADATA
    # =============================================

    "updated_at": None,

    "last_error": None,
}

# =========================================================
# SNAPSHOT
# =========================================================

def get_registry_snapshot():

    with _registry_lock:

        return dict(
            _MENU_REGISTRY
        )

# =========================================================
# VERSION
# =========================================================

def get_menu_version():

    with _registry_lock:

        return int(

            _MENU_REGISTRY.get(
                "version",
                0,
            )
        )

# =========================================================
# UPDATED AT
# =========================================================

def get_menu_updated_at():

    with _registry_lock:

        return _MENU_REGISTRY.get(
            "updated_at"
        )

# =========================================================
# LAST ERROR
# =========================================================

def get_last_error():

    with _registry_lock:

        return _MENU_REGISTRY.get(
            "last_error"
        )

# =========================================================
# DIRTY
# =========================================================

def is_dirty():

    with _registry_lock:

        return bool(

            _MENU_REGISTRY.get(
                "dirty",
                True,
            )
        )

# =========================================================
# LOADING
# =========================================================

def is_loading():

    with _registry_lock:

        return bool(

            _MENU_REGISTRY.get(
                "loading",
                False,
            )
        )

# =========================================================
# MARK DIRTY
# =========================================================

def mark_menu_dirty():

    LOGGER.info(
        "Menu marcado dirty."
    )

    with _registry_lock:

        _MENU_REGISTRY[
            "dirty"
        ] = True

        _MENU_REGISTRY[
            "updated_at"
        ] = datetime.now()

# =========================================================
# RESET
# =========================================================

def reset_menu_registry():

    LOGGER.warning(
        "Reset menu registry."
    )

    with _registry_lock:

        _MENU_REGISTRY[
            "dirty"
        ] = True

        _MENU_REGISTRY[
            "loading"
        ] = False

        _MENU_REGISTRY[
            "version"
        ] = 0

        _MENU_REGISTRY[
            "updated_at"
        ] = None

        _MENU_REGISTRY[
            "last_error"
        ] = None

# =========================================================
# RELOAD
# =========================================================

def reload_menu_registry(
    force=False,
):

    with _registry_lock:

        # =============================================
        # IGNORA
        # =============================================

        if (

            not force

            and

            not is_dirty()

        ):

            LOGGER.info(
                "Registry limpo."
            )

            return

        # =============================================
        # JÁ CARREGANDO
        # =============================================

        if is_loading():

            LOGGER.warning(
                "Registry em reload."
            )

            return

        # =============================================
        # START
        # =============================================

        _MENU_REGISTRY[
            "loading"
        ] = True

    try:

        LOGGER.info(
            "Reload registry."
        )

        with _registry_lock:

            _MENU_REGISTRY[
                "dirty"
            ] = False

            _MENU_REGISTRY[
                "version"
            ] += 1

            _MENU_REGISTRY[
                "updated_at"
            ] = datetime.now()

            _MENU_REGISTRY[
                "last_error"
            ] = None

        LOGGER.info(

            "Registry atualizado. "
            f"Version="
            f"{_MENU_REGISTRY['version']}"
        )

    except Exception as ex:

        LOGGER.exception(
            "Erro reload registry."
        )

        with _registry_lock:

            _MENU_REGISTRY[
                "last_error"
            ] = str(ex)

            _MENU_REGISTRY[
                "dirty"
            ] = True

    finally:

        with _registry_lock:

            _MENU_REGISTRY[
                "loading"
            ] = False

# =========================================================
# ENSURE
# =========================================================

def ensure_menu_registry():

    if is_dirty():

        reload_menu_registry()

# =========================================================
# FORCE
# =========================================================

def force_reload_menu_registry():

    reload_menu_registry(
        force=True
    )