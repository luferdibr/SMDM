import flet as ft

from modules.cadastros.figurinos.service import (
    COLUNAS,
    DISPONIBILIDADES,
    excluir_figurino,
    formatar_data,
    listar_atores,
    listar_figurinos,
    listar_sedes,
    obter_figurino,
    salvar_figurino,
)


def campo(label, width=220, multiline=False):
    return ft.TextField(
        label=label,
        width=width,
        multiline=multiline,
        min_lines=3 if multiline else None,
        max_lines=5 if multiline else None,
    )


def figurinos_view(page):
    lista = ft.Column(
        spacing=6,
    )

    figurino_editando = {
        "id": None,
    }

    txt_nome_longo = campo(
        "Nome longo",
        420,
    )

    txt_nome_curto = campo(
        "Nome curto",
        220,
    )

    txt_data_aquisicao = campo(
        "Data aquisição",
        160,
    )

    txt_data_ultimo_uso = campo(
        "Data último uso",
        160,
    )

    txt_observacoes = campo(
        "Observações",
        760,
        True,
    )

    txt_filtro = campo(
        "Pesquisar",
        280,
    )

    ddl_sede = ft.Dropdown(
        label="Sede",
        width=280,
    )

    ddl_disponibilidade = ft.Dropdown(
        label="Disponibilidade",
        width=220,
        value="DISPONIVEL",
        options=[
            ft.dropdown.Option(
                key=item,
                text=item.replace(
                    "_",
                    " ",
                ).title(),
            )
            for item in DISPONIBILIDADES
        ],
    )

    ddl_ator = ft.Dropdown(
        label="Ator do último uso",
        width=320,
    )

    chk_ativo = ft.Checkbox(
        label="Ativo",
        value=True,
    )

    def mostrar_mensagem(texto):
        page.snack_bar = ft.SnackBar(
            ft.Text(texto)
        )
        page.snack_bar.open = True
        page.update()

    def carregar_sedes_atores():
        ddl_sede.options = [
            ft.dropdown.Option(
                key="",
                text="Sem sede",
            )
        ]

        ddl_sede.options.extend([
            ft.dropdown.Option(
                key=str(row[0]),
                text=str(row[1]),
            )
            for row in listar_sedes()
        ])

        ddl_ator.options = [
            ft.dropdown.Option(
                key="",
                text="Sem ator",
            )
        ]

        ddl_ator.options.extend([
            ft.dropdown.Option(
                key=str(row[0]),
                text=str(row[1]),
            )
            for row in listar_atores()
        ])

    def dados_formulario():
        return {
            "nome_longo": txt_nome_longo.value,
            "nome_curto": txt_nome_curto.value,
            "data_aquisicao": txt_data_aquisicao.value,
            "sede_id": ddl_sede.value,
            "disponibilidade": ddl_disponibilidade.value,
            "data_ultimo_uso": txt_data_ultimo_uso.value,
            "ultimo_ator_id": ddl_ator.value,
            "observacoes": txt_observacoes.value,
            "ativo": chk_ativo.value,
        }

    def limpar(e=None):
        figurino_editando["id"] = None

        txt_nome_longo.value = ""
        txt_nome_curto.value = ""
        txt_data_aquisicao.value = ""
        ddl_sede.value = ""
        ddl_disponibilidade.value = "DISPONIVEL"
        txt_data_ultimo_uso.value = ""
        ddl_ator.value = ""
        txt_observacoes.value = ""
        chk_ativo.value = True

        page.update()

    def carregar(atualizar=True):
        lista.controls.clear()

        figurinos = listar_figurinos(
            txt_filtro.value
        )

        if not figurinos:
            lista.controls.append(
                ft.Container(
                    padding=16,
                    content=ft.Text(
                        "Nenhum figurino cadastrado"
                    ),
                )
            )

            if atualizar:
                page.update()

            return

        for row in figurinos:
            figurino_id = row[0]
            nome_longo = row[1] or ""
            nome_curto = row[2] or ""
            sede = row[3] or ""
            disponibilidade = row[4] or ""
            data_ultimo_uso = formatar_data(row[5])
            ator = row[6] or ""
            ativo = bool(row[7])

            lista.controls.append(
                ft.Container(
                    padding=10,
                    border=ft.border.all(
                        1,
                        ft.Colors.GREY_300,
                    ),
                    border_radius=6,
                    content=ft.Row(
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Column(
                                spacing=1,
                                expand=True,
                                controls=[
                                    ft.Text(
                                        nome_longo,
                                        size=15,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    ft.Text(
                                        f"{nome_curto or '-'} | Sede: {sede or '-'} | {disponibilidade}",
                                        size=12,
                                    ),
                                    ft.Text(
                                        f"Último uso: {data_ultimo_uso or '-'} | Ator: {ator or '-'}",
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
                                on_click=lambda e, id=figurino_id: editar(id),
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE,
                                tooltip="Excluir",
                                on_click=lambda e, id=figurino_id: excluir(e, id),
                            ),
                        ],
                    ),
                )
            )

        if atualizar:
            page.update()

    def editar(figurino_id):
        row = obter_figurino(
            figurino_id
        )

        if not row:
            return

        figurino_editando["id"] = row[0]

        dados = dict(
            zip(
                COLUNAS,
                row[1:],
            )
        )

        txt_nome_longo.value = dados.get("NomeLongo") or ""
        txt_nome_curto.value = dados.get("NomeCurto") or ""
        txt_data_aquisicao.value = formatar_data(
            dados.get("DataAquisicao")
        )
        ddl_sede.value = (
            str(dados.get("SedeID"))
            if dados.get("SedeID")
            else ""
        )
        ddl_disponibilidade.value = (
            dados.get("Disponibilidade")
            or "DISPONIVEL"
        )
        txt_data_ultimo_uso.value = formatar_data(
            dados.get("DataUltimoUso")
        )
        ddl_ator.value = (
            str(dados.get("UltimoAtorID"))
            if dados.get("UltimoAtorID")
            else ""
        )
        txt_observacoes.value = dados.get("Observacoes") or ""
        chk_ativo.value = bool(dados.get("Ativo"))

        page.update()

    def excluir(e, figurino_id):
        try:
            excluir_figurino(
                figurino_id
            )
            carregar(False)
            limpar()
            mostrar_mensagem(
                "Figurino removido"
            )
        except Exception as ex:
            mostrar_mensagem(str(ex))

    def salvar(e=None):
        try:
            salvar_figurino(
                figurino_editando["id"],
                dados_formulario(),
            )
            carregar(False)
            limpar()
            mostrar_mensagem(
                "Figurino salvo"
            )
        except Exception as ex:
            mostrar_mensagem(str(ex))

    def bloco(titulo, itens):
        return ft.Column(
            spacing=8,
            controls=[
                ft.Text(
                    titulo,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.ResponsiveRow(
                    controls=[
                        ft.Container(
                            item,
                            col={"md": 3},
                        )
                        for item in itens
                    ],
                ),
            ],
        )

    txt_filtro.on_change = lambda e: carregar()

    carregar_sedes_atores()
    carregar(False)

    return ft.Column(
        expand=True,
        scroll=ft.ScrollMode.AUTO,
        spacing=10,
        controls=[
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Text(
                        "Cadastro de Figurinos",
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
            bloco("Identificação", [
                txt_nome_longo,
                txt_nome_curto,
                txt_data_aquisicao,
                ddl_sede,
                ddl_disponibilidade,
                chk_ativo,
            ]),
            bloco("Último uso", [
                txt_data_ultimo_uso,
                ddl_ator,
            ]),
            ft.Text(
                "Data do último uso e ator serão atualizados pela conclusão do evento.",
                size=12,
                color=ft.Colors.GREY_700,
            ),
            bloco("Observações", [
                txt_observacoes,
            ]),
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
            txt_filtro,
            lista,
        ],
    )
