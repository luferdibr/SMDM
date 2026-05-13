
import flet as ft

from services.loc_ambientes_service import (

    listar_locais_combo,

    listar_ambientes,

    obter_ambiente,

    salvar_ambiente,

    excluir_ambiente
)


# ==================================================
# VIEW
# ==================================================

def loc_ambientes_view(page):

    lista = ft.Column()

    ambientes_cache = []

    # ==================================================
    # CAMPOS FORM
    # ==================================================

    cmb_local = ft.Dropdown(

        label="Local",

        width=350
    )

    txt_nome = ft.TextField(

        label="Nome Ambiente",

        width=350
    )

    txt_sentado = ft.TextField(

        label="Capacidade Sentado",

        width=180
    )

    txt_pe = ft.TextField(

        label="Capacidade em Pé",

        width=180
    )

    txt_metragem = ft.TextField(

        label="Metragem",

        width=180
    )

    txt_pe_direito = ft.TextField(

        label="Pé Direito",

        width=180
    )

    chk_ar = ft.Checkbox(

        label="Ar Condicionado"
    )

    txt_preco = ft.TextField(

        label="Preço Base",

        width=180
    )

    ambiente_id = None

    # ==================================================
    # CARREGAR COMBO
    # ==================================================

    def carregar_locais():

        cmb_local.options.clear()

        locais = listar_locais_combo()

        for l in locais:

            cmb_local.options.append(

                ft.dropdown.Option(

                    key=str(l[0]),

                    text=l[1]
                )
            )

    # ==================================================
    # LIMPAR FORM
    # ==================================================

    def limpar_form():

        nonlocal ambiente_id

        ambiente_id = None

        txt_nome.value = ""

        txt_sentado.value = ""

        txt_pe.value = ""

        txt_metragem.value = ""

        txt_pe_direito.value = ""

        txt_preco.value = ""

        chk_ar.value = False

        page.update()

    # ==================================================
    # CARREGAR GRID
    # ==================================================

    def carregar():

        lista.controls.clear()

        local_id = cmb_local.value

        if not local_id:

            page.update()

            return

        ambientes = listar_ambientes(
            int(local_id)
        )

        ambientes_cache.clear()

        ambientes_cache.extend(ambientes)

        if not ambientes:

            lista.controls.append(

                ft.Text(
                    "Nenhum ambiente cadastrado."
                )
            )

            page.update()

            return

        for a in ambientes:

            lista.controls.append(

                criar_card(a)
            )

        page.update()

    # ==================================================
    # EDITAR
    # ==================================================

    def editar(e, id):

        nonlocal ambiente_id

        dados = obter_ambiente(id)

        if not dados:
            return

        ambiente_id = dados[0]

        cmb_local.value = str(dados[1])

        txt_nome.value = dados[2]

        txt_sentado.value = str(dados[3] or "")

        txt_pe.value = str(dados[4] or "")

        txt_metragem.value = str(dados[5] or "")

        txt_pe_direito.value = str(dados[6] or "")

        chk_ar.value = bool(dados[7])

        txt_preco.value = str(dados[8] or "")

        page.update()

    # ==================================================
    # EXCLUIR
    # ==================================================

    def excluir(e, id):

        try:

            excluir_ambiente(id)

            carregar()

            page.snack_bar = ft.SnackBar(

                ft.Text(
                    "Ambiente removido."
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

    def salvar(e):

        nonlocal ambiente_id

        try:

            if not cmb_local.value:

                raise Exception(
                    "Selecione o local."
                )

            if not txt_nome.value.strip():

                raise Exception(
                    "Informe o nome."
                )

            dados = {

                "id": ambiente_id,

                "local_id": int(
                    cmb_local.value
                ),

                "nome": txt_nome.value,

                "sentado": txt_sentado.value,

                "pe": txt_pe.value,

                "metragem": txt_metragem.value,

                "pe_direito": txt_pe_direito.value,

                "ar": chk_ar.value,

                "preco": txt_preco.value
            }

            salvar_ambiente(dados)

            limpar_form()

            carregar()

            page.snack_bar = ft.SnackBar(

                ft.Text(
                    "Ambiente salvo."
                )
            )

        except Exception as ex:

            page.snack_bar = ft.SnackBar(

                ft.Text(str(ex))
            )

        page.snack_bar.open = True

        page.update()

    # ==================================================
    # CARD
    # ==================================================

    def criar_card(a):

        return ft.Container(

            content=ft.Column([

                ft.Row([

                    ft.Column([

                        ft.Text(

                            a[2],

                            size=18,

                            weight="bold"
                        ),

                        ft.Text(
                            f"Capacidade Sentado: {a[3] or 0}"
                        ),

                        ft.Text(
                            f"Capacidade em Pé: {a[4] or 0}"
                        ),

                        ft.Text(
                            f"Metragem: {a[5] or 0}"
                        ),

                        ft.Text(
                            f"Preço Base: R$ {a[6] or 0}"
                        )

                    ],

                        expand=True
                    ),

                    ft.Row([

                        ft.IconButton(

                            icon=ft.Icons.EDIT,

                            on_click=lambda e,
                            id=a[0]: editar(e, id)
                        ),

                        ft.IconButton(

                            icon=ft.Icons.DELETE,

                            on_click=lambda e,
                            id=a[0]: excluir(e, id)
                        )

                    ])

                ])

            ]),

            border=ft.border.all(
                1,
                ft.Colors.GREY_300
            ),

            border_radius=10,

            padding=15,

            margin=ft.margin.only(
                bottom=10
            )
        )

    # ==================================================
    # EVENTO LOCAL
    # ==================================================

    cmb_local.on_change = lambda e: carregar()

    carregar_locais()

    # ==================================================
    # LAYOUT
    # ==================================================

    return ft.Column([

        ft.Text(

            "Ambientes",

            size=28,

            weight="bold"
        ),

        ft.Divider(),

        cmb_local,

        ft.Row([

            txt_nome

        ]),

        ft.Row([

            txt_sentado,

            txt_pe

        ]),

        ft.Row([

            txt_metragem,

            txt_pe_direito

        ]),

        ft.Row([

            txt_preco,

            chk_ar

        ]),

        ft.Row([

            ft.ElevatedButton(

                "Salvar",

                icon=ft.Icons.SAVE,

                on_click=salvar
            ),

            ft.OutlinedButton(

                "Limpar",

                icon=ft.Icons.CLEAR,

                on_click=lambda e: limpar_form()
            )

        ]),

        ft.Divider(),

        lista

    ],

        scroll=ft.ScrollMode.AUTO,

        expand=True
    )