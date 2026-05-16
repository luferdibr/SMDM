
import logging

import flet as ft

from config.settings import (
    APP_CONFIG
)

from services.perfil_service import (

    listar_perfis,

    criar_perfil,

    atualizar_perfil,

    excluir_perfil
)

from services.menu_admin_service import (
    get_permissoes_usuario
)

from ui.dashboard import (
    navegar
)


# ==================================================
# CONFIG
# ==================================================

ROOT_LEVEL = 100


# ==================================================
# LOGGER
# ==================================================

LOGGER = logging.getLogger(
    "MDM_PERFIS_UI"
)


# ==================================================
# HELPERS
# ==================================================

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


def get_cor_admin(level):

    if level >= ROOT_LEVEL:

        return ft.Colors.RED

    if level >= 50:

        return ft.Colors.ORANGE

    return ft.Colors.BLUE


def get_nome_admin(level):

    if level >= ROOT_LEVEL:
        return "ROOT"

    if level >= 50:
        return "ADMIN"

    return "OPERACIONAL"


# ==================================================
# VIEW
# ==================================================

def perfil_view(page):

    usuario = get_usuario(page)

    # ==============================================
    # SESSÃO
    # ==============================================

    if not usuario:

        return ft.Container(

            expand=True,

            alignment=ft.alignment.center,

            content=ft.Column([

                ft.Icon(
                    ft.Icons.ERROR,
                    size=70,
                    color=ft.Colors.RED
                ),

                ft.Text(
                    "Sessão inválida.",
                    size=24,
                    weight="bold"
                )

            ],
                spacing=20,
                horizontal_alignment=(
                    ft.CrossAxisAlignment.CENTER
                )
            )
        )

    usuario_level = int(
        usuario.get(
            "admin_level",
            0
        )
    )

    is_root = (
        usuario_level >= ROOT_LEVEL
    )

    # ==============================================
    # RBAC
    # ==============================================

    permissoes = get_permissoes_usuario(

        usuario,

        "perfis"
    )

    if not permissoes.get("ver"):

        return ft.Container(

            expand=True,

            alignment=ft.alignment.center,

            content=ft.Column([

                ft.Icon(
                    ft.Icons.LOCK,
                    size=72,
                    color=ft.Colors.RED
                ),

                ft.Text(
                    "Acesso negado.",
                    size=24,
                    weight="bold"
                )

            ],
                spacing=20,
                horizontal_alignment=(
                    ft.CrossAxisAlignment.CENTER
                )
            )
        )

    pode_editar = bool(
        permissoes.get("editar")
    )

    # ==============================================
    # COMPONENTES
    # ==============================================

    txt_id = ft.TextField(
        visible=False
    )

    txt_nome = ft.TextField(

        label="Nome Perfil",

        width=320
    )

    txt_validade = ft.TextField(

        label="Validade Senha (dias)",

        width=220
    )

    txt_admin_level = ft.TextField(

        label="Admin Level",

        width=180
    )

    chk_ativo = ft.Checkbox(

        label="Ativo",

        value=True
    )

    chk_sistema = ft.Checkbox(

        label="Perfil Sistêmico",

        value=False
    )

    txt_filtro = ft.TextField(

        label="Pesquisar",

        width=320,

        prefix_icon=ft.Icons.SEARCH
    )

    tabela = ft.Column(

        spacing=8,

        scroll=ft.ScrollMode.AUTO,

        expand=True
    )

    # ==============================================
    # HELPERS
    # ==============================================

    def limpar():

        txt_id.value = ""

        txt_nome.value = ""

        txt_validade.value = ""

        txt_admin_level.value = "10"

        chk_ativo.value = True

        chk_sistema.value = False

    # ==============================================
    # CARD PERFIL
    # ==============================================

    def criar_card(perfil):

        level = int(
            perfil["admin_level"]
        )

        sistema = bool(
            perfil["sistema"]
        )

        ativo = bool(
            perfil["ativo"]
        )

        return ft.Container(

            padding=12,

            border_radius=12,

            bgcolor=ft.Colors.WHITE,

            border=ft.border.all(

                1,

                ft.Colors.GREY_300
            ),

            content=ft.Row([

                # ==================================
                # INFO
                # ==================================

                ft.Container(

                    expand=True,

                    content=ft.Column([

                        ft.Row([

                            ft.Icon(

                                ft.Icons.ADMIN_PANEL_SETTINGS,

                                color=get_cor_admin(
                                    level
                                )
                            ),

                            ft.Text(

                                perfil["nome"],

                                size=16,

                                weight="bold"
                            ),

                            ft.Container(

                                padding=ft.padding.symmetric(

                                    horizontal=8,

                                    vertical=2
                                ),

                                bgcolor=get_cor_admin(
                                    level
                                ),

                                border_radius=20,

                                content=ft.Text(

                                    get_nome_admin(
                                        level
                                    ),

                                    color=ft.Colors.WHITE,

                                    size=11
                                )
                            )

                        ],
                            spacing=10
                        ),

                        ft.Text(

                            (
                                f"ID: {perfil['id']} | "
                                f"AdminLevel: {level}"
                            ),

                            size=11,

                            color=ft.Colors.GREY_700
                        ),

                        ft.Row([

                            ft.Icon(

                                (
                                    ft.Icons.CHECK_CIRCLE
                                    if ativo
                                    else
                                    ft.Icons.CANCEL
                                ),

                                color=(

                                    ft.Colors.GREEN

                                    if ativo

                                    else

                                    ft.Colors.RED
                                ),

                                size=16
                            ),

                            ft.Text(

                                (
                                    "Ativo"
                                    if ativo
                                    else
                                    "Inativo"
                                ),

                                size=12
                            ),

                            ft.Container(width=20),

                            ft.Icon(

                                (
                                    ft.Icons.SECURITY
                                    if sistema
                                    else
                                    ft.Icons.PERSON
                                ),

                                color=(

                                    ft.Colors.BLUE

                                    if sistema

                                    else

                                    ft.Colors.GREY
                                ),

                                size=16
                            ),

                            ft.Text(

                                (
                                    "Sistêmico"
                                    if sistema
                                    else
                                    "Operacional"
                                ),

                                size=12
                            )

                        ],
                            spacing=6
                        )

                    ],
                        spacing=6
                    )
                ),

                # ==================================
                # AÇÕES
                # ==================================

                ft.Row([

                    ft.IconButton(

                        icon=ft.Icons.EDIT,

                        disabled=(
                            not pode_editar
                        ),

                        on_click=lambda e,
                        p=perfil: editar(p)
                    ),

                    ft.IconButton(

                        icon=ft.Icons.DELETE,

                        disabled=(
                            not pode_editar
                        ),

                        icon_color=ft.Colors.RED,

                        on_click=lambda e,
                        p=perfil: remover(p)
                    )

                ])
            ])
        )

    # ==============================================
    # LOAD
    # ==============================================

    def carregar_perfis_view(e=None):

        try:

            filtro = str(
                txt_filtro.value or ""
            ).strip()

            tabela.controls.clear()

            perfis = listar_perfis(
                filtro
            )

            for perfil in perfis:

                tabela.controls.append(
                    criar_card(perfil)
                )

            page.update()

        except Exception as ex:

            LOGGER.exception(
                "LOAD PERFIS ERROR"
            )

            snackbar(
                page,
                str(ex),
                erro=True
            )

    # ==============================================
    # EDIT
    # ==============================================

    def editar(perfil):

        txt_id.value = perfil["id"]

        txt_nome.value = perfil["nome"]

        txt_validade.value = str(
            perfil["validade_senha"]
            or ""
        )

        txt_admin_level.value = str(
            perfil["admin_level"]
        )

        chk_ativo.value = bool(
            perfil["ativo"]
        )

        chk_sistema.value = bool(
            perfil["sistema"]
        )

        page.update()

    # ==============================================
    # REMOVE
    # ==============================================

    def remover(perfil):

        try:

            excluir_perfil(

                perfil["id"],

                usuario
            )

            carregar_perfis_view()

            snackbar(
                page,
                "Perfil removido."
            )

        except Exception as ex:

            LOGGER.exception(
                "DELETE PERFIL ERROR"
            )

            snackbar(
                page,
                str(ex),
                erro=True
            )

    # ==============================================
    # SAVE
    # ==============================================

    def salvar(e):

        try:

            if not pode_editar:

                snackbar(
                    page,
                    "Sem permissão.",
                    erro=True
                )

                return

            payload = {

                "nome": txt_nome.value,

                "validade_senha": (
                    txt_validade.value
                ),

                "admin_level": (
                    txt_admin_level.value
                ),

                "ativo": chk_ativo.value,

                "sistema": chk_sistema.value
            }

            # ======================================
            # NOVO
            # ======================================

            if not txt_id.value:

                criar_perfil(

                    payload,

                    usuario
                )

                snackbar(
                    page,
                    "Perfil criado."
                )

            # ======================================
            # UPDATE
            # ======================================

            else:

                atualizar_perfil(

                    int(txt_id.value),

                    payload,

                    usuario
                )

                snackbar(
                    page,
                    "Perfil atualizado."
                )

            limpar()

            carregar_perfis_view()

        except Exception as ex:

            LOGGER.exception(
                "SAVE PERFIL ERROR"
            )

            snackbar(
                page,
                str(ex),
                erro=True
            )

    # ==============================================
    # EVENTOS
    # ==============================================

    txt_filtro.on_change = (
        carregar_perfis_view
    )

    # ==============================================
    # BOTÕES
    # ==============================================

    btn_novo = ft.OutlinedButton(

        "Novo",

        icon=ft.Icons.ADD,

        disabled=not pode_editar,

        on_click=lambda e: (
            limpar(),
            page.update()
        )
    )

    btn_salvar = ft.ElevatedButton(

        "Salvar",

        icon=ft.Icons.SAVE,

        disabled=not pode_editar,

        on_click=salvar
    )

    btn_voltar = ft.TextButton(

        "Voltar",

        icon=ft.Icons.ARROW_BACK,

        on_click=lambda e: navegar(
            page,
            "dashboard"
        )
    )

    # ==============================================
    # INIT
    # ==============================================

    limpar()

    carregar_perfis_view()

    # ==============================================
    # LAYOUT
    # ==============================================

    return ft.Container(

        expand=True,

        padding=20,

        content=ft.Column([

            # ======================================
            # HEADER
            # ======================================

            ft.Row([

                ft.Column([

                    ft.Text(

                        "Perfis",

                        size=30,

                        weight="bold"
                    ),

                    ft.Text(

                        APP_CONFIG["name"],

                        size=13,

                        color=ft.Colors.GREY_700
                    )

                ],
                    spacing=2,
                    expand=True
                ),

                btn_voltar
            ]),

            ft.Divider(),

            # ======================================
            # FORM
            # ======================================

            ft.Row([

                txt_nome,

                txt_validade,

                txt_admin_level

            ],

                wrap=True,

                spacing=12
            ),

            ft.Row([

                chk_ativo,

                chk_sistema

            ]),

            ft.Row([

                btn_novo,

                btn_salvar

            ]),

            ft.Divider(),

            # ======================================
            # FILTRO
            # ======================================

            ft.Row([

                txt_filtro

            ]),

            # ======================================
            # LISTA
            # ======================================

            ft.Container(

                expand=True,

                padding=12,

                bgcolor=ft.Colors.GREY_100,

                border_radius=12,

                content=tabela
            )

        ],

            spacing=16,

            expand=True
        )
    )
