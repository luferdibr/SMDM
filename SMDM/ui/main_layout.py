# =========================================================
# ui/main_layout.py
# =========================================================

import logging

import flet as ft

from config.settings import (
    APP_CONFIG,
)

from security.session_service import (

    obter_usuario,

    encerrar_sessao,
)

from modules.administracao.menus.services.menu_service import (
    invalidate_menu_cache,
    listar_menus_usuario,
)

from ui.dashboard import (
    dashboard_view,
)

from ui.login import (
    login_view,
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
    "MAIN_LAYOUT"
)

CONTENT_AREA = None

SIDEBAR_AREA = None

SIDEBAR_DIVIDER = None

# =========================================================
# ROUTES
# =========================================================

def resolver_view(
    rota,
):

    rota = str(
        rota or "dashboard"
    ).strip().lower()

    if rota in (
        "",
        "dashboard",
        "/dashboard",
    ):

        return dashboard_view

    rotas = {

        "usuarios": (
            "modules.administracao.menus.ui.usuarios",
            "usuarios_view",
        ),

        "perfis": (
            "modules.administracao.perfis.ui.perfis",
            "perfil_view",
        ),

        "menus": (
            "modules.administracao.menus.ui.menu_admin",
            "menu_admin_view",
        ),

        "menu": (
            "modules.administracao.menus.ui.menu_admin",
            "menu_admin_view",
        ),

        "menu_admin": (
            "modules.administracao.menus.ui.menu_admin",
            "menu_admin_view",
        ),

        "menu_config": (
            "modules.administracao.menus.ui.menu_admin",
            "menu_admin_view",
        ),

        "menu_editor": (
            "modules.administracao.menus.ui.menu_editor",
            "menu_editor_view",
        ),

        "menus_editor": (
            "modules.administracao.menus.ui.menu_editor",
            "menu_editor_view",
        ),

        "editor_menu": (
            "modules.administracao.menus.ui.menu_editor",
            "menu_editor_view",
        ),

        "locais": (
            "ui.locais",
            "locais_view",
        ),

        "loc_tipos": (
            "ui.loc_tipos",
            "loc_tipos_view",
        ),

        "loc_estruturas": (
            "ui.loc_estruturas",
            "loc_estruturas_view",
        ),

        "loc_ambientes": (
            "ui.loc_ambientes",
            "loc_ambientes_view",
        ),

<<<<<<< HEAD
=======
        "atores": (
            "modules.cadastros.atores.ui",
            "atores_view",
        ),

        "clientes": (
            "modules.cadastros.clientes.ui",
            "clientes_view",
        ),

        "empresas": (
            "modules.cadastros.empresas.ui",
            "empresas_view",
        ),

>>>>>>> 25/05/2026 - 12:09
        "auditoria": (
            "ui.auditoria",
            "auditoria_view",
        ),
    }

    destino = rotas.get(
        rota.strip("/")
    )

    if not destino:

        return None

    module_name, view_name = destino

    try:

        module = __import__(
            module_name,
            fromlist=[view_name],
        )

        return getattr(
            module,
            view_name,
        )

    except Exception:

        LOGGER.exception(
            "Erro carregando rota: %s",
            rota,
        )

        return None


def navegar(
    page: ft.Page,
    rota,
):

    global CONTENT_AREA
    global SIDEBAR_AREA
    global SIDEBAR_DIVIDER

    rota_normalizada = str(
        rota or "dashboard"
    ).strip().lower()

    if rota_normalizada in (
        "",
        "dashboard",
        "/dashboard",
    ) and CONTENT_AREA:

        carregar_main_layout(
            page
        )

        return

    view = resolver_view(
        rota
    )

    if not view:

        content = ft.Container(

            expand=True,

            alignment=ft.Alignment(0, 0),

            content=ft.Column(

                horizontal_alignment=(
                    ft.CrossAxisAlignment.CENTER
                ),

                alignment=(
                    ft.MainAxisAlignment.CENTER
                ),

                controls=[

                    ft.Icon(

                        ft.Icons.CONSTRUCTION,

                        size=72,

                        color=PRIMARY_COLOR,
                    ),

                    ft.Text(

                        "item em produção, aguarde!",

                        size=24,

                        weight=ft.FontWeight.BOLD,
                    ),
                ],
            ),
        )

    else:

        content = view(
            page
        )

    if CONTENT_AREA:

        if SIDEBAR_AREA:

            SIDEBAR_AREA.visible = False

        if SIDEBAR_DIVIDER:

            SIDEBAR_DIVIDER.visible = False

        CONTENT_AREA.content = content

        page.update()

# =========================================================
# MENU BUTTON
# =========================================================

def menu_button(

    text,

    icon,

    on_click=None,

    level=0,

    selected=False,
):

    indent = min(
        int(level) * 12,
        36,
    )

    return ft.Container(

        margin=ft.Margin(
            indent,
            0,
            0,
            1,
        ),

        height=32,

        border_radius=4,

        bgcolor=(
            ft.Colors.TRANSPARENT
        ),

        padding=ft.Padding(
            6,
            0,
            6,
            0,
        ),

        on_click=on_click,

        content=ft.Row(

            spacing=8,

            vertical_alignment=(
                ft.CrossAxisAlignment.CENTER
            ),

            controls=[

                ft.Icon(
                    icon,
                    size=15,
                    color=(
                        PRIMARY_COLOR
                        if on_click
                        else TEXT_SECONDARY
                    ),
                ),

                ft.Text(
                    text,
                    size=12,
                    weight=(
                        ft.FontWeight.W_600
                        if selected
                        else ft.FontWeight.W_400
                    ),
                    color=(
                        TEXT_PRIMARY
                        if on_click
                        else TEXT_SECONDARY
                    ),
                    expand=True,
                    max_lines=1,
                    overflow=ft.TextOverflow.ELLIPSIS,
                ),
            ],
        ),
    )


def menu_group(

    text,

    icon,

    level=0,
):

    indent = min(
        int(level) * 12,
        36,
    )

    return ft.Container(

        margin=ft.Margin(
            indent,
            8,
            0,
            2,
        ),

        padding=ft.Padding(
            6,
            0,
            6,
            0,
        ),

        content=ft.Text(
            str(text or "").upper(),
            size=10,
            weight=ft.FontWeight.BOLD,
            color=TEXT_SECONDARY,
            max_lines=1,
            overflow=ft.TextOverflow.ELLIPSIS,
        ),
    )


def resolver_icone(
    nome,
):

    nome = str(
        nome or ""
    ).strip().upper()

    if not nome:

        return ft.Icons.CIRCLE

    return getattr(
        ft.Icons,
        nome,
        ft.Icons.CIRCLE,
    )


def montar_menu_controls(
    page,
    menus,
    level=0,
):

    controls = []

    for item in menus:

        filhos = (
            item.get("filhos")
            or []
        )

        rota = item.get(
            "rota"
        )

        tipo = str(
            item.get(
                "tipo",
                "T",
            )
        ).strip().upper()

        nome = item.get(
            "nome",
            "-",
        )

        icone = resolver_icone(
            item.get("icone")
        )

        if tipo == "S" and rota:

            controls.append(

                menu_button(

                    nome,

                    icone,

                    lambda e, r=rota: navegar(
                        page,
                        r,
                    ),

                    level=level,
                )
            )

        else:

            filhos_controls = montar_menu_controls(
                page,
                filhos,
                level + 1,
            )

            controls.append(

                menu_group(
                    nome,
                    icone,
                    level=level,
                )
            )

            controls.extend(
                filhos_controls
            )

    return controls

# =========================================================
# SIDEBAR
# =========================================================

def sidebar(
    page: ft.Page,
):

    usuario = (
        obter_usuario()
        or {}
    )

    try:

        menus_usuario = listar_menus_usuario(
            usuario
        )

    except Exception:

        LOGGER.exception(
            "Erro carregando menu do usuário."
        )

        menus_usuario = []

    # =====================================================
    # LOGOUT
    # =====================================================

    def logout(e):

        LOGGER.info(
            "Logout."
        )

        try:

            from services.auditoria_service import (
                auditoria_logout,
            )

            auditoria_logout(
                usuario.get(
                    "login",
                    "SYSTEM",
                )
            )

        except Exception:

            LOGGER.exception(
                "Erro auditoria logout."
            )

        encerrar_sessao()

        page.clean()

        login_view(page)

    return ft.Container(

        width=240,

        bgcolor=SURFACE_COLOR,

        padding=ft.Padding(
            14,
            16,
            14,
            12,
        ),

        content=ft.Column(

            spacing=10,

            controls=[

                ft.Text(

                    APP_CONFIG.get(
                        "short_name",
                        "SMDM",
                    ),

                    size=22,

                    weight=(
                        ft.FontWeight.BOLD
                    ),

                    color=PRIMARY_COLOR,
                ),

                ft.Divider(height=1),

                ft.Text(

                    usuario.get(
                        "login",
                        "-"
                    ),

                    size=13,

                    weight=(
                        ft.FontWeight.BOLD
                    ),
                ),

                ft.Text(

                    usuario.get(
                        "nome",
                        "-"
                    ),

                    size=11,

                    color=TEXT_SECONDARY,
                ),

                ft.Divider(height=1),

                ft.Container(

                    expand=True,

                    content=ft.Column(

                        spacing=0,

                        expand=True,

                        scroll=ft.ScrollMode.AUTO,

                        controls=montar_menu_controls(
                            page,
                            menus_usuario,
                        ),
                    ),
                ),

                ft.Divider(height=1),

                menu_button(

                    "Logout",

                    ft.Icons.LOGOUT,

                    logout,
                ),
            ],
        ),
    )

# =========================================================
# TOPBAR
# =========================================================

def topbar(
    page: ft.Page,
):

    def voltar_menu(e):

        carregar_main_layout(
            page
        )

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

                    APP_CONFIG.get(
                        "system_name",
                        APP_CONFIG.get(
                            "name",
                            "Sistema",
                        ),
                    ),

                    size=22,

                    weight=(
                        ft.FontWeight.BOLD
                    ),
                ),

                ft.Row(

                    spacing=10,

                    vertical_alignment=(
                        ft.CrossAxisAlignment.CENTER
                    ),

                    controls=[

                        ft.Text(
                            APP_CONFIG.get(
                                "name",
                                "ERP",
                            )
                        ),

                        ft.OutlinedButton(

                            content=ft.Row(

                                spacing=6,

                                alignment=(
                                    ft.MainAxisAlignment.CENTER
                                ),

                                controls=[

                                    ft.Icon(
                                        ft.Icons.MENU,
                                        size=16,
                                    ),

                                    ft.Text(
                                        "Menu",
                                        size=12,
                                    ),
                                ],
                            ),

                            height=34,

                            on_click=voltar_menu,
                        ),
                    ],
                ),
            ],
        ),
    )

# =========================================================
# MAIN CONTENT
# =========================================================

def main_content(
    page: ft.Page,
):

    return ft.Container(

        expand=True,

        bgcolor=BACKGROUND_COLOR,

        padding=20,

        content=dashboard_view(
            page
        ),
    )

# =========================================================
# MAIN LAYOUT
# =========================================================

def carregar_main_layout(
    page: ft.Page,
):

    global CONTENT_AREA
    global SIDEBAR_AREA
    global SIDEBAR_DIVIDER

    LOGGER.info(
        "Main layout."
    )

    invalidate_menu_cache()

    page.clean()

    page.bgcolor = (
        BACKGROUND_COLOR
    )

    page.horizontal_alignment = (
        ft.CrossAxisAlignment.START
    )

    page.vertical_alignment = (
        ft.MainAxisAlignment.START
    )

    page.usuario_logado = (
        obter_usuario()
        or {}
    )

    CONTENT_AREA = ft.Container(

        expand=True,

        bgcolor=BACKGROUND_COLOR,

        padding=20,

        content=dashboard_view(
            page
        ),
    )

    SIDEBAR_AREA = sidebar(
        page
    )

    SIDEBAR_DIVIDER = ft.VerticalDivider(
        width=1
    )

    page.add(

        ft.Row(

            expand=True,

            spacing=0,

            controls=[

                SIDEBAR_AREA,

                SIDEBAR_DIVIDER,

                ft.Container(

                    expand=True,

                    content=ft.Column(

                        expand=True,

                        spacing=0,

                        controls=[

                            topbar(page),

                            CONTENT_AREA,
                        ],
                    ),
                ),
            ],
        )
    )

    page.update()
