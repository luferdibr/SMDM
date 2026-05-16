# ui/menu_admin.py

import logging

import flet as ft

from config.settings import (
    APP_CONFIG
)

from services.user_service import (
    listar_perfis
)

from services.menu_admin_service import (

    listar_menus_com_permissao,

    salvar_permissoes,

    copiar_permissoes,

    get_permissoes_usuario
)

from services.menu_tree_service import (

    build_menu_tree,

    flatten_tree
)

from core.menu_constants import (

    MENU_UI_CONFIG,

    ADMIN_LEVEL_ROOT,

    TIPO_TITULO,

    TIPO_MENU,

    TIPO_SUBMENU,

    get_label,

    get_icone,

    get_cor,

    get_indent,

    is_bold
)


# =========================================================
# LOGGER
# =========================================================

LOGGER = logging.getLogger(
    "MDM_MENU_ADMIN"
)


# =========================================================
# HELPERS
# =========================================================

def get_usuario(page):

    usuario = getattr(
        page,
        "usuario_logado",
        None
    )

    if (
        not usuario
        or
        not isinstance(usuario, dict)
    ):
        return None

    return usuario


def snackbar(
    page,
    mensagem,
    erro=False
):

    page.snack_bar = ft.SnackBar(

        content=ft.Text(
            mensagem
        ),

        bgcolor=(

            ft.Colors.RED_400

            if erro

            else

            ft.Colors.GREEN_600
        )
    )

    page.snack_bar.open = True

    page.update()


def voltar_dashboard(page):

    from ui.main_layout import (
        carregar_conteudo
    )

    carregar_conteudo(

        page,

        page.content_area,

        "dashboard",

        page.usuario_logado
    )


def get_icon(tipo):

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

    return icon_map.get(

        get_icone(tipo),

        ft.Icons.HELP
    )


# =========================================================
# CHECKBOX
# =========================================================

def compact_checkbox(
    value,
    disabled=False
):

    return ft.Checkbox(

        value=bool(value),

        disabled=disabled,

        visual_density=(
            ft.VisualDensity.COMPACT
        ),

        scale=0.85
    )


# =========================================================
# LINHA MENU
# =========================================================

def criar_linha_menu(

    menu,

    controles,

    pode_editar
):

    tipo = menu.get(
        "tipo_menu"
    )

    nivel = int(
        menu.get(
            "_nivel",
            0
        )
    )

    chk_ver = compact_checkbox(
        menu.get("ver"),
        not pode_editar
    )

    chk_editar = compact_checkbox(
        menu.get("editar"),
        not pode_editar
    )

    chk_excluir = compact_checkbox(
        menu.get("excluir"),
        not pode_editar
    )

    controles.append({

        "menu_id": menu["id"],

        "ver": chk_ver,

        "editar": chk_editar,

        "excluir": chk_excluir
    })

    return ft.Container(

        height=MENU_UI_CONFIG[
            "compact_height"
        ],

        padding=ft.padding.only(
            left=6,
            right=6
        ),

        border_radius=MENU_UI_CONFIG[
            "border_radius"
        ],

        bgcolor=getattr(

            ft.Colors,

            get_cor(tipo),

            ft.Colors.WHITE
        ),

        content=ft.Row([

            # =================================================
            # MENU
            # =================================================

            ft.Container(

                expand=True,

                padding=ft.padding.only(
                    left=get_indent(nivel)
                ),

                content=ft.Row([

                    ft.Icon(

                        get_icon(tipo),

                        size=MENU_UI_CONFIG[
                            "icon_size"
                        ],

                        color=ft.Colors.BLUE_700
                    ),

                    ft.Column([

                        ft.Text(

                            menu["nome"],

                            weight=(

                                "bold"

                                if is_bold(tipo)

                                else None
                            ),

                            size=MENU_UI_CONFIG[
                                "font_size"
                            ]
                        ),

                        ft.Text(

                            (
                                f"ID {menu['id']} | "
                                f"{get_label(tipo)}"
                            ),

                            size=MENU_UI_CONFIG[
                                "sub_font_size"
                            ],

                            color=ft.Colors.GREY_700
                        )

                    ],

                        spacing=0
                    )

                ],
                    spacing=6
                )
            ),

            # =================================================
            # VER
            # =================================================

            ft.Container(
                width=55,
                alignment=ft.alignment.center,
                content=chk_ver
            ),

            # =================================================
            # EDITAR
            # =================================================

            ft.Container(
                width=55,
                alignment=ft.alignment.center,
                content=chk_editar
            ),

            # =================================================
            # EXCLUIR
            # =================================================

            ft.Container(
                width=55,
                alignment=ft.alignment.center,
                content=chk_excluir
            )

        ],

            spacing=4
        )
    )


# =========================================================
# VIEW
# =========================================================

def menu_admin_view(page):

    usuario = get_usuario(page)

    # =====================================================
    # SESSÃO
    # =====================================================

    if not usuario:

        return ft.Container(

            expand=True,

            alignment=ft.alignment.center,

            content=ft.Text(
                "Sessão inválida."
            )
        )

    usuario_level = int(
        usuario.get(
            "admin_level",
            0
        )
    )

    is_root = (
        usuario_level >= ADMIN_LEVEL_ROOT
    )

    permissoes_usuario = get_permissoes_usuario(

        usuario,

        "menu_config"
    )

    if not permissoes_usuario.get("ver"):

        return ft.Container(

            expand=True,

            alignment=ft.alignment.center,

            content=ft.Text(
                "Acesso negado."
            )
        )

    pode_editar = bool(
        permissoes_usuario.get(
            "editar"
        )
    )

    controles = []

    # =====================================================
    # COMPONENTES
    # =====================================================

    txt_filtro = ft.TextField(

        label="Pesquisar",

        dense=True,

        height=40,

        width=220,

        prefix_icon=ft.Icons.SEARCH
    )

    ddl_perfil = ft.Dropdown(

        label="Perfil",

        dense=True,

        height=40,

        width=220
    )

    ddl_copiar = ft.Dropdown(

        label="Copiar de",

        dense=True,

        height=40,

        width=220
    )

    progress = ft.ProgressRing(

        visible=False,

        width=18,

        height=18
    )

    txt_status = ft.Text(
        "",
        color=ft.Colors.RED,
        size=12
    )

    lista = ft.Column(

        spacing=4,

        scroll=ft.ScrollMode.AUTO,

        expand=True
    )

    # =====================================================
    # PERFIS
    # =====================================================

    def carregar_perfis():

        try:

            perfis = listar_perfis()

            options = []

            for perfil in perfis:

                options.append(

                    ft.dropdown.Option(

                        key=str(
                            perfil["id"]
                        ),

                        text=(
                            f"{perfil['nome']} "
                            f"[{perfil['admin_level']}]"
                        )
                    )
                )

            ddl_perfil.options = options

            ddl_copiar.options = options.copy()

            page.update()

        except Exception as ex:

            LOGGER.exception(
                "LOAD_PERFIS_ERROR"
            )

            snackbar(
                page,
                str(ex),
                erro=True
            )

    # =====================================================
    # MENUS
    # =====================================================

    def carregar_menus(e=None):

        try:

            perfil_id = ddl_perfil.value

            if not perfil_id:

                lista.controls.clear()

                page.update()

                return

            progress.visible = True

            lista.controls.clear()

            controles.clear()

            page.update()

            menus = listar_menus_com_permissao(
                int(perfil_id)
            )

            tree = build_menu_tree(
                menus
            )

            flat = flatten_tree(
                tree
            )

            filtro = str(
                txt_filtro.value or ""
            ).strip().lower()

            for menu in flat:

                texto = (
                    f"{menu['nome']} "
                    f"{menu.get('rota') or ''}"
                ).lower()

                if filtro:

                    if filtro not in texto:
                        continue

                lista.controls.append(

                    criar_linha_menu(

                        menu,

                        controles,

                        pode_editar
                    )
                )

            progress.visible = False

            page.update()

        except Exception as ex:

            LOGGER.exception(
                "LOAD_MENU_ERROR"
            )

            progress.visible = False

            txt_status.value = str(ex)

            page.update()

    # =====================================================
    # SALVAR
    # =====================================================

    def salvar(e):

        try:

            perfil_id = ddl_perfil.value

            if not perfil_id:

                snackbar(
                    page,
                    "Selecione perfil.",
                    erro=True
                )

                return

            permissoes = []

            for item in controles:

                permissoes.append({

                    "menu_id": item["menu_id"],

                    "ver": bool(
                        item["ver"].value
                    ),

                    "editar": bool(
                        item["editar"].value
                    ),

                    "excluir": bool(
                        item["excluir"].value
                    )
                })

            resultado = salvar_permissoes(

                int(perfil_id),

                permissoes,

                usuario
            )

            if not resultado["sucesso"]:

                raise Exception(
                    resultado["mensagem"]
                )

            snackbar(
                page,
                resultado["mensagem"]
            )

        except Exception as ex:

            LOGGER.exception(
                "SAVE_PERMISSION_ERROR"
            )

            snackbar(
                page,
                str(ex),
                erro=True
            )

    # =====================================================
    # COPIAR
    # =====================================================

    def copiar(e):

        try:

            origem = ddl_copiar.value

            destino = ddl_perfil.value

            if not origem or not destino:

                snackbar(
                    page,
                    "Selecione perfis.",
                    erro=True
                )

                return

            resultado = copiar_permissoes(

                int(origem),

                int(destino),

                usuario
            )

            if not resultado["sucesso"]:

                raise Exception(
                    resultado["mensagem"]
                )

            carregar_menus()

            snackbar(
                page,
                resultado["mensagem"]
            )

        except Exception as ex:

            LOGGER.exception(
                "COPY_PERMISSION_ERROR"
            )

            snackbar(
                page,
                str(ex),
                erro=True
            )

    txt_filtro.on_change = carregar_menus

    ddl_perfil.on_change = carregar_menus

    # =====================================================
    # BOTÕES
    # =====================================================

    btn_salvar = ft.ElevatedButton(

        "Salvar",

        height=38,

        icon=ft.Icons.SAVE,

        disabled=not pode_editar,

        on_click=salvar
    )

    btn_copiar = ft.OutlinedButton(

        "Copiar",

        height=38,

        icon=ft.Icons.CONTENT_COPY,

        disabled=(

            not pode_editar
            and
            not is_root
        ),

        on_click=copiar
    )

    btn_voltar = ft.TextButton(

        "Voltar",

        icon=ft.Icons.ARROW_BACK,

        on_click=lambda e:
            voltar_dashboard(page)
    )

    carregar_perfis()

    # =====================================================
    # VIEW
    # =====================================================

    return ft.Container(

        expand=True,

        padding=12,

        content=ft.Column([

            # =================================================
            # HEADER
            # =================================================

            ft.Row([

                ft.Column([

                    ft.Text(

                        "Permissões de Menu",

                        size=24,

                        weight="bold"
                    ),

                    ft.Text(

                        APP_CONFIG["name"],

                        size=11,

                        color=ft.Colors.GREY_700
                    )

                ],

                    spacing=0,
                    expand=True
                ),

                btn_voltar
            ]),

            # =================================================
            # FILTROS
            # =================================================

            ft.Row([

                ddl_perfil,

                ddl_copiar,

                txt_filtro,

                progress

            ],

                wrap=True,

                spacing=8
            ),

            # =================================================
            # AÇÕES
            # =================================================

            ft.Row([

                btn_salvar,

                btn_copiar

            ],
                spacing=8
            ),

            txt_status,

            # =================================================
            # HEADER GRID
            # =================================================

            ft.Container(

                padding=8,

                border_radius=8,

                bgcolor=ft.Colors.BLUE_100,

                content=ft.Row([

                    ft.Container(
                        expand=True,
                        content=ft.Text(
                            "Menu",
                            weight="bold"
                        )
                    ),

                    ft.Container(
                        width=55,
                        alignment=ft.alignment.center,
                        content=ft.Text(
                            "Ver",
                            weight="bold",
                            size=12
                        )
                    ),

                    ft.Container(
                        width=55,
                        alignment=ft.alignment.center,
                        content=ft.Text(
                            "Editar",
                            weight="bold",
                            size=12
                        )
                    ),

                    ft.Container(
                        width=55,
                        alignment=ft.alignment.center,
                        content=ft.Text(
                            "Excluir",
                            weight="bold",
                            size=12
                        )
                    )

                ])
            ),

            # =================================================
            # LISTA
            # =================================================

            ft.Container(

                expand=True,

                padding=6,

                bgcolor=ft.Colors.GREY_100,

                border_radius=10,

                content=lista
            )

        ],

            spacing=10,

            expand=True
        )
    )