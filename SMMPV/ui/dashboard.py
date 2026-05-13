
import logging

import flet as ft

from services.menu_service import (
    get_menu_usuario
)

from services.menu_admin_service import (
    get_permissoes_usuario
)


# ==================================================
# CONFIG
# ==================================================

ROOT_LEVEL = 100

ROTAS_INTERNAS = {

    "dashboard",

    "logout",

    "fechar_app"
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


def is_root(usuario):

    return bool(
        usuario
        and
        int(
            usuario.get(
                "admin_level",
                0
            )
        ) >= ROOT_LEVEL
    )


def limpar_layout(page):

    try:

        page.clean()

    except Exception:

        logging.exception(
            "LAYOUT CLEAN ERROR"
        )


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


def renderizar_conteudo(
    page,
    conteudo
):

    if (
        not hasattr(page, "conteudo")
        or
        page.conteudo is None
    ):
        return

    page.conteudo.content = conteudo

    page.update()


def exibir_erro(
    page,
    titulo,
    mensagem
):

    renderizar_conteudo(

        page,

        ft.Container(

            content=ft.Column([

                ft.Icon(

                    ft.Icons.ERROR,

                    size=72,

                    color=ft.Colors.RED
                ),

                ft.Text(

                    titulo,

                    size=24,

                    weight="bold",

                    color=ft.Colors.RED
                ),

                ft.Text(

                    mensagem,

                    size=15
                )

            ],

                spacing=15,

                horizontal_alignment=(
                    ft.CrossAxisAlignment.CENTER
                )
            ),

            alignment=ft.Alignment(0, 0),

            expand=True
        )
    )


# ==================================================
# DASHBOARD HOME
# ==================================================

def dashboard_home(page):

    usuario = get_usuario(page)

    login = (
        usuario.get("login")
        if usuario
        else ""
    )

    perfil = (
        usuario.get("perfil_nome")
        if usuario
        else ""
    )

    admin_level = (
        usuario.get(
            "admin_level",
            0
        )
        if usuario
        else 0
    )

    return ft.Column([

        ft.Text(

            "Dashboard",

            size=30,

            weight="bold"
        ),

        ft.Divider(),

        ft.Container(

            content=ft.Column([

                ft.Text(
                    f"Usuário: {login}",
                    size=16
                ),

                ft.Text(
                    f"Perfil: {perfil}",
                    size=14
                ),

                ft.Text(

                    (
                        f"Nível Administrativo: "
                        f"{admin_level}"
                    ),

                    size=13,

                    color=ft.Colors.GREY_700
                )

            ],

                spacing=5
            ),

            padding=15,

            border_radius=10,

            bgcolor=ft.Colors.BLUE_50
        ),

        ft.Container(

            content=ft.Column([

                ft.Text(

                    "Bem-vindo ao ERP SMMPV.",

                    size=22,

                    weight="bold"
                ),

                ft.Text(

                    (
                        "Sistema operacional "
                        "em estruturação."
                    ),

                    size=15
                )

            ],

                spacing=10
            ),

            padding=20
        )

    ],

        spacing=20
    )


# ==================================================
# PLACEHOLDER
# ==================================================

def funcionalidade_nao_implementada(
    rota
):

    return ft.Container(

        content=ft.Column([

            ft.Icon(

                ft.Icons.CONSTRUCTION,

                size=72,

                color=ft.Colors.ORANGE
            ),

            ft.Text(

                "Funcionalidade em desenvolvimento",

                size=24,

                weight="bold"
            ),

            ft.Text(

                (
                    f"A opção '{rota}' "
                    "ainda não possui "
                    "rotina implementada."
                ),

                size=16
            )

        ],

            spacing=15,

            horizontal_alignment=(
                ft.CrossAxisAlignment.CENTER
            )
        ),

        alignment=ft.Alignment(0, 0),

        expand=True
    )


# ==================================================
# IMPORT DINÂMICO
# ==================================================

def safe_import(
    modulo,
    view_name,
    page
):

    try:

        module = __import__(
            modulo,
            fromlist=[view_name]
        )

        view = getattr(
            module,
            view_name
        )

        return view(page)

    except Exception as ex:

        logging.exception(
            "IMPORT VIEW ERROR"
        )

        return ft.Container(

            content=ft.Column([

                ft.Icon(

                    ft.Icons.ERROR,

                    size=70,

                    color=ft.Colors.RED
                ),

                ft.Text(

                    "Erro carregando módulo",

                    size=22,

                    weight="bold"
                ),

                ft.Text(
                    str(ex)
                )

            ],

                spacing=15,

                horizontal_alignment=(
                    ft.CrossAxisAlignment.CENTER
                )
            ),

            alignment=ft.Alignment(0, 0),

            expand=True
        )


# ==================================================
# ROTAS
# ==================================================

ROTAS = {

    "dashboard":
    lambda p: dashboard_home(p),

    "usuarios":
    lambda p: safe_import(
        "ui.usuarios",
        "usuarios_view",
        p
    ),

    "perfis":
    lambda p: safe_import(
        "ui.perfis",
        "perfis_view",
        p
    ),

    "menu_config":
    lambda p: safe_import(
        "ui.menu_admin",
        "menu_admin_view",
        p
    ),

    "editor_menu":
    lambda p: safe_import(
        "ui.menu_editor",
        "menu_editor_view",
        p
    ),

    "alterar_senha":
    lambda p: safe_import(
        "ui.alterar_senha",
        "alterar_senha_view",
        p
    ),

    "locais":
    lambda p: safe_import(
        "ui.locais",
        "locais_view",
        p
    ),

    "loc_ambientes":
    lambda p: safe_import(
        "ui.loc_ambientes",
        "loc_ambientes_view",
        p
    ),

    "loc_tipos":
    lambda p: safe_import(
        "ui.loc_tipos",
        "loc_tipos_view",
        p
    ),

    "loc_estruturas":
    lambda p: safe_import(
        "ui.loc_estruturas",
        "loc_estruturas_view",
        p
    )
}


# ==================================================
# MENU ITEM
# ==================================================

def criar_botao_menu(
    page,
    texto,
    rota,
    nivel=0
):

    ativo = (
        getattr(
            page,
            "rota_atual",
            ""
        ) == rota
    )

    return ft.Container(

        content=ft.TextButton(

            content=ft.Row([

                ft.Icon(

                    ft.Icons.CHEVRON_RIGHT,

                    size=16
                ),

                ft.Text(
                    texto,
                    size=14
                )

            ]),

            style=ft.ButtonStyle(

                bgcolor=(

                    ft.Colors.BLUE_50

                    if ativo

                    else None
                )
            ),

            on_click=lambda e:
            navegar(
                page,
                rota
            )

        ),

        padding=ft.padding.only(
            left=nivel * 10
        )
    )


# ==================================================
# TITLE
# ==================================================

def criar_titulo(
    texto,
    nivel=0
):

    return ft.Container(

        content=ft.Text(

            texto,

            size=16,

            weight="bold"
        ),

        padding=ft.padding.only(

            top=10,

            bottom=5,

            left=(nivel * 10) + 5
        )
    )


# ==================================================
# SUBMENU
# ==================================================

def criar_submenu(
    page,
    nome,
    filhos,
    nivel=0
):

    itens = []

    renderizar_menu_recursivo(

        page,

        filhos,

        itens,

        nivel + 1
    )

    return ft.Container(

        content=ft.ExpansionTile(

            title=ft.Text(

                nome,

                size=14,

                weight="bold"
            ),

            controls=itens
        ),

        padding=ft.padding.only(
            left=nivel * 10
        )
    )


# ==================================================
# MENU RECURSIVO
# ==================================================

def renderizar_menu_recursivo(
    page,
    menus,
    itens,
    nivel=0
):

    for m in menus:

        try:

            tipo = m.get("tipo")

            nome = m.get("nome")

            rota = m.get("rota")

            filhos = m.get(
                "filhos",
                []
            )

            if tipo == "T":

                itens.append(

                    criar_titulo(
                        nome,
                        nivel
                    )
                )

                if filhos:

                    renderizar_menu_recursivo(

                        page,

                        filhos,

                        itens,

                        nivel + 1
                    )

            elif tipo == "S":

                itens.append(

                    criar_submenu(

                        page,

                        nome,

                        filhos,

                        nivel
                    )
                )

            else:

                itens.append(

                    criar_botao_menu(

                        page,

                        nome,

                        rota,

                        nivel
                    )
                )

        except Exception:

            logging.exception(
                "MENU RENDER ERROR"
            )


# ==================================================
# MENU CACHE
# ==================================================

def carregar_menu(page):

    usuario = get_usuario(page)

    if not usuario:

        return []

    try:

        cache = getattr(
            page,
            "menu_cache",
            None
        )

        if cache:

            return cache

        menus = get_menu_usuario(
            usuario
        )

        page.menu_cache = menus

        return menus

    except Exception:

        logging.exception(
            "MENU LOAD ERROR"
        )

        return []


# ==================================================
# MENU SIDEBAR
# ==================================================

def montar_menu(page):

    menus = carregar_menu(page)

    itens = []

    renderizar_menu_recursivo(
        page,
        menus,
        itens
    )

    itens.append(ft.Divider())

    itens.append(

        criar_botao_menu(

            page,

            "Dashboard",

            "dashboard"
        )
    )

    itens.append(

        criar_botao_menu(

            page,

            "Logout",

            "logout"
        )
    )

    itens.append(

        criar_botao_menu(

            page,

            "Encerrar Sistema",

            "fechar_app"
        )
    )

    return ft.Column(

        controls=itens,

        spacing=5,

        scroll=ft.ScrollMode.AUTO
    )


# ==================================================
# TOPBAR
# ==================================================

def montar_topbar(page):

    usuario = get_usuario(page)

    login = (
        usuario.get("login")
        if usuario
        else ""
    )

    perfil = (
        usuario.get("perfil_nome")
        if usuario
        else ""
    )

    return ft.Container(

        content=ft.Row([

            ft.Column([

                ft.Text(

                    "SMMPV ERP",

                    size=22,

                    weight="bold"
                ),

                ft.Text(

                    (
                        f"{login} | "
                        f"{perfil}"
                    ),

                    size=12,

                    color=ft.Colors.GREY_700
                )

            ],

                spacing=2
            ),

            ft.Row([

                ft.IconButton(

                    icon=ft.Icons.HOME,

                    tooltip="Dashboard",

                    on_click=lambda e:
                    navegar(
                        page,
                        "dashboard"
                    )
                ),

                ft.IconButton(

                    icon=ft.Icons.LOGOUT,

                    tooltip="Logout",

                    on_click=lambda e:
                    navegar(
                        page,
                        "logout"
                    )
                )

            ])

        ],

            alignment=(
                ft.MainAxisAlignment.SPACE_BETWEEN
            )
        ),

        padding=15,

        border=ft.border.only(

            bottom=ft.BorderSide(

                1,

                ft.Colors.GREY_300
            )
        ),

        bgcolor=ft.Colors.WHITE
    )


# ==================================================
# VIEW
# ==================================================

def dashboard_view(page):

    usuario = get_usuario(page)

    # ==============================================
    # SEM SESSÃO
    # ==============================================

    if not usuario:

        from ui.login import login_view

        limpar_layout(page)

        page.add(
            login_view(page)
        )

        page.update()

        return

    # ==============================================
    # TROCAR SENHA
    # ==============================================

    if (

        usuario.get("trocar_senha")

        or

        usuario.get("senha_expirada")
    ):

        from ui.alterar_senha import (
            alterar_senha_view
        )

        limpar_layout(page)

        page.add(
            alterar_senha_view(page)
        )

        page.update()

        return

    # ==============================================
    # ESTADO
    # ==============================================

    page.rota_atual = "dashboard"

    # ==============================================
    # CONTENT
    # ==============================================

    conteudo = ft.Container(

        content=dashboard_home(page),

        expand=True,

        padding=20
    )

    page.conteudo = conteudo

    # ==============================================
    # SIDEBAR
    # ==============================================

    sidebar = ft.Container(

        content=montar_menu(page),

        width=320,

        padding=10,

        border=ft.border.only(

            right=ft.BorderSide(

                1,

                ft.Colors.GREY_300
            )
        ),

        bgcolor=ft.Colors.WHITE
    )

    # ==============================================
    # MAIN
    # ==============================================

    main = ft.Column([

        montar_topbar(page),

        conteudo

    ],

        expand=True,

        spacing=0
    )

    # ==============================================
    # LAYOUT
    # ==============================================

    layout = ft.Row([

        sidebar,

        main

    ],

        expand=True,

        spacing=0
    )

    limpar_layout(page)

    page.add(layout)

    page.update()


# ==================================================
# LOGOUT
# ==================================================

def logout(page):

    try:

        page.usuario_logado = None

        page.menu_cache = None

        page.rota_atual = None

        page.conteudo = None

    except Exception:

        logging.exception(
            "LOGOUT ERROR"
        )

    limpar_layout(page)

    from ui.login import login_view

    page.add(
        login_view(page)
    )

    page.update()


# ==================================================
# FECHAR
# ==================================================

def fechar_sistema(page):

    try:

        limpar_layout(page)

        page.add(

            ft.Container(

                content=ft.Column([

                    ft.Icon(

                        ft.Icons.POWER_SETTINGS_NEW,

                        size=80,

                        color=ft.Colors.RED
                    ),

                    ft.Text(

                        "Sistema encerrado.",

                        size=28,

                        weight="bold"
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
        )

        page.update()

    except Exception:

        logging.exception(
            "APP CLOSE ERROR"
        )


# ==================================================
# RBAC
# ==================================================

def validar_acesso(
    usuario,
    rota
):

    if rota in ROTAS_INTERNAS:
        return True

    if is_root(usuario):
        return True

    permissao = get_permissoes_usuario(

        usuario,

        rota
    )

    return bool(
        permissao.get("ver")
    )


# ==================================================
# NAVEGAR
# ==================================================

def navegar(
    page,
    rota
):

    # ==============================================
    # INTERNO
    # ==============================================

    if rota == "logout":

        logout(page)

        return

    if rota == "fechar_app":

        fechar_sistema(page)

        return

    # ==============================================
    # SESSÃO
    # ==============================================

    usuario = get_usuario(page)

    if not usuario:

        logout(page)

        return

    # ==============================================
    # CONTENT
    # ==============================================

    if (
        not hasattr(page, "conteudo")
        or
        page.conteudo is None
    ):

        dashboard_view(page)

        return

    # ==============================================
    # RBAC
    # ==============================================

    if not validar_acesso(
        usuario,
        rota
    ):

        exibir_erro(

            page,

            "Acesso negado.",

            (
                "Você não possui "
                "permissão para "
                "acessar este módulo."
            )
        )

        return

    try:

        abrir = ROTAS.get(rota)

        if not abrir:

            resultado = (
                funcionalidade_nao_implementada(
                    rota
                )
            )

        else:

            resultado = abrir(page)

        if resultado is None:

            raise Exception(
                f"View '{rota}' retornou None."
            )

        page.rota_atual = rota

        renderizar_conteudo(
            page,
            resultado
        )

    except Exception as ex:

        logging.exception(
            "NAVIGATION ERROR"
        )

        exibir_erro(

            page,

            "Erro ao carregar módulo",

            str(ex)
        )