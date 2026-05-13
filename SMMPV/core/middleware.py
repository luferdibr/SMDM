
import traceback
from functools import wraps

import flet as ft

from core.logger import get_logger

from core.responses import (

    ok,

    erro,

    from_exception
)

from core.exceptions import (
    SMMPVError
)

from services.auditoria_service import (
    registrar_erro
)


# ==================================================
# LOGGER
# ==================================================

logger = get_logger("middleware")


# ==================================================
# ERROR VIEW
# ==================================================

def build_error_view(

    titulo,

    mensagem
):

    return ft.Container(

        expand=True,

        alignment=ft.Alignment(0, 0),

        content=ft.Column([

            ft.Icon(

                ft.Icons.ERROR,

                size=80,

                color=ft.Colors.RED
            ),

            ft.Text(

                titulo,

                size=26,

                weight="bold",

                color=ft.Colors.RED
            ),

            ft.Container(

                content=ft.Text(

                    str(mensagem),

                    selectable=True,

                    size=14
                ),

                padding=15,

                border_radius=10,

                bgcolor=ft.Colors.RED_50,

                width=700
            )

        ],

            spacing=20,

            horizontal_alignment=(
                ft.CrossAxisAlignment.CENTER
            )
        )
    )


# ==================================================
# HANDLE EXCEPTION
# ==================================================

def handle_exception(

    ex,

    contexto="APP",

    usuario=None
):

    try:

        # ==========================================
        # CUSTOM
        # ==========================================

        if isinstance(
            ex,
            SMMPVError
        ):

            ex.registrar_log()

        else:

            logger.exception(

                (
                    f"UNHANDLED ERROR "
                    f"{contexto}"
                )
            )

        # ==========================================
        # AUDITORIA
        # ==========================================

        try:

            registrar_erro(

                ex,

                usuario=usuario,

                modulo=contexto
            )

        except Exception:

            logger.exception(
                "AUDIT ERROR"
            )

        # ==========================================
        # RESPONSE
        # ==========================================

        return from_exception(ex)

    except Exception as fatal:

        logger.exception(
            "FATAL HANDLE ERROR"
        )

        return erro(

            mensagem=str(fatal),

            codigo="FATAL_HANDLE_ERROR"
        )


# ==================================================
# SAFE EXECUTE
# ==================================================

def safe_execute(

    func,

    *args,

    contexto=None,

    usuario=None,

    default=None,

    **kwargs
):

    try:

        return func(
            *args,
            **kwargs
        )

    except Exception as ex:

        contexto = (

            contexto

            or

            func.__name__
        )

        handle_exception(

            ex,

            contexto=contexto,

            usuario=usuario
        )

        return default


# ==================================================
# SAFE SERVICE
# ==================================================

def safe_service(func):

    @wraps(func)
    def wrapper(*args, **kwargs):

        try:

            return func(
                *args,
                **kwargs
            )

        except Exception as ex:

            return handle_exception(

                ex,

                contexto=func.__name__
            )

    return wrapper


# ==================================================
# SAFE UI
# ==================================================

def safe_ui(func):

    @wraps(func)
    def wrapper(*args, **kwargs):

        page = None

        try:

            # ======================================
            # PAGE
            # ======================================

            for arg in args:

                if isinstance(
                    arg,
                    ft.Page
                ):

                    page = arg

                    break

            if not page:

                page = kwargs.get("page")

            return func(
                *args,
                **kwargs
            )

        except Exception as ex:

            handle_exception(

                ex,

                contexto=func.__name__
            )

            if page:

                try:

                    page.clean()

                    page.add(

                        build_error_view(

                            "Erro interface",

                            (
                                f"{ex}\n\n"
                                f"{traceback.format_exc()}"
                            )
                        )
                    )

                    page.update()

                except Exception:

                    logger.exception(
                        "SAFE UI ERROR"
                    )

            return None

    return wrapper


# ==================================================
# SAFE EVENT
# ==================================================

def safe_event(func):

    @wraps(func)
    def wrapper(e):

        try:

            return func(e)

        except Exception as ex:

            handle_exception(

                ex,

                contexto=func.__name__
            )

            return None

    return wrapper


# ==================================================
# SAFE PAGE UPDATE
# ==================================================

def safe_page_update(page):

    try:

        if page:

            page.update()

            return True

    except Exception:

        logger.exception(
            "PAGE UPDATE ERROR"
        )

    return False


# ==================================================
# SAFE PAGE CLEAN
# ==================================================

def safe_page_clean(page):

    try:

        if page:

            page.clean()

            return True

    except Exception:

        logger.exception(
            "PAGE CLEAN ERROR"
        )

    return False


# ==================================================
# SAFE APP CLOSE
# ==================================================

def safe_close(page):

    try:

        try:

            page.window.close()

            return ok(
                "Aplicação encerrada."
            )

        except Exception:
            pass

        try:

            page.window.destroy()

            return ok(
                "Aplicação encerrada."
            )

        except Exception:
            pass

        try:

            page.window_destroy()

            return ok(
                "Aplicação encerrada."
            )

        except Exception:
            pass

        return erro(
            "Falha encerramento."
        )

    except Exception as ex:

        return handle_exception(

            ex,

            contexto="safe_close"
        )


# ==================================================
# SAFE IMPORT
# ==================================================

def safe_import(

    importer,

    default=None,

    contexto="IMPORT"
):

    try:

        return importer()

    except Exception as ex:

        handle_exception(

            ex,

            contexto=contexto
        )

        return default


# ==================================================
# SAFE CALLBACK
# ==================================================

def safe_callback(

    callback,

    *args,

    **kwargs
):

    try:

        return callback(
            *args,
            **kwargs
        )

    except Exception as ex:

        handle_exception(

            ex,

            contexto="callback"
        )

        return None


# ==================================================
# STARTUP
# ==================================================

logger.info(
    "Middleware global inicializado."
)
