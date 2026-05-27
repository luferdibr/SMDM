import flet as ft

from services.loc_tipo_service import (
    listar_loc_tipos,
    obter_loc_tipo,
    salvar_loc_tipo,
    excluir_loc_tipo
)


def loc_tipos_view(page):

    lista = ft.Column(
        spacing=4,
    )

    tipo_editando = {
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
        label="Tipo de Local",
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

        tipo_editando["id"] = None

        txt_nome.value = ""

        chk_ativo.value = True

        page.update()

    # ==================================================
    # EDITAR
    # ==================================================

    def editar(tipo_id):

        dados = obter_loc_tipo(tipo_id)

        if not dados:
            return

        tipo_editando["id"] = dados[0]

        txt_nome.value = dados[1] or ""

        chk_ativo.value = bool(dados[2])

        page.update()

    # ==================================================
    # EXCLUIR
    # ==================================================

    def excluir(e, tipo_id):

        try:

            excluir_loc_tipo(tipo_id)

            carregar()

            limpar()

            page.snack_bar = ft.SnackBar(
                ft.Text("Tipo removido")
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
                ft.Text("Informe o nome")
            )

            page.snack_bar.open = True

            page.update()

            return

        dados = {

            "id": tipo_editando["id"],

            "nome": nome,

            "ativo": chk_ativo.value
        }

        salvar_loc_tipo(dados)

        carregar()

        limpar()

        page.snack_bar = ft.SnackBar(
            ft.Text("Tipo salvo")
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

        tipos = listar_loc_tipos()

        if not tipos:

            lista.controls.append(

                ft.Text(
                    "Nenhum tipo cadastrado"
                )
            )

            if atualizar:

                page.update()

            return

        for t in tipos:

            tipo_id = t[0]

            nome = t[1]

            ativo = bool(t[2])

            status = "ATIVO"

            if not ativo:

                status = "INATIVO"

            lista.controls.append(

                ft.Container(

                    content=ft.Row([

                        ft.Text(

                            nome,

                            size=14,

                            weight="bold",

                            expand=True,
                        ),

                        ft.Text(

                            status,

                            size=11,

                            color=(
                                ft.Colors.GREEN_700
                                if ativo
                                else ft.Colors.RED_700
                            ),
                        ),

                        ft.IconButton(

                            icon=ft.Icons.EDIT,

                            icon_size=18,

                            width=32,

                            height=32,

                            tooltip="Editar",

                            on_click=lambda e, id=tipo_id: editar(id)
                        ),

                        ft.IconButton(

                            icon=ft.Icons.DELETE,

                            icon_size=18,

                            width=32,

                            height=32,

                            tooltip="Excluir",

                            on_click=lambda e, id=tipo_id: excluir(e, id)
                        )

                    ]),

                    padding=ft.padding.symmetric(
                        horizontal=8,
                        vertical=2,
                    ),

                    border=ft.border.all(
                        1,
                        ft.Colors.GREY_300
                    ),

                    border_radius=4
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

                "Tipos de Local",

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

        ft.ResponsiveRow(

            spacing=8,

            run_spacing=4,

            vertical_alignment=ft.CrossAxisAlignment.CENTER,

            controls=[

                ft.Container(
                    txt_nome,
                    col={"md": 8},
                ),

                ft.Container(
                    chk_ativo,
                    col={"md": 2},
                ),
            ],
        ),

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
