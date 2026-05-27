# =========================================================
# modules/administracao/menus/ui/menu_admin.py
# =========================================================

import logging

import flet as ft

from core.icons import (
    ICON_DELETE,
    ICON_EDIT,
    ICON_MENU,
)

from core.messages import (
    MSG_DELETE_SUCCESS,
    MSG_SAVE_SUCCESS,
    TITLE_MENUS,
)

from modules.administracao.menus.services.menu_service import (
    excluir_menu,
    listar_menus,
    salvar_menu,
)

from ui.components.base_view import (
    base_view,
)

from ui.components.buttons import (
    icon_button,
    new_button,
    save_button,
)

from ui.components.cards import (
    section_card,
)

from ui.components.dialogs import (
    confirm_dialog,
)

from ui.components.fields import (
    app_dropdown,
    app_switch,
    app_textfield,
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

from ui.components.validators import (
    field_required,
)

from utils.error_formatter import (
    format_error_message,
)

# =========================================================
# LOGGER
# =========================================================

LOGGER = logging.getLogger(
    "SMDM_MENU_ADMIN"
)

# =========================================================
# FLATTEN
# =========================================================

def flatten_menu_tree(
    menus,
    level=0,
):

    resultado = []

    for item in menus:

        novo = dict(item)

        novo["_level"] = level

        resultado.append(novo)

        filhos = (
            item.get("filhos", [])
            or []
        )

        resultado.extend(

            flatten_menu_tree(
                filhos,
                level + 1,
            )
        )

    return resultado

# =========================================================
# VIEW
# =========================================================

def menu_admin_view(
    page: ft.Page,
):

    LOGGER.info(
        "Inicializando menu admin."
    )

    registro_atual = {
        "id": None,
    }

    # =====================================================
    # FIELDS
    # =====================================================

    txt_nome = app_textfield(
        label="Nome",
    )

    txt_rota = app_textfield(
        label="Rota",
    )

    txt_icone = app_textfield(
        label="Ícone",
    )

    txt_ordem = app_textfield(
        label="Ordem",
        value="0",
    )

    cmb_tipo = app_dropdown(

        label="Tipo",

        options=[

            ("T", "T"),

            ("M", "M"),

            ("S", "S"),
        ],
    )

    cmb_pai = app_dropdown(
        label="Pai",
        options=[],
    )

    sw_ativo = app_switch(
        label="Ativo",
        value=True,
    )

    tabela_container = ft.Container(
        expand=True,
    )

    # =====================================================
    # SIDEBAR REFRESH
    # =====================================================

    def atualizar_sidebar():

        LOGGER.info(
            "Menu será atualizado ao retornar."
        )

    # =====================================================
    # VALID PARENTS
    # =====================================================

    def carregar_pais():

        try:

            tipo = (
                cmb_tipo.value
                or "S"
            )

            arvore = listar_menus()

            registros = flatten_menu_tree(
                arvore
            )

            options = []

            if tipo == "T":

                options = [
                    ("", "SEM PAI")
                ]

            elif tipo == "M":

                for item in registros:

                    if item.get(
                        "tipo"
                    ) == "T":

                        options.append(

                            (
                                str(
                                    item["id"]
                                ),

                                item[
                                    "nome"
                                ],
                            )
                        )

            else:

                for item in registros:

                    if item.get(
                        "tipo"
                    ) in ("T", "M"):

                        ident = (
                            "   "
                            * item.get(
                                "_level",
                                0,
                            )
                        )

                        options.append(

                            (
                                str(
                                    item["id"]
                                ),

                                (
                                    ident
                                    + item[
                                        "nome"
                                    ]
                                ),
                            )
                        )

            cmb_pai.options = [

                ft.dropdown.Option(
                    key=x[0],
                    text=x[1],
                )

                for x in options
            ]

        except Exception:

            LOGGER.exception(
                "Erro pais."
            )

    # =====================================================
    # TYPE RULES
    # =====================================================

    def aplicar_regras_tipo():

        tipo = (
            cmb_tipo.value
            or "S"
        )

        if tipo == "T":

            txt_rota.value = ""

            txt_rota.disabled = True

            cmb_pai.value = ""

            cmb_pai.disabled = True

        elif tipo == "M":

            txt_rota.value = ""

            txt_rota.disabled = True

            cmb_pai.disabled = False

        else:

            txt_rota.disabled = False

            cmb_pai.disabled = False

        carregar_pais()

    # =====================================================
    # TYPE CHANGE
    # =====================================================

    def tipo_change(e):

        aplicar_regras_tipo()

        page.update()

    cmb_tipo.on_change = tipo_change

    # =====================================================
    # CLEAR
    # =====================================================

    def limpar_form():

        registro_atual["id"] = None

        txt_nome.value = ""

        txt_rota.value = ""

        txt_icone.value = ""

        txt_ordem.value = "0"

        cmb_tipo.value = "S"

        cmb_pai.value = None

        sw_ativo.value = True

        aplicar_regras_tipo()

    # =====================================================
    # LOAD FORM
    # =====================================================

    def carregar_form(
        registro,
    ):

        registro_atual["id"] = (
            registro.get("id")
        )

        txt_nome.value = (
            registro.get("nome")
            or ""
        )

        txt_rota.value = (
            registro.get("rota")
            or ""
        )

        txt_icone.value = (
            registro.get("icone")
            or ""
        )

        txt_ordem.value = str(

            registro.get(
                "ordem",
                0,
            )
        )

        cmb_tipo.value = (
            registro.get("tipo")
            or "S"
        )

        aplicar_regras_tipo()

        cmb_pai.value = str(

            registro.get(
                "menu_pai"
            )

            or ""
        )

        sw_ativo.value = bool(
            registro.get(
                "ativo",
                True,
            )
        )

        page.update()

    # =====================================================
    # TABLE
    # =====================================================

    def carregar_tabela(
        atualizar=True
    ):

        try:

            arvore = listar_menus()

            registros = flatten_menu_tree(
                arvore
            )

            rows = []

            for item in registros:

                level = item.get(
                    "_level",
                    0,
                )

                ident = (
                    "  " * level
                )

                rows.append(

                    table_row(

                        controls=[

                            text_cell(
                                item.get("id"),
                                width=45,
                            ),

                            text_cell(

                                (
                                    ident
                                    + item.get(
                                        "nome"
                                    )
                                ),

                                expand=True,

                                bold=(
                                    item.get(
                                        "tipo"
                                    ) == "T"
                                ),
                            ),

                            text_cell(
                                item.get("tipo"),
                                width=35,
                            ),

                            text_cell(

                                item.get(
                                    "menu_pai"
                                ),

                                width=45,
                            ),

                            text_cell(

                                item.get(
                                    "ordem"
                                ),

                                width=45,
                            ),

                            action_cell(

                                controls=[

                                    icon_button(

                                        icon=ICON_EDIT,

                                        tooltip="Editar",

                                        on_click=lambda e, x=item: carregar_form(x),
                                    ),

                                    icon_button(

                                        icon=ICON_DELETE,

                                        tooltip="Excluir",

                                        icon_color=ft.Colors.RED_400,

                                        on_click=lambda e, x=item: confirmar_exclusao(x),
                                    ),
                                ]
                            ),
                        ]
                    )
                )

            tabela_container.content = (

                simple_table(

                    dense=True,

                    columns=[

                        {
                            "label": "ID",
                            "width": 45,
                        },

                        {
                            "label": "Nome",
                            "expand": True,
                        },

                        {
                            "label": "T",
                            "width": 35,
                        },

                        {
                            "label": "Pai",
                            "width": 45,
                        },

                        {
                            "label": "Ord",
                            "width": 45,
                        },

                        {
                            "label": "",
                            "width": 80,
                        },
                    ],

                    rows=rows,
                )
            )

            page.update()

        except Exception as ex:

            LOGGER.exception(
                "Erro tabela."
            )

            show_error(
                page,
                str(ex),
            )

    # =====================================================
    # VALIDATE
    # =====================================================

    def validar():

        if not field_required(
            txt_nome
        ):

            return False

        tipo = (
            cmb_tipo.value
            or "S"
        )

        pai = cmb_pai.value

        if tipo == "M" and not pai:

            show_error(
                page,
                "M requer T pai."
            )

            return False

        if tipo == "S":

            if not pai:

                show_error(
                    page,
                    "S requer pai."
                )

                return False

            if not txt_rota.value:

                show_error(
                    page,
                    "Rota obrigatória."
                )

                return False

        return True

    # =====================================================
    # SAVE
    # =====================================================

    def salvar(e):

        try:

            LOGGER.info(
                "[SALVAR_MENU] Clique recebido."
            )

            if not validar():

                LOGGER.warning(
                    "[SALVAR_MENU] Validação falhou."
                )

                return

            LOGGER.info(
                "[SALVAR_MENU] Validação OK."
            )

            registro = {

                "id": registro_atual[
                    "id"
                ],

                "nome": (
                    txt_nome.value
                    or ""
                ).strip(),

                "rota": (
                    txt_rota.value
                    or ""
                ).strip(),

                "icone": (
                    txt_icone.value
                    or ""
                ).strip(),

                "tipo": (
                    cmb_tipo.value
                    or "S"
                ),

                "menu_pai": (
                    cmb_pai.value
                    or None
                ),

                "ordem": int(
                    txt_ordem.value
                    or 0
                ),

                "ativo": bool(
                    sw_ativo.value
                ),
            }

            LOGGER.info(
                "[SALVAR_MENU] Dados preparados: %s",
                registro,
            )

            LOGGER.info(
                "[SALVAR_MENU] Chamando service salvar_menu."
            )

            salvar_menu(
                registro
            )

            LOGGER.info(
                "[SALVAR_MENU] Service concluiu gravação."
            )

            show_success(
                page,
                MSG_SAVE_SUCCESS,
            )

            LOGGER.info(
                "[SALVAR_MENU] Limpando formulário."
            )

            limpar_form()

            LOGGER.info(
                "[SALVAR_MENU] Recarregando tabela."
            )

            carregar_tabela()

            LOGGER.info(
                "[SALVAR_MENU] Recarregando lista de pais."
            )

            carregar_pais()

            atualizar_sidebar()

            if atualizar:

                page.update()

            LOGGER.info(
                "[SALVAR_MENU] Fluxo concluído."
            )

            LOGGER.info(
                "[SALVAR_MENU] Fluxo concluído."
            )

        except Exception as ex:

            LOGGER.exception(
                "Erro save."
            )

            show_error(
                page,
                format_error_message(
                    ex,
                    contexto="Salvar menu",
                ),
                duration=8000,
            )

    # =====================================================
    # DELETE
    # =====================================================

    def excluir(
        registro,
    ):

        try:

            excluir_menu(
                registro["id"]
            )

            show_success(
                page,
                MSG_DELETE_SUCCESS,
            )

            limpar_form()

            carregar_tabela()

            carregar_pais()

            atualizar_sidebar()

            page.update()

        except Exception as ex:

            LOGGER.exception(
                "ERRO EXCLUIR()"
            )

            show_error(
                page,
                str(ex),
            )

    # =====================================================
    # CONFIRM DELETE
    # =====================================================

    def confirmar_exclusao(
        registro,
    ):

        def confirmar(e):

            excluir(
                registro
            )

        confirm_dialog(

            page=page,

            title="Excluir",

            message=(
                f"Excluir "
                f"{registro['nome']}?"
            ),

            on_confirm=confirmar,
        )

    # =====================================================
    # NEW
    # =====================================================

    def novo(e):

        limpar_form()

        page.update()

    # =====================================================
    # FORM
    # =====================================================

    form_panel = section_card(

        title="Menu",

        subtitle="Cadastro",

        icon=ICON_MENU,

        content=ft.Column(

            spacing=6,

            controls=[

                txt_nome,

                ft.Row(

                    spacing=6,

                    controls=[

                        ft.Container(
                            width=80,
                            content=cmb_tipo,
                        ),

                        ft.Container(
                            width=90,
                            content=txt_ordem,
                        ),

                        ft.Container(
                            expand=True,
                            content=txt_rota,
                        ),
                    ],
                ),

                ft.Row(

                    spacing=6,

                    controls=[

                        ft.Container(
                            expand=True,
                            content=txt_icone,
                        ),

                        ft.Container(
                            width=220,
                            content=cmb_pai,
                        ),
                    ],
                ),

                sw_ativo,

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

    tabela = section_card(

        title="Menus",

        subtitle="Estrutura",

        icon=ICON_MENU,

        content=tabela_container,
    )

    limpar_form()

    carregar_tabela(
        atualizar=False
    )

    return base_view(

        title=TITLE_MENUS,

        subtitle="Administração de menus",

        content_controls=[

            ft.Row(

                expand=True,

                spacing=8,

                vertical_alignment=(
                    ft.CrossAxisAlignment.START
                ),

                controls=[

                    ft.Container(
                        width=320,
                        content=form_panel,
                    ),

                    ft.Container(
                        expand=True,
                        content=tabela,
                    ),
                ],
            )
        ],
    )
