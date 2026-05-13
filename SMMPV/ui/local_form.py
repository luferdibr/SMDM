import flet as ft

from services.local_service import (
    criar_local,
    atualizar_local,
    obter_local,
    listar_ambientes,
    obter_ambiente,
    salvar_ambiente_db,
    remover_ambiente
)

from services.loc_tipo_service import (
    listar_loc_tipos
)

from services.loc_estrutura_service import (
    listar_loc_estruturas,
    listar_estruturas_local,
    salvar_estruturas_local
)


def local_form_view(page, local_id=None):

    lista_ambientes = ft.Column()

    ambiente_editando = {"id": None}

    estruturas_checks = []

    # ==================================================
    # VOLTAR
    # ==================================================

    def voltar(e=None):

        from ui.locais import locais_view

        page.conteudo.content = locais_view(page)

        page.update()

    # ==================================================
    # CAMPOS LOCAL
    # ==================================================

    txt_nome = ft.TextField(
        label="Nome do Local",
        width=400
    )

    ddl_tipo = ft.Dropdown(
        label="Tipo de Local",
        width=300
    )

    txt_endereco = ft.TextField(
        label="Endereço",
        width=700,
        multiline=True,
        min_lines=2,
        max_lines=3
    )

    txt_responsavel = ft.TextField(
        label="Responsável",
        width=300
    )

    txt_contato = ft.TextField(
        label="Contato",
        width=200
    )

    txt_obs = ft.TextField(
        label="Observações",
        width=700,
        multiline=True,
        min_lines=3,
        max_lines=5
    )

    # ==================================================
    # ESTRUTURAS
    # ==================================================

    estrutura_container = ft.Column()

    def carregar_estruturas():

        estrutura_container.controls.clear()

        estruturas = listar_loc_estruturas()

        selecionadas = []

        if local_id:

            selecionadas = listar_estruturas_local(
                local_id
            )

        estruturas_checks.clear()

        for e in estruturas:

            estrutura_id = e[0]

            nome = e[1]

            ativo = bool(e[2])

            if not ativo:
                continue

            chk = ft.Checkbox(
                label=nome,
                value=estrutura_id in selecionadas
            )

            estruturas_checks.append(
                (estrutura_id, chk)
            )

            estrutura_container.controls.append(
                chk
            )

    def obter_estruturas_selecionadas():

        selecionadas = []

        for estrutura_id, chk in estruturas_checks:

            if chk.value:

                selecionadas.append(
                    estrutura_id
                )

        return selecionadas

    # ==================================================
    # CARREGAR TIPOS
    # ==================================================

    def carregar_tipos():

        tipos = listar_loc_tipos()

        ddl_tipo.options = []

        for t in tipos:

            ddl_tipo.options.append(

                ft.dropdown.Option(
                    str(t[0]),
                    t[1]
                )
            )

    # ==================================================
    # CAMPOS AMBIENTE
    # ==================================================

    txt_amb_nome = ft.TextField(
        label="Nome Ambiente",
        width=300
    )

    txt_sentado = ft.TextField(
        label="Capacidade Sentados",
        width=180
    )

    txt_pe = ft.TextField(
        label="Capacidade em Pé",
        width=180
    )

    txt_metragem = ft.TextField(
        label="Metragem",
        width=150
    )

    txt_pe_direito = ft.TextField(
        label="Pé Direito",
        width=150
    )

    chk_ar = ft.Checkbox(
        label="Ar Condicionado"
    )

    txt_preco = ft.TextField(
        label="Preço Base",
        width=180
    )

    # ==================================================
    # CARREGAR LOCAL
    # ==================================================

    def carregar_local():

        if not local_id:
            return

        dados = obter_local(local_id)

        if not dados:
            return

        txt_nome.value = dados[1] or ""

        ddl_tipo.value = (
            str(dados[2])
            if dados[2]
            else None
        )

        txt_endereco.value = dados[3] or ""

        txt_responsavel.value = dados[4] or ""

        txt_contato.value = dados[5] or ""

        txt_obs.value = dados[7] or ""

    # ==================================================
    # CARREGAR AMBIENTES
    # ==================================================

    def carregar_ambientes():

        lista_ambientes.controls.clear()

        if not local_id:
            return

        ambientes = listar_ambientes(local_id)

        if not ambientes:

            lista_ambientes.controls.append(
                ft.Text("Nenhum ambiente cadastrado")
            )

        for a in ambientes:

            lista_ambientes.controls.append(

                ft.Container(

                    content=ft.Row([

                        ft.Column([

                            ft.Text(
                                a[1],
                                size=16,
                                weight="bold"
                            ),

                            ft.Text(
                                f"Sentados: {a[2] or 0}"
                            ),

                            ft.Text(
                                f"Em pé: {a[3] or 0}"
                            )

                        ],

                            expand=True
                        ),

                        ft.Text(
                            f"R$ {a[4] or 0}"
                        ),

                        ft.IconButton(
                            icon=ft.Icons.EDIT,
                            tooltip="Editar",
                            on_click=lambda e, a=a: editar_ambiente(a)
                        ),

                        ft.IconButton(
                            icon=ft.Icons.DELETE,
                            tooltip="Excluir",
                            on_click=lambda e, id=a[0]: excluir_ambiente(id)
                        )

                    ]),

                    padding=10,

                    border=ft.border.all(
                        1,
                        ft.Colors.GREY_300
                    ),

                    border_radius=8
                )
            )

    # ==================================================
    # SALVAR LOCAL
    # ==================================================

    def salvar_local(e):

        nonlocal local_id

        nome = txt_nome.value.strip()

        if not nome:

            page.snack_bar = ft.SnackBar(
                ft.Text("Informe o nome")
            )

            page.snack_bar.open = True

            page.update()

            return

        if not ddl_tipo.value:

            page.snack_bar = ft.SnackBar(
                ft.Text("Selecione o tipo de local")
            )

            page.snack_bar.open = True

            page.update()

            return

        dados = {

            "nome": nome,

            "loc_tipo_id": ddl_tipo.value,

            "endereco": txt_endereco.value,

            "responsavel": txt_responsavel.value,

            "contato": txt_contato.value,

            "estacionamento": False,

            "observacoes": txt_obs.value
        }

        try:

            if local_id:

                atualizar_local(
                    local_id,
                    dados
                )

            else:

                local_id = criar_local(
                    dados
                )

            estruturas = obter_estruturas_selecionadas()

            salvar_estruturas_local(
                local_id,
                estruturas
            )

            carregar_ambientes()

            page.snack_bar = ft.SnackBar(
                ft.Text("Local salvo")
            )

        except Exception as ex:

            page.snack_bar = ft.SnackBar(
                ft.Text(str(ex))
            )

        page.snack_bar.open = True

        page.update()

    # ==================================================
    # LIMPAR AMBIENTE
    # ==================================================

    def limpar_ambiente():

        ambiente_editando["id"] = None

        txt_amb_nome.value = ""
        txt_sentado.value = ""
        txt_pe.value = ""
        txt_metragem.value = ""
        txt_pe_direito.value = ""
        txt_preco.value = ""

        chk_ar.value = False

    # ==================================================
    # EDITAR AMBIENTE
    # ==================================================

    def editar_ambiente(a):

        ambiente_editando["id"] = a[0]

        dados = obter_ambiente(a[0])

        if not dados:
            return

        txt_amb_nome.value = dados[2] or ""
        txt_sentado.value = str(dados[3] or "")
        txt_pe.value = str(dados[4] or "")
        txt_metragem.value = str(dados[5] or "")
        txt_pe_direito.value = str(dados[6] or "")
        chk_ar.value = bool(dados[7])
        txt_preco.value = str(dados[8] or "")

        dlg.open = True

        page.update()

    # ==================================================
    # EXCLUIR AMBIENTE
    # ==================================================

    def excluir_ambiente(id):

        remover_ambiente(id)

        carregar_ambientes()

        page.update()

    # ==================================================
    # SALVAR AMBIENTE
    # ==================================================

    def salvar_ambiente(e):

        if not local_id:

            page.snack_bar = ft.SnackBar(
                ft.Text("Salve o local primeiro")
            )

            page.snack_bar.open = True

            page.update()

            return

        nome = txt_amb_nome.value.strip()

        if not nome:

            page.snack_bar = ft.SnackBar(
                ft.Text("Informe o nome do ambiente")
            )

            page.snack_bar.open = True

            page.update()

            return

        dados = {

            "id": ambiente_editando["id"],

            "local_id": local_id,

            "nome": nome,

            "sentado": txt_sentado.value or 0,

            "pe": txt_pe.value or 0,

            "metragem": txt_metragem.value or 0,

            "pe_direito": txt_pe_direito.value or 0,

            "ar": chk_ar.value,

            "preco": txt_preco.value or 0
        }

        try:

            salvar_ambiente_db(dados)

            dlg.open = False

            limpar_ambiente()

            carregar_ambientes()

            page.update()

        except Exception as ex:

            page.snack_bar = ft.SnackBar(
                ft.Text(str(ex))
            )

            page.snack_bar.open = True

            page.update()

    # ==================================================
    # NOVO AMBIENTE
    # ==================================================

    def novo_ambiente(e):

        limpar_ambiente()

        dlg.open = True

        page.update()

    # ==================================================
    # DIALOG
    # ==================================================

    def fechar_dialog(e=None):

        dlg.open = False

        page.update()

    dlg = ft.AlertDialog(

        modal=True,

        title=ft.Text("Ambiente"),

        content=ft.Container(

            width=500,

            content=ft.Column([

                txt_amb_nome,

                ft.Row([
                    txt_sentado,
                    txt_pe
                ]),

                ft.Row([
                    txt_metragem,
                    txt_pe_direito
                ]),

                chk_ar,

                txt_preco

            ], tight=True)
        ),

        actions=[

            ft.TextButton(
                "Cancelar",
                on_click=fechar_dialog
            ),

            ft.ElevatedButton(
                "Salvar",
                on_click=salvar_ambiente
            )

        ]
    )

    page.overlay.append(dlg)

    # ==================================================
    # INICIALIZAÇÃO
    # ==================================================

    carregar_tipos()

    carregar_local()

    carregar_estruturas()

    carregar_ambientes()

    # ==================================================
    # LAYOUT
    # ==================================================

    return ft.Column([

        ft.Row([

            ft.Text(
                "Cadastro de Local",
                size=28,
                weight="bold"
            ),

            ft.ElevatedButton(
                "Voltar",
                icon=ft.Icons.ARROW_BACK,
                on_click=voltar
            )

        ],

            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        ),

        ft.Divider(),

        ft.Text(
            "Dados Gerais",
            size=20,
            weight="bold"
        ),

        txt_nome,

        ddl_tipo,

        txt_endereco,

        ft.Row([
            txt_responsavel,
            txt_contato
        ]),

        ft.Divider(),

        ft.Text(
            "Estruturas do Local",
            size=20,
            weight="bold"
        ),

        estrutura_container,

        ft.Divider(),

        ft.Text(
            "Observações",
            size=20,
            weight="bold"
        ),

        txt_obs,

        ft.Row([

            ft.ElevatedButton(
                "Salvar Local",
                icon=ft.Icons.SAVE,
                on_click=salvar_local
            )

        ]),

        ft.Divider(),

        ft.Row([

            ft.Text(
                "Ambientes",
                size=20,
                weight="bold"
            ),

            ft.ElevatedButton(
                "Novo Ambiente",
                icon=ft.Icons.ADD,
                on_click=novo_ambiente
            )

        ],

            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        ),

        lista_ambientes

    ],

        scroll=ft.ScrollMode.AUTO,

        expand=True
    )