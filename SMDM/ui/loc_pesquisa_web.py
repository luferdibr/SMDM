import threading

import flet as ft

from services.local_pesquisa_web_service import (
    COLUNAS_PESQUISA_WEB,
    STATUS_PESQUISA,
    carregar_termos_pesquisa_web,
    coletar_locais_web_fluxo,
    listar_pesquisas,
    listar_municipios_prioritarios_sedes,
    listar_ultimas_pesquisas,
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
    ultimos_pesquisados = ft.Column(spacing=4)
    pesquisa_estado = {
        "rodando": False,
        "parar": False,
    }
    municipios_rs = listar_municipios_prioritarios_sedes()
    termos_pesquisa = carregar_termos_pesquisa_web()

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
    ddl_municipio_coleta = ft.Dropdown(
        label="Município RS",
        width=260,
        options=[
            ft.dropdown.Option(municipio)
            for municipio in municipios_rs
        ],
    )
    ddl_termo_coleta = ft.Dropdown(
        label="Termo de busca",
        width=300,
        value=termos_pesquisa[0] if termos_pesquisa else None,
        options=[
            ft.dropdown.Option(termo)
            for termo in termos_pesquisa
        ],
    )
    txt_limite_coleta = campo("Limite", 90)
    txt_limite_coleta.value = "5"
    lbl_status_coleta = ft.Text(
        "Pesquisa parada.",
        size=12,
        color=ft.Colors.GREY_700,
    )
    indicador_coleta = ft.Container(
        width=12,
        height=12,
        border_radius=6,
        bgcolor=ft.Colors.GREY_400,
        tooltip="Pesquisa parada",
    )
    lbl_indicador_coleta = ft.Text(
        "PARADO",
        size=12,
        weight=ft.FontWeight.BOLD,
        color=ft.Colors.GREY_700,
    )
    btn_start_stop = ft.ElevatedButton(
        "Start",
        icon=ft.Icons.PLAY_ARROW,
    )
    ddl_status = dropdown_status()
    chk_duplicidade = ft.Checkbox(label="Possível duplicidade")
    chk_descartado = ft.Checkbox(label="Descartado")
    txt_observacao = campo("Observação da pesquisa", 700, True)

    def mostrar(texto):
        page.snack_bar = ft.SnackBar(ft.Text(texto))
        page.snack_bar.open = True
        page.update()

    def atualizar_controles_coleta():
        if pesquisa_estado["rodando"]:
            btn_start_stop.text = "Stop"
            btn_start_stop.icon = ft.Icons.STOP
            btn_start_stop.bgcolor = ft.Colors.RED_600
            btn_start_stop.color = ft.Colors.WHITE
            indicador_coleta.bgcolor = ft.Colors.GREEN_600
            indicador_coleta.tooltip = "Pesquisa em execução"
            lbl_indicador_coleta.value = "RODANDO"
            lbl_indicador_coleta.color = ft.Colors.GREEN_700
            lbl_status_coleta.value = "Pesquisa em execução."
            ddl_municipio_coleta.disabled = True
            ddl_termo_coleta.disabled = True
            txt_limite_coleta.disabled = True
        else:
            btn_start_stop.text = "Start"
            btn_start_stop.icon = ft.Icons.PLAY_ARROW
            btn_start_stop.bgcolor = None
            btn_start_stop.color = None
            indicador_coleta.bgcolor = ft.Colors.GREY_400
            indicador_coleta.tooltip = "Pesquisa parada"
            lbl_indicador_coleta.value = "PARADO"
            lbl_indicador_coleta.color = ft.Colors.GREY_700
            ddl_municipio_coleta.disabled = False
            ddl_termo_coleta.disabled = False
            txt_limite_coleta.disabled = False

    def atualizar_ultimos_pesquisados():
        ultimos_pesquisados.controls.clear()
        rows = listar_ultimas_pesquisas(5)

        if not rows:
            ultimos_pesquisados.controls.append(
                ft.Text(
                    "Nenhum local gravado na tabela de pesquisa.",
                    size=12,
                    color=ft.Colors.GREY_600,
                )
            )
            return

        for row in rows:
            status = str(row[5] or "-")
            cor_status = ft.Colors.GREY_600

            if status == "APTO_TRANSFERENCIA":
                cor_status = ft.Colors.GREEN_700
            elif status == "NAO_SERVE":
                cor_status = ft.Colors.RED_700
            elif status == "PONTUACAO_BAIXA":
                cor_status = ft.Colors.ORANGE_700

            ultimos_pesquisados.controls.append(
                ft.Container(
                    padding=ft.padding.symmetric(vertical=2),
                    content=ft.Row(
                        spacing=6,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Container(
                                width=8,
                                height=8,
                                border_radius=4,
                                bgcolor=cor_status,
                            ),
                            ft.Text(
                                str(row[1] or "-"),
                                expand=True,
                                size=12,
                                no_wrap=True,
                            ),
                            ft.Text(
                                f"{row[2] or '-'} / {row[3] or '-'}",
                                width=145,
                                size=12,
                                color=ft.Colors.GREY_700,
                                no_wrap=True,
                            ),
                            ft.Text(
                                str(row[4] or 0),
                                width=40,
                                size=11,
                                color=ft.Colors.GREY_700,
                            ),
                            ft.Text(
                                status,
                                width=120,
                                size=10,
                                color=cor_status,
                                no_wrap=True,
                            ),
                        ],
                    ),
                )
            )

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
            atualizar_ultimos_pesquisados()
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

    def pesquisar_fluxo_background(municipio, termo, limite):
        try:
            def deve_parar():
                return bool(pesquisa_estado["parar"])

            def ao_pesquisar(item):
                if item.get("status") == "INCLUIDO":
                    atualizar_ultimos_pesquisados()
                    page.update()

            resultado = coletar_locais_web_fluxo(
                municipio=municipio,
                uf="RS",
                termos=[termo],
                limite_por_termo=limite,
                deve_parar=deve_parar,
                ao_pesquisar=ao_pesquisar,
            )

            carregar_lista()

            if resultado.get("interrompido"):
                lbl_status_coleta.value = (
                    "Pesquisa interrompida: "
                    f"{resultado['inseridos']} incluído(s), "
                    f"{resultado['ignorados']} ignorado(s)."
                )
            else:
                lbl_status_coleta.value = (
                    "Pesquisa concluída: "
                    f"{resultado['inseridos']} incluído(s), "
                    f"{resultado['ignorados']} ignorado(s)."
                )
        except Exception as ex:
            lbl_status_coleta.value = str(ex)
        finally:
            pesquisa_estado["rodando"] = False
            pesquisa_estado["parar"] = False
            atualizar_controles_coleta()
            page.update()

    def alternar_pesquisa(e=None):
        if pesquisa_estado["rodando"]:
            pesquisa_estado["parar"] = True
            lbl_status_coleta.value = "Parando pesquisa..."
            page.update()
            return

        municipio = (
            ddl_municipio_coleta.value
            or txt_municipio.value
        )
        termo = ddl_termo_coleta.value

        if not municipio:
            mostrar("Informe o município para pesquisar.")
            return

        if not termo:
            mostrar("Selecione um termo de busca.")
            return

        pesquisa_estado["rodando"] = True
        pesquisa_estado["parar"] = False
        atualizar_controles_coleta()
        atualizar_ultimos_pesquisados()
        page.update()

        threading.Thread(
            target=pesquisar_fluxo_background,
            args=(
                municipio,
                termo,
                txt_limite_coleta.value,
            ),
            daemon=True,
        ).start()

    btn_start_stop.on_click = alternar_pesquisa

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
    atualizar_ultimos_pesquisados()
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
                    ft.Container(ddl_municipio_coleta, col={"md": 3}),
                    ft.Container(ddl_termo_coleta, col={"md": 4}),
                    ft.Container(txt_limite_coleta, col={"md": 1}),
                    ft.Container(
                        btn_start_stop,
                        col={"md": 1},
                    ),
                    ft.Container(
                        ft.Row(
                            spacing=6,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                indicador_coleta,
                                lbl_indicador_coleta,
                            ],
                        ),
                        col={"md": 2},
                    ),
                    ft.Container(lbl_status_coleta, col={"md": 2}),
                ],
            ),
            ft.Container(
                padding=8,
                border=ft.border.all(1, ft.Colors.GREY_200),
                border_radius=4,
                content=ft.Column(
                    spacing=4,
                    controls=[
                        ft.Text(
                            "Últimos 5 pesquisados",
                            size=13,
                            weight=ft.FontWeight.BOLD,
                        ),
                        ultimos_pesquisados,
                    ],
                ),
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
