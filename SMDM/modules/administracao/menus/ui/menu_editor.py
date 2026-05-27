# =========================================================
# modules/administracao/menus/ui/menu_editor.py
# =========================================================

import logging

import flet as ft

from core.icons import (
    ICON_MENU,
    ICON_NEW,
    ICON_EDIT,
    ICON_DELETE,
)

from modules.administracao.menus.services.menu_service import (
    listar_menus,
)

from ui.components.base_view import (
    base_view,
)

from ui.components.buttons import (
    icon_button,
)

from ui.components.cards import (
    section_card,
)

from ui.components.snackbars import (
    show_info,
)

# =========================================================
# LOGGER
# =========================================================

LOGGER = logging.getLogger(
    "SMDM_MENU_EDITOR"
)

# =========================================================
# CONFIG
# =========================================================

ROW_HEIGHT = 34

INDENT = 18

# =========================================================
# TYPE COLOR
# =========================================================

def tipo_color(tipo):

    tipo = str(tipo)

    if tipo == "T":

        return ft.Colors.BLUE_700

    if tipo == "M":

        return ft.Colors.GREEN_700

    return ft.Colors.GREY_700

# =========================================================
# TYPE LABEL
# =========================================================

def tipo_label(tipo):

    if tipo == "T":

        return "T"

    if tipo == "M":

        return "M"

    return "S"

# =========================================================
# NODE
# =========================================================

def build_node(
    page,
    menu,
    level=0,
):

    controls = []

    filhos = menu.get(
        "filhos",
        []
    ) or []

    # =====================================================
    # HEADER
    # =====================================================

    linha = ft.Container(

        height=ROW_HEIGHT,

        border_radius=6,

        padding=ft.Padding(
            6,
            0,
            6,
            0,
        ),

        margin=ft.margin.only(
            left=level * INDENT,
        ),

        bgcolor=ft.Colors.WHITE,

        content=ft.Row(

            spacing=6,

            vertical_alignment=(
                ft.CrossAxisAlignment.CENTER
            ),

            controls=[

                ft.Container(
                    width=12,
                ),

                ft.Text(

                    tipo_label(
                        menu.get("tipo")
                    ),

                    size=10,

                    weight=(
                        ft.FontWeight.BOLD
                    ),

                    color=tipo_color(
                        menu.get("tipo")
                    ),
                ),

                ft.Icon(

                    ICON_MENU,

                    size=14,

                    color=tipo_color(
                        menu.get("tipo")
                    ),
                ),

                ft.Text(

                    menu.get(
                        "nome",
                        "-"
                    ),

                    size=12,

                    weight=(
                        ft.FontWeight.BOLD
                    ),

                    expand=True,
                ),

                ft.Text(

                    menu.get(
                        "rota",
                        ""
                    ),

                    size=10,

                    color=(
                        ft.Colors.GREY_700
                    ),

                    width=180,
                ),

                ft.Text(

                    str(
                        menu.get(
                            "ordem",
                            ""
                        )
                    ),

                    size=10,

                    width=30,
                ),

                icon_button(

                    icon=ICON_NEW,

                    tooltip="Novo",

                    icon_size=14,

                    on_click=lambda e: (
                        show_info(
                            page,
                            (
                                "Novo submenu"
                            ),
                        )
                    ),
                ),

                icon_button(

                    icon=ICON_EDIT,

                    tooltip="Editar",

                    icon_size=14,

                    on_click=lambda e: (
                        show_info(
                            page,
                            (
                                "Editar menu"
                            ),
                        )
                    ),
                ),

                icon_button(

                    icon=ICON_DELETE,

                    tooltip="Excluir",

                    icon_size=14,

                    icon_color=(
                        ft.Colors.RED_400
                    ),

                    on_click=lambda e: (
                        show_info(
                            page,
                            (
                                "Excluir menu"
                            ),
                        )
                    ),
                ),
            ],
        ),
    )

    controls.append(
        linha
    )

    # =====================================================
    # CHILDREN
    # =====================================================

    for filho in filhos:

        controls.extend(

            build_node(
                page,
                filho,
                level + 1,
            )
        )

    return controls

# =========================================================
# TREE
# =========================================================

def build_tree(
    page,
    menus,
):

    controls = []

    # =====================================================
    # HEADER
    # =====================================================

    controls.append(

        ft.Container(

            height=34,

            padding=ft.Padding(
                6,
                0,
                6,
                0,
            ),

            bgcolor=ft.Colors.BLUE_GREY_50,

            border_radius=6,

            content=ft.Row(

                spacing=6,

                vertical_alignment=(
                    ft.CrossAxisAlignment.CENTER
                ),

                controls=[

                    ft.Container(
                        width=20,
                    ),

                    ft.Text(
                        "Tp",
                        size=10,
                        width=20,
                        weight=(
                            ft.FontWeight.BOLD
                        ),
                    ),

                    ft.Text(
                        "Menu",
                        expand=True,
                        size=10,
                        weight=(
                            ft.FontWeight.BOLD
                        ),
                    ),

                    ft.Text(
                        "Rota",
                        width=180,
                        size=10,
                        weight=(
                            ft.FontWeight.BOLD
                        ),
                    ),

                    ft.Text(
                        "Ord",
                        width=30,
                        size=10,
                        weight=(
                            ft.FontWeight.BOLD
                        ),
                    ),

                    ft.Container(
                        width=90,
                    ),
                ],
            ),
        )
    )

    # =====================================================
    # ITEMS
    # =====================================================

    for menu in menus:

        controls.extend(

            build_node(
                page,
                menu,
            )
        )

    return ft.Column(

        spacing=2,

        controls=controls,
    )

# =========================================================
# TOOLBAR
# =========================================================

def build_toolbar():

    return ft.Row(

        height=36,

        vertical_alignment=(
            ft.CrossAxisAlignment.CENTER
        ),

        controls=[

            ft.Icon(
                ICON_MENU,
                size=18,
            ),

            ft.Text(

                "Estrutura Hierárquica",

                size=16,

                weight=(
                    ft.FontWeight.BOLD
                ),
            ),
        ],
    )

# =========================================================
# VIEW
# =========================================================

def menu_editor_view(
    page: ft.Page,
):

    LOGGER.info(
        "Carregando editor."
    )

    try:

        menus = listar_menus()

    except Exception as ex:

        LOGGER.exception(
            "Erro menus."
        )

        return ft.Container(

            padding=20,

            content=ft.Text(
                str(ex)
            ),
        )

    tree = build_tree(
        page,
        menus,
    )

    content = section_card(

        title="Menus",

        subtitle=(
            "Estrutura "
            "hierárquica"
        ),

        icon=ICON_MENU,

        content=ft.Column(

            spacing=8,

            controls=[

                build_toolbar(),

                tree,
            ],
        ),
    )

    return base_view(

        title="Editor Hierárquico",

        subtitle=(
            "Visualização "
            "compacta"
        ),

        content_controls=[

            content,
        ],
    )