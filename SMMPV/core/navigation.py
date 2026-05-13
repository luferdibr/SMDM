
import traceback

import flet as ft

from core.logger import get_logger

from core.session import (

    get_user,

    is_logged,

    logout,

    set_route,

    get_route
)

from core.responses import (
    ok,
    erro
)

from core.exceptions import (
    PermissionDeniedError
)


# ==================================================
# LOGGER
# ==================================================

logger = get_logger("navigation")


# ==================================================
# ROUTES
# ==================================================

_ROUTES = {}


# ==================================================
# REGISTER
# ==================================================

def register_route(

    route,

    view_factory,

    admin_level=0,

    auth_required=True
):

    route = normalize_route(route)

    _ROUTES[route] = {

        "factory": view_factory,

        "admin_level": int(admin_level),

        "auth_required": bool(
            auth_required
        )
    }

    logger.info(
        f"ROUTE REGISTER {route}"
    )


# ==================================================
# NORMALIZE
# ==================================================

def normalize_route(route):

    if not route:
        return "home"

    return str(route).strip().lower()


# ==================================================
# GET ROUTE
# ==================================================

def get_registered_route(route):

    route = normalize_route(route)

    return _ROUTES.get(route)


# ==================================================
# PERMISSION
# ==================================================

def validate_route_permission(

    page,

    route
):

    route_data = get_registered_route(
        route
    )

    if not route_data:

        raise PermissionDeniedError(
            "Rota inválida."
        )

    # ==============================================
    # AUTH
    # ==============================================

    if route_data["auth_required"]:

        if not is_logged(page):

            raise PermissionDeniedError(
                "Login necessário."
            )

    # ==============================================
    # LEVEL
    # ==============================================

    usuario = get_user(page)

    admin_level = 0

    if usuario:

        try:

            admin_level = int(

                usuario.get(
                    "admin_level",
                    0
                )
            )

        except Exception:
            pass

    if admin_level < route_data["admin_level"]:

        raise PermissionDeniedError(
            "Permissão insuficiente."
        )

    return True


# ==================================================
# CONTENT
# ==================================================

def clear_content(page):

    try:

        page.clean()

    except Exception:

        logger.exception(
            "CLEAR CONTENT ERROR"
        )


def render_content(

    page,

    control
):

    clear_content(page)

    page.add(control)

    page.update()


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

                bgcolor=ft.Colors.RED_50,

                border_radius=10,

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
# NAVIGATE
# ==================================================

def navigate(

    page,

    route,

    **kwargs
):

    try:

        route = normalize_route(
            route
        )

        logger.info(
            f"NAVIGATE {route}"
        )

        # ==========================================
        # VALIDATE
        # ==========================================

        validate_route_permission(

            page,

            route
        )

        route_data = get_registered_route(
            route
        )

        if not route_data:

            raise Exception(
                "Rota inexistente."
            )

        # ==========================================
        # FACTORY
        # ==========================================

        factory = route_data["factory"]

        view = factory(

            page,

            **kwargs
        )

        # ==========================================
        # STATE
        # ==========================================

        set_route(
            page,
            route
        )

        # ==========================================
        # RENDER
        # ==========================================

        render_content(
            page,
            view
        )

        return ok(
            f"Rota {route} carregada."
        )

    except PermissionDeniedError as ex:

        logger.warning(str(ex))

        render_content(

            page,

            build_error_view(

                "Acesso negado",

                str(ex)
            )
        )

        return erro(str(ex))

    except Exception as ex:

        logger.exception(
            "NAVIGATION ERROR"
        )

        render_content(

            page,

            build_error_view(

                "Erro navegação",

                (
                    f"{ex}\n\n"
                    f"{traceback.format_exc()}"
                )
            )
        )

        return erro(str(ex))


# ==================================================
# CURRENT ROUTE
# ==================================================

def refresh_route(page):

    route = get_route(page)

    if not route:

        return erro(
            "Rota atual inválida."
        )

    return navigate(
        page,
        route
    )


# ==================================================
# LOGOUT
# ==================================================

def perform_logout(page):

    try:

        logger.info(
            "Executando logout."
        )

        logout(

            page,

            redirect=False
        )

        from ui.login import login_view

        render_content(

            page,

            login_view(page)
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
# CLOSE APP
# ==================================================

def close_application(page):

    try:

        logger.info(
            "Fechando aplicação."
        )

        try:

            page.window.close()

            return ok(
                "Aplicação encerrada."
            )

        except Exception:

            logger.warning(
                "WINDOW CLOSE FAIL"
            )

        try:

            page.window.destroy()

            return ok(
                "Aplicação encerrada."
            )

        except Exception:

            logger.warning(
                "WINDOW DESTROY FAIL"
            )

        try:

            page.window_destroy()

            return ok(
                "Aplicação encerrada."
            )

        except Exception:

            logger.warning(
                "WINDOW_DESTROY FAIL"
            )

        return erro(
            "Falha encerramento."
        )

    except Exception as ex:

        logger.exception(
            "CLOSE APP ERROR"
        )

        return erro(str(ex))


# ==================================================
# ROUTES INFO
# ==================================================

def get_routes():

    return _ROUTES.copy()


# ==================================================
# EXISTS
# ==================================================

def route_exists(route):

    route = normalize_route(route)

    return route in _ROUTES


# ==================================================
# REMOVE ROUTE
# ==================================================

def unregister_route(route):

    route = normalize_route(route)

    if route in _ROUTES:

        del _ROUTES[route]

        logger.info(
            f"ROUTE REMOVE {route}"
        )

        return True

    return False


# ==================================================
# STARTUP
# ==================================================

logger.info(
    "Navigation manager inicializado."
)
