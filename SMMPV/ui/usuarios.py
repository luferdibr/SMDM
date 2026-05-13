
import logging

import flet as ft

from ui.dashboard import navegar

from services.user_service import (

    listar_usuarios,

    listar_perfis,

    criar_usuario,

    atualizar_usuario,

    excluir_usuario,

    resetar_senha
)

from services.menu_admin_service import (
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

def usuarios_view(page):

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

        "usuarios"
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

    usuario_editando = {
        "id": None
    }

    usuarios_cache = []

    # ==============================================
    # COMPONENTES
    # ==============================================

    txt_filtro = ft.TextField(

        label="Pesquisar",

        width=300,

        prefix_icon=ft.Icons.SEARCH
    )

    txt_login = ft.TextField(

        label="Login",

        width=220,

        disabled=not pode_editar
    )

    txt_nome = ft.TextField(

        label="Nome",

        width=300,

        disabled=not pode_editar
    )

    ddl_perfil = ft.Dropdown(

        label="Perfil",

        width=260,

        disabled=not pode_editar
    )

    chk_ativo = ft.Checkbox(

        label="Ativo",

        value=True,

        disabled=not pode_editar
    )

    chk_bloqueado = ft.Checkbox(

        label="Bloqueado",

        value=False,

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

        txt_login.disabled = (
            status or not pode_editar
        )

        txt_nome.disabled = (
            status or not pode_editar
        )

        ddl_perfil.disabled = (
            status or not pode_editar
        )

        chk_ativo.disabled = (
            status or not pode_editar
        )

        chk_bloqueado.disabled = (
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
    # PERFIS
    # ==============================================

    resultado_perfis = listar_perfis(
        usuario
    )

    if resultado_perfis["sucesso"]:

        ddl_perfil.options = [

            ft.dropdown.Option(

                str(p["id"]),

                (
                    f"{p['nome']} "
                    f"(L{p.get('admin_level',0)})"
                )
            )

            for p in resultado_perfis[
                "dados"
            ]
        ]

    # ==============================================
    # LIMPAR
    # ==============================================

    def limpar(e=None):

        usuario_editando["id"] = None

        txt_login.value = ""

        txt_nome.value = ""

        ddl_perfil.value = None

        chk_ativo.value = True

        chk_bloqueado.value = False

        txt_status.value = ""

        page.update()

    btn_limpar.on_click = limpar

    # ==============================================
    # VISIBILIDADE
    # ==============================================

    def pode_visualizar_usuario(u):

        if is_root:
            return True

        if u.get("sistema"):
            return False

        if int(
            u.get(
                "admin_level",
                0
            )
        ) >= usuario_level:

            return False

        return True

    # ==============================================
    # EDITAR
    # ==============================================

    def editar(u):

        if not pode_editar:

            exibir_snackbar(

                page,

                "Sem permissão.",

                erro=True
            )

            return

        usuario_editando["id"] = u["id"]

        txt_login.value = str(
            u["login"]
        ).strip()

        txt_nome.value = str(
            u["nome"]
        ).strip()

        chk_ativo.value = bool(
            u["ativo"]
        )

        chk_bloqueado.value = bool(
            u["bloqueado"]
        )

        ddl_perfil.value = str(
            u["perfil_id"]
        )

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

            login = str(

                txt_login.value or ""

            ).strip().upper()

            nome = str(

                txt_nome.value or ""

            ).strip()

            if not login:

                raise Exception(
                    "Informe login."
                )

            if not nome:

                raise Exception(
                    "Informe nome."
                )

            if not ddl_perfil.value:

                raise Exception(
                    "Selecione perfil."
                )

            perfil_id = int(
                ddl_perfil.value
            )

            ativo = int(
                bool(
                    chk_ativo.value
                )
            )

            bloqueado = int(
                bool(
                    chk_bloqueado.value
                )
            )

            # ======================================
            # NOVO
            # ======================================

            if not usuario_editando["id"]:

                resultado = criar_usuario(

                    usuario,

                    login,

                    nome,

                    perfil_id
                )

            # ======================================
            # UPDATE
            # ======================================

            else:

                resultado = atualizar_usuario(

                    usuario,

                    usuario_editando["id"],

                    login,

                    nome,

                    perfil_id,

                    ativo,

                    bloqueado
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
                "USUARIO SAVE ERROR"
            )

            status(str(ex))

        finally:

            carregando = False

            bloquear_ui(False)

    btn_salvar.on_click = salvar

    # ==============================================
    # REMOVER
    # ==============================================

    def remover(u):

        try:

            resultado = excluir_usuario(

                usuario,

                u["id"]
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
                "USER DELETE ERROR"
            )

            exibir_snackbar(

                page,

                str(ex),

                erro=True
            )

    # ==============================================
    # RESET
    # ==============================================

    def resetar(u):

        try:

            resultado = resetar_senha(

                usuario,

                u["id"]
            )

            if not resultado["sucesso"]:

                raise Exception(
                    resultado["mensagem"]
                )

            exibir_snackbar(

                page,

                resultado["mensagem"]
            )

        except Exception as ex:

            logging.exception(
                "RESET PASSWORD ERROR"
            )

            exibir_snackbar(

                page,

                str(ex),

                erro=True
            )

    # ==============================================
    # GRID
    # ==============================================

    def render_usuario(u):

        cor = None

        if u.get("sistema"):

            cor = ft.Colors.RED_50

        elif u["bloqueado"]:

            cor = ft.Colors.ORANGE_50

        elif not u["ativo"]:

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

                    on_click=lambda e,
                    x=u: editar(x)
                )
            )

            controles.append(

                ft.IconButton(

                    icon=ft.Icons.LOCK_RESET,

                    tooltip="Resetar Senha",

                    on_click=lambda e,
                    x=u: resetar(x)
                )
            )

        # ==========================================
        # EXCLUIR
        # ==========================================

        if (
            pode_excluir

            and

            u["id"] != usuario["id"]
        ):

            controles.append(

                ft.IconButton(

                    icon=ft.Icons.DELETE,

                    tooltip="Desativar",

                    on_click=lambda e,
                    x=u: remover(x)
                )
            )

        return ft.Container(

            content=ft.Row([

                ft.Text(

                    u["login"],

                    width=140,

                    weight=(

                        "bold"

                        if u.get("sistema")

                        else None
                    )
                ),

                ft.Text(

                    u["nome"],

                    width=220
                ),

                ft.Text(

                    (
                        f"{u['perfil_nome']} "
                        f"(L{u.get('admin_level',0)})"
                    ),

                    width=220
                ),

                ft.Text(

                    "Ativo"

                    if u["ativo"]

                    else "Inativo",

                    width=80
                ),

                ft.Text(

                    "Bloqueado"

                    if u["bloqueado"]

                    else "",

                    width=100,

                    color=ft.Colors.RED
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

        resultado = listar_usuarios(
            usuario
        )

        if not resultado["sucesso"]:

            status(
                resultado["mensagem"]
            )

            return

        usuarios_cache.clear()

        usuarios_cache.extend(
            resultado["dados"]
        )

        filtro = str(

            txt_filtro.value or ""

        ).strip().upper()

        usuarios_filtrados = []

        for u in usuarios_cache:

            if not pode_visualizar_usuario(u):
                continue

            texto = (
                f"{u['login']} "
                f"{u['nome']} "
                f"{u['perfil_nome']}"
            ).upper()

            if filtro:

                if filtro not in texto:
                    continue

            usuarios_filtrados.append(u)

        for u in usuarios_filtrados:

            lista.controls.append(
                render_usuario(u)
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

                "Usuários",

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

            txt_login,

            txt_nome,

            ddl_perfil

        ],

            wrap=True
        ),

        ft.Row([

            chk_ativo,

            chk_bloqueado

        ]),

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
                    "Login",
                    width=140,
                    weight="bold"
                ),

                ft.Text(
                    "Nome",
                    width=220,
                    weight="bold"
                ),

                ft.Text(
                    "Perfil",
                    width=220,
                    weight="bold"
                ),

                ft.Text(
                    "Status",
                    width=80,
                    weight="bold"
                ),

                ft.Text(
                    "Bloqueio",
                    width=100,
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