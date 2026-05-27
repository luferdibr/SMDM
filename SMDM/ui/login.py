# =========================================================
# ui/login.py
# =========================================================

import logging

import flet as ft

from security.auth_service import (
    autenticar_usuario,
)

from ui.components.buttons import (
    LoadingButton,
)

from ui.components.notifications import (

    notify_error,

    notify_success,
)

from ui.components.forms import (

    text_field,

    password_field,
)

from core.themes import (

    PRIMARY_COLOR,

    BACKGROUND_COLOR,

    SURFACE_COLOR,

    TEXT_PRIMARY,

    TEXT_SECONDARY,
)

# =========================================================
# LOGGER
# =========================================================

LOGGER = logging.getLogger(
    "LOGIN_VIEW"
)

# =========================================================
# LOGIN CARD
# =========================================================

def login_card(
    page: ft.Page,
):

    usuario_input = text_field(
        label="Usuário"
    )

    senha_input = password_field(
        label="Senha"
    )

    loading_button = LoadingButton(

        text="Entrar",

        icon=ft.Icons.LOGIN,
    )

    # =====================================================
    # LOGIN
    # =====================================================

    def realizar_login(e):

        loading_button.start_loading()

        page.update()

        try:

            usuario = (
                usuario_input.value
                or ""
            ).strip()

            senha = (
                senha_input.value
                or ""
            ).strip()

            if not usuario:

                notify_error(

                    page,

                    "Informe o usuário.",
                )

                return

            if not senha:

                notify_error(

                    page,

                    "Informe a senha.",
                )

                return

            LOGGER.info(
                f"Login: {usuario}"
            )

            auth = autenticar_usuario(

                login=usuario,

                senha=senha,
            )

            if not auth:

                notify_error(

                    page,

                    "Usuário ou senha inválidos.",
                )

                return

            notify_success(

                page,

                "Login realizado.",
            )

            if (
                auth.get("deve_trocar")
                or
                auth.get("trocar_senha")
                or
                auth.get("senha_expirada")
            ):

                from ui.alterar_senha import (
                    alterar_senha_view,
                )

                page.clean()

                page.add(
                    alterar_senha_view(page)
                )

                page.update()

                return

            # =============================================
            # IMPORT LOCAL
            # =============================================

            from ui.main_layout import (
                carregar_main_layout,
            )

            carregar_main_layout(
                page
            )

        except Exception as ex:

            LOGGER.exception(
                "Erro login."
            )

            notify_error(

                page,

                str(ex),
            )

        finally:

            loading_button.stop_loading()

            page.update()

    # =====================================================
    # ENTER
    # =====================================================


    def submit_enter(e):
         
        realizar_login(e)
    usuario_input.on_submit = (
        submit_enter
    )

    senha_input.on_submit = (
        submit_enter
    )

    loading_button.user_on_click = (
        realizar_login
    )

    return ft.Container(

        width=420,

        padding=40,

        border_radius=20,

        bgcolor=SURFACE_COLOR,

        shadow=ft.BoxShadow(

            blur_radius=18,

            spread_radius=1,

            color=ft.Colors.BLACK12,
        ),

        content=ft.Column(

            spacing=22,

            horizontal_alignment=(
                ft.CrossAxisAlignment.CENTER
            ),

            controls=[

                ft.Icon(

                    ft.Icons.ADMIN_PANEL_SETTINGS,

                    size=64,

                    color=PRIMARY_COLOR,
                ),

                ft.Text(

                    "SMDM",

                    size=30,

                    weight=(
                        ft.FontWeight.BOLD
                    ),

                    color=TEXT_PRIMARY,
                ),

                ft.Text(

                    "Sistema Modular de Gestão",

                    size=13,

                    color=TEXT_SECONDARY,
                ),

                ft.Divider(height=1),

                usuario_input,

                senha_input,

                ft.Container(
                    height=6
                ),

                loading_button.control,
            ],
        ),
    )

# =========================================================
# LOGIN VIEW
# =========================================================

def login_view(
    page: ft.Page,
):

    LOGGER.info(
        "Carregando login."
    )

    page.clean()

    page.title = "SMDM"

    page.bgcolor = (
        BACKGROUND_COLOR
    )

    page.horizontal_alignment = (
        ft.CrossAxisAlignment.CENTER
    )

    page.vertical_alignment = (
        ft.MainAxisAlignment.CENTER
    )

    page.add(

        ft.Container(

            expand=True,

            alignment=ft.Alignment(
                0,
                0,
            ),

            content=login_card(
                page
            ),
        )
    )

    page.update()
