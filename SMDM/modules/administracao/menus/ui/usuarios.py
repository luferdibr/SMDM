
import logging

import flet as ft

from config.settings import (
    APP_CONFIG,
    ADMIN_CONFIG,
)

from modules.administracao.usuarios.services.user_service import (

    listar_usuarios,

    criar_usuario,

    atualizar_usuario,

    excluir_usuario,

    resetar_senha_usuario
)

from modules.administracao.perfis.services.perfil_service import (
    listar_perfis
)

from services.menu_admin_service import (
    get_permissoes_usuario
)

from ui.dashboard import (
    navegar
)


# ==================================================
# CONFIG
# ==================================================

ROOT_LEVEL = 100


# ==================================================
# LOGGER
# ==================================================

LOGGER = logging.getLogger(
    "MDM_USUARIOS_UI"
)


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


def snackbar(

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
        )
    )

    page.snack_bar.open = True

    page.update()


def get_cor_admin(level):

    if level >= ROOT_LEVEL:
        return ft.Colors.RED

    if level >= 50:
        return ft.Colors.ORANGE

    return ft.Colors.BLUE


def get_nome_admin(level):

    if level >= ROOT_LEVEL:
        return "ROOT"

    if level >= 50:
        return "ADMIN"

    return "OPERACIONAL"


# ==================================================
# VIEW
# ==================================================

def usuarios_view(page):

    usuario_logado = get_usuario(page)

    # ==============================================
    # SESSÃO
    # ==============================================

    if not usuario_logado:

        return ft.Container(

            expand=True,

            alignment=ft.Alignment(x=0, y=0),

            content=ft.Column([

                ft.Icon(
                    ft.Icons.ERROR,
                    size=70,
                    color=ft.Colors.RED
                ),

                ft.Text(
                    "Sessão inválida.",
                    size=24,
                    weight="bold"
                )

            ],
                spacing=20,
                horizontal_alignment=(
                    ft.CrossAxisAlignment.CENTER
                )
            )
        )

    # ==============================================
    # RBAC
    # ==============================================

    permissoes = get_permissoes_usuario(

        usuario_logado,

        "usuarios"
    )

    if not permissoes.get("ver"):

        return ft.Container(

            expand=True,

            alignment=ft.Alignment(x=0, y=0),

            content=ft.Column([

                ft.Icon(
                    ft.Icons.LOCK,
                    size=72,
                    color=ft.Colors.RED
                ),

                ft.Text(
                    "Acesso negado.",
                    size=24,
                    weight="bold"
                )

            ],
                spacing=20,
                horizontal_alignment=(
                    ft.CrossAxisAlignment.CENTER
                )
            )
        )

    pode_editar = bool(
        permissoes.get("editar")
    )

    # ==============================================
    # COMPONENTES
    # ==============================================

    txt_id = ft.TextField(
        visible=False
    )

    txt_login = ft.TextField(

        label="Login",

        width=220
    )

    txt_nome = ft.TextField(

        label="Nome",

        width=320
    )

    txt_email = ft.TextField(

        label="E-mail",

        width=320
    )

    txt_senha = ft.TextField(

        label="Senha",

        password=True,

        can_reveal_password=True,

        disabled=True,

        value=ADMIN_CONFIG["admin_senha"],

        width=240
    )

    ddl_perfil = ft.Dropdown(

        label="Perfil",

        width=280
    )

    chk_ativo = ft.Checkbox(

        label="Ativo",

        value=True
    )

    chk_trocar = ft.Checkbox(

        label="Trocar senha no próximo login",

        value=True,

        disabled=True
    )

    txt_filtro = ft.TextField(

        label="Pesquisar",

        width=320,

        prefix_icon=ft.Icons.SEARCH
    )

    tabela = ft.Column(

        spacing=8,

        scroll=ft.ScrollMode.AUTO,

        expand=True
    )

    # ==============================================
    # HELPERS
    # ==============================================

    def limpar():

        txt_id.value = ""

        txt_login.value = ""

        txt_login.disabled = False

        txt_nome.value = ""

        txt_email.value = ""

        txt_senha.value = ADMIN_CONFIG[
            "admin_senha"
        ]

        txt_senha.disabled = True

        ddl_perfil.value = None

        chk_ativo.value = True

        chk_trocar.value = True

        chk_trocar.disabled = True

    # ==============================================
    # PERFIS
    # ==============================================

    def carregar_perfis(
        e=None,
        atualizar=True
    ):

        try:

            perfis = listar_perfis()

            LOGGER.info(
                "Perfis carregados no combo de usuário: %s",
                len(perfis)
            )

            ddl_perfil.options = [

                ft.dropdown.Option(

                    key=str(
                        p["id"]
                    ),

                    text=(
                        f"{p['nome']} "
                        f"[{p['admin_level']}]"
                    )
                )

                for p in perfis
            ]

            if atualizar:

                page.update()

        except Exception as ex:

            LOGGER.exception(
                "LOAD PERFIS ERROR"
            )

            ddl_perfil.options = []

            if atualizar:

                snackbar(
                    page,
                    str(ex),
                    erro=True
                )

    # ==============================================
    # CARD
    # ==============================================

    def criar_card(usuario):

        level = int(
            usuario.get(
                "admin_level",
                0
            )
        )

        return ft.Container(

            padding=12,

            border_radius=12,

            bgcolor=ft.Colors.WHITE,

            border=ft.border.all(

                1,

                ft.Colors.GREY_300
            ),

            content=ft.Row([

                # ==================================
                # INFO
                # ==================================

                ft.Container(

                    expand=True,

                    content=ft.Column([

                        ft.Row([

                            ft.Icon(

                                ft.Icons.PERSON,

                                color=get_cor_admin(
                                    level
                                )
                            ),

                            ft.Text(

                                usuario["nome"],

                                size=16,

                                weight="bold"
                            ),

                            ft.Container(

                                padding=ft.padding.symmetric(

                                    horizontal=8,

                                    vertical=2
                                ),

                                bgcolor=get_cor_admin(
                                    level
                                ),

                                border_radius=20,

                                content=ft.Text(

                                    get_nome_admin(
                                        level
                                    ),

                                    color=ft.Colors.WHITE,

                                    size=11
                                )
                            )

                        ],
                            spacing=10
                        ),

                        ft.Text(

                            (
                                f"Login: "
                                f"{usuario['login']} | "
                                f"Perfil: "
                                f"{usuario['perfil_nome']}"
                            ),

                            size=11,

                            color=ft.Colors.GREY_700
                        ),

                        ft.Row([

                            ft.Icon(

                                (
                                    ft.Icons.CHECK_CIRCLE
                                    if usuario["ativo"]
                                    else
                                    ft.Icons.CANCEL
                                ),

                                color=(

                                    ft.Colors.GREEN

                                    if usuario["ativo"]

                                    else

                                    ft.Colors.RED
                                ),

                                size=16
                            ),

                            ft.Text(

                                (
                                    "Ativo"
                                    if usuario["ativo"]
                                    else
                                    "Inativo"
                                ),

                                size=12
                            ),

                            ft.Container(width=20),

                            ft.Icon(

                                (
                                    ft.Icons.LOCK_RESET
                                    if usuario.get(
                                        "deve_trocar"
                                    )
                                    else
                                    ft.Icons.LOCK_OPEN
                                ),

                                color=ft.Colors.ORANGE,

                                size=16
                            ),

                            ft.Text(

                                (
                                    "Troca obrigatória"
                                    if usuario.get(
                                        "deve_trocar"
                                    )
                                    else
                                    "Senha válida"
                                ),

                                size=12
                            )

                        ],
                            spacing=6
                        )

                    ],
                        spacing=6
                    )
                ),

                # ==================================
                # AÇÕES
                # ==================================

                ft.Row([

                    ft.IconButton(

                        icon=ft.Icons.EDIT,

                        disabled=(
                            not pode_editar
                        ),

                        on_click=lambda e,
                        u=usuario: editar(u)
                    ),

                    ft.IconButton(

                        icon=ft.Icons.LOCK_RESET,

                        tooltip="Resetar senha",

                        disabled=(
                            not pode_editar
                        ),

                        on_click=lambda e,
                        u=usuario: resetar(u)
                    ),

                    ft.IconButton(

                        icon=ft.Icons.DELETE,

                        icon_color=ft.Colors.RED,

                        disabled=(
                            not pode_editar
                        ),

                        on_click=lambda e,
                        u=usuario: remover(u)
                    )

                ])
            ])
        )

    # ==============================================
    # LOAD
    # ==============================================

    def carregar_usuarios(
        e=None,
        atualizar=True
    ):

        try:

            filtro = str(
                txt_filtro.value or ""
            ).strip()

            tabela.controls.clear()

            usuarios = listar_usuarios(
                filtro
            )

            if not usuarios:

                tabela.controls.append(
                    ft.Container(
                        padding=20,
                        alignment=ft.Alignment(0, 0),
                        content=ft.Text(
                            "Nenhum usuário cadastrado encontrado.",
                            size=14,
                            color=ft.Colors.GREY_700
                        )
                    )
                )

            for usuario in usuarios:

                tabela.controls.append(
                    criar_card(usuario)
                )

            if atualizar:

                page.update()

        except Exception as ex:

            LOGGER.exception(
                "LOAD USERS ERROR"
            )

            tabela.controls.clear()

            tabela.controls.append(
                ft.Text(
                    f"Erro carregando usuários: {ex}",
                    color=ft.Colors.RED,
                    selectable=True
                )
            )

            if atualizar:

                snackbar(
                    page,
                    str(ex),
                    erro=True
                )

    # ==============================================
    # EDIT
    # ==============================================

    def editar(usuario):

        txt_id.value = usuario["id"]

        txt_login.value = usuario["login"]

        txt_login.disabled = True

        txt_nome.value = usuario["nome"]

        txt_email.value = (
            usuario.get("email")
            or ""
        )

        ddl_perfil.value = str(
            usuario["perfil_id"]
        )

        chk_ativo.value = bool(
            usuario["ativo"]
        )

        chk_trocar.value = bool(
            usuario.get(
                "deve_trocar"
            )
        )

        chk_trocar.disabled = False

        txt_senha.value = ""

        txt_senha.disabled = False

        page.update()

    # ==============================================
    # REMOVE
    # ==============================================

    def remover(usuario):

        try:

            excluir_usuario(

                usuario["id"],

                usuario_logado
            )

            carregar_usuarios()

            snackbar(
                page,
                "Usuário removido."
            )

        except Exception as ex:

            LOGGER.exception(
                "DELETE USER ERROR"
            )

            snackbar(
                page,
                str(ex),
                erro=True
            )

    # ==============================================
    # RESET
    # ==============================================

    def resetar(usuario):

        try:

            resetar_senha_usuario(

                usuario["id"],

                usuario_logado
            )

            snackbar(
                page,
                (
                    "Senha resetada "
                    "com sucesso."
                )
            )

        except Exception as ex:

            LOGGER.exception(
                "RESET PASSWORD ERROR"
            )

            snackbar(
                page,
                str(ex),
                erro=True
            )

    # ==============================================
    # SAVE
    # ==============================================

    def salvar(e):

        try:

            if not pode_editar:

                snackbar(
                    page,
                    "Sem permissão.",
                    erro=True
                )

                return

            payload = {

                "login": txt_login.value,

                "nome": txt_nome.value,

                "email": txt_email.value,

                "senha": txt_senha.value,

                "perfil_id": ddl_perfil.value,

                "ativo": chk_ativo.value,

                "deve_trocar": (
                    chk_trocar.value
                )
            }

            # ======================================
            # CREATE
            # ======================================

            if not txt_id.value:

                criar_usuario(

                    payload,

                    usuario_logado
                )

                snackbar(
                    page,
                    "Usuário criado."
                )

            # ======================================
            # UPDATE
            # ======================================

            else:

                atualizar_usuario(

                    int(txt_id.value),

                    payload,

                    usuario_logado
                )

                snackbar(
                    page,
                    "Usuário atualizado."
                )

            limpar()

            carregar_usuarios()

        except Exception as ex:

            LOGGER.exception(
                "SAVE USER ERROR"
            )

            snackbar(
                page,
                str(ex),
                erro=True
            )

    # ==============================================
    # EVENTOS
    # ==============================================

    txt_filtro.on_change = (
        carregar_usuarios
    )

    # ==============================================
    # BOTÕES
    # ==============================================

    btn_novo = ft.OutlinedButton(

        content=ft.Row(
            spacing=6,
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                ft.Icon(ft.Icons.ADD, size=16),
                ft.Text("Novo", size=12),
            ],
        ),

        disabled=not pode_editar,

        on_click=lambda e: (
            limpar(),
            page.update()
        )
    )

    btn_salvar = ft.ElevatedButton(

        content=ft.Row(
            spacing=6,
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                ft.Icon(ft.Icons.SAVE, size=16),
                ft.Text("Salvar", size=12),
            ],
        ),

        disabled=not pode_editar,

        on_click=salvar
    )

    btn_voltar = ft.TextButton(

        content=ft.Row(
            spacing=6,
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                ft.Icon(ft.Icons.ARROW_BACK, size=16),
                ft.Text("Voltar", size=12),
            ],
        ),

        on_click=lambda e: navegar(
            page,
            "dashboard"
        )
    )

    # ==============================================
    # INIT
    # ==============================================

    limpar()

    carregar_perfis(
        atualizar=False
    )

    carregar_usuarios(
        atualizar=False
    )

    # ==============================================
    # LAYOUT
    # ==============================================

    return ft.Container(

        expand=True,

        padding=20,

        content=ft.Column([

            # ======================================
            # HEADER
            # ======================================

            ft.Row([

                ft.Column([

                    ft.Text(

                        "Usuários",

                        size=30,

                        weight="bold"
                    ),

                    ft.Text(

                        APP_CONFIG["name"],

                        size=13,

                        color=ft.Colors.GREY_700
                    )

                ],
                    spacing=2,
                    expand=True
                ),

                btn_voltar
            ]),

            ft.Divider(),

            # ======================================
            # FORM
            # ======================================

            ft.ResponsiveRow(

                spacing=12,

                controls=[

                    ft.Container(
                        col={
                            "xs": 12,
                            "md": 3,
                        },
                        content=txt_login
                    ),

                    ft.Container(
                        col={
                            "xs": 12,
                            "md": 5,
                        },
                        content=txt_nome
                    ),

                    ft.Container(
                        col={
                            "xs": 12,
                            "md": 4,
                        },
                        content=txt_email
                    ),
                ],
            ),

            ft.ResponsiveRow(

                spacing=12,

                controls=[

                    ft.Container(
                        col={
                            "xs": 12,
                            "md": 4,
                        },
                        content=txt_senha
                    ),

                    ft.Container(
                        col={
                            "xs": 12,
                            "md": 4,
                        },
                        content=ddl_perfil
                    ),
                ],
            ),

            ft.Row([

                chk_ativo,

                chk_trocar

            ]),

            ft.Row([

                btn_novo,

                btn_salvar

            ]),

            ft.Divider(),

            # ======================================
            # FILTRO
            # ======================================

            ft.Row([

                txt_filtro

            ]),

            # ======================================
            # LISTA
            # ======================================

            ft.Container(

                expand=True,

                padding=12,

                bgcolor=ft.Colors.GREY_100,

                border_radius=12,

                content=tabela
            )

        ],

            spacing=16,

            expand=True
        )
    )
