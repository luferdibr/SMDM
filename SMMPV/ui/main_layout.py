# ui/main_layout.py

import logging

import flet as ft

from services.menu_service import (
    listar_menus_usuario
)

from services.menu_tree_service import (
    flatten_tree
)

from core.menu_constants import (

    MENU_UI_CONFIG,

    SCREEN_ROUTE_MAP,

    TIPO_TITULO,

    get_label,

    get_icone,

    get_cor,

    get_indent,

    is_bold,

    is_expandable
)


LOGGER = logging.getLogger(
    "MDM_MAIN_LAYOUT"
)


# =========================================================
# SCREEN REGISTRY
# =========================================================

def get_screen_registry():

    from ui.menu_editor import (
        menu_editor_view
    )

    from ui.menu_admin import (
        menu_admin_view
    )

    registry = {

        "menus":
            menu_editor_view,

        "menu_config":
            menu_admin_view
    }

    return registry


# =========================================================
# LOGOUT
# =========================================================

def logout(page):

    LOGGER.info(
        "Logout executado"
    )

    try:

        page.usuario_logado = None

    except Exception:

        pass

    page.clean()

    from ui.login import (
        login_view
    )

    page.add(
        login_view(page)
    )

    page.update()


# =========================================================
# RESPONSIVIDADE
# =========================================================

def calcular_layout(page):

    altura = page.height or 800

    cfg = dict(
        MENU_UI_CONFIG
    )

    # =====================================================
    # TELAS PEQUENAS
    # =====================================================

    if altura <= 650:

        cfg["compact_height"] = 30

        cfg["dense_spacing"] = 0

        cfg["indent_size"] = 14

        cfg["padding_x"] = 4

    # =====================================================
    # MÉDIA
    # =====================================================

    elif altura <= 850:

        cfg["compact_height"] = 34

        cfg["dense_spacing"] = 1

        cfg["indent_size"] = 18

    return cfg


# =========================================================
# LOAD SCREEN
# =========================================================

def carregar_conteudo(
    page,
    content_area,
    rota,
    usuario
):

    try:

        rota = str(
            rota or ""
        ).strip().lower()

        LOGGER.info(
            (
                f"LOAD SCREEN "
                f"{rota}"
            )
        )

        registry = get_screen_registry()

        # =================================================
        # VIEW REGISTRADA
        # =================================================

        if rota in registry:

            content_area.content = registry[
                rota
            ](page)

        # =================================================
        # VIEW PADRÃO
        # =================================================

        else:

            content_area.content = ft.Container(

                expand=True,

                alignment=ft.alignment.center,

                content=ft.Column([

                    ft.Icon(
                        ft.Icons.WEB,
                        size=48
                    ),

                    ft.Text(

                        (
                            f"Tela: "
                            f"{rota}"
                        ),

                        size=24,

                        weight="bold"
                    ),

                    ft.Text(

                        (
                            f"Usuário: "
                            f"{usuario['login']}"
                        )
                    )

                ],

                    horizontal_alignment=(
                        ft.CrossAxisAlignment.CENTER
                    ),

                    spacing=10
                )
            )

        page.update()

    except Exception:

        LOGGER.exception(
            "LOAD SCREEN ERROR"
        )


# =========================================================
# MENU BUTTON
# =========================================================

def menu_button(

    menu,

    page,

    content_area,

    usuario,

    layout_cfg
):

    nome = menu["nome"]

    rota = menu.get(
        "rota"
    )

    tipo = menu.get(
        "tipo"
    )

    nivel = int(
        menu.get(
            "_nivel",
            0
        )
    )

    icone = get_icone(tipo)

    icon_map = {

        "folder":
            ft.Icons.FOLDER,

        "menu":
            ft.Icons.MENU,

        "web":
            ft.Icons.WEB,

        "help":
            ft.Icons.HELP
    }

    return ft.Container(

        height=layout_cfg[
            "compact_height"
        ],

        border_radius=layout_cfg[
            "border_radius"
        ],

        bgcolor=getattr(
            ft.Colors,
            get_cor(tipo),
            ft.Colors.WHITE
        ),

        padding=ft.padding.only(

            left=get_indent(nivel),

            right=4
        ),

        content=ft.TextButton(

            content=ft.Row([

                ft.Icon(

                    icon_map.get(
                        icone,
                        ft.Icons.HELP
                    ),

                    size=layout_cfg[
                        "icon_size"
                    ]
                ),

                ft.Text(

                    nome,

                    size=layout_cfg[
                        "font_size"
                    ],

                    weight=(

                        "bold"

                        if is_bold(tipo)

                        else None
                    )
                )

            ],

                spacing=6
            ),

            style=ft.ButtonStyle(

                padding=layout_cfg[
                    "padding_y"
                ],

                visual_density=(
                    ft.VisualDensity.COMPACT
                )
            ),

            on_click=lambda e:
                carregar_conteudo(

                    page,

                    content_area,

                    rota,

                    usuario
                )
        )
    )


# =========================================================
# BUILD MENU CONTROLS
# =========================================================

def build_menu_controls(

    page,

    menus,

    content_area,

    usuario,

    layout_cfg
):

    controls = []

    tree = flatten_tree(
        menus
    )

    for menu in tree:

        controls.append(

            menu_button(

                menu,

                page,

                content_area,

                usuario,

                layout_cfg
            )
        )

    return controls


# =========================================================
# MAIN LAYOUT
# =========================================================

def carregar_main_layout(
    page,
    usuario
):

    LOGGER.info(
        (
            f"MAIN LAYOUT "
            f"{usuario['login']}"
        )
    )

    page.clean()

    menus = listar_menus_usuario(
        usuario
    )

    LOGGER.info(
        (
            f"Menus carregados "
            f"{len(menus)}"
        )
    )

    layout_cfg = calcular_layout(
        page
    )

    # =====================================================
    # CONTENT AREA
    # =====================================================

    content_area = ft.Container(

        expand=True,

        padding=20,

        content=ft.Column([

            ft.Text(

                (
                    f"Bem-vindo "
                    f"{usuario['login']}"
                ),

                size=26,

                weight="bold"
            ),

            ft.Text(

                (
                    f"Perfil: "
                    f"{usuario['perfil_nome']}"
                ),

                size=15
            )

        ],

            spacing=5
        )
    )

    # =====================================================
    # MENU
    # =====================================================

    menu_controls = build_menu_controls(

        page,

        menus,

        content_area,

        usuario,

        layout_cfg
    )

    # =====================================================
    # SIDEBAR
    # =====================================================

    sidebar = ft.Container(

        width=260,

        bgcolor=ft.Colors.GREY_200,

        padding=layout_cfg[
            "padding_x"
        ],

        content=ft.Column([

            # =============================================
            # HEADER
            # =============================================

            ft.Container(

                padding=ft.padding.only(
                    bottom=6
                ),

                content=ft.Text(

                    "MENU",

                    size=20,

                    weight="bold"
                )
            ),

            # =============================================
            # MENUS
            # =============================================

            *menu_controls,

            ft.Divider(height=10),

            # =============================================
            # LOGOUT
            # =============================================

            ft.ElevatedButton(

                "Logout",

                icon=ft.Icons.LOGOUT,

                height=38,

                on_click=lambda e:
                    logout(page)
            )

        ],

            spacing=layout_cfg[
                "dense_spacing"
            ],

            scroll=ft.ScrollMode.AUTO,

            expand=True
        )
    )

    # =====================================================
    # LAYOUT
    # =====================================================

    layout = ft.Row([

        sidebar,

        content_area

    ],

        expand=True
    )

    page.add(layout)

    page.update()