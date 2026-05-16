# ui/menu_editor.py

import logging

import flet as ft

from services.menu_editor_service import (

    listar_menus,

    salvar_menu,

    excluir_menu
)

from services.menu_tree_service import (

    build_menu_tree,

    flatten_tree
)

from core.menu_constants import (

    MENU_UI_CONFIG,

    tipos_menu,

    get_label,

    get_icone,

    get_cor,

    get_indent,

    permite_rota,

    permite_pai,

    is_bold
)


# =========================================================
# LOGGER
# =========================================================

LOGGER = logging.getLogger(
    "MDM_MENU_EDITOR"
)


# =========================================================
# HELPERS
# =========================================================

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

            ft.Colors.GREEN_700
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
# FORM RESET
# =========================================================

def limpar_form(

    txt_id,
    txt_nome,
    txt_rota,
    txt_ordem,
    chk_ativo,
    chk_sistema,
    ddl_tipo,
    ddl_pai
):

    txt_id.value = ""

    txt_nome.value = ""

    txt_rota.value = ""

    txt_ordem.value = "10"

    chk_ativo.value = True

    chk_sistema.value = False

    ddl_tipo.value = None

    ddl_pai.value = None


# =========================================================
# BUILD OPTIONS
# =========================================================

def build_tipo_options():

    options = []

    for tipo in tipos_menu():

        options.append(

            ft.dropdown.Option(

                key=tipo,

                text=(
                    f"{tipo} - "
                    f"{get_label(tipo)}"
                )
            )
        )

    return options


# =========================================================
# BUILD MENU OPTIONS
# =========================================================

def build_menu_options(menus):

    options = [

        ft.dropdown.Option(
            key="",
            text="Sem pai"
        )
    ]

    for menu in menus:

        nivel = int(
            menu.get(
                "_nivel",
                0
            )
        )

        prefixo = (
            "· " * nivel
        )

        options.append(

            ft.dropdown.Option(

                key=str(
                    menu["id"]
                ),

                text=(
                    f"{prefixo}"
                    f"{menu['nome']}"
                )
            )
        )

    return options


# =========================================================
# ROW MENU
# =========================================================

def build_menu_row(

    menu,

    on_editar,

    on_excluir
):

    tipo = menu.get(
        "tipo"
    )

    nivel = int(
        menu.get(
            "_nivel",
            0
        )
    )

    return ft.Container(

        height=MENU_UI_CONFIG[
            "compact_height"
        ],

        bgcolor=getattr(

            ft.Colors,

            get_cor(tipo),

            ft.Colors.WHITE
        ),

        border_radius=MENU_UI_CONFIG[
            "border_radius"
        ],

        padding=ft.padding.only(

            left=get_indent(nivel),

            right=6
        ),

        content=ft.Row([

            # =================================================
            # MENU
            # =================================================

            ft.Container(

                expand=True,

                content=ft.Row([

                    ft.Icon(

                        get_icon(tipo),

                        size=MENU_UI_CONFIG[
                            "icon_size"
                        ]
                    ),

                    ft.Column([

                        ft.Text(

                            menu["nome"],

                            size=MENU_UI_CONFIG[
                                "font_size"
                            ],

                            weight=(

                                "bold"

                                if is_bold(tipo)

                                else None
                            )
                        ),

                        ft.Text(

                            (
                                f"ID {menu['id']} | "
                                f"{get_label(tipo)} | "
                                f"{menu.get('rota') or '-'}"
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
            # BOTÕES
            # =================================================

            ft.IconButton(

                icon=ft.Icons.EDIT,

                tooltip="Editar",

                icon_size=18,

                on_click=lambda e:
                    on_editar(menu)
            ),

            ft.IconButton(

                icon=ft.Icons.DELETE,

                tooltip="Excluir",

                icon_color=ft.Colors.RED_400,

                icon_size=18,

                on_click=lambda e:
                    on_excluir(menu)
            )

        ],

            spacing=4
        )
    )


# =========================================================
# VIEW
# =========================================================

def menu_editor_view(page):

    usuario = getattr(
        page,
        "usuario_logado",
        None
    )

    menus_flat = []

    # =====================================================
    # COMPONENTES
    # =====================================================

    txt_id = ft.TextField(
        visible=False
    )

    txt_nome = ft.TextField(

        label="Nome",

        dense=True,

        expand=True
    )

    txt_rota = ft.TextField(

        label="Rota",

        dense=True,

        expand=True
    )

    txt_ordem = ft.TextField(

        label="Ordem",

        dense=True,

        width=100,

        value="10"
    )

    chk_ativo = ft.Checkbox(

        label="Ativo",

        value=True
    )

    chk_sistema = ft.Checkbox(

        label="Sistema",

        value=False
    )

    ddl_tipo = ft.Dropdown(

        label="Tipo",

        dense=True,

        width=180,

        options=build_tipo_options()
    )

    ddl_pai = ft.Dropdown(

        label="Menu Pai",

        dense=True,

        expand=True
    )

    lista = ft.Column(

        expand=True,

        scroll=ft.ScrollMode.AUTO,

        spacing=4
    )

    txt_status = ft.Text(
        "",
        size=12,
        color=ft.Colors.RED
    )

    # =====================================================
    # REFRESH
    # =====================================================

    def refresh(e=None):

        try:

            resultado = listar_menus()

            if not resultado["sucesso"]:

                raise Exception(
                    resultado["mensagem"]
                )

            menus = resultado["dados"]

            tree = build_menu_tree(
                menus
            )

            flat = flatten_tree(
                tree
            )

            menus_flat.clear()

            menus_flat.extend(flat)

            lista.controls.clear()

            ddl_pai.options = (
                build_menu_options(
                    flat
                )
            )

            for menu in flat:

                lista.controls.append(

                    build_menu_row(

                        menu,

                        editar_menu,

                        excluir_menu_click
                    )
                )

            page.update()

        except Exception as ex:

            LOGGER.exception(
                "REFRESH_ERROR"
            )

            txt_status.value = str(ex)

            page.update()

    # =====================================================
    # TIPO CHANGE
    # =====================================================

    def tipo_change(e):

        tipo = ddl_tipo.value

        txt_rota.disabled = (
            not permite_rota(tipo)
        )

        ddl_pai.disabled = (
            not permite_pai(tipo)
        )

        if not permite_rota(tipo):

            txt_rota.value = ""

        if not permite_pai(tipo):

            ddl_pai.value = ""

        page.update()

    ddl_tipo.on_change = tipo_change

    # =====================================================
    # EDITAR
    # =====================================================

    def editar_menu(menu):

        txt_id.value = str(
            menu["id"]
        )

        txt_nome.value = (
            menu["nome"]
        )

        txt_rota.value = (
            menu.get("rota")
            or ""
        )

        txt_ordem.value = str(
            menu.get(
                "ordem",
                10
            )
        )

        chk_ativo.value = bool(
            menu.get(
                "ativo",
                True
            )
        )

        chk_sistema.value = bool(
            menu.get(
                "sistema",
                False
            )
        )

        ddl_tipo.value = (
            menu.get("tipo")
        )

        pai = (

            menu.get("pai")

            or

            menu.get(
                "menu_pai"
            )
        )

        ddl_pai.value = (

            str(pai)

            if pai

            else ""
        )

        tipo_change(None)

        page.update()

    # =====================================================
    # SALVAR
    # =====================================================

    def salvar_click(e):

        try:

            dados = {

                "id": (

                    int(txt_id.value)

                    if txt_id.value

                    else None
                ),

                "nome":
                    txt_nome.value,

                "rota":
                    txt_rota.value,

                "pai": (

                    int(ddl_pai.value)

                    if ddl_pai.value

                    else None
                ),

                "ordem": int(
                    txt_ordem.value
                ),

                "ativo":
                    chk_ativo.value,

                "sistema":
                    chk_sistema.value,

                "tipo":
                    ddl_tipo.value,

                "admin_level": 10
            }

            resultado = salvar_menu(

                usuario,

                dados
            )

            if not resultado["sucesso"]:

                raise Exception(
                    resultado["mensagem"]
                )

            snackbar(

                page,

                resultado["mensagem"]
            )

            limpar_form(

                txt_id,
                txt_nome,
                txt_rota,
                txt_ordem,
                chk_ativo,
                chk_sistema,
                ddl_tipo,
                ddl_pai
            )

            refresh()

        except Exception as ex:

            LOGGER.exception(
                "SAVE_ERROR"
            )

            snackbar(
                page,
                str(ex),
                erro=True
            )

    # =====================================================
    # EXCLUIR
    # =====================================================

    def excluir_menu_click(menu):

        def confirmar(e):

            try:

                resultado = excluir_menu(

                    usuario,

                    menu["id"]
                )

                dlg.open = False

                page.update()

                if not resultado["sucesso"]:

                    raise Exception(
                        resultado["mensagem"]
                    )

                snackbar(

                    page,

                    resultado["mensagem"]
                )

                refresh()

            except Exception as ex:

                LOGGER.exception(
                    "DELETE_ERROR"
                )

                snackbar(
                    page,
                    str(ex),
                    erro=True
                )

        dlg = ft.AlertDialog(

            modal=True,

            title=ft.Text(
                "Confirmar"
            ),

            content=ft.Text(

                (
                    f"Excluir "
                    f"{menu['nome']}?"
                )
            ),

            actions=[

                ft.TextButton(

                    "Cancelar",

                    on_click=lambda e:
                        fechar_dialog()
                ),

                ft.ElevatedButton(

                    "Excluir",

                    color=ft.Colors.WHITE,

                    bgcolor=ft.Colors.RED,

                    on_click=confirmar
                )
            ]
        )

        def fechar_dialog():

            dlg.open = False

            page.update()

        page.dialog = dlg

        dlg.open = True

        page.update()

    # =====================================================
    # NOVO
    # =====================================================

    def novo_click(e):

        limpar_form(

            txt_id,
            txt_nome,
            txt_rota,
            txt_ordem,
            chk_ativo,
            chk_sistema,
            ddl_tipo,
            ddl_pai
        )

        page.update()

    # =====================================================
    # BOTÕES
    # =====================================================

    btn_salvar = ft.ElevatedButton(

        "Salvar",

        icon=ft.Icons.SAVE,

        height=38,

        on_click=salvar_click
    )

    btn_novo = ft.OutlinedButton(

        "Novo",

        icon=ft.Icons.ADD,

        height=38,

        on_click=novo_click
    )

    btn_refresh = ft.IconButton(

        icon=ft.Icons.REFRESH,

        tooltip="Atualizar",

        on_click=refresh
    )

    btn_voltar = ft.TextButton(

        "Voltar",

        icon=ft.Icons.ARROW_BACK,

        on_click=lambda e:
            voltar_dashboard(page)
    )

    refresh()

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

                        "Editor de Menus",

                        size=24,

                        weight="bold"
                    ),

                    ft.Text(

                        "Estrutura dinâmica",

                        size=11,

                        color=ft.Colors.GREY_700
                    )

                ],

                    spacing=0,

                    expand=True
                ),

                btn_refresh,

                btn_voltar
            ]),

            # =================================================
            # FORM
            # =================================================

            ft.Container(

                padding=10,

                border_radius=10,

                bgcolor=ft.Colors.GREY_100,

                content=ft.Column([

                    ft.Row([

                        txt_nome,

                        ddl_tipo

                    ],

                        spacing=8
                    ),

                    ft.Row([

                        txt_rota,

                        ddl_pai,

                        txt_ordem

                    ],

                        spacing=8
                    ),

                    ft.Row([

                        chk_ativo,

                        chk_sistema

                    ],

                        spacing=10
                    ),

                    ft.Row([

                        btn_salvar,

                        btn_novo

                    ],

                        spacing=8
                    )

                ],

                    spacing=8
                )
            ),

            txt_status,

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