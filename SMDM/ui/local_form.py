import flet as ft

from ui.locais import trocar_conteudo
from ui.components.endereco_dialog import abrir_endereco_dialog

from services.local_service import (
    COLUNAS_LOCAL,
    atualizar_local,
    criar_local,
    listar_ambientes,
    obter_ambiente,
    obter_local,
    remover_ambiente,
    salvar_ambiente_db,
)

from services.loc_estrutura_service import (
    listar_estruturas_local,
    listar_loc_estruturas,
    salvar_estruturas_local,
)

from services.loc_tipo_service import (
    listar_loc_tipos,
)

from services.documento_service import (
    normalizar_documento,
)


TIPOS_ESPACO = [
    "Interno",
    "Externo",
]


def campo(label, width=220, multiline=False):

    return ft.TextField(
        label=label,
        width=width,
        multiline=multiline,
        min_lines=3 if multiline else None,
        max_lines=5 if multiline else None,
    )


def dropdown_opcoes(label, opcoes, width=180):

    return ft.Dropdown(
        label=label,
        width=width,
        options=[
            ft.dropdown.Option(opcao)
            for opcao in opcoes
        ],
    )


def local_form_view(page, local_id=None):

    lista_ambientes = ft.Column()
    ambiente_editando = {"id": None}
    estruturas_checks = []

    def voltar(e=None):

        from ui.locais import locais_view

        trocar_conteudo(
            page,
            locais_view(page)
        )

    txt_nome = campo("Nome", 360)
    txt_nome_fantasia = campo("Nome fantasia", 360)
    ddl_tipo = ft.Dropdown(label="Tipo de Local", width=300)
    txt_cnpj = campo("CPF (11) / CNPJ (14)", 220)
    txt_telefone = campo("Telefone", 180)
    txt_celular = campo("Celular", 180)
    txt_email = campo("E-mail", 300)
    txt_site = campo("Site", 300)
    txt_instagram = campo("Instagram", 300)
    txt_facebook = campo("Facebook", 300)
    txt_outras_redes = campo("Outras redes", 520, True)
    txt_horario = campo("Horário de funcionamento", 520, True)
    txt_responsavel = campo("Responsável", 300)
    txt_contato = campo("Contato principal", 260)
    txt_cep = campo("CEP", 150)
    txt_logradouro = campo("Endereço", 420)
    txt_numero = campo("Número", 120)
    txt_complemento = campo("Complemento", 220)
    txt_bairro = campo("Bairro", 260)
    txt_municipio = campo("Cidade", 260)
    txt_uf = campo("Estado", 100)
    txt_pais = campo("País", 180)
    txt_quem_indicou = campo("Quem indicou", 300)
    txt_obs = campo("Observações", 760, True)

    txt_uf.value = "RS"
    txt_pais.value = "Brasil"
    geo_endereco = {
        "latitude": None,
        "longitude": None,
        "fonte_geo": None,
        "data_geo": None,
    }
    lbl_geo = ft.Text(
        "",
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
            "cep": txt_cep.value,
            "logradouro": txt_logradouro.value,
            "numero": txt_numero.value,
            "complemento": txt_complemento.value,
            "bairro": txt_bairro.value,
            "municipio": txt_municipio.value,
            "uf": txt_uf.value,
            "pais": txt_pais.value,
            **geo_endereco,
        }

    def aplicar_endereco(dados):

        txt_cep.value = dados.get("cep") or ""
        txt_logradouro.value = dados.get("logradouro") or ""
        txt_numero.value = dados.get("numero") or ""
        txt_complemento.value = dados.get("complemento") or ""
        txt_bairro.value = dados.get("bairro") or ""
        txt_municipio.value = dados.get("municipio") or ""
        txt_uf.value = dados.get("uf") or "RS"
        txt_pais.value = dados.get("pais") or "Brasil"
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

    contatos = {}

    for indice in (1, 2, 3):
        contatos[f"contato{indice}_nome"] = campo(f"Contato {indice} - Nome", 300)
        contatos[f"contato{indice}_telefone"] = campo(f"Contato {indice} - Telefone", 180)
        contatos[f"contato{indice}_cargo"] = campo(f"Contato {indice} - Cargo", 220)

    chk_estacionamento = ft.Checkbox(label="Possui estacionamento", value=False)
    chk_ativo = ft.Checkbox(label="Ativo", value=True)
    chk_captado_web = ft.Checkbox(label="Captado na web", value=False)
    chk_complementado_web = ft.Checkbox(label="Complementado pela web", value=False)
    chk_cadastro_validado = ft.Checkbox(label="Cadastro validado", value=False)
    chk_pesquisa_incompleta = ft.Checkbox(label="Pesquisa incompleta", value=False)
    chk_necessita_complemento = ft.Checkbox(label="Necessita complemento", value=False)
    chk_necessita_revisao = ft.Checkbox(label="Necessita revisão", value=False)
    txt_pontuacao_origem_web = campo("Pontuação origem web", 180)
    txt_fonte_origem_web = campo("Fonte origem web", 260)
    txt_data_origem_web = campo("Data origem web", 220)
    txt_local_pesquisa_web_id = campo("ID pesquisa web", 180)
    txt_data_validacao = campo("Data validação cadastro", 220)
    txt_observacao_pesquisa = campo("Observação da pesquisa", 760, True)

    estrutura_container = ft.ResponsiveRow(
        spacing=4,
        run_spacing=0,
    )

    def carregar_estruturas():

        estrutura_container.controls.clear()
        estruturas = listar_loc_estruturas()
        selecionadas = listar_estruturas_local(local_id) if local_id else []
        estruturas_checks.clear()

        for estrutura in estruturas:
            estrutura_id = estrutura[0]
            nome = estrutura[1]
            ativo = bool(estrutura[2])

            if not ativo:
                continue

            chk = ft.Checkbox(
                label=nome,
                value=estrutura_id in selecionadas,
            )
            estruturas_checks.append((estrutura_id, chk))
            estrutura_container.controls.append(
                ft.Container(
                    chk,
                    col={"md": 4},
                )
            )

    def obter_estruturas_selecionadas():

        return [
            estrutura_id
            for estrutura_id, chk in estruturas_checks
            if chk.value
        ]

    def carregar_tipos():

        ddl_tipo.options = []

        for tipo in listar_loc_tipos():
            ddl_tipo.options.append(
                ft.dropdown.Option(str(tipo[0]), tipo[1])
            )

    def valor_tela(valor):

        return "" if valor in ("", None) else str(valor)

    txt_amb_nome = campo("Nome do espaço", 300)
    ddl_tipo_espaco = dropdown_opcoes("Espaço", TIPOS_ESPACO, 180)
    txt_capacidade = campo("Capacidade convidados", 180)
    txt_comprimento = campo("Comprimento (m)", 170)
    txt_largura = campo("Largura (m)", 170)
    txt_pe_direito = campo("Pé direito", 150)
    txt_servicos = campo("Serviços oferecidos", 460, True)
    chk_ar = ft.Checkbox(label="Ar Condicionado")
    txt_preco = campo("Preço Base", 180)

    def carregar_local():

        if not local_id:
            return

        row = obter_local(local_id)

        if not row:
            return

        dados = dict(zip(COLUNAS_LOCAL, row[1:]))

        txt_nome.value = dados.get("NomeCasa") or ""
        txt_nome_fantasia.value = dados.get("NomeFantasia") or ""
        ddl_tipo.value = str(dados.get("LocTipoID")) if dados.get("LocTipoID") else None
        txt_cnpj.value = dados.get("CNPJ") or ""
        txt_cep.value = dados.get("CEP") or ""
        txt_logradouro.value = dados.get("Logradouro") or ""
        txt_numero.value = dados.get("Numero") or ""
        txt_complemento.value = dados.get("Complemento") or ""
        txt_bairro.value = dados.get("Bairro") or ""
        txt_municipio.value = dados.get("Municipio") or ""
        txt_uf.value = dados.get("UF") or "RS"
        txt_pais.value = dados.get("Pais") or "Brasil"
        geo_endereco["latitude"] = dados.get("Latitude")
        geo_endereco["longitude"] = dados.get("Longitude")
        geo_endereco["fonte_geo"] = dados.get("FonteGeo")
        geo_endereco["data_geo"] = dados.get("DataGeo")
        atualizar_status_geo()
        txt_telefone.value = dados.get("Telefone") or ""
        txt_celular.value = dados.get("Celular") or ""
        txt_email.value = dados.get("Email") or ""
        txt_site.value = dados.get("Site") or ""
        txt_instagram.value = dados.get("Instagram") or ""
        txt_facebook.value = dados.get("Facebook") or ""
        txt_outras_redes.value = dados.get("OutrasRedes") or ""
        txt_horario.value = dados.get("HorarioFuncionamento") or ""
        txt_responsavel.value = dados.get("Responsavel") or ""
        txt_contato.value = dados.get("Contato") or ""
        txt_quem_indicou.value = dados.get("QuemIndicou") or ""
        txt_obs.value = dados.get("Observacoes") or ""
        chk_estacionamento.value = bool(dados.get("PossuiEstacionamento"))
        chk_ativo.value = bool(dados.get("Ativo"))
        chk_captado_web.value = bool(dados.get("CaptadoWeb"))
        chk_complementado_web.value = bool(dados.get("ComplementadoWeb"))
        chk_cadastro_validado.value = bool(dados.get("CadastroValidado"))
        chk_pesquisa_incompleta.value = bool(dados.get("PesquisaIncompleta"))
        chk_necessita_complemento.value = bool(dados.get("NecessitaComplemento"))
        chk_necessita_revisao.value = bool(dados.get("NecessitaRevisao"))
        txt_pontuacao_origem_web.value = valor_tela(dados.get("PontuacaoOrigemWeb"))
        txt_fonte_origem_web.value = dados.get("FonteOrigemWeb") or ""
        txt_data_origem_web.value = valor_tela(dados.get("DataOrigemWeb"))
        txt_local_pesquisa_web_id.value = valor_tela(dados.get("LocalPesquisaWebId"))
        txt_data_validacao.value = valor_tela(dados.get("DataValidacaoCadastro"))
        txt_observacao_pesquisa.value = dados.get("ObservacaoPesquisa") or ""

        for indice in (1, 2, 3):
            contatos[f"contato{indice}_nome"].value = dados.get(f"Contato{indice}Nome") or ""
            contatos[f"contato{indice}_telefone"].value = dados.get(f"Contato{indice}Telefone") or ""
            contatos[f"contato{indice}_cargo"].value = dados.get(f"Contato{indice}Cargo") or ""

    def carregar_ambientes():

        lista_ambientes.controls.clear()

        if not local_id:
            lista_ambientes.controls.append(
                ft.Text("Salve o local para cadastrar espaços.")
            )
            return

        ambientes = listar_ambientes(local_id)

        if not ambientes:
            lista_ambientes.controls.append(
                ft.Text("Nenhum espaço cadastrado")
            )

        for ambiente in ambientes:
            lista_ambientes.controls.append(
                ft.Container(
                    padding=10,
                    border=ft.border.all(1, ft.Colors.GREY_300),
                    border_radius=6,
                    content=ft.Row(
                        controls=[
                            ft.Column(
                                expand=True,
                                spacing=2,
                                controls=[
                                    ft.Text(ambiente[1], size=16, weight=ft.FontWeight.BOLD),
                                    ft.Text(f"{ambiente[2] or '-'} | Capacidade: {ambiente[3] or 0} convidados"),
                                    ft.Text(f"Dimensão: {ambiente[4] or 0}m x {ambiente[5] or 0}m"),
                                    ft.Text(f"Serviços: {ambiente[6] or '-'}"),
                                ],
                            ),
                            ft.IconButton(
                                icon=ft.Icons.EDIT,
                                tooltip="Editar",
                                on_click=lambda e, a=ambiente: editar_ambiente(a[0]),
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE,
                                tooltip="Excluir",
                                on_click=lambda e, id=ambiente[0]: excluir_ambiente(id),
                            ),
                        ],
                    ),
                )
            )

    def mostrar_mensagem(texto):

        page.snack_bar = ft.SnackBar(ft.Text(texto))
        page.snack_bar.open = True
        page.update()

    def validar_documento_local(e=None):

        txt_cnpj.error = None

        try:
            normalizar_documento(
                txt_cnpj.value,
                campo="CPF/CNPJ",
            )
        except Exception as ex:
            txt_cnpj.error = str(ex)
            page.update()
            return False

        if e:
            page.update()

        return True

    txt_cnpj.on_blur = validar_documento_local

    def validar_formulario():

        return validar_documento_local()

    def dados_local():

        dados = {
            "nome": txt_nome.value,
            "nome_fantasia": txt_nome_fantasia.value,
            "loc_tipo_id": ddl_tipo.value,
            "cnpj": txt_cnpj.value,
            "cep": txt_cep.value,
            "logradouro": txt_logradouro.value,
            "numero": txt_numero.value,
            "complemento": txt_complemento.value,
            "bairro": txt_bairro.value,
            "municipio": txt_municipio.value,
            "uf": txt_uf.value,
            "pais": txt_pais.value,
            "latitude": geo_endereco.get("latitude"),
            "longitude": geo_endereco.get("longitude"),
            "fonte_geo": geo_endereco.get("fonte_geo"),
            "data_geo": geo_endereco.get("data_geo"),
            "telefone": txt_telefone.value,
            "celular": txt_celular.value,
            "email": txt_email.value,
            "site": txt_site.value,
            "instagram": txt_instagram.value,
            "facebook": txt_facebook.value,
            "outras_redes": txt_outras_redes.value,
            "horario_funcionamento": txt_horario.value,
            "responsavel": txt_responsavel.value,
            "contato": txt_contato.value,
            "quem_indicou": txt_quem_indicou.value,
            "estacionamento": chk_estacionamento.value,
            "observacoes": txt_obs.value,
            "ativo": chk_ativo.value,
            "captado_web": chk_captado_web.value,
            "complementado_web": chk_complementado_web.value,
            "cadastro_validado": chk_cadastro_validado.value,
            "pesquisa_incompleta": chk_pesquisa_incompleta.value,
            "necessita_complemento": chk_necessita_complemento.value,
            "necessita_revisao": chk_necessita_revisao.value,
            "pontuacao_origem_web": txt_pontuacao_origem_web.value,
            "fonte_origem_web": txt_fonte_origem_web.value,
            "data_origem_web": txt_data_origem_web.value,
            "local_pesquisa_web_id": txt_local_pesquisa_web_id.value,
            "data_validacao_cadastro": txt_data_validacao.value,
            "observacao_pesquisa": txt_observacao_pesquisa.value,
        }

        for chave, controle in contatos.items():
            dados[chave] = controle.value

        return dados

    def salvar_local(e):

        nonlocal local_id

        try:
            if not validar_formulario():
                mostrar_mensagem("Corrija os campos destacados.")
                return

            if local_id:
                resultado = atualizar_local(local_id, dados_local())
            else:
                resultado = criar_local(dados_local())

            if isinstance(resultado, dict):
                local_id = resultado.get("id")
                geo_erro = resultado.get("geo_erro")
            else:
                local_id = resultado
                geo_erro = ""

            salvar_estruturas_local(
                local_id,
                obter_estruturas_selecionadas(),
            )

            carregar_local()
            carregar_estruturas()
            carregar_ambientes()
            page.update()
            if geo_erro:
                mostrar_mensagem(
                    f"Local salvo. Localização não gerada: {geo_erro}"
                )
            else:
                mostrar_mensagem("Local salvo")
        except Exception as ex:
            mostrar_mensagem(str(ex))

    def limpar_ambiente():

        ambiente_editando["id"] = None
        txt_amb_nome.value = ""
        ddl_tipo_espaco.value = None
        txt_capacidade.value = ""
        txt_comprimento.value = ""
        txt_largura.value = ""
        txt_pe_direito.value = ""
        txt_servicos.value = ""
        txt_preco.value = ""
        chk_ar.value = False

    def editar_ambiente(ambiente_id):

        dados = obter_ambiente(ambiente_id)

        if not dados:
            return

        ambiente_editando["id"] = dados[0]
        txt_amb_nome.value = dados[2] or ""
        ddl_tipo_espaco.value = dados[3] or None
        txt_capacidade.value = str(dados[4] or "")
        txt_comprimento.value = str(dados[10] or "")
        txt_largura.value = str(dados[11] or "")
        txt_pe_direito.value = str(dados[7] or "")
        chk_ar.value = bool(dados[8])
        txt_preco.value = str(dados[9] or "")
        txt_servicos.value = dados[12] or ""
        dlg.open = True
        page.update()

    def excluir_ambiente(ambiente_id):

        try:
            remover_ambiente(ambiente_id)
            carregar_ambientes()
            mostrar_mensagem("Espaço removido")
        except Exception as ex:
            mostrar_mensagem(str(ex))

    def salvar_ambiente(e):

        if not local_id:
            mostrar_mensagem("Salve o local primeiro")
            return

        try:
            salvar_ambiente_db({
                "id": ambiente_editando["id"],
                "local_id": local_id,
                "nome": txt_amb_nome.value,
                "tipo_espaco": ddl_tipo_espaco.value,
                "sentado": txt_capacidade.value,
                "pe": txt_capacidade.value,
                "comprimento": txt_comprimento.value,
                "largura": txt_largura.value,
                "pe_direito": txt_pe_direito.value,
                "servicos": txt_servicos.value,
                "ar": chk_ar.value,
                "preco": txt_preco.value,
            })
            dlg.open = False
            limpar_ambiente()
            carregar_ambientes()
            page.update()
        except Exception as ex:
            mostrar_mensagem(str(ex))

    def novo_ambiente(e):

        limpar_ambiente()
        dlg.open = True
        page.update()

    def fechar_dialog(e=None):

        dlg.open = False
        page.update()

    dlg = ft.AlertDialog(
        modal=True,
        title=ft.Text("Espaço"),
        content=ft.Container(
            width=620,
            content=ft.Column(
                tight=True,
                spacing=8,
                controls=[
                    txt_amb_nome,
                    ft.Row([ddl_tipo_espaco, txt_capacidade]),
                    ft.Row([txt_comprimento, txt_largura, txt_pe_direito]),
                    ft.Row([txt_preco, chk_ar]),
                    txt_servicos,
                ],
            ),
        ),
        actions=[
            ft.TextButton("Cancelar", on_click=fechar_dialog),
            ft.ElevatedButton("Salvar", on_click=salvar_ambiente),
        ],
    )

    page.overlay.append(dlg)

    def bloco(titulo, itens):

        return ft.Column(
            spacing=6,
            controls=[
                ft.Text(titulo, size=18, weight=ft.FontWeight.BOLD),
                ft.ResponsiveRow(
                    spacing=8,
                    run_spacing=8,
                    controls=[
                        ft.Container(item, col={"md": 3})
                        for item in itens
                    ],
                ),
            ],
        )

    def painel(controles):

        return ft.Container(
            expand=True,
            padding=ft.padding.only(top=8, right=8),
            content=ft.Column(
                expand=True,
                scroll=ft.ScrollMode.AUTO,
                spacing=10,
                controls=controles,
            ),
        )

    def linha_contato(indice):

        return ft.ResponsiveRow(
            spacing=8,
            run_spacing=6,
            controls=[
                ft.Container(
                    contatos[f"contato{indice}_nome"],
                    col={"md": 5},
                ),
                ft.Container(
                    contatos[f"contato{indice}_telefone"],
                    col={"md": 3},
                ),
                ft.Container(
                    contatos[f"contato{indice}_cargo"],
                    col={"md": 4},
                ),
            ],
        )

    carregar_tipos()
    carregar_local()
    carregar_estruturas()
    carregar_ambientes()

    conteudo_secao = ft.Container(expand=True)
    botoes_secao = []

    secoes = [
        (
            "Dados",
            painel([
                bloco("Dados gerais", [
                    txt_nome,
                    txt_nome_fantasia,
                    ddl_tipo,
                    txt_cnpj,
                    txt_telefone,
                    txt_celular,
                    txt_email,
                    txt_site,
                    txt_instagram,
                    txt_facebook,
                    txt_responsavel,
                    txt_contato,
                    chk_estacionamento,
                    chk_ativo,
                ]),
            ]),
        ),
        (
            "Web",
            painel([
                bloco("Origem e redes", [
                    txt_outras_redes,
                    txt_horario,
                    txt_fonte_origem_web,
                    txt_pontuacao_origem_web,
                    txt_data_origem_web,
                    txt_local_pesquisa_web_id,
                ]),
                bloco("Controle da pesquisa", [
                    chk_captado_web,
                    chk_complementado_web,
                    chk_cadastro_validado,
                    chk_pesquisa_incompleta,
                    chk_necessita_complemento,
                    chk_necessita_revisao,
                    txt_data_validacao,
                    txt_observacao_pesquisa,
                ]),
            ]),
        ),
        (
            "Endereço",
            painel([
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text("Endereço", size=18, weight=ft.FontWeight.BOLD),
                        ft.TextButton(
                            "Editar endereço",
                            icon=ft.Icons.MAP,
                            on_click=editar_endereco,
                        ),
                    ],
                ),
                ft.ResponsiveRow(
                    spacing=8,
                    run_spacing=8,
                    controls=[
                        ft.Container(txt_cep, col={"md": 2}),
                        ft.Container(txt_logradouro, col={"md": 5}),
                        ft.Container(txt_numero, col={"md": 2}),
                        ft.Container(txt_complemento, col={"md": 3}),
                        ft.Container(txt_bairro, col={"md": 3}),
                        ft.Container(txt_municipio, col={"md": 3}),
                        ft.Container(txt_uf, col={"md": 2}),
                        ft.Container(txt_pais, col={"md": 3}),
                        ft.Container(lbl_geo, col={"md": 12}),
                    ],
                ),
            ]),
        ),
        (
            "Contatos",
            painel([
                ft.Text("Contatos", size=18, weight=ft.FontWeight.BOLD),
                linha_contato(1),
                linha_contato(2),
                linha_contato(3),
            ]),
        ),
        (
            "Serviços",
            painel([
                bloco("Serviços e indicação", [
                    txt_quem_indicou,
                    txt_obs,
                ]),
                ft.Text(
                    "Serviços oferecidos / infraestrutura",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                ),
                estrutura_container,
            ]),
        ),
        (
            "Espaços",
            painel([
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text("Espaços", size=18, weight=ft.FontWeight.BOLD),
                        ft.ElevatedButton(
                            "Novo Espaço",
                            icon=ft.Icons.ADD,
                            on_click=novo_ambiente,
                        ),
                    ],
                ),
                lista_ambientes,
            ]),
        ),
    ]

    def selecionar_secao(indice):

        conteudo_secao.content = secoes[indice][1]

        for i, botao in enumerate(botoes_secao):
            botao.disabled = i == indice

        page.update()

    for indice, secao in enumerate(secoes):
        botoes_secao.append(
            ft.TextButton(
                secao[0],
                on_click=lambda e, i=indice: selecionar_secao(i),
            )
        )

    conteudo_secao.content = secoes[0][1]
    botoes_secao[0].disabled = True

    return ft.Column(
        expand=True,
        spacing=8,
        controls=[
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Text("Cadastro de Local de Evento", size=24, weight=ft.FontWeight.BOLD),
                    ft.Row(
                        spacing=8,
                        controls=[
                            ft.ElevatedButton(
                                "Salvar",
                                icon=ft.Icons.SAVE,
                                on_click=salvar_local,
                            ),
                            ft.OutlinedButton(
                                "Voltar",
                                icon=ft.Icons.ARROW_BACK,
                                on_click=voltar,
                            ),
                        ],
                    ),
                ],
            ),
            ft.Divider(),
            ft.Row(
                spacing=4,
                controls=botoes_secao,
            ),
            conteudo_secao,
        ],
    )
