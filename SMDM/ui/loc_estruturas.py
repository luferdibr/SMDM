import flet as ft

from services.loc_estrutura_service import (
    listar_loc_estruturas,
    obter_loc_estrutura,
    salvar_loc_estrutura,
    excluir_loc_estrutura
)


def loc_estruturas_view(page):

    lista = ft.Column()

    estrutura_editando = {
        "id": None
    }

    # ==================================================
    # VOLTAR
    # ==================================================

    def voltar(e=None):

        from ui.dashboard import navegar

        navegar(page, "dashboard")

    # ==================================================
    # CAMPOS
    # ==================================================

    txt_nome = ft.TextField(
        label="Estrutura",
        width=400
    )

    chk_ativo = ft.Checkbox(
        label="Ativo",
        value=True
    )

    # ==================================================
    # LIMPAR
    # ==================================================

    def limpar():

        estrutura_editando["id"] = None

        txt_nome.value = ""

        chk_ativo.value = True

        page.update()

    # ==================================================
    # EDITAR
    # ==================================================

    def editar(estrutura_id):

        dados = obter_loc_estrutura(
            estrutura_id
        )

        if not dados:
            return

        estrutura_editando["id"] = dados[0]

        txt_nome.value = dados[1] or ""

        chk_ativo.value = bool(dados[2])

        page.update()

    # ==================================================
    # EXCLUIR
    # ==================================================

    def excluir(e, estrutura_id):

        try:

            excluir_loc_estrutura(
                estrutura_id
            )

            carregar()

            limpar()

            page.snack_bar = ft.SnackBar(
                ft.Text(
                    "Estrutura removida"
                )
            )

        except Exception as ex:

            page.snack_bar = ft.SnackBar(
                ft.Text(str(ex))
            )

        page.snack_bar.open = True

        page.update()

    # ==================================================
    # SALVAR
    # ==================================================

    def salvar(e=None):

        nome = txt_nome.value.strip()

        if not nome:

            page.snack_bar = ft.SnackBar(
                ft.Text(
                    "Informe o nome"
                )
            )

            page.snack_bar.open = True

            page.update()

            return

        dados = {

            "id": estrutura_editando["id"],

            "nome": nome,

            "ativo": chk_ativo.value
        }

        try:

            salvar_loc_estrutura(
                dados
            )

            carregar()

            limpar()

            page.snack_bar = ft.SnackBar(
                ft.Text(
                    "Estrutura salva"
                )
            )

        except Exception as ex:

            page.snack_bar = ft.SnackBar(
                ft.Text(str(ex))
            )

        page.snack_bar.open = True

        page.update()

    # ==================================================
    # CARREGAR
    # ==================================================

    def carregar(
        atualizar=True
    ):

        lista.controls.clear()

        estruturas = listar_loc_estruturas()

        if not estruturas:

            lista.controls.append(

                ft.Text(
                    "Nenhuma estrutura cadastrada"
                )
            )

            if atualizar:

                page.update()

            return

        for e in estruturas:

            estrutura_id = e[0]

            nome = e[1]

            ativo = bool(e[2])

            status = "ATIVO"

            if not ativo:

                status = "INATIVO"

            lista.controls.append(

                ft.Container(

                    content=ft.Row([

                        ft.Column([

                            ft.Text(

                                nome,

                                size=16,

                                weight="bold"
                            ),

                            ft.Text(
                                status
                            )

                        ],

                            expand=True
                        ),

                        ft.IconButton(

                            icon=ft.Icons.EDIT,

                            tooltip="Editar",

                            on_click=lambda ev, id=estrutura_id: editar(id)
                        ),

                        ft.IconButton(

                            icon=ft.Icons.DELETE,

                            tooltip="Excluir",

                            on_click=lambda ev, id=estrutura_id: excluir(ev, id)
                        )

                    ]),

                    padding=12,

                    border=ft.border.all(
                        1,
                        ft.Colors.GREY_300
                    ),

                    border_radius=10
                )
            )

        if atualizar:

            page.update()

    carregar(
        atualizar=False
    )

    # ==================================================
    # LAYOUT
    # ==================================================

    return ft.Column([

        ft.Row([

            ft.Text(

                "Estruturas dos Locais",

                size=28,

                weight="bold"
            ),

            ft.ElevatedButton(

                "Novo",

                icon=ft.Icons.ADD,

                on_click=lambda e: limpar()
            ),

            ft.ElevatedButton(

                "Voltar",

                icon=ft.Icons.ARROW_BACK,

                on_click=voltar
            )

        ]),

        ft.Divider(),

        txt_nome,

        chk_ativo,

        ft.Row([

            ft.ElevatedButton(

                "Salvar",

                icon=ft.Icons.SAVE,

                on_click=salvar
            )

        ]),

        ft.Divider(),

        lista

    ],

        expand=True,

        scroll=ft.ScrollMode.AUTO
    )
