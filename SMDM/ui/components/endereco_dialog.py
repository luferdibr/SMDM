import flet as ft

import flet as ft

from services.endereco_service import (
    buscar_cep,
    geocodificar_endereco,
    montar_texto_endereco,
    pesquisar_endereco,
)


def abrir_endereco_dialog(page, valores=None, on_confirm=None):

    valores = valores or {}
    resultados = []
    geo = {
        "latitude": valores.get("latitude"),
        "longitude": valores.get("longitude"),
        "fonte_geo": valores.get("fonte_geo") or valores.get("fonte"),
        "data_geo": valores.get("data_geo"),
        "endereco_geo": montar_texto_endereco(valores),
    }

    txt_cep = ft.TextField(
        label="CEP",
        value=valores.get("cep") or "",
        width=150,
    )

    txt_logradouro = ft.TextField(
        label="Endereço",
        value=valores.get("logradouro") or "",
        width=420,
    )

    txt_numero = ft.TextField(
        label="Número",
        value=valores.get("numero") or "",
        width=120,
    )

    txt_complemento = ft.TextField(
        label="Complemento",
        value=valores.get("complemento") or "",
        width=220,
    )

    txt_bairro = ft.TextField(
        label="Bairro",
        value=valores.get("bairro") or "",
        width=260,
    )

    txt_municipio = ft.TextField(
        label="Cidade",
        value=valores.get("municipio") or valores.get("cidade") or "",
        width=260,
    )

    txt_uf = ft.TextField(
        label="Estado",
        value=valores.get("uf") or valores.get("estado") or "RS",
        width=100,
        max_length=2,
    )

    txt_pais = ft.TextField(
        label="País",
        value=valores.get("pais") or "Brasil",
        width=180,
    )

    txt_pesquisa = ft.TextField(
        label="Pesquisar por endereço",
        hint_text="Rua, cidade, UF",
        width=520,
    )

    lbl_status = ft.Text(
        "",
        color=ft.Colors.RED_600,
        size=12,
    )

    lbl_geo = ft.Text(
        "",
        color=ft.Colors.GREY_700,
        size=12,
    )

    txt_latitude = ft.TextField(
        label="Latitude",
        value=str(valores.get("latitude") or ""),
        width=180,
    )

    txt_longitude = ft.TextField(
        label="Longitude",
        value=str(valores.get("longitude") or ""),
        width=180,
    )

    ddl_resultados = ft.Dropdown(
        label="Resultados encontrados",
        width=620,
        visible=False,
        options=[],
    )

    def preencher(endereco):

        txt_cep.value = endereco.get("cep") or txt_cep.value
        txt_logradouro.value = endereco.get("logradouro") or txt_logradouro.value
        txt_complemento.value = endereco.get("complemento") or txt_complemento.value
        txt_bairro.value = endereco.get("bairro") or txt_bairro.value
        txt_municipio.value = endereco.get("municipio") or txt_municipio.value
        txt_uf.value = endereco.get("uf") or txt_uf.value
        txt_pais.value = endereco.get("pais") or "Brasil"
        limpar_geo()

    def limpar_geo():

        geo["latitude"] = None
        geo["longitude"] = None
        geo["fonte_geo"] = None
        geo["data_geo"] = None
        geo["endereco_geo"] = None
        txt_latitude.value = ""
        txt_longitude.value = ""
        lbl_geo.value = ""

    def normalizar_float(valor, campo, minimo, maximo):

        valor = str(valor or "").strip().replace(",", ".")

        if not valor:
            return None

        try:
            numero = float(valor)
        except Exception as ex:
            raise Exception(f"{campo} inválida.") from ex

        if numero < minimo or numero > maximo:
            raise Exception(
                f"{campo} deve estar entre {minimo} e {maximo}."
            )

        return numero

    def aplicar_coordenadas_manuais():

        txt_latitude.error = None
        txt_longitude.error = None

        latitude = normalizar_float(
            txt_latitude.value,
            "Latitude",
            -90,
            90,
        )
        longitude = normalizar_float(
            txt_longitude.value,
            "Longitude",
            -180,
            180,
        )

        if (latitude is None) != (longitude is None):
            raise Exception(
                "Informe latitude e longitude, ou deixe ambas vazias."
            )

        if latitude is None:
            geo["latitude"] = None
            geo["longitude"] = None
            geo["fonte_geo"] = None
            geo["data_geo"] = None
            geo["endereco_geo"] = None
            lbl_geo.value = ""
            return

        geo["latitude"] = latitude
        geo["longitude"] = longitude
        geo["fonte_geo"] = "manual"
        geo["data_geo"] = None
        geo["endereco_geo"] = montar_texto_endereco(
            dados_atualizados()
        )
        lbl_geo.value = (
            f"Localização: {latitude}, {longitude} (manual)"
        )

    def dados_atualizados():

        return {
            "cep": txt_cep.value,
            "logradouro": txt_logradouro.value,
            "numero": txt_numero.value,
            "complemento": txt_complemento.value,
            "bairro": txt_bairro.value,
            "municipio": txt_municipio.value,
            "uf": txt_uf.value,
            "pais": txt_pais.value,
            "latitude": geo.get("latitude"),
            "longitude": geo.get("longitude"),
            "fonte_geo": geo.get("fonte_geo"),
            "data_geo": geo.get("data_geo"),
        }

    def endereco_mudou():

        endereco_geo = geo.get("endereco_geo")

        if not endereco_geo:
            return False

        return montar_texto_endereco(dados_atualizados()) != endereco_geo

    def mostrar_erro(texto):

        lbl_status.value = texto
        page.update()

    def gerar_localizacao(e=None):

        try:
            endereco = geocodificar_endereco(
                dados_atualizados()
            )
            geo["latitude"] = endereco.get("latitude")
            geo["longitude"] = endereco.get("longitude")
            geo["fonte_geo"] = endereco.get("fonte")
            geo["data_geo"] = endereco.get("data_geo")
            txt_latitude.value = str(geo["latitude"] or "")
            txt_longitude.value = str(geo["longitude"] or "")
            geo["endereco_geo"] = montar_texto_endereco(
                dados_atualizados()
            )
            lbl_geo.value = (
                f"Localização: {geo['latitude']}, {geo['longitude']} "
                f"({geo['fonte_geo']})"
            )
            lbl_status.value = "Localização gerada. Confira e aplique."
            lbl_status.color = ft.Colors.GREEN_700
        except Exception as ex:
            lbl_status.value = str(ex)
            lbl_status.color = ft.Colors.RED_600

        page.update()

    def buscar_por_cep(e=None):

        try:
            endereco = buscar_cep(txt_cep.value)
            preencher(endereco)
            ddl_resultados.visible = False
            lbl_status.value = "Endereço preenchido pelo CEP."
            lbl_status.color = ft.Colors.GREEN_700
        except Exception as ex:
            lbl_status.value = str(ex)
            lbl_status.color = ft.Colors.RED_600

        page.update()

    def pesquisar(e=None):

        nonlocal resultados

        try:
            resultados = pesquisar_endereco(
                logradouro=txt_logradouro.value,
                municipio=txt_municipio.value,
                uf=txt_uf.value,
                texto=txt_pesquisa.value,
            )

            ddl_resultados.options = []

            for indice, endereco in enumerate(resultados):
                descricao = (
                    f"{endereco.get('logradouro') or '-'}, "
                    f"{endereco.get('bairro') or '-'} - "
                    f"{endereco.get('municipio') or '-'} / "
                    f"{endereco.get('uf') or '-'} "
                    f"CEP {endereco.get('cep') or '-'}"
                )
                ddl_resultados.options.append(
                    ft.dropdown.Option(
                        str(indice),
                        descricao,
                    )
                )

            if resultados:
                ddl_resultados.value = "0"
                ddl_resultados.visible = True
                preencher(resultados[0])
                lbl_status.value = "Confira o resultado e aplique."
                lbl_status.color = ft.Colors.GREEN_700
            else:
                ddl_resultados.visible = False
                lbl_status.value = "Nenhum endereço encontrado."
                lbl_status.color = ft.Colors.RED_600

        except Exception as ex:
            lbl_status.value = str(ex)
            lbl_status.color = ft.Colors.RED_600

        page.update()

    def usar_resultado(e=None):

        if not ddl_resultados.value:
            mostrar_erro("Selecione um resultado.")
            return

        indice = int(ddl_resultados.value)

        if indice < 0 or indice >= len(resultados):
            mostrar_erro("Resultado inválido.")
            return

        preencher(resultados[indice])
        lbl_status.value = "Resultado aplicado."
        lbl_status.color = ft.Colors.GREEN_700
        page.update()

    def fechar(e=None):

        dlg.open = False
        page.update()

    def aplicar(e=None):

        try:
            aplicar_coordenadas_manuais()
        except Exception as ex:
            lbl_status.value = str(ex)
            lbl_status.color = ft.Colors.RED_600
            page.update()
            return

        if endereco_mudou() and not (
            geo.get("latitude")
            and geo.get("longitude")
        ):
            limpar_geo()

        if on_confirm:
            on_confirm(dados_atualizados())

        fechar()

    dlg = ft.AlertDialog(
        modal=True,
        title=ft.Text("Endereço"),
        content=ft.Container(
            width=700,
            content=ft.Column(
                tight=True,
                spacing=10,
                controls=[
                    ft.Row(
                        controls=[
                            txt_cep,
                            ft.ElevatedButton(
                                "Buscar CEP",
                                icon=ft.Icons.SEARCH,
                                on_click=buscar_por_cep,
                            ),
                        ],
                    ),
                    ft.Row(
                        controls=[
                            txt_pesquisa,
                            ft.OutlinedButton(
                                "Pesquisar",
                                icon=ft.Icons.MANAGE_SEARCH,
                                on_click=pesquisar,
                            ),
                        ],
                    ),
                    ddl_resultados,
                    ft.Row(
                        controls=[
                            ft.OutlinedButton(
                                "Usar resultado",
                                icon=ft.Icons.CHECK,
                                on_click=usar_resultado,
                            ),
                        ],
                    ),
                    ft.ResponsiveRow(
                        controls=[
                            ft.Container(txt_logradouro, col={"md": 6}),
                            ft.Container(txt_numero, col={"md": 2}),
                            ft.Container(txt_complemento, col={"md": 4}),
                            ft.Container(txt_bairro, col={"md": 3}),
                            ft.Container(txt_municipio, col={"md": 3}),
                            ft.Container(txt_uf, col={"md": 2}),
                            ft.Container(txt_pais, col={"md": 3}),
                        ],
                    ),
                    ft.Row(
                        controls=[
                            ft.OutlinedButton(
                                "Gerar localização",
                                icon=ft.Icons.MY_LOCATION,
                                on_click=gerar_localizacao,
                            ),
                            lbl_geo,
                        ],
                    ),
                    ft.Row(
                        controls=[
                            txt_latitude,
                            txt_longitude,
                        ],
                    ),
                    lbl_status,
                ],
            ),
        ),
        actions=[
            ft.TextButton("Cancelar", on_click=fechar),
            ft.ElevatedButton("Aplicar no cadastro", icon=ft.Icons.CHECK, on_click=aplicar),
        ],
    )

    page.overlay.append(dlg)
    dlg.open = True
    page.update()
