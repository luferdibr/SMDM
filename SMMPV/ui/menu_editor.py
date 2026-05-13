
import logging

import flet as ft

from ui.dashboard import navegar

from services.menu_editor_service import (

    listar_menus,

    salvar_menu,

    excluir_menu
)

from services.menu_admin_service import (
    get_permissoes_usuario
)


# ==================================================
# CONFIG
# ==================================================

ROOT_LEVEL = 100

ROTAS_PROTEGIDAS = {

    "dashboard",

    "alterar_senha",

    "usuarios",

    "perfis",

    "menu_config"
}


# ==================================================
# HELPERS
# ==================================================

def get_usuario(page):

    usuario = getattr(
        page,
        "usuario_logado",
        None
    )

    if (
        not usuario
        or
        not isinstance(usuario, dict)
    ):
        return None

    return usuario


def exibir_snackbar(
    page,
    mensagem,
    erro=False
):

    page.snack_bar = ft.SnackBar(

        content=ft.Text(
            mensagem
        ),

        bgcolor=(

            ft.Colors.RED_400

            if erro

            else

            ft.Colors.GREEN_600
        ),

        open=True
    )

    page.update()


# ==================================================
# VIEW
# ==================================================

def menu_editor_view(page):

    usuario = get_usuario(page)

    # ==============================================
    # SESSÃO
    # ==============================================

    if not usuario:

        return ft.Container(

            content=ft.Column([

                ft.Icon(
                    ft.Icons.ERROR,
                    size=72,
                    color=ft.Colors.RED
                ),

                ft.Text(
                    "Sessão inválida.",
                    size=24,
                    weight="bold",
                    color=ft.Colors.RED
                )

            ],

                spacing=20,

                horizontal_alignment=(
                    ft.CrossAxisAlignment.CENTER
                )
            ),

            alignment=ft.Alignment(0, 0),

            expand=True
        )

    usuario_level = int(
        usuario.get(
            "admin_level",
            0
        )
    )

    is_root = (
        usuario_level >= ROOT_LEVEL
    )

    # ==============================================
    # PERMISSÕES
    # ==============================================

    permissoes = get_permissoes_usuario(

        usuario,

        "editor_menu"
    )

    if not permissoes.get("ver"):

        return ft.Container(

            content=ft.Column([

                ft.Icon(
                    ft.Icons.LOCK,
                    size=72,
                    color=ft.Colors.RED
                ),

                ft.Text(
                    "Acesso negado.",
                    size=24,
                    weight="bold",
                    color=ft.Colors.RED
                )

            ],

                spacing=20,

                horizontal_alignment=(
                    ft.CrossAxisAlignment.CENTER
                )
            ),

            alignment=ft.Alignment(0, 0),

            expand=True
        )

    pode_editar = bool(
        permissoes.get("editar")
    )

    pode_excluir = bool(
        permissoes.get("excluir")
    )

    carregando = False

    menu_editando = {
        "id": None
    }

    menus_cache = []

    # ==============================================
    # COMPONENTES
    # ==============================================

    txt_filtro = ft.TextField(

        label="Pesquisar",

        width=320,

        prefix_icon=ft.Icons.SEARCH
    )

    txt_nome = ft.TextField(

        label="Nome",

        width=260,

        disabled=not pode_editar
    )

    txt_rota = ft.TextField(

        label="Rota",

        width=260,

        disabled=not pode_editar
    )

    txt_ordem = ft.TextField(

        label="Ordem",

        width=120,

        value="10",

        disabled=not pode_editar
    )

    txt_admin_level = ft.TextField(

        label="Admin Level",

        width=150,

        value="10",

        visible=is_root,

        disabled=not pode_editar
    )

    ddl_tipo = ft.Dropdown(

        label="Tipo",

        width=180,

        value="M",

        disabled=not pode_editar,

        options=[

            ft.dropdown.Option(
                "T",
                "Título"
            ),

            ft.dropdown.Option(
                "S",
                "Submenu"
            ),

            ft.dropdown.Option(
                "M",
                "Menu"
            )
        ]
    )

    ddl_pai = ft.Dropdown(

        label="Menu Pai",

        width=320,

        disabled=not pode_editar
    )

    chk_ativo = ft.Checkbox(

        label="Ativo",

        value=True,

        disabled=not pode_editar
    )

    chk_sistema = ft.Checkbox(

        label="Estrutural",

        value=False,

        visible=is_root,

        disabled=(
            not pode_editar
            or
            not is_root
        )
    )

    txt_status = ft.Text(
        "",
        color=ft.Colors.RED
    )

    progress = ft.ProgressRing(
        visible=False
    )

    lista = ft.Column(
        spacing=6
    )

    # ==============================================
    # BOTÕES
    # ==============================================

    btn_salvar = ft.ElevatedButton(

        "Salvar",

        icon=ft.Icons.SAVE,

        disabled=not pode_editar
    )

    btn_limpar = ft.OutlinedButton(

        "Limpar",

        icon=ft.Icons.CLEAR,

        disabled=not pode_editar
    )

    btn_voltar = ft.ElevatedButton(

        "Voltar",

        icon=ft.Icons.ARROW_BACK
    )

    # ==============================================
    # LOCK UI
    # ==============================================

    def bloquear_ui(status):

        progress.visible = status

        btn_salvar.disabled = (
            status or not pode_editar
        )

        btn_limpar.disabled = (
            status or not pode_editar
        )

        btn_voltar.disabled = status

        txt_nome.disabled = (
            status or not pode_editar
        )

        txt_rota.disabled = (
            status or not pode_editar
        )

        txt_ordem.disabled = (
            status or not pode_editar
        )

        ddl_tipo.disabled = (
            status or not pode_editar
        )

        ddl_pai.disabled = (
            status or not pode_editar
        )

        chk_ativo.disabled = (
            status or not pode_editar
        )

        txt_admin_level.disabled = (

            status

            or

            not pode_editar

            or

            not is_root
        )

        chk_sistema.disabled = (

            status

            or

            not pode_editar

            or

            not is_root
        )

        page.update()

    # ==============================================
    # STATUS
    # ==============================================

    def status(
        texto,
        erro=True
    ):

        txt_status.value = texto

        txt_status.color = (

            ft.Colors.RED

            if erro

            else ft.Colors.GREEN
        )

        page.update()

    # ==============================================
    # PREFIXO
    # ==============================================

    def prefixo(menu):

        if menu["sistema"]:
            return "🔒"

        if menu["tipo"] == "T":
            return "📁"

        if menu["tipo"] == "S":
            return "📂"

        return "📄"

    # ==============================================
    # NÍVEL
    # ==============================================

    def obter_nivel(menu, lookup):

        nivel = 0

        atual = menu

        contador = 0

        while (

            atual.get("pai")
            and
            contador < 30
        ):

            atual = lookup.get(
                atual["pai"]
            )

            if not atual:
                break

            nivel += 1

            contador += 1

        return nivel

    # ==============================================
    # VISUALIZAÇÃO
    # ==============================================

    def pode_visualizar(menu):

        if is_root:
            return True

        if menu["sistema"]:
            return False

        if int(
            menu.get(
                "admin_level",
                0
            )
        ) >= ROOT_LEVEL:

            return False

        return True

    # ==============================================
    # ROTA VISÍVEL
    # ==============================================

    def atualizar_campos_tipo(e=None):

        tipo = ddl_tipo.value

        txt_rota.visible = (
            tipo == "M"
        )

        ddl_pai.visible = (
            tipo != "T"
        )

        page.update()

    ddl_tipo.on_change = (
        atualizar_campos_tipo
    )

    # ==============================================
    # COMBO PAIS
    # ==============================================

    def carregar_combo_pais():

        ddl_pai.options.clear()

        ddl_pai.options.append(

            ft.dropdown.Option(
                "",
                "(Raiz)"
            )
        )

        lookup = {
            m["id"]: m
            for m in menus_cache
        }

        for m in menus_cache:

            if not pode_visualizar(m):
                continue

            if m["tipo"] == "M":
                continue

            if (
                menu_editando["id"]
                and
                m["id"]
                == menu_editando["id"]
            ):
                continue

            nivel = obter_nivel(
                m,
                lookup
            )

            espaco = "   " * nivel

            ddl_pai.options.append(

                ft.dropdown.Option(

                    str(m["id"]),

                    (
                        f"{espaco}"
                        f"{prefixo(m)} "
                        f"{m['nome']}"
                    )
                )
            )

    # ==============================================
    # LIMPAR
    # ==============================================

    def limpar(e=None):

        menu_editando["id"] = None

        txt_nome.value = ""

        txt_rota.value = ""

        txt_ordem.value = "10"

        txt_admin_level.value = "10"

        ddl_tipo.value = "M"

        ddl_pai.value = ""

        chk_ativo.value = True

        chk_sistema.value = False

        txt_status.value = ""

        atualizar_campos_tipo()

        carregar_combo_pais()

        page.update()

    btn_limpar.on_click = limpar

    # ==============================================
    # VOLTAR
    # ==============================================

    def voltar_dashboard(e=None):

        navegar(page, "dashboard")

    btn_voltar.on_click = voltar_dashboard

    # ==============================================
    # VALIDAR
    # ==============================================

    def validar():

        nome = str(

            txt_nome.value or ""

        ).strip()

        if not nome:

            raise Exception(
                "Informe nome."
            )

        tipo = ddl_tipo.value

        rota = str(

            txt_rota.value or ""

        ).strip().lower()

        if tipo == "M":

            if not rota:

                raise Exception(
                    "Informe rota."
                )

        if rota in ROTAS_PROTEGIDAS:

            raise Exception(
                "Rota protegida."
            )

        try:

            ordem = int(
                txt_ordem.value
            )

            if ordem < 0:

                raise Exception()

        except:

            raise Exception(
                "Ordem inválida."
            )

        if is_root:

            try:

                level = int(
                    txt_admin_level.value
                )

                if level < 0:
                    raise Exception()

            except:

                raise Exception(
                    "AdminLevel inválido."
                )

    # ==============================================
    # EDITAR
    # ==============================================

    def editar(menu):

        if not pode_editar:

            exibir_snackbar(

                page,

                "Sem permissão.",

                erro=True
            )

            return

        menu_editando["id"] = menu["id"]

        txt_nome.value = menu["nome"]

        txt_rota.value = (
            menu["rota"] or ""
        )

        txt_ordem.value = str(
            menu["ordem"]
        )

        txt_admin_level.value = str(
            menu.get(
                "admin_level",
                10
            )
        )

        ddl_tipo.value = menu["tipo"]

        ddl_pai.value = (

            str(menu["pai"])

            if menu["pai"]

            else ""
        )

        chk_ativo.value = bool(
            menu["ativo"]
        )

        chk_sistema.value = bool(
            menu["sistema"]
        )

        atualizar_campos_tipo()

        carregar_combo_pais()

        page.update()

    # ==============================================
    # SALVAR
    # ==============================================

    def salvar(e=None):

        nonlocal carregando

        if carregando:
            return

        carregando = True

        bloquear_ui(True)

        try:

            validar()

            tipo = ddl_tipo.value

            rota = None

            if tipo == "M":

                rota = str(

                    txt_rota.value or ""

                ).strip().lower()

            pai = None

            if (
                tipo != "T"
                and
                ddl_pai.value
            ):

                pai = int(
                    ddl_pai.value
                )

            dados = {

                "id": menu_editando["id"],

                "nome": str(

                    txt_nome.value or ""

                ).strip(),

                "rota": rota,

                "pai": pai,

                "ordem": int(
                    txt_ordem.value
                ),

                "ativo": int(
                    bool(
                        chk_ativo.value
                    )
                ),

                "tipo": tipo,

                "sistema": int(
                    bool(
                        chk_sistema.value
                    )
                ),

                "admin_level": (

                    int(
                        txt_admin_level.value
                    )

                    if is_root

                    else 10
                )
            }

            resultado = salvar_menu(

                usuario,

                dados
            )

            if not resultado["sucesso"]:

                raise Exception(
                    resultado["mensagem"]
                )

            limpar()

            carregar()

            exibir_snackbar(

                page,

                resultado["mensagem"]
            )

        except Exception as ex:

            logging.exception(
                "MENU SAVE ERROR"
            )

            status(str(ex))

        finally:

            carregando = False

            bloquear_ui(False)

    btn_salvar.on_click = salvar

    # ==============================================
    # REMOVER
    # ==============================================

    def remover(menu):

        try:

            resultado = excluir_menu(

                usuario,

                menu["id"]
            )

            if not resultado["sucesso"]:

                raise Exception(
                    resultado["mensagem"]
                )

            carregar()

            exibir_snackbar(

                page,

                resultado["mensagem"]
            )

        except Exception as ex:

            logging.exception(
                "MENU DELETE ERROR"
            )

            exibir_snackbar(

                page,

                str(ex),

                erro=True
            )

    # ==============================================
    # GRID
    # ==============================================

    def render_menu(menu):

        sistema = bool(
            menu["sistema"]
        )

        rota_protegida = (
            menu.get("rota")
            in ROTAS_PROTEGIDAS
        )

        cor = None

        if sistema:

            cor = ft.Colors.RED_50

        elif menu["tipo"] == "T":

            cor = ft.Colors.BLUE_50

        elif menu["tipo"] == "S":

            cor = ft.Colors.GREY_100

        controles = []

        # ==========================================
        # EDITAR
        # ==========================================

        if pode_editar:

            controles.append(

                ft.IconButton(

                    icon=ft.Icons.EDIT,

                    tooltip="Editar",

                    disabled=(

                        sistema

                        and

                        not is_root
                    ),

                    on_click=lambda e,
                    x=menu: editar(x)
                )
            )

        # ==========================================
        # DELETE
        # ==========================================

        if pode_excluir:

            controles.append(

                ft.IconButton(

                    icon=ft.Icons.DELETE,

                    tooltip="Desativar",

                    disabled=(

                        sistema

                        or

                        rota_protegida
                    ),

                    on_click=lambda e,
                    x=menu: remover(x)
                )
            )

        return ft.Container(

            content=ft.Row([

                ft.Container(

                    content=ft.Text(

                        (
                            f"{prefixo(menu)} "
                            f"{menu['nome']}"
                        ),

                        weight=(

                            "bold"

                            if menu["tipo"] in [
                                "T",
                                "S"
                            ]

                            else None
                        )
                    ),

                    width=360,

                    padding=ft.padding.only(

                        left=(
                            obter_nivel(

                                menu,

                                {
                                    m["id"]: m
                                    for m in menus_cache
                                }
                            ) * 24
                        )
                    )
                ),

                ft.Text(

                    menu["rota"] or "",

                    width=180
                ),

                ft.Text(

                    menu["tipo"],

                    width=60
                ),

                ft.Text(

                    str(
                        menu.get(
                            "admin_level",
                            0
                        )
                    ),

                    width=80
                ),

                ft.Text(

                    str(
                        menu["ordem"]
                    ),

                    width=60
                ),

                ft.Text(

                    "Ativo"

                    if menu["ativo"]

                    else "Inativo",

                    width=90
                ),

                *controles

            ],

                wrap=True
            ),

            padding=10,

            border=ft.border.all(

                1,

                ft.Colors.GREY_300
            ),

            border_radius=8,

            bgcolor=cor
        )

    # ==============================================
    # CARREGAR
    # ==============================================

    def carregar():

        lista.controls.clear()

        resultado = listar_menus()

        if not resultado["sucesso"]:

            status(
                resultado["mensagem"]
            )

            return

        menus_cache.clear()

        menus_cache.extend(
            resultado["dados"]
        )

        carregar_combo_pais()

        filtro = str(

            txt_filtro.value or ""

        ).strip().upper()

        for menu in menus_cache:

            if not pode_visualizar(menu):
                continue

            texto = (
                f"{menu['nome']} "
                f"{menu.get('rota') or ''}"
            ).upper()

            if filtro:

                if filtro not in texto:
                    continue

            lista.controls.append(
                render_menu(menu)
            )

        page.update()

    txt_filtro.on_change = (
        lambda e: carregar()
    )

    # ==============================================
    # INIT
    # ==============================================

    atualizar_campos_tipo()

    carregar()

    # ==============================================
    # LAYOUT
    # ==============================================

    return ft.Column([

        ft.Row([

            ft.Text(

                "Editor de Menu",

                size=28,

                weight="bold"
            ),

            progress

        ],

            alignment=(
                ft.MainAxisAlignment.SPACE_BETWEEN
            )
        ),

        ft.Divider(),

        txt_filtro,

        ft.Row([

            txt_nome,

            txt_rota

        ],

            wrap=True
        ),

        ft.Row([

            txt_ordem,

            ddl_tipo,

            ddl_pai,

            chk_ativo,

            chk_sistema,

            txt_admin_level

        ],

            wrap=True
        ),

        txt_status,

        ft.Row([

            btn_salvar,

            btn_limpar,

            btn_voltar

        ],

            wrap=True
        ),

        ft.Divider(),

        ft.Container(

            content=ft.Row([

                ft.Text(
                    "Menu",
                    width=360,
                    weight="bold"
                ),

                ft.Text(
                    "Rota",
                    width=180,
                    weight="bold"
                ),

                ft.Text(
                    "Tipo",
                    width=60,
                    weight="bold"
                ),

                ft.Text(
                    "Level",
                    width=80,
                    weight="bold"
                ),

                ft.Text(
                    "Ordem",
                    width=60,
                    weight="bold"
                ),

                ft.Text(
                    "Status",
                    width=90,
                    weight="bold"
                )

            ],

                wrap=True
            ),

            padding=10
        ),

        lista

    ],

        expand=True,

        scroll=ft.ScrollMode.AUTO
    )