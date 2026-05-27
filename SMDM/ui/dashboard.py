# =========================================================
# ui/dashboard.py
# =========================================================

import logging

import flet as ft

from core.state.state import (
    get_user,
)

from core.themes import (
    BACKGROUND_COLOR,
    ERROR_COLOR,
    PRIMARY_COLOR,
    TEXT_SECONDARY,
)

from ui.components.cards import (
    app_card,
)

from utils.error_formatter import (
    format_error_message,
)

# =========================================================
# LOGGER
# =========================================================

LOGGER = logging.getLogger(
    "SMDM_DASHBOARD"
)

# =========================================================
# NAVIGATION COMPAT
# =========================================================

def navegar(
    page,
    rota,
):

    from ui.main_layout import navegar as navegar_main

    navegar_main(
        page,
        rota,
    )

# =========================================================
# HELPERS
# =========================================================

def action_button(
    page,
    label,
    rota,
    icon,
):

    return ft.OutlinedButton(

        content=ft.Row(

            spacing=6,

            alignment=ft.MainAxisAlignment.CENTER,

            controls=[

                ft.Icon(
                    icon,
                    size=16,
                ),

                ft.Text(
                    label,
                    size=12,
                ),
            ],
        ),

        height=34,

        on_click=lambda e, r=rota: navegar(
            page,
            r,
        ),
    )


def info_line(
    label,
    value,
):

    return ft.Row(

        spacing=8,

        controls=[

            ft.Text(
                label,
                width=90,
                size=12,
                color=TEXT_SECONDARY,
            ),

            ft.Text(
                str(value or "-"),
                size=12,
                expand=True,
            ),
        ],
    )


def user_card():

    usuario = (
        get_user()
        or {}
    )

    return app_card(

        title="Sessão",

        subtitle="Usuário atual",

        content=ft.Column(

            spacing=8,

            controls=[

                info_line(
                    "Login",
                    usuario.get("login"),
                ),

                info_line(
                    "Nome",
                    usuario.get("nome"),
                ),

                info_line(
                    "Perfil",
                    usuario.get("perfil_nome"),
                ),

                info_line(
                    "Nível",
                    usuario.get("admin_level"),
                ),
            ],
        ),
    )


def system_card():

    return app_card(

        title="Sistema",

        subtitle="Resumo operacional",

        content=ft.Column(

            spacing=8,

            controls=[

                info_line(
                    "Banco",
                    "SQL Server",
                ),

                info_line(
                    "Interface",
                    "Flet",
                ),

                info_line(
                    "Status",
                    "Operacional",
                ),
            ],
        ),
    )


def actions_card(
    page,
):

    return app_card(

        title="Acesso rápido",

        subtitle="Rotinas administrativas",

        content=ft.ResponsiveRow(

            spacing=8,

            controls=[

                ft.Container(
                    col={
                        "xs": 12,
                        "sm": 6,
                        "md": 3,
                    },
                    content=action_button(
                        page,
                        "Usuários",
                        "usuarios",
                        ft.Icons.PERSON,
                    ),
                ),

                ft.Container(
                    col={
                        "xs": 12,
                        "sm": 6,
                        "md": 3,
                    },
                    content=action_button(
                        page,
                        "Perfis",
                        "perfis",
                        ft.Icons.SECURITY,
                    ),
                ),

                ft.Container(
                    col={
                        "xs": 12,
                        "sm": 6,
                        "md": 3,
                    },
                    content=action_button(
                        page,
                        "Menus",
                        "menus",
                        ft.Icons.MENU,
                    ),
                ),

                ft.Container(
                    col={
                        "xs": 12,
                        "sm": 6,
                        "md": 3,
                    },
                    content=action_button(
                        page,
                        "Editor",
                        "menu_editor",
                        ft.Icons.EDIT,
                    ),
                ),
            ],
        ),
    )

# =========================================================
# DASHBOARD VIEW
# =========================================================

def dashboard_view(
    page: ft.Page,
):

    LOGGER.info(
        "Carregando dashboard."
    )

    try:

        return ft.Container(

            expand=True,

            bgcolor=BACKGROUND_COLOR,

            padding=20,

            content=ft.Column(

                scroll=ft.ScrollMode.AUTO,

                spacing=14,

                controls=[

                    ft.Text(

                        "Dashboard",

                        size=22,

                        weight=ft.FontWeight.BOLD,

                        color=PRIMARY_COLOR,
                    ),

                    actions_card(
                        page
                    ),

                    ft.ResponsiveRow(

                        spacing=12,

                        vertical_alignment=(
                            ft.CrossAxisAlignment.START
                        ),

                        controls=[

                            ft.Container(
                                col={
                                    "xs": 12,
                                    "md": 6,
                                },
                                content=user_card(),
                            ),

                            ft.Container(
                                col={
                                    "xs": 12,
                                    "md": 6,
                                },
                                content=system_card(),
                            ),
                        ],
                    ),
                ],
            ),
        )

    except Exception as ex:

        LOGGER.exception(
            "Erro dashboard."
        )

        return ft.Container(

            padding=40,

            alignment=ft.Alignment(0, 0),

            content=ft.Text(

                (
                    "Erro carregando dashboard.\n"
                    f"{format_error_message(ex)}"
                ),

                size=18,

                color=ERROR_COLOR,

                selectable=True,
            ),
        )
