
import asyncio
import logging

import flet as ft

from services.auditoria_service import (
    registrar_evento
)

from config.settings import (
    APP_CONFIG
)


# ==================================================
# LOGGER
# ==================================================

LOGGER = logging.getLogger(
    "MDM_DASHBOARD"
)


# ==================================================
# HELPERS
# ==================================================

def logout(page):

    try:

        usuario = getattr(
            page,
            "usuario_logado",
            None
        )

        if usuario:

            registrar_evento(

                usuario_id=usuario["id"],

                login=usuario["login"],

                acao="LOGOUT",

                entidade="SESSION"
            )

        page.usuario_logado = None

        asyncio.create_task(
            page.window.destroy()
        )

    except Exception:

        LOGGER.exception(
            "LOGOUT ERROR"
        )


def build_user_card(usuario):

    admin_level = int(

        usuario.get(
            "admin_level",
            0
        )
    )

    cor = ft.Colors.BLUE

    if admin_level >= 100:

        cor = ft.Colors.RED

    elif admin_level >= 90:

        cor = ft.Colors.ORANGE

    return ft.Card(

        elevation=4,

        content=ft.Container(

            padding=20,

            content=ft.Column(

                [

                    ft.Row(

                        [

                            ft.Icon(

                                ft.Icons.ACCOUNT_CIRCLE,

                                size=48,

                                color=cor
                            ),

                            ft.Column(

                                [

                                    ft.Text(

                                        usuario[
                                            "nome"
                                        ],

                                        size=22,

                                        weight="bold"
                                    ),

                                    ft.Text(

                                        (
                                            f"Login: "
                                            f"{usuario['login']}"
                                        ),

                                        size=14
                                    ),

                                    ft.Text(

                                        (
                                            f"Perfil: "
                                            f"{usuario['perfil_nome']}"
                                        ),

                                        size=14
                                    )
                                ],

                                spacing=3
                            )

                        ],

                        spacing=15
                    ),

                    ft.Divider(),

                    ft.Text(

                        (
                            f"Admin Level: "
                            f"{admin_level}"
                        ),

                        size=14
                    )

                ],

                spacing=10
            )
        )
    )


def build_system_card():

    return ft.Card(

        elevation=4,

        content=ft.Container(

            padding=20,

            content=ft.Column(

                [

                    ft.Text(

                        APP_CONFIG["name"],

                        size=24,

                        weight="bold"
                    ),

                    ft.Text(

                        (
                            f"Versão "
                            f"{APP_CONFIG['version']}"
                        ),

                        size=14
                    ),

                    ft.Text(

                        "Sistema inicializado "
                        "com sucesso.",

                        size=14
                    )

                ],

                spacing=10
            )
        )
    )


def build_actions(page):

    return ft.Card(

        elevation=4,

        content=ft.Container(

            padding=20,

            content=ft.Column(

                [

                    ft.Text(

                        "Ações rápidas",

                        size=18,

                        weight="bold"
                    ),

                    ft.ElevatedButton(

                        "Usuários",

                        width=220,

                        icon=ft.Icons.PEOPLE
                    ),

                    ft.ElevatedButton(

                        "Perfis",

                        width=220,

                        icon=ft.Icons.ADMIN_PANEL_SETTINGS
                    ),

                    ft.ElevatedButton(

                        "Menus",

                        width=220,

                        icon=ft.Icons.MENU
                    ),

                    ft.OutlinedButton(

                        "Logout",

                        width=220,

                        icon=ft.Icons.LOGOUT,

                        on_click=lambda e: logout(
                            page
                        )
                    )

                ],

                spacing=12
            )
        )
    )


# ==================================================
# DASHBOARD
# ==================================================

def dashboard_view(page: ft.Page):

    try:

        usuario = getattr(

            page,

            "usuario_logado",

            None
        )

        if not usuario:

            return ft.Container(

                expand=True,

                alignment=(
                    ft.Alignment(0, 0)
                ),

                content=ft.Text(

                    "Usuário não autenticado.",

                    size=18,

                    color=ft.Colors.RED
                )
            )

        registrar_evento(

            usuario_id=usuario["id"],

            login=usuario["login"],

            acao="OPEN_DASHBOARD",

            entidade="DASHBOARD"
        )

        content = ft.Column(

            [

                ft.Text(

                    "Dashboard Principal",

                    size=30,

                    weight="bold"
                ),

                build_user_card(
                    usuario
                ),

                build_system_card(),

                build_actions(page)

            ],

            spacing=20,

            scroll=ft.ScrollMode.AUTO
        )

        return ft.Container(

            expand=True,

            padding=30,

            bgcolor=ft.Colors.GREY_100,

            content=content
        )

    except Exception as ex:

        LOGGER.exception(
            "DASHBOARD ERROR"
        )

        return ft.Container(

            expand=True,

            alignment=(
                ft.Alignment(0, 0)
            ),

            content=ft.Column(

                [

                    ft.Icon(

                        ft.Icons.ERROR,

                        size=80,

                        color=ft.Colors.RED
                    ),

                    ft.Text(

                        "Erro ao carregar dashboard.",

                        size=20,

                        weight="bold"
                    ),

                    ft.Text(

                        str(ex),

                        size=14
                    )

                ],

                spacing=15,

                horizontal_alignment=(
                    ft.CrossAxisAlignment.CENTER
                )
            )
        )