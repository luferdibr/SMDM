import flet as ft

from services.local_service import (
    listar_locais,
    excluir_local
)

from services.loc_estrutura_service import (
    listar_estruturas_local,
    listar_loc_estruturas
)


def locais_view(page):

    lista = ft.Column()

    # ==================================================
    # MAPA ESTRUTURAS
    # ==================================================

    mapa_estruturas = {}

    def carregar_mapa_estruturas():

        estruturas = listar_loc_estruturas()

        mapa_estruturas.clear()

        for e in estruturas:

            mapa_estruturas[e[0]] = e[1]

    # ==================================================
    # RESUMO ESTRUTURAS
    # ==================================================

    def obter_resumo_estruturas(local_id):

        ids = listar_estruturas_local(
            local_id
        )

        nomes = []

        for estrutura_id in ids:

            nome = mapa_estruturas.get(
                estrutura_id
            )

            if nome:
                nomes.append(nome)

        if not nomes:
            return "Nenhuma estrutura"

        return ", ".join(nomes)

    # ==================================================
    # ABRIR FORM
    # ==================================================

    def abrir_formulario(local_id=None):

        from ui.local_form import local_form_view

        page.conteudo.content = local_form_view(
            page,
            local_id
        )

        page.update()

    # ==================================================
    # EXCLUIR
    # ==================================================

    def excluir(e, local_id):

        try:

            excluir_local(local_id)

            carregar()

            page.snack_bar = ft.SnackBar(
                ft.Text("Local removido")
            )

        except Exception as ex:

            page.snack_bar = ft.SnackBar(
                ft.Text(str(ex))
            )

        page.snack_bar.open = True

        page.update()

    # ==================================================
    # CARD LOCAL
    # ==================================================

    def criar_card_local(l):

        local_id = l[0]

        nome = l[1] or ""

        tipo = l[2] or "Não informado"

        contato = l[3] or ""

        estruturas = obter_resumo_estruturas(
            local_id
        )

        return ft.Container(

            content=ft.Column([

                # ======================================
                # TOPO
                # ======================================

                ft.Row([

                    ft.Column([

                        ft.Text(
                            nome,
                            size=20,
                            weight="bold"
                        ),

                        ft.Text(
                            f"Tipo: {tipo}"
                        ),

                        ft.Text(
                            f"Contato: {contato}"
                        )

                    ],

                        expand=True,

                        spacing=4
                    ),

                    ft.Row([

                        ft.IconButton(

                            icon=ft.Icons.EDIT,

                            tooltip="Editar",

                            on_click=lambda e, id=local_id: abrir_formulario(id)
                        ),

                        ft.IconButton(

                            icon=ft.Icons.DELETE,

                            tooltip="Excluir",

                            on_click=lambda e, id=local_id: excluir(e, id)
                        )

                    ])

                ],

                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),

                ft.Divider(),

                # ======================================
                # ESTRUTURAS
                # ======================================

                ft.Text(
                    "Estruturas",
                    weight="bold"
                ),

                ft.Text(
                    estruturas
                )

            ]),

            padding=16,

            margin=ft.margin.only(bottom=12),

            border=ft.border.all(
                1,
                ft.Colors.GREY_300
            ),

            border_radius=12
        )

    # ==================================================
    # CARREGAR
    # ==================================================

    def carregar():

        lista.controls.clear()

        carregar_mapa_estruturas()

        locais = listar_locais()

        # ==============================================
        # SEM REGISTROS
        # ==============================================

        if not locais:

            lista.controls.append(

                ft.Container(

                    content=ft.Text(
                        "Nenhum local cadastrado"
                    ),

                    padding=20
                )
            )

            page.update()

            return

        # ==============================================
        # LISTAGEM
        # ==============================================

        for l in locais:

            lista.controls.append(
                criar_card_local(l)
            )

        page.update()

    carregar()

    # ==================================================
    # LAYOUT
    # ==================================================

    return ft.Column([

        ft.Row([

            ft.Text(

                "Cadastro de Locais",

                size=28,

                weight="bold"
            ),

            ft.ElevatedButton(

                "Novo Local",

                icon=ft.Icons.ADD,

                on_click=lambda e: abrir_formulario()
            )

        ],

            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        ),

        ft.Divider(),

        lista

    ],

        expand=True,

        scroll=ft.ScrollMode.AUTO
    )