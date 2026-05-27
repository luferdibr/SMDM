import flet as ft

from services.local_pesquisa_web_service import (
    COLUNAS_PESQUISA_WEB,
    STATUS_PESQUISA,
    listar_pesquisas,
    obter_pesquisa,
    salvar_pesquisa,
    transferir_pesquisa_para_local,
)


def campo(label, width=220, multiline=False):
    return ft.TextField(
        label=label,
        width=width,
        multiline=multiline,
        min_lines=3 if multiline else None,
        max_lines=5 if multiline else None,
    )


def dropdown_status():
    return ft.Dropdown(
        label="Status",
        width=260,
        options=[
            ft.dropdown.Option(status)
            for status in STATUS_PESQUISA
        ],
    )


def pesquisa_web_base_view(page, modo="pesquisa"):
    pesquisa_id = {"valor": None}
    lista = ft.Column(spacing=6)

    txt_nome = campo("Nome do local", 320)
    txt_tipo = campo("Tipo sugerido", 220)
    txt_municipio = campo("Cidade", 220)
    txt_uf = campo("UF", 80)
    txt_telefone = campo("Telefone", 160)
    txt_whatsapp = campo("WhatsApp", 160)
    txt_site = campo("Site", 300)
    txt_instagram = campo("Instagram", 260)
    txt_facebook = campo("Facebook", 260)
    txt_endereco = campo("Endereço", 520)
    txt_pontuacao = campo("Pontuação", 120)
    ddl_status = dropdown_status()
    chk_duplicidade = ft.Checkbox(label="Possível duplicidade")
    chk_descartado = ft.Checkbox(label="Descartado")
    txt_observacao = campo("Observação da pesquisa", 700, True)

    def mostrar(texto):
        page.snack_bar = ft.SnackBar(ft.Text(texto))
        page.snack_bar.open = True
        page.update()

    def limpar_formulario(e=None):
        pesquisa_id["valor"] = None

        for controle in (
            txt_nome,
            txt_tipo,
            txt_municipio,
            txt_uf,
            txt_telefone,
            txt_whatsapp,
            txt_site,
            txt_instagram,
            txt_facebook,
            txt_endereco,
            txt_pontuacao,
            txt_observacao,
        ):
            controle.value = ""

        ddl_status.value = "PENDENTE_ANALISE"
        chk_duplicidade.value = False
        chk_descartado.value = False
        page.update()

    def dados_formulario():
        return {
            "nome": txt_nome.value,
            "tipo_local_sugerido": txt_tipo.value,
            "municipio": txt_municipio.value,
            "uf": txt_uf.value,
            "telefone": txt_telefone.value,
            "whatsapp": txt_whatsapp.value,
            "site": txt_site.value,
            "instagram": txt_instagram.value,
            "facebook": txt_facebook.value,
            "endereco": txt_endereco.value,
            "pontuacao": txt_pontuacao.value,
            "status": ddl_status.value,
            "possivel_duplicidade": chk_duplicidade.value,
            "descartado": chk_descartado.value,
            "observacao_pesquisa": txt_observacao.value,
        }

    def carregar_formulario(id_pesquisa):
        row = obter_pesquisa(id_pesquisa)

        if not row:
            mostrar("Pesquisa web não encontrada.")
            return

        dados = dict(zip(COLUNAS_PESQUISA_WEB, row[1:]))
        pesquisa_id["valor"] = row[0]
        txt_nome.value = dados.get("NomeCasa") or ""
        txt_tipo.value = dados.get("TipoLocalSugerido") or ""
        txt_municipio.value = dados.get("Municipio") or ""
        txt_uf.value = dados.get("UF") or ""
        txt_telefone.value = dados.get("Telefone") or ""
        txt_whatsapp.value = dados.get("WhatsApp") or ""
        txt_site.value = dados.get("Site") or ""
        txt_instagram.value = dados.get("Instagram") or ""
        txt_facebook.value = dados.get("Facebook") or ""
        txt_endereco.value = dados.get("Endereco") or ""
        txt_pontuacao.value = str(dados.get("PontuacaoConfiabilidade") or "")
        ddl_status.value = dados.get("StatusPesquisa") or "PENDENTE_ANALISE"
        chk_duplicidade.value = bool(dados.get("PossivelDuplicidade"))
        chk_descartado.value = bool(dados.get("Descartado"))
        txt_observacao.value = dados.get("ObservacaoPesquisa") or ""
        page.update()

    def salvar(e=None):
        try:
            pesquisa_id["valor"] = salvar_pesquisa(
                pesquisa_id["valor"],
                dados_formulario(),
            )
            carregar_lista()
            mostrar("Pesquisa web salva.")
        except Exception as ex:
            mostrar(str(ex))

    def transferir(id_pesquisa):
        try:
            local_id = transferir_pesquisa_para_local(id_pesquisa)
            carregar_lista()
            mostrar(f"Pesquisa transferida para o local {local_id}.")
        except Exception as ex:
            mostrar(str(ex))

    def criar_linha(row):
        id_pesquisa = row[0]
        transferido = bool(row[8])
        descartado = bool(row[9])

        acoes = [
            ft.IconButton(
                icon=ft.Icons.EDIT,
                tooltip="Editar",
                on_click=lambda e, id=id_pesquisa: carregar_formulario(id),
            ),
        ]

        if modo == "transferencia":
            acoes.append(
                ft.IconButton(
                    icon=ft.Icons.CHECK,
                    tooltip="Transferir para cadastro oficial",
                    on_click=lambda e, id=id_pesquisa: transferir(id),
                )
            )

        return ft.Container(
            padding=8,
            border=ft.border.all(1, ft.Colors.GREY_300),
            border_radius=4,
            content=ft.Row(
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Column(
                        expand=True,
                        spacing=2,
                        controls=[
                            ft.Text(row[1] or "-", weight=ft.FontWeight.BOLD, size=14),
                            ft.Text(f"{row[2] or '-'} / {row[3] or '-'}"),
                            ft.Text(f"Tel: {row[4] or '-'} | Site: {row[5] or '-'}"),
                        ],
                    ),
                    ft.Text(str(row[6] or 0), width=70),
                    ft.Text(row[7] or "-", width=150),
                    ft.Text(
                        "Transferido" if transferido else ("Descartado" if descartado else ""),
                        width=90,
                    ),
                    ft.Row(spacing=0, controls=acoes),
                ],
            ),
        )

    def carregar_lista():
        lista.controls.clear()

        rows = listar_pesquisas(
            apenas_transferiveis=(modo == "transferencia")
        )

        if not rows:
            lista.controls.append(
                ft.Container(
                    padding=12,
                    content=ft.Text("Nenhum registro encontrado."),
                )
            )
        else:
            for row in rows:
                lista.controls.append(criar_linha(row))

        page.update()

    titulo = {
        "pesquisa": "Pesquisa Web de Locais",
        "edicao": "Edição de Locais Pesquisados",
        "transferencia": "Transferência de Locais Pesquisados",
    }.get(modo, "Pesquisa Web de Locais")

    subtitulo = {
        "pesquisa": "Registro e acompanhamento dos locais encontrados em pesquisa web.",
        "edicao": "Revisão e correção dos dados captados antes da transferência.",
        "transferencia": "Somente pesquisas aptas, não descartadas e com pontuação mínima entram aqui.",
    }.get(modo, "")

    limpar_formulario()
    carregar_lista()

    return ft.Column(
        expand=True,
        scroll=ft.ScrollMode.AUTO,
        spacing=10,
        controls=[
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Column(
                        spacing=2,
                        controls=[
                            ft.Text(titulo, size=24, weight=ft.FontWeight.BOLD),
                            ft.Text(subtitulo, size=12, color=ft.Colors.GREY_700),
                        ],
                    ),
                    ft.Row(
                        controls=[
                            ft.OutlinedButton(
                                "Novo",
                                icon=ft.Icons.ADD,
                                on_click=limpar_formulario,
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
                spacing=8,
                run_spacing=8,
                controls=[
                    ft.Container(txt_nome, col={"md": 4}),
                    ft.Container(txt_tipo, col={"md": 3}),
                    ft.Container(txt_municipio, col={"md": 3}),
                    ft.Container(txt_uf, col={"md": 2}),
                    ft.Container(txt_telefone, col={"md": 2}),
                    ft.Container(txt_whatsapp, col={"md": 2}),
                    ft.Container(txt_site, col={"md": 4}),
                    ft.Container(txt_instagram, col={"md": 2}),
                    ft.Container(txt_facebook, col={"md": 2}),
                    ft.Container(txt_endereco, col={"md": 6}),
                    ft.Container(txt_pontuacao, col={"md": 2}),
                    ft.Container(ddl_status, col={"md": 3}),
                    ft.Container(chk_duplicidade, col={"md": 2}),
                    ft.Container(chk_descartado, col={"md": 2}),
                    ft.Container(txt_observacao, col={"md": 12}),
                ],
            ),
            ft.Divider(),
            lista,
        ],
    )


def loc_pesquisa_web_view(page):
    return pesquisa_web_base_view(page, "pesquisa")


def loc_pesquisa_web_edicao_view(page):
    return pesquisa_web_base_view(page, "edicao")


def loc_pesquisa_web_transferencia_view(page):
    return pesquisa_web_base_view(page, "transferencia")
