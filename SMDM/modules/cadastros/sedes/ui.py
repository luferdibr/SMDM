import flet as ft

import flet as ft

from ui.components.endereco_dialog import abrir_endereco_dialog

from modules.cadastros.sedes.service import (
    COLUNAS,
    excluir_sede,
    listar_sedes,
    obter_sede,
    salvar_sede,
)

from services.documento_service import (
    normalizar_cnpj,
)


def campo(label, width=220, multiline=False):

    return ft.TextField(
        label=label,
        width=width,
        multiline=multiline,
        min_lines=3 if multiline else None,
        max_lines=5 if multiline else None,
    )


def sedes_view(page):

    lista = ft.Column(
        spacing=8,
    )

    sede_editando = {
        "id": None,
    }

    controles = {
        "nome_sede": campo("Nome da sede", 320),
        "cnpj": campo("CNPJ", 180),
        "responsavel": campo("Responsável", 320),
        "telefone": campo("Telefone", 180),
        "celular": campo("Celular", 180),
        "email": campo("E-mail", 300),
        "cep": campo("CEP", 150),
        "logradouro": campo("Endereço", 420),
        "numero": campo("Número", 120),
        "complemento": campo("Complemento", 220),
        "bairro": campo("Bairro", 260),
        "municipio": campo("Cidade", 260),
        "uf": campo("Estado", 100),
        "pais": campo("País", 180),
        "observacoes": campo("Observações", 760, True),
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

    chk_operacional = ft.Checkbox(
        label="Operacional",
        value=True,
    )

    chk_fantasma = ft.Checkbox(
        label="Sede fantasma",
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

    def validar_cnpj_sede(e=None):

        controles["cnpj"].error = None

        try:
            normalizar_cnpj(
                controles["cnpj"].value,
            )
        except Exception as ex:
            controles["cnpj"].error = str(ex)
            page.update()
            return False

        if e:
            page.update()

        return True

    controles["cnpj"].on_blur = validar_cnpj_sede

    def dados_formulario():

        dados = {
            chave: controle.value
            for chave, controle in controles.items()
        }

        dados["operacional"] = chk_operacional.value
        dados["fantasma"] = chk_fantasma.value
        dados["ativo"] = chk_ativo.value
        dados.update(geo_endereco)

        return dados

    def limpar(e=None):

        sede_editando["id"] = None

        for controle in controles.values():
            controle.value = ""

        controles["uf"].value = "RS"
        controles["pais"].value = "Brasil"
        controles["cnpj"].error = None
        chk_operacional.value = True
        chk_fantasma.value = False
        chk_ativo.value = True
        geo_endereco["latitude"] = None
        geo_endereco["longitude"] = None
        geo_endereco["fonte_geo"] = None
        geo_endereco["data_geo"] = None
        atualizar_status_geo()

        page.update()

    def carregar(atualizar=True):

        lista.controls.clear()

        sedes = listar_sedes()

        if not sedes:

            lista.controls.append(
                ft.Container(
                    padding=16,
                    content=ft.Text(
                        "Nenhuma sede cadastrada"
                    ),
                )
            )

            if atualizar:
                page.update()

            return

        for sede in sedes:

            sede_id = sede[0]
            nome = sede[1] or ""
            municipio = sede[2] or ""
            uf = sede[3] or ""
            cep = sede[4] or ""
            responsavel = sede[5] or ""
            celular = sede[6] or ""
            operacional = bool(sede[7])
            fantasma = bool(sede[8])
            ativo = bool(sede[9])

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
                                    ft.Text(nome, size=15, weight=ft.FontWeight.BOLD),
                                    ft.Text(f"{municipio or '-'} / {uf or '-'} | CEP: {cep or '-'}", size=12),
                                    ft.Text(
                                        f"Responsável: {responsavel or '-'} | Celular: {celular or '-'}",
                                        size=12,
                                        color=ft.Colors.GREY_700,
                                    ),
                                ],
                            ),
                            ft.Text("FANTASMA" if fantasma else ("OPERACIONAL" if operacional else "APOIO"), size=11),
                            ft.Text("ATIVA" if ativo else "INATIVA", size=11),
                            ft.IconButton(
                                icon=ft.Icons.EDIT,
                                tooltip="Editar",
                                on_click=lambda e, id=sede_id: editar(id),
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE,
                                tooltip="Excluir",
                                on_click=lambda e, id=sede_id: excluir(e, id),
                            ),
                        ],
                    ),
                )
            )

        if atualizar:
            page.update()

    def editar(sede_id):

        row = obter_sede(
            sede_id
        )

        if not row:
            return

        sede_editando["id"] = row[0]

        dados = dict(
            zip(
                COLUNAS,
                row[1:],
            )
        )

        mapa = {
            "NomeSede": "nome_sede",
            "CNPJ": "cnpj",
            "Responsavel": "responsavel",
            "Telefone": "telefone",
            "Celular": "celular",
            "Email": "email",
            "CEP": "cep",
            "Logradouro": "logradouro",
            "Numero": "numero",
            "Complemento": "complemento",
            "Bairro": "bairro",
            "Municipio": "municipio",
            "UF": "uf",
            "Pais": "pais",
            "Observacoes": "observacoes",
        }

        for coluna, chave in mapa.items():
            controles[chave].value = dados.get(coluna) or ""

        geo_endereco["latitude"] = dados.get("Latitude")
        geo_endereco["longitude"] = dados.get("Longitude")
        geo_endereco["fonte_geo"] = dados.get("FonteGeo")
        geo_endereco["data_geo"] = dados.get("DataGeo")
        atualizar_status_geo()

        chk_operacional.value = bool(
            dados.get("Operacional")
        )

        chk_fantasma.value = bool(
            dados.get("Fantasma")
        )

        chk_ativo.value = bool(
            dados.get("Ativo")
        )

        page.update()

    def excluir(e, sede_id):

        try:

            excluir_sede(
                sede_id
            )

            carregar(False)

            limpar()

            mostrar_mensagem(
                "Sede removida"
            )

        except Exception as ex:
            mostrar_mensagem(str(ex))

    def salvar(e=None):

        try:
            if not validar_cnpj_sede():
                mostrar_mensagem("Corrija os campos destacados.")
                return


            resultado = salvar_sede(
                sede_editando["id"],
                dados_formulario(),
            )
            geo_erro = ""

            if isinstance(resultado, dict):
                geo_erro = resultado.get("geo_erro") or ""

            carregar(False)

            limpar()

            if geo_erro:
                mostrar_mensagem(
                    f"Sede salva. Localização não gerada: {geo_erro}"
                )
            else:
                mostrar_mensagem(
                    "Sede salva"
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
                    ft.Text("Cadastro de Sedes", size=24, weight=ft.FontWeight.BOLD),
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
            bloco("Sede", [
                controles["nome_sede"],
                controles["cnpj"],
                controles["responsavel"],
                controles["telefone"],
                controles["celular"],
                controles["email"],
                chk_operacional,
                chk_fantasma,
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
            bloco("Observações", [
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
