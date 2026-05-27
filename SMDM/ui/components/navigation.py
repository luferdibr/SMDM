# =========================================================
# ui/components/navigation.py
# =========================================================

import logging

import flet as ft

from core.themes import (

    PRIMARY_COLOR,

    SURFACE_COLOR,

    BACKGROUND_COLOR,

    TEXT_PRIMARY,

    TEXT_SECONDARY,
)

from security.session_service import (
    obter_usuario,
)

# =========================================================
# LOGGER
# =========================================================

LOGGER = logging.getLogger(
    "NAVIGATION"
)

# =========================================================
# NAV ITEM
# =========================================================

def nav_item(

    text,

    icon,

    on_click=None,

    selected=False,
):

    bgcolor = (
        ft.Colors.BLUE_50
        if selected
        else SURFACE_COLOR
    )

    return ft.Container(

        border_radius=12,

        bgcolor=bgcolor,

        padding=10,

        ink=True,

        on_click=on_click,

        content=ft.Row(

            spacing=12,

            vertical_alignment=(
                ft.CrossAxisAlignment.CENTER
            ),

            controls=[

                ft.Icon(

                    icon,

                    color=PRIMARY_COLOR,
                ),

                ft.Text(

                    text,

                    size=14,

                    weight=(
                        ft.FontWeight.W_500
                    ),

                    color=TEXT_PRIMARY,
                ),
            ],
        ),
    )

# =========================================================
# NAV SECTION
# =========================================================

def nav_section(

    title,

    items,
):

    return ft.Column(

        spacing=10,

        controls=[

            ft.Text(

                title,

                size=12,

                color=TEXT_SECONDARY,

                weight=(
                    ft.FontWeight.BOLD
                ),
            ),

            *items,
        ],
    )

# =========================================================
# USER PANEL
# =========================================================

def user_panel():

    usuario = (
        obter_usuario()
        or {}
    )

    return ft.Container(

        padding=16,

        border_radius=16,

        bgcolor=BACKGROUND_COLOR,

        content=ft.Column(

            spacing=6,

            horizontal_alignment=(
                ft.CrossAxisAlignment.CENTER
            ),

            controls=[

                ft.CircleAvatar(

                    content=ft.Text(

                        usuario.get(
                            "login",
                            "?"
                        )[:1],

                        weight=(
                            ft.FontWeight.BOLD
                        ),
                    ),

                    radius=28,
                ),

                ft.Text(

                    usuario.get(
                        "login",
                        "-"
                    ),

                    weight=(
                        ft.FontWeight.BOLD
                    ),
                ),

                ft.Text(

                    usuario.get(
                        "nome",
                        "-"
                    ),

                    size=12,

                    color=TEXT_SECONDARY,
                ),
            ],
        ),
    )

# =========================================================
# SIDEBAR NAVIGATION
# =========================================================

def sidebar_navigation():

    LOGGER.info(
        "Sidebar navigation."
    )

    return ft.Container(

        width=260,

        bgcolor=SURFACE_COLOR,

        padding=20,

        content=ft.Column(

            spacing=20,

            scroll=ft.ScrollMode.AUTO,

            controls=[

                ft.Text(

                    "SMDM",

                    size=30,

                    color=PRIMARY_COLOR,

                    weight=(
                        ft.FontWeight.BOLD
                    ),
                ),

                user_panel(),

                nav_section(

                    "GERAL",

                    [

                        nav_item(

                            "Dashboard",

                            ft.Icons.DASHBOARD,

                            selected=True,
                        ),

                        nav_item(

                            "Início",

                            ft.Icons.HOME,
                        ),
                    ],
                ),

                nav_section(

                    "ADMINISTRAÇÃO",

                    [

                        nav_item(

                            "Usuários",

                            ft.Icons.PEOPLE,
                        ),

                        nav_item(

                            "Perfis",

                            ft.Icons.ADMIN_PANEL_SETTINGS,
                        ),

                        nav_item(

                            "Permissões",

                            ft.Icons.SECURITY,
                        ),

                        nav_item(

                            "Menus",

                            ft.Icons.MENU,
                        ),
                    ],
                ),

                nav_section(

                    "SISTEMA",

                    [

                        nav_item(

                            "Auditoria",

                            ft.Icons.HISTORY,
                        ),

                        nav_item(

                            "Logs",

                            ft.Icons.DESCRIPTION,
                        ),

                        nav_item(

                            "Configurações",

                            ft.Icons.SETTINGS,
                        ),
                    ],
                ),
            ],
        ),
    )

# =========================================================
# TOP NAVIGATION
# =========================================================

def top_navigation(

    title="Dashboard",
):

    return ft.Container(

        height=70,

        bgcolor=SURFACE_COLOR,

        padding=20,

        content=ft.Row(

            alignment=(
                ft.MainAxisAlignment.SPACE_BETWEEN
            ),

            vertical_alignment=(
                ft.CrossAxisAlignment.CENTER
            ),

            controls=[

                ft.Text(

                    title,

                    size=24,

                    weight=(
                        ft.FontWeight.BOLD
                    ),
                ),

                ft.Row(

                    spacing=10,

                    controls=[

                        ft.IconButton(
                            icon=ft.Icons.SEARCH
                        ),

                        ft.IconButton(
                            icon=ft.Icons.NOTIFICATIONS
                        ),

                        ft.IconButton(
                            icon=ft.Icons.ACCOUNT_CIRCLE
                        ),
                    ],
                ),
            ],
        ),
    )

# =========================================================
# APP SHELL
# =========================================================

def app_shell(

    content,
):

    return ft.Row(

        expand=True,

        spacing=0,

        controls=[

            sidebar_navigation(),

            ft.VerticalDivider(
                width=1
            ),

            ft.Container(

                expand=True,

                bgcolor=BACKGROUND_COLOR,

                content=ft.Column(

                    expand=True,

                    spacing=0,

                    controls=[

                        top_navigation(),

                        ft.Container(

                            expand=True,

                            padding=20,

                            content=content,
                        ),
                    ],
                ),
            ),
        ],
    )