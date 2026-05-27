import flet as ft

from modules.cadastros.clientes.service import (
    excluir_cliente,
    listar_clientes,
    obter_cliente,
    salvar_cliente,
)


SEXO_OPCOES = [
    "Masculino",
    "Feminino",
]

RESUMO_OPCOES = [
    "Não",
    "Semana",
    "Quinzena",
    "Mensal",
]


def dropdown_opcoes(label, opcoes, width=220):

    return ft.Dropdown(
        label=label,
        width=width,
        options=[
            ft.dropdown.Option(
                opcao
            )
            for opcao in opcoes
        ],
    )


def clientes_view(page):

    lista = ft.Column(
        spacing=8,
    )

    cliente_editando = {
        "id": None,
    }

    txt_nome = ft.TextField(
        label="Nome",
        width=420,
    )

    txt_cidade = ft.TextField(
        label="Cidade",
        width=260,
    )

    txt_estado = ft.TextField(
        label="Estado",
        value="RS",
        width=100,
        max_length=2,
    )

    txt_pais = ft.TextField(
        label="País",
        value="Brasil",
        width=180,
    )

    txt_celular = ft.TextField(
        label="Celular",
        width=180,
    )

    txt_data_nascimento = ft.TextField(
        label="Data de nascimento",
        hint_text="DD/MM/AAAA",
        width=180,
    )

    txt_cpf = ft.TextField(
        label="CPF",
        width=180,
    )

    txt_email = ft.TextField(
        label="E-mail",
        width=360,
    )

    dd_sexo = dropdown_opcoes(
        "Sexo",
        SEXO_OPCOES,
        width=180,
    )

    dd_resumo = dropdown_opcoes(
        "Receber resumo da programação",
        RESUMO_OPCOES,
        width=260,
    )

    txt_profissao = ft.TextField(
        label="Profissão",
        width=300,
    )

    txt_primeiro_canal = ft.TextField(
        label="Primeiro canal de contato",
        width=360,
    )

    txt_observacoes = ft.TextField(
        label="Observações / Comentários",
        multiline=True,
        min_lines=3,
        max_lines=5,
        width=760,
    )

    chk_ativo = ft.Checkbox(
        label="Ativo",
        value=True,
    )

    campos = [
        txt_nome,
        txt_cidade,
        txt_estado,
        txt_pais,
        txt_celular,
        txt_data_nascimento,
        txt_cpf,
        txt_email,
        dd_sexo,
        dd_resumo,
        txt_profissao,
        txt_primeiro_canal,
        txt_observacoes,
    ]

    def mostrar_mensagem(texto):

        page.snack_bar = ft.SnackBar(
            ft.Text(
                texto
            )
        )

        page.snack_bar.open = True

        page.update()

    def limpar(e=None):

        cliente_editando["id"] = None

        for campo in campos:
            campo.value = ""

        txt_estado.value = "RS"
        txt_pais.value = "Brasil"
        dd_resumo.value = "Não"
        chk_ativo.value = True

        page.update()

    def carregar(atualizar=True):

        lista.controls.clear()

        clientes = listar_clientes()

        if not clientes:

            lista.controls.append(
                ft.Container(
                    padding=16,
                    content=ft.Text(
                        "Nenhum cliente cadastrado"
                    ),
                )
            )

            if atualizar:
                page.update()

            return

        for cliente in clientes:

            cliente_id = cliente[0]
            nome = cliente[1] or ""
            cpf = cliente[2] or ""
            celular = cliente[3] or ""
            email = cliente[4] or ""
            municipio = cliente[5] or ""
            uf = cliente[6] or ""
            ativo = bool(
                cliente[7]
            )

            lista.controls.append(
                ft.Container(
                    padding=12,
                    border=ft.border.all(
                        1,
                        ft.Colors.GREY_300,
                    ),
                    border_radius=6,
                    content=ft.Row(
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Column(
                                spacing=2,
                                expand=True,
                                controls=[
                                    ft.Text(
                                        nome,
                                        size=15,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    ft.Text(
                                        f"{municipio or '-'} / {uf or '-'}",
                                        size=12,
                                    ),
                                    ft.Text(
                                        f"CPF: {cpf or '-'} | Celular: {celular or '-'} | E-mail: {email or '-'}",
                                        size=12,
                                        color=ft.Colors.GREY_700,
                                    ),
                                ],
                            ),
                            ft.Text(
                                "ATIVO" if ativo else "INATIVO",
                                size=11,
                            ),
                            ft.IconButton(
                                icon=ft.Icons.EDIT,
                                tooltip="Editar",
                                on_click=lambda e, id=cliente_id: editar(id),
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE,
                                tooltip="Excluir",
                                on_click=lambda e, id=cliente_id: excluir(e, id),
                            ),
                        ],
                    ),
                )
            )

        if atualizar:
            page.update()

    def editar(cliente_id):

        dados = obter_cliente(
            cliente_id
        )

        if not dados:
            return

        cliente_editando["id"] = dados[0]
        txt_nome.value = dados[1] or ""
        txt_cidade.value = dados[2] or ""
        txt_estado.value = dados[3] or "RS"
        txt_pais.value = dados[4] or "Brasil"
        txt_celular.value = dados[5] or ""
        txt_data_nascimento.value = (
            dados[6].strftime("%d/%m/%Y")
            if dados[6]
            else ""
        )
        txt_cpf.value = dados[7] or ""
        txt_email.value = dados[8] or ""
        dd_sexo.value = dados[9] or ""
        dd_resumo.value = dados[10] or "Não"
        txt_profissao.value = dados[11] or ""
        txt_observacoes.value = dados[12] or ""
        txt_primeiro_canal.value = dados[13] or ""
        chk_ativo.value = bool(
            dados[14]
        )

        page.update()

    def excluir(e, cliente_id):

        try:

            excluir_cliente(
                cliente_id
            )

            carregar(
                atualizar=False
            )

            limpar()

            mostrar_mensagem(
                "Cliente removido"
            )

        except Exception as ex:

            mostrar_mensagem(
                str(ex)
            )

    def salvar(e=None):

        dados = {
            "id": cliente_editando["id"],
            "nome": txt_nome.value,
            "municipio": txt_cidade.value,
            "uf": txt_estado.value,
            "pais": txt_pais.value,
            "celular": txt_celular.value,
            "data_nascimento": txt_data_nascimento.value,
            "cpf": txt_cpf.value,
            "email": txt_email.value,
            "sexo": dd_sexo.value,
            "receber_resumo": dd_resumo.value,
            "profissao": txt_profissao.value,
            "observacoes": txt_observacoes.value,
            "primeiro_canal": txt_primeiro_canal.value,
            "ativo": chk_ativo.value,
        }

        try:

            salvar_cliente(
                dados
            )

            carregar(
                atualizar=False
            )

            limpar()

            mostrar_mensagem(
                "Cliente salvo"
            )

        except Exception as ex:

            mostrar_mensagem(
                str(ex)
            )

    carregar(
        atualizar=False
    )

    return ft.Column(
        expand=True,
        scroll=ft.ScrollMode.AUTO,
        spacing=10,
        controls=[
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Text(
                        "Cadastro de Clientes",
                        size=24,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Row(
                        spacing=8,
                        controls=[
                            ft.ElevatedButton(
                                "Novo",
                                icon=ft.Icons.ADD,
                                on_click=limpar,
                            ),
                            ft.ElevatedButton(
                                "Salvar",
                                icon=ft.Icons.SAVE,
                                on_click=salvar,
                            ),
                        ],
                    ),
                ],
            ),
            ft.Divider(),
            ft.ResponsiveRow(
                controls=[
                    ft.Container(txt_nome, col={"md": 6}),
                    ft.Container(txt_cpf, col={"md": 3}),
                    ft.Container(txt_data_nascimento, col={"md": 3}),
                    ft.Container(txt_cidade, col={"md": 3}),
                    ft.Container(txt_estado, col={"md": 2}),
                    ft.Container(txt_pais, col={"md": 3}),
                    ft.Container(txt_celular, col={"md": 3}),
                    ft.Container(txt_email, col={"md": 5}),
                    ft.Container(dd_sexo, col={"md": 2}),
                    ft.Container(dd_resumo, col={"md": 4}),
                    ft.Container(txt_profissao, col={"md": 4}),
                    ft.Container(txt_primeiro_canal, col={"md": 4}),
                    ft.Container(chk_ativo, col={"md": 2}),
                    ft.Container(txt_observacoes, col={"md": 8}),
                ],
            ),
            ft.Row(
                spacing=8,
                controls=[
                    ft.ElevatedButton(
                        "Salvar",
                        icon=ft.Icons.SAVE,
                        on_click=salvar,
                    ),
                    ft.OutlinedButton(
                        "Limpar",
                        icon=ft.Icons.CLEAR,
                        on_click=limpar,
                    ),
                ],
            ),
            ft.Divider(),
            lista,
        ],
    )
