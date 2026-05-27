import logging

import flet as ft

<<<<<<< HEAD
from config.settings import (
    APP_CONFIG
)

from modules.administracao.perfis.services.perfil_service import (

    listar_perfis,

    criar_perfil,

=======
from modules.administracao.perfis.services.perfil_service import (
>>>>>>> 25/05/2026 - 12:09
    atualizar_perfil,
    criar_perfil,
    excluir_perfil,
    listar_perfis,
)

from services.menu_admin_service import (
    get_permissoes_usuario,
)

from ui.components.base_view import (
    base_view,
)

from ui.components.buttons import (
    new_button,
    save_button,
)

from ui.components.cards import (
    section_card,
)

from ui.components.fields import (
    app_switch,
    app_textfield,
    number_field,
    search_field,
)

from ui.components.snackbars import (
    show_error,
    show_success,
)

from ui.components.tables import (
    action_cell,
    simple_table,
    table_row,
    text_cell,
)

from utils.error_formatter import (
    format_error_message,
)


ROOT_LEVEL = 100

LOGGER = logging.getLogger(
    "MDM_PERFIS_UI"
)


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


def get_nome_admin(level):

    if level >= ROOT_LEVEL:
        return "ROOT"

    if level >= 50:
        return "ADMIN"

    return "OPERACIONAL"


def get_cor_admin(level):

    if level >= ROOT_LEVEL:
        return ft.Colors.RED_700

    if level >= 50:
        return ft.Colors.ORANGE_700

    return ft.Colors.BLUE_700


def status_text(value):

    return "Sim" if value else "Não"


def perfil_view(page):

    usuario = get_usuario(page)

    if not usuario:

        return ft.Container(

            expand=True,

            alignment=ft.Alignment(0, 0),

            content=ft.Text(
                "Sessão inválida.",
                size=18,
                color=ft.Colors.RED,
            ),
        )

    permissoes = get_permissoes_usuario(
        usuario,
        "perfis",
    )

    if not permissoes.get("ver"):

        return ft.Container(

            expand=True,

            alignment=ft.Alignment(0, 0),

            content=ft.Text(
                "Acesso negado.",
                size=18,
                color=ft.Colors.RED,
            ),
        )

    pode_editar = bool(
        permissoes.get("editar")
    )

    registro_atual = {
        "id": None,
    }

    txt_nome = app_textfield(
        label="Nome do perfil",
    )

    txt_validade = number_field(
        label="Validade senha",
        width=150,
    )

    txt_admin_level = number_field(
        label="Admin level",
        value="10",
        width=130,
    )

    sw_ativo = app_switch(
        label="Ativo",
        value=True,
    )

    sw_sistema = app_switch(
        label="Sistêmico",
        value=False,
    )

    txt_filtro = search_field(
        label="Pesquisar perfil",
        width=260,
    )

    lbl_status = ft.Text(
        "Registros: -",
        size=11,
        color=ft.Colors.GREY_700,
    )

    tabela_container = ft.Container()

    def limpar_form():

        registro_atual["id"] = None

        txt_nome.value = ""

        txt_validade.value = ""

        txt_admin_level.value = "10"

        sw_ativo.value = True

        sw_sistema.value = False

    def carregar_form(perfil):

        registro_atual["id"] = perfil.get(
            "id"
        )

        txt_nome.value = perfil.get(
            "nome",
            "",
        )

        txt_validade.value = str(
            perfil.get("validade_senha")
            or ""
        )

        txt_admin_level.value = str(
            perfil.get(
                "admin_level",
                0,
            )
        )

        sw_ativo.value = bool(
            perfil.get(
                "ativo",
                True,
            )
        )

        sw_sistema.value = bool(
            perfil.get(
                "sistema",
                False,
            )
        )

        page.update()

    def montar_linhas(perfis):

        rows = []

        for perfil in perfis:

            level = int(
                perfil.get(
                    "admin_level",
                    0,
                )
            )

            rows.append(

                table_row(

                    controls=[

                        text_cell(
                            perfil.get("id"),
                            width=50,
                        ),

                        text_cell(
                            perfil.get("nome"),
                            expand=True,
                            bold=True,
                        ),

                        text_cell(
                            perfil.get("validade_senha")
                            or "-",
                            width=90,
                        ),

                        text_cell(
                            status_text(
                                perfil.get("ativo")
                            ),
                            width=55,
                        ),

                        text_cell(
                            str(level),
                            width=70,
                            color=get_cor_admin(
                                level
                            ),
                        ),

                        text_cell(
                            get_nome_admin(
                                level
                            ),
                            width=90,
                        ),

                        text_cell(
                            status_text(
                                perfil.get("sistema")
                            ),
                            width=70,
                        ),

                        action_cell(

                            width=80,

                            controls=[

                                ft.IconButton(

                                    icon=ft.Icons.EDIT,

                                    tooltip="Editar",

                                    disabled=not pode_editar,

                                    on_click=(
                                        lambda e, p=perfil: carregar_form(p)
                                    ),
                                ),

                                ft.IconButton(

                                    icon=ft.Icons.DELETE,

                                    tooltip="Excluir",

                                    icon_color=ft.Colors.RED_400,

                                    disabled=not pode_editar,

                                    on_click=(
                                        lambda e, p=perfil: remover(p)
                                    ),
                                ),
                            ],
                        ),
                    ],
                )
            )

        return rows

    def carregar_tabela(
        e=None,
        atualizar=True,
    ):

        try:

            filtro = str(
                txt_filtro.value
                or ""
            ).strip()

            perfis = listar_perfis(
                filtro
            )

            LOGGER.info(
                "Perfis retornados para tela: %s",
                len(perfis)
            )

            lbl_status.value = (
                f"Registros: {len(perfis)}"
            )

            if not perfis:

                tabela_container.content = ft.Container(

                    padding=20,

                    alignment=ft.Alignment(0, 0),

                    content=ft.Text(
                        "Nenhum perfil cadastrado encontrado.",
                        size=13,
                        color=ft.Colors.GREY_700,
                    ),
                )

            else:

                tabela_container.content = simple_table(

                    dense=True,

                    columns=[

                        {
                            "label": "ID",
                            "width": 50,
                        },

                        {
                            "label": "Perfil",
                            "expand": True,
                        },

                        {
                            "label": "Validade",
                            "width": 90,
                        },

                        {
                            "label": "Ativo",
                            "width": 55,
                        },

                        {
                            "label": "Nível",
                            "width": 70,
                        },

                        {
                            "label": "Tipo",
                            "width": 90,
                        },

                        {
                            "label": "Sistema",
                            "width": 70,
                        },

                        {
                            "label": "",
                            "width": 80,
                        },
                    ],

                    rows=montar_linhas(
                        perfis
                    ),
                )

            if atualizar:

                page.update()

        except Exception as ex:

            LOGGER.exception(
                "LOAD PERFIS ERROR"
            )

            tabela_container.content = ft.Text(
                format_error_message(
                    ex,
                    contexto="Listar perfis",
                ),
                color=ft.Colors.RED,
                selectable=True,
            )

            lbl_status.value = (
                "Registros: erro na consulta"
            )

            if atualizar:

                page.update()

                show_error(
                    page,
                    format_error_message(
                        ex,
                        contexto="Listar perfis",
                    ),
                    duration=8000,
                )

    def remover(perfil):

        try:

            excluir_perfil(
                perfil["id"],
                usuario,
            )

            limpar_form()

            carregar_tabela()

            show_success(
                page,
                "Perfil removido."
            )

        except Exception as ex:

            LOGGER.exception(
                "DELETE PERFIL ERROR"
            )

            show_error(
                page,
                format_error_message(
                    ex,
                    contexto="Excluir perfil",
                ),
                duration=8000,
            )

    def salvar(e):

        try:

            LOGGER.info(
                "[SALVAR_PERFIL] Clique recebido."
            )

            if not pode_editar:

                show_error(
                    page,
                    "Sem permissão."
                )

                return

            payload = {

                "nome": txt_nome.value,

                "validade_senha": txt_validade.value,

                "admin_level": txt_admin_level.value,

                "ativo": sw_ativo.value,

                "sistema": sw_sistema.value,
            }

            LOGGER.info(
                "[SALVAR_PERFIL] Payload: %s",
                payload,
            )

            if not registro_atual["id"]:

                perfil_id = criar_perfil(
                    payload,
                    usuario,
                )

                LOGGER.info(
                    "[SALVAR_PERFIL] Perfil criado id=%s",
                    perfil_id,
                )

                show_success(
                    page,
                    "Perfil criado."
                )

            else:

                atualizar_perfil(
                    int(
                        registro_atual["id"]
                    ),
                    payload,
                    usuario,
                )

                LOGGER.info(
                    "[SALVAR_PERFIL] Perfil atualizado id=%s",
                    registro_atual["id"],
                )

                show_success(
                    page,
                    "Perfil atualizado."
                )

            limpar_form()

            carregar_tabela()

            LOGGER.info(
                "[SALVAR_PERFIL] Tabela recarregada."
            )

        except Exception as ex:

            LOGGER.exception(
                "SAVE PERFIL ERROR"
            )

            show_error(
                page,
                format_error_message(
                    ex,
                    contexto="Salvar perfil",
                ),
                duration=8000,
            )

    def novo(e=None):

        limpar_form()

        page.update()

    txt_filtro.on_change = carregar_tabela

<<<<<<< HEAD
        content=ft.Row(
            spacing=6,
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                ft.Icon(ft.Icons.ADD, size=16),
                ft.Text("Novo", size=12),
            ],
        ),
=======
    form_panel = section_card(

        title="Perfil",
>>>>>>> 25/05/2026 - 12:09

        subtitle="Cadastro e manutenção",

        icon=ft.Icons.ADMIN_PANEL_SETTINGS,

        content=ft.Column(

<<<<<<< HEAD
        content=ft.Row(
            spacing=6,
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                ft.Icon(ft.Icons.SAVE, size=16),
                ft.Text("Salvar", size=12),
            ],
        ),

        disabled=not pode_editar,

        on_click=salvar
    )

    btn_voltar = ft.TextButton(

        content=ft.Row(
            spacing=6,
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                ft.Icon(ft.Icons.ARROW_BACK, size=16),
                ft.Text("Voltar", size=12),
            ],
        ),

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
=======
            spacing=8,

            controls=[
>>>>>>> 25/05/2026 - 12:09

                txt_nome,

                ft.Row(

                    spacing=8,

                    controls=[

                        ft.Container(
                            width=150,
                            content=txt_validade,
                        ),

                        ft.Container(
                            width=130,
                            content=txt_admin_level,
                        ),
                    ],
                ),

                ft.Row(

                    spacing=12,

                    controls=[

                        sw_ativo,

                        sw_sistema,
                    ],
                ),

                ft.Row(

                    spacing=6,

                    controls=[

                        new_button(
                            on_click=novo,
                        ),

                        save_button(
                            on_click=salvar,
                        ),
                    ],
                ),
            ],
        ),
    )

    tabela_panel = section_card(

        title="Perfis cadastrados",

        subtitle="Lista lida diretamente da tabela Perfis",

        icon=ft.Icons.SECURITY,

        content=ft.Column(

            spacing=8,

            controls=[

                ft.Row(

                    alignment=(
                        ft.MainAxisAlignment.SPACE_BETWEEN
                    ),

                    controls=[
                        lbl_status,
                        txt_filtro,
                    ],
                ),

                tabela_container,
            ],
        ),
    )

    limpar_form()

    carregar_tabela(
        atualizar=False
    )

    return base_view(

        title="Perfis",

        subtitle="Administração de perfis de acesso",

        content_controls=[

            ft.Row(

                expand=True,

                spacing=8,

                vertical_alignment=ft.CrossAxisAlignment.START,

                controls=[

                    ft.Container(
                        width=330,
                        content=form_panel,
                    ),

                    ft.Container(
                        expand=True,
                        content=tabela_panel,
                    ),
                ],
            )
        ],
    )
