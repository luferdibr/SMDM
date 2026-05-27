import flet as ft

from modules.cadastros.atores.service import (
    excluir_ator,
    listar_atores,
    obter_ator,
    salvar_ator,
)


NACIONALIDADE_OPCOES = [
    "Brasileiro",
    "Naturalizado",
    "Estrangeiro",
]

ENSINO_OPCOES = [
    "Básico",
    "Médio",
    "Superior",
    "Formação",
]

SEXO_OPCOES = [
    "Masculino",
    "Feminino",
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


def atores_view(page):

    lista = ft.Column(
        spacing=8,
    )

    ator_editando = {
        "id": None,
    }

    txt_nome = ft.TextField(
        label="Nome",
        width=420,
    )

    txt_nome_profissional = ft.TextField(
        label="Nome profissional",
        width=420,
    )

    txt_cep = ft.TextField(
        label="CEP",
        width=150,
    )

    txt_logradouro = ft.TextField(
        label="Rua",
        width=420,
    )

    txt_numero = ft.TextField(
        label="Número",
        width=120,
    )

    txt_complemento = ft.TextField(
        label="Complemento",
        width=220,
    )

    txt_bairro = ft.TextField(
        label="Bairro",
        width=260,
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

    dd_nacionalidade = dropdown_opcoes(
        "Nacionalidade",
        NACIONALIDADE_OPCOES,
    )

    txt_telefone = ft.TextField(
        label="Telefone",
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

    txt_rg = ft.TextField(
        label="RG",
        width=180,
    )

    txt_email = ft.TextField(
        label="E-mail",
        width=360,
    )

    dd_ensino = dropdown_opcoes(
        "Ensino",
        ENSINO_OPCOES,
    )

    dd_sexo = dropdown_opcoes(
        "Sexo",
        SEXO_OPCOES,
        width=180,
    )

    chk_ativo = ft.Checkbox(
        label="Ativo",
        value=True,
    )

    campos = [
        txt_nome,
        txt_nome_profissional,
        txt_cep,
        txt_logradouro,
        txt_numero,
        txt_complemento,
        txt_bairro,
        txt_cidade,
        txt_estado,
        txt_pais,
        dd_nacionalidade,
        txt_telefone,
        txt_celular,
        txt_data_nascimento,
        txt_cpf,
        txt_rg,
        txt_email,
        dd_ensino,
        dd_sexo,
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

        ator_editando["id"] = None

        for campo in campos:

            campo.value = ""

        txt_estado.value = "RS"
        txt_pais.value = "Brasil"
        chk_ativo.value = True

        page.update()

    def carregar(atualizar=True):

        lista.controls.clear()

        atores = listar_atores()

        if not atores:

            lista.controls.append(
                ft.Container(
                    padding=16,
                    content=ft.Text(
                        "Nenhum ator cadastrado"
                    ),
                )
            )

            if atualizar:
                page.update()

            return

        for ator in atores:

            ator_id = ator[0]
            nome = ator[1] or ""
            nome_profissional = ator[2] or ""
            cpf = ator[3] or ""
            celular = ator[4] or ""
            email = ator[5] or ""
            ativo = bool(
                ator[6]
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
                                        nome_profissional
                                        or "Sem nome profissional",
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
                                on_click=lambda e, id=ator_id: editar(id),
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE,
                                tooltip="Excluir",
                                on_click=lambda e, id=ator_id: excluir(e, id),
                            ),
                        ],
                    ),
                )
            )

        if atualizar:
            page.update()

    def editar(ator_id):

        dados = obter_ator(
            ator_id
        )

        if not dados:
            return

        ator_editando["id"] = dados[0]
        txt_nome.value = dados[1] or ""
        txt_nome_profissional.value = dados[2] or ""
        txt_cep.value = dados[3] or ""
        txt_logradouro.value = dados[4] or ""
        txt_numero.value = dados[5] or ""
        txt_complemento.value = dados[6] or ""
        txt_bairro.value = dados[7] or ""
        txt_cidade.value = dados[8] or ""
        txt_estado.value = dados[9] or "RS"
        txt_pais.value = dados[10] or "Brasil"
        dd_nacionalidade.value = dados[12] or ""
        txt_telefone.value = dados[13] or ""
        txt_celular.value = dados[14] or ""
        txt_data_nascimento.value = (
            dados[15].strftime("%d/%m/%Y")
            if dados[15]
            else ""
        )
        txt_cpf.value = dados[16] or ""
        txt_rg.value = dados[17] or ""
        txt_email.value = dados[18] or ""
        dd_ensino.value = dados[19] or ""
        dd_sexo.value = dados[20] or ""
        chk_ativo.value = bool(
            dados[21]
        )

        page.update()

    def excluir(e, ator_id):

        try:

            excluir_ator(
                ator_id
            )

            carregar(
                atualizar=False
            )

            limpar()

            mostrar_mensagem(
                "Ator removido"
            )

        except Exception as ex:

            mostrar_mensagem(
                str(ex)
            )

    def salvar(e=None):

        dados = {
            "id": ator_editando["id"],
            "nome": txt_nome.value,
            "nome_profissional": txt_nome_profissional.value,
            "cep": txt_cep.value,
            "logradouro": txt_logradouro.value,
            "numero": txt_numero.value,
            "complemento": txt_complemento.value,
            "bairro": txt_bairro.value,
            "municipio": txt_cidade.value,
            "uf": txt_estado.value,
            "pais": txt_pais.value,
            "nacionalidade": dd_nacionalidade.value,
            "telefone": txt_telefone.value,
            "celular": txt_celular.value,
            "data_nascimento": txt_data_nascimento.value,
            "cpf": txt_cpf.value,
            "rg": txt_rg.value,
            "email": txt_email.value,
            "ensino": dd_ensino.value,
            "sexo": dd_sexo.value,
            "ativo": chk_ativo.value,
        }

        try:

            salvar_ator(
                dados
            )

            carregar(
                atualizar=False
            )

            limpar()

            mostrar_mensagem(
                "Ator salvo"
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
                        "Cadastro de Atores",
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
            ft.Text(
                "Identificação",
                weight=ft.FontWeight.BOLD,
            ),
            ft.ResponsiveRow(
                controls=[
                    ft.Container(txt_nome, col={"md": 6}),
                    ft.Container(txt_nome_profissional, col={"md": 6}),
                    ft.Container(txt_cpf, col={"md": 3}),
                    ft.Container(txt_rg, col={"md": 3}),
                    ft.Container(txt_data_nascimento, col={"md": 3}),
                    ft.Container(dd_sexo, col={"md": 3}),
                    ft.Container(dd_nacionalidade, col={"md": 3}),
                    ft.Container(dd_ensino, col={"md": 3}),
                    ft.Container(txt_email, col={"md": 6}),
                    ft.Container(txt_telefone, col={"md": 3}),
                    ft.Container(txt_celular, col={"md": 3}),
                    ft.Container(chk_ativo, col={"md": 2}),
                ],
            ),
            ft.Text(
                "Endereço",
                weight=ft.FontWeight.BOLD,
            ),
            ft.ResponsiveRow(
                controls=[
                    ft.Container(txt_cep, col={"md": 2}),
                    ft.Container(txt_logradouro, col={"md": 6}),
                    ft.Container(txt_numero, col={"md": 2}),
                    ft.Container(txt_complemento, col={"md": 2}),
                    ft.Container(txt_bairro, col={"md": 3}),
                    ft.Container(txt_cidade, col={"md": 3}),
                    ft.Container(txt_estado, col={"md": 2}),
                    ft.Container(txt_pais, col={"md": 3}),
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
