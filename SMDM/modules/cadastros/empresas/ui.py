import flet as ft

import flet as ft

from ui.components.endereco_dialog import abrir_endereco_dialog

from modules.cadastros.empresas.service import (
    COLUNAS,
    excluir_empresa,
    listar_empresas,
    obter_empresa,
    salvar_empresa,
)

from services.documento_service import (
    normalizar_cpf,
    normalizar_documento,
)


TIPO_PESSOA_OPCOES = [
    "Jurídica",
    "Física",
]


def dropdown_opcoes(label, opcoes, width=180):

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


def campo(label, width=220, multiline=False):

    return ft.TextField(
        label=label,
        width=width,
        multiline=multiline,
        min_lines=3 if multiline else None,
        max_lines=5 if multiline else None,
    )


def empresas_view(page):

    lista = ft.Column(
        spacing=8,
    )

    empresa_editando = {
        "id": None,
    }

    controles = {
        "razao_social": campo("Razão Social", 420),
        "nome_fantasia": campo("Nome Fantasia", 420),
        "tipo_pessoa": dropdown_opcoes("Pessoa", TIPO_PESSOA_OPCOES),
        "documento": campo("CPF (11) / CNPJ (14)", 220),
        "inscricao_estadual": campo("Inscrição estadual", 200),
        "inscricao_municipal": campo("Inscrição municipal", 200),
        "inscricao": campo("Inscrição", 180),
        "data_fundacao": campo("Data da fundação", 180),
        "atividade_economica": campo("Atividade econômica", 360),
        "quantidade_funcionarios": campo("Quantidade funcionários", 200),
        "cnae1": campo("CNAE 1", 160),
        "cnae2": campo("CNAE 2", 160),
        "cnae3": campo("CNAE 3", 160),
        "cep": campo("CEP", 150),
        "logradouro": campo("Endereço", 420),
        "numero": campo("Número", 120),
        "complemento": campo("Complemento", 220),
        "bairro": campo("Bairro", 260),
        "municipio": campo("Cidade", 260),
        "uf": campo("Estado", 100),
        "pais": campo("País", 180),
        "website": campo("Website", 300),
        "facebook": campo("Facebook", 260),
        "twitter": campo("Twitter", 260),
        "instagram": campo("Instagram", 260),
        "telefone1": campo("Telefone 1", 180),
        "telefone2": campo("Telefone 2", 180),
        "telefone3": campo("Telefone 3", 180),
        "contato_nome": campo("Contato", 300),
        "contato_departamento": campo("Departamento", 220),
        "contato_cargo": campo("Cargo", 220),
        "contato_telefone_fixo": campo("Telefone fixo", 180),
        "contato_celular": campo("Celular", 180),
        "contato_email": campo("E-mail contato", 300),
        "quem_indicou": campo("Quem indicou", 300),
        "primeiro_canal": campo("Primeiro canal de contato", 360),
        "observacoes": campo("Observações / Comentários", 760, True),
    }

    controles["uf"].value = "RS"
    controles["pais"].value = "Brasil"
    geo_endereco = {
        "latitude": None,
        "longitude": None,
        "fonte_geo": None,
        "data_geo": None,
    }
    lbl_geo = ft.Text(
        "Localização não gerada.",
        size=12,
        color=ft.Colors.GREY_700,
    )

    def atualizar_status_geo():

        if geo_endereco.get("latitude") and geo_endereco.get("longitude"):
            lbl_geo.value = (
                f"Localização: {geo_endereco['latitude']}, "
                f"{geo_endereco['longitude']}"
            )
        else:
            lbl_geo.value = "Localização não gerada."

    def endereco_atual():

        return {
            "cep": controles["cep"].value,
            "logradouro": controles["logradouro"].value,
            "numero": controles["numero"].value,
            "complemento": controles["complemento"].value,
            "bairro": controles["bairro"].value,
            "municipio": controles["municipio"].value,
            "uf": controles["uf"].value,
            "pais": controles["pais"].value,
            **geo_endereco,
        }

    def aplicar_endereco(dados):

        controles["cep"].value = dados.get("cep") or ""
        controles["logradouro"].value = dados.get("logradouro") or ""
        controles["numero"].value = dados.get("numero") or ""
        controles["complemento"].value = dados.get("complemento") or ""
        controles["bairro"].value = dados.get("bairro") or ""
        controles["municipio"].value = dados.get("municipio") or ""
        controles["uf"].value = dados.get("uf") or "RS"
        controles["pais"].value = dados.get("pais") or "Brasil"
        geo_endereco["latitude"] = dados.get("latitude")
        geo_endereco["longitude"] = dados.get("longitude")
        geo_endereco["fonte_geo"] = dados.get("fonte_geo")
        geo_endereco["data_geo"] = dados.get("data_geo")
        atualizar_status_geo()
        page.update()

    def editar_endereco(e=None):

        abrir_endereco_dialog(
            page,
            endereco_atual(),
            aplicar_endereco,
        )

    for indice in (1, 2, 3):

        prefixo = f"responsavel{indice}"

        controles[f"{prefixo}_cargo"] = campo(f"Responsável {indice} - Cargo/Função", 260)
        controles[f"{prefixo}_nome"] = campo(f"Responsável {indice} - Nome", 320)
        controles[f"{prefixo}_nacionalidade"] = campo(f"Responsável {indice} - Nacionalidade", 220)
        controles[f"{prefixo}_estado_civil"] = campo(f"Responsável {indice} - Estado civil", 200)
        controles[f"{prefixo}_rg"] = campo(f"Responsável {indice} - RG", 180)
        controles[f"{prefixo}_cpf"] = campo(f"Responsável {indice} - CPF", 180)
        controles[f"{prefixo}_data_nascimento"] = campo(f"Responsável {indice} - Dt. Nasc.", 180)
        controles[f"{prefixo}_telefone"] = campo(f"Responsável {indice} - Telefone profissional", 240)
        controles[f"{prefixo}_email"] = campo(f"Responsável {indice} - E-mail", 280)
        controles[f"{prefixo}_comerciante"] = ft.Checkbox(
            label=f"Responsável {indice} comerciante",
            value=False,
        )

    chk_ativo = ft.Checkbox(
        label="Ativo",
        value=True,
    )

    def mostrar_mensagem(texto):

        page.snack_bar = ft.SnackBar(
            ft.Text(
                texto
            )
        )

        page.snack_bar.open = True

        page.update()

    def validar_documento_empresa(e=None):

        controles["documento"].error = None

        try:
            normalizar_documento(
                controles["documento"].value,
                campo="CPF/CNPJ",
            )
        except Exception as ex:
            controles["documento"].error = str(ex)
            page.update()
            return False

        if e:
            page.update()

        return True

    def validar_cpf_responsavel(chave, e=None):

        controles[chave].error = None

        try:
            normalizar_cpf(
                controles[chave].value,
                campo=controles[chave].label,
            )
        except Exception as ex:
            controles[chave].error = str(ex)
            page.update()
            return False

        if e:
            page.update()

        return True

    controles["documento"].on_blur = validar_documento_empresa

    for indice in (1, 2, 3):
        chave = f"responsavel{indice}_cpf"
        controles[chave].on_blur = (
            lambda e, c=chave: validar_cpf_responsavel(c, e)
        )

    def validar_documentos():

        valido = validar_documento_empresa()

        for indice in (1, 2, 3):
            chave = f"responsavel{indice}_cpf"

            if not validar_cpf_responsavel(chave):
                valido = False

        return valido

    def dados_formulario():

        dados = {
            chave: controle.value
            for chave, controle in controles.items()
        }

        dados["ativo"] = chk_ativo.value
        dados.update(geo_endereco)

        return dados

    def limpar(e=None):

        empresa_editando["id"] = None

        for controle in controles.values():
            controle.value = False if isinstance(controle, ft.Checkbox) else ""
            if hasattr(controle, "error"):
                controle.error = None

        controles["uf"].value = "RS"
        controles["pais"].value = "Brasil"
        chk_ativo.value = True
        geo_endereco["latitude"] = None
        geo_endereco["longitude"] = None
        geo_endereco["fonte_geo"] = None
        geo_endereco["data_geo"] = None
        atualizar_status_geo()

        page.update()

    def carregar(atualizar=True):

        lista.controls.clear()

        empresas = listar_empresas()

        if not empresas:

            lista.controls.append(
                ft.Container(
                    padding=16,
                    content=ft.Text(
                        "Nenhuma empresa cadastrada"
                    ),
                )
            )

            if atualizar:
                page.update()

            return

        for empresa in empresas:

            empresa_id = empresa[0]
            razao = empresa[1] or ""
            fantasia = empresa[2] or ""
            documento = empresa[3] or ""
            contato = empresa[4] or ""
            celular = empresa[5] or ""
            email = empresa[6] or ""
            ativo = bool(empresa[7])

            lista.controls.append(
                ft.Container(
                    padding=12,
                    border=ft.border.all(1, ft.Colors.GREY_300),
                    border_radius=6,
                    content=ft.Row(
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Column(
                                spacing=2,
                                expand=True,
                                controls=[
                                    ft.Text(razao, size=15, weight=ft.FontWeight.BOLD),
                                    ft.Text(fantasia or "Sem nome fantasia", size=12),
                                    ft.Text(
                                        f"Doc: {documento or '-'} | Contato: {contato or '-'} | Celular: {celular or '-'} | E-mail: {email or '-'}",
                                        size=12,
                                        color=ft.Colors.GREY_700,
                                    ),
                                ],
                            ),
                            ft.Text("ATIVO" if ativo else "INATIVO", size=11),
                            ft.IconButton(
                                icon=ft.Icons.EDIT,
                                tooltip="Editar",
                                on_click=lambda e, id=empresa_id: editar(id),
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE,
                                tooltip="Excluir",
                                on_click=lambda e, id=empresa_id: excluir(e, id),
                            ),
                        ],
                    ),
                )
            )

        if atualizar:
            page.update()

    def editar(empresa_id):

        row = obter_empresa(
            empresa_id
        )

        if not row:
            return

        empresa_editando["id"] = row[0]

        dados = dict(
            zip(
                COLUNAS,
                row[1:],
            )
        )

        mapa = {
            "RazaoSocial": "razao_social",
            "NomeFantasia": "nome_fantasia",
            "TipoPessoa": "tipo_pessoa",
            "Documento": "documento",
            "InscricaoEstadual": "inscricao_estadual",
            "InscricaoMunicipal": "inscricao_municipal",
            "Inscricao": "inscricao",
            "DataFundacao": "data_fundacao",
            "AtividadeEconomica": "atividade_economica",
            "QuantidadeFuncionarios": "quantidade_funcionarios",
            "CEP": "cep",
            "Logradouro": "logradouro",
            "Numero": "numero",
            "Complemento": "complemento",
            "Bairro": "bairro",
            "Municipio": "municipio",
            "UF": "uf",
            "Pais": "pais",
            "Website": "website",
            "Facebook": "facebook",
            "Twitter": "twitter",
            "Instagram": "instagram",
            "Telefone1": "telefone1",
            "Telefone2": "telefone2",
            "Telefone3": "telefone3",
            "ContatoNome": "contato_nome",
            "ContatoDepartamento": "contato_departamento",
            "ContatoCargo": "contato_cargo",
            "ContatoTelefoneFixo": "contato_telefone_fixo",
            "ContatoCelular": "contato_celular",
            "ContatoEmail": "contato_email",
            "QuemIndicou": "quem_indicou",
            "PrimeiroCanalContato": "primeiro_canal",
            "Observacoes": "observacoes",
        }

        for coluna in ("CNAE1", "CNAE2", "CNAE3"):
            mapa[coluna] = coluna.lower()

        for indice in (1, 2, 3):

            base_db = f"Responsavel{indice}"
            base_form = f"responsavel{indice}"

            mapa[f"{base_db}Cargo"] = f"{base_form}_cargo"
            mapa[f"{base_db}Nome"] = f"{base_form}_nome"
            mapa[f"{base_db}Nacionalidade"] = f"{base_form}_nacionalidade"
            mapa[f"{base_db}EstadoCivil"] = f"{base_form}_estado_civil"
            mapa[f"{base_db}RG"] = f"{base_form}_rg"
            mapa[f"{base_db}CPF"] = f"{base_form}_cpf"
            mapa[f"{base_db}DataNascimento"] = f"{base_form}_data_nascimento"
            mapa[f"{base_db}Telefone"] = f"{base_form}_telefone"
            mapa[f"{base_db}Email"] = f"{base_form}_email"

            controles[f"{base_form}_comerciante"].value = bool(
                dados.get(f"{base_db}Comerciante")
            )

        for coluna, chave in mapa.items():

            valor = dados.get(coluna)

            if hasattr(valor, "strftime"):
                valor = valor.strftime("%d/%m/%Y")

            controles[chave].value = valor or ""

        geo_endereco["latitude"] = dados.get("Latitude")
        geo_endereco["longitude"] = dados.get("Longitude")
        geo_endereco["fonte_geo"] = dados.get("FonteGeo")
        geo_endereco["data_geo"] = dados.get("DataGeo")
        atualizar_status_geo()

        chk_ativo.value = bool(
            dados.get("Ativo")
        )

        page.update()

    def excluir(e, empresa_id):

        try:

            excluir_empresa(
                empresa_id
            )

            carregar(False)

            limpar()

            mostrar_mensagem(
                "Empresa removida"
            )

        except Exception as ex:
            mostrar_mensagem(str(ex))

    def salvar(e=None):

        try:
            if not validar_documentos():
                mostrar_mensagem("Corrija os campos destacados.")
                return


            salvar_empresa(
                empresa_editando["id"],
                dados_formulario(),
            )

            carregar(False)

            limpar()

            mostrar_mensagem(
                "Empresa salva"
            )

        except Exception as ex:
            mostrar_mensagem(str(ex))

    def bloco(titulo, itens):

        return ft.Column(
            spacing=8,
            controls=[
                ft.Text(titulo, weight=ft.FontWeight.BOLD),
                ft.ResponsiveRow(
                    controls=[
                        ft.Container(item, col={"md": 3})
                        for item in itens
                    ],
                ),
            ],
        )

    carregar(False)

    return ft.Column(
        expand=True,
        scroll=ft.ScrollMode.AUTO,
        spacing=10,
        controls=[
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Text("Cadastro de Empresas", size=24, weight=ft.FontWeight.BOLD),
                    ft.Row(
                        spacing=8,
                        controls=[
                            ft.ElevatedButton("Novo", icon=ft.Icons.ADD, on_click=limpar),
                            ft.ElevatedButton("Salvar", icon=ft.Icons.SAVE, on_click=salvar),
                        ],
                    ),
                ],
            ),
            ft.Divider(),
            bloco("Empresa", [
                controles["razao_social"],
                controles["nome_fantasia"],
                controles["tipo_pessoa"],
                controles["documento"],
                controles["inscricao_estadual"],
                controles["inscricao_municipal"],
                controles["inscricao"],
                controles["data_fundacao"],
                controles["atividade_economica"],
                controles["quantidade_funcionarios"],
                controles["cnae1"],
                controles["cnae2"],
                controles["cnae3"],
                chk_ativo,
            ]),
            bloco("Endereço", [
                ft.TextButton(
                    "Editar endereço",
                    icon=ft.Icons.MAP,
                    on_click=editar_endereco,
                ),
                controles["cep"],
                controles["logradouro"],
                controles["numero"],
                controles["complemento"],
                controles["bairro"],
                controles["municipio"],
                controles["uf"],
                controles["pais"],
                lbl_geo,
            ]),
            bloco("Contato e redes", [
                controles["telefone1"],
                controles["telefone2"],
                controles["telefone3"],
                controles["website"],
                controles["facebook"],
                controles["twitter"],
                controles["instagram"],
                controles["contato_nome"],
                controles["contato_departamento"],
                controles["contato_cargo"],
                controles["contato_telefone_fixo"],
                controles["contato_celular"],
                controles["contato_email"],
            ]),
            bloco("Responsável 1", [
                controles["responsavel1_cargo"],
                controles["responsavel1_nome"],
                controles["responsavel1_nacionalidade"],
                controles["responsavel1_estado_civil"],
                controles["responsavel1_comerciante"],
                controles["responsavel1_rg"],
                controles["responsavel1_cpf"],
                controles["responsavel1_data_nascimento"],
                controles["responsavel1_telefone"],
                controles["responsavel1_email"],
            ]),
            bloco("Responsável 2", [
                controles["responsavel2_cargo"],
                controles["responsavel2_nome"],
                controles["responsavel2_nacionalidade"],
                controles["responsavel2_estado_civil"],
                controles["responsavel2_comerciante"],
                controles["responsavel2_rg"],
                controles["responsavel2_cpf"],
                controles["responsavel2_data_nascimento"],
                controles["responsavel2_telefone"],
                controles["responsavel2_email"],
            ]),
            bloco("Responsável 3", [
                controles["responsavel3_cargo"],
                controles["responsavel3_nome"],
                controles["responsavel3_nacionalidade"],
                controles["responsavel3_estado_civil"],
                controles["responsavel3_comerciante"],
                controles["responsavel3_rg"],
                controles["responsavel3_cpf"],
                controles["responsavel3_data_nascimento"],
                controles["responsavel3_telefone"],
                controles["responsavel3_email"],
            ]),
            bloco("Origem e observações", [
                controles["quem_indicou"],
                controles["primeiro_canal"],
                controles["observacoes"],
            ]),
            ft.Row(
                spacing=8,
                controls=[
                    ft.ElevatedButton("Salvar", icon=ft.Icons.SAVE, on_click=salvar),
                    ft.OutlinedButton("Limpar", icon=ft.Icons.CLEAR, on_click=limpar),
                ],
            ),
            ft.Divider(),
            lista,
        ],
    )
