
import logging

import flet as ft

from ui.dashboard import navegar

from services.perfil_service import (

    listar_perfis,

    criar_perfil,

    atualizar_perfil,

    excluir_perfil
)

from services.menu_admin_service import (

    copiar_permissoes,

    get_permissoes_usuario
)


# ==================================================
# CONFIG
# ==================================================

ROOT_LEVEL = 100


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

def perfis_view(page):

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

        "perfis"
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

    perfil_editando = {
        "id": None
    }

    perfis_cache = []

    # ==============================================
    # COMPONENTES
    # ==============================================

    txt_filtro = ft.TextField(

        label="Pesquisar",

        width=320,

        prefix_icon=ft.Icons.SEARCH
    )

    txt_nome = ft.TextField(

        label="Nome Perfil",

        width=260,

        disabled=not pode_editar
    )

    txt_validade = ft.TextField(

        label="Validade Senha (dias)",

        width=180,

        disabled=not pode_editar
    )

    txt_admin = ft.TextField(

        label="Admin Level",

        width=160,

        value="10",

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

        disabled=(
            not pode_editar
            or
            not is_root
        )
    )

    ddl_copiar = ft.Dropdown(

        label="Copiar permissões de",

        width=320,

        disabled=not pode_editar
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
    # UI LOCK
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

        txt_validade.disabled = (
            status or not pode_editar
        )

        txt_admin.disabled = (
            status or not pode_editar
        )

        chk_ativo.disabled = (
            status or not pode_editar
        )

        chk_sistema.disabled = (

            status

            or

            not pode_editar

            or

            not is_root
        )

        ddl_copiar.disabled = (
            status or not pode_editar
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
    # VOLTAR
    # ==============================================

    def voltar_dashboard(e=None):

        navegar(page, "dashboard")

    btn_voltar.on_click = voltar_dashboard

    # ==============================================
    # VISIBILIDADE
    # ==============================================

    def pode_visualizar(p):

        if is_root:
            return True

        if p.get("sistema"):
            return False

        if int(
            p.get(
                "admin_level",
                0
            )
        ) >= usuario_level:

            return False

        return True

    # ==============================================
    # LIMPAR
    # ==============================================

    def limpar(e=None):

        perfil_editando["id"] = None

        txt_nome.value = ""

        txt_validade.value = ""

        txt_admin.value = "10"

        chk_ativo.value = True

        chk_sistema.value = False

        ddl_copiar.value = None

        txt_status.value = ""

        page.update()

    btn_limpar.on_click = limpar

    # ==============================================
    # EDITAR
    # ==============================================

    def editar(p):

        if not pode_editar:

            exibir_snackbar(

                page,

                "Sem permissão.",

                erro=True
            )

            return

        perfil_editando["id"] = p["id"]

        txt_nome.value = str(
            p["nome"]
        ).strip()

        txt_validade.value = str(

            p.get(
                "validade"
            ) or ""
        )

        txt_admin.value = str(

            p.get(
                "admin_level",
                10
            )
        )

        chk_ativo.value = bool(
            p["ativo"]
        )

        chk_sistema.value = bool(
            p.get("sistema")
        )

        page.update()

    # ==============================================
    # PERMISSÕES
    # ==============================================

    def abrir_permissoes(p):

        page.perfil_permissoes = (
            p["id"]
        )

        navegar(
            page,
            "menu_config"
        )

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

            nome = str(

                txt_nome.value or ""

            ).strip()

            if not nome:

                raise Exception(
                    "Informe nome."
                )

            validade = None

            if txt_validade.value:

                validade = int(
                    txt_validade.value
                )

            admin_level = int(

                txt_admin.value or 0
            )

            ativo = int(
                bool(
                    chk_ativo.value
                )
            )

            sistema = int(
                bool(
                    chk_sistema.value
                )
            )

            # ======================================
            # UPDATE
            # ======================================

            if perfil_editando["id"]:

                resultado = atualizar_perfil(

                    usuario,

                    perfil_editando["id"],

                    nome,

                    validade,

                    admin_level,

                    ativo,

                    sistema
                )

                perfil_id = (
                    perfil_editando["id"]
                )

            # ======================================
            # INSERT
            # ======================================

            else:

                resultado = criar_perfil(

                    usuario,

                    nome,

                    validade,

                    admin_level,

                    ativo,

                    sistema
                )

                perfil_id = resultado[
                    "dados"
                ]

            if not resultado["sucesso"]:

                raise Exception(
                    resultado["mensagem"]
                )

            # ======================================
            # COPIAR
            # ======================================

            if ddl_copiar.value:

                copiar = copiar_permissoes(

                    usuario,

                    int(
                        ddl_copiar.value
                    ),

                    perfil_id
                )

                if not copiar["sucesso"]:

                    raise Exception(
                        copiar["mensagem"]
                    )

            limpar()

            carregar()

            exibir_snackbar(

                page,

                resultado["mensagem"]
            )

        except Exception as ex:

            logging.exception(
                "PERFIL SAVE ERROR"
            )

            status(str(ex))

        finally:

            carregando = False

            bloquear_ui(False)

    btn_salvar.on_click = salvar

    # ==============================================
    # EXCLUIR
    # ==============================================

    def remover(p):

        try:

            resultado = excluir_perfil(

                usuario,

                p["id"]
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
                "PERFIL DELETE ERROR"
            )

            exibir_snackbar(

                page,

                str(ex),

                erro=True
            )

    # ==============================================
    # GRID
    # ==============================================

    def render_perfil(p):

        sistema = bool(
            p.get("sistema")
        )

        cor = None

        if sistema:

            cor = ft.Colors.RED_50

        elif not p["ativo"]:

            cor = ft.Colors.GREY_200

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
                    x=p: editar(x)
                )
            )

            controles.append(

                ft.IconButton(

                    icon=ft.Icons.SECURITY,

                    tooltip="Permissões",

                    disabled=(

                        sistema

                        and

                        not is_root
                    ),

                    on_click=lambda e,
                    x=p: abrir_permissoes(x)
                )
            )

        # ==========================================
        # DELETE
        # ==========================================

        if pode_excluir:

            controles.append(

                ft.IconButton(

                    icon=ft.Icons.DELETE,

                    tooltip="Excluir",

                    disabled=(

                        sistema

                        or

                        p["id"] == 1
                    ),

                    on_click=lambda e,
                    x=p: remover(x)
                )
            )

        return ft.Container(

            content=ft.Row([

                ft.Text(

                    p["nome"],

                    width=220,

                    weight=(

                        "bold"

                        if sistema

                        else None
                    )
                ),

                ft.Text(

                    str(
                        p.get(
                            "validade"
                        ) or ""
                    ),

                    width=120
                ),

                ft.Text(

                    str(
                        p.get(
                            "admin_level",
                            0
                        )
                    ),

                    width=80
                ),

                ft.Text(

                    "Estrutural"

                    if sistema

                    else "",

                    width=120,

                    color=ft.Colors.RED
                ),

                ft.Text(

                    "Ativo"

                    if p["ativo"]

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

        ddl_copiar.options.clear()

        resultado = listar_perfis(
            usuario
        )

        if not resultado["sucesso"]:

            status(
                resultado["mensagem"]
            )

            return

        perfis_cache.clear()

        perfis_cache.extend(
            resultado["dados"]
        )

        for p in perfis_cache:

            if not pode_visualizar(p):
                continue

            ddl_copiar.options.append(

                ft.dropdown.Option(

                    str(p["id"]),

                    (
                        f"{p['nome']} "
                        f"(L{p.get('admin_level',0)})"
                    )
                )
            )

        filtro = str(

            txt_filtro.value or ""

        ).strip().upper()

        for p in perfis_cache:

            if not pode_visualizar(p):
                continue

            texto = (
                f"{p['nome']} "
                f"{p.get('admin_level',0)}"
            ).upper()

            if filtro:

                if filtro not in texto:
                    continue

            lista.controls.append(
                render_perfil(p)
            )

        page.update()

    txt_filtro.on_change = (
        lambda e: carregar()
    )

    # ==============================================
    # INIT
    # ==============================================

    carregar()

    # ==============================================
    # LAYOUT
    # ==============================================

    return ft.Column([

        ft.Row([

            ft.Text(

                "Perfis",

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

            txt_validade,

            txt_admin

        ],

            wrap=True
        ),

        ft.Row([

            chk_ativo,

            chk_sistema

        ]),

        ddl_copiar,

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
                    "Nome",
                    width=220,
                    weight="bold"
                ),

                ft.Text(
                    "Validade",
                    width=120,
                    weight="bold"
                ),

                ft.Text(
                    "Level",
                    width=80,
                    weight="bold"
                ),

                ft.Text(
                    "Estrutura",
                    width=120,
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