
import logging

import flet as ft

from services.auth_service import (
    autenticar
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
            else ft.Colors.GREEN_600
        ),

        open=True
    )

    page.update()


def bloquear_ui(
    status,
    progress,
    btn_entrar,
    btn_sair,
    txt_user,
    txt_pass,
    page
):

    progress.visible = status

    btn_entrar.disabled = status

    btn_sair.disabled = status

    txt_user.disabled = status

    txt_pass.disabled = status

    page.update()


def limpar_status(
    txt_status,
    page
):

    txt_status.value = ""

    page.update()


# ==================================================
# LOGIN VIEW
# ==================================================

def login_view(page: ft.Page):

    # ==============================================
    # JÁ LOGADO
    # ==============================================

    usuario = get_usuario(page)

    if usuario:

        try:

            trocar = bool(

                usuario.get(
                    "trocar_senha"
                )

                or

                usuario.get(
                    "senha_expirada"
                )
            )

            # ======================================
            # TROCAR SENHA
            # ======================================

            if trocar:

                from ui.alterar_senha import (
                    alterar_senha_view
                )

                return alterar_senha_view(
                    page
                )

            # ======================================
            # DASHBOARD
            # ======================================

            from ui.dashboard import (
                dashboard_view
            )

            dashboard_view(page)

            return ft.Container()

        except Exception:

            logging.exception(
                "LOGIN REDIRECT ERROR"
            )

    # ==============================================
    # CONFIG PAGE
    # ==============================================

    page.title = "SMMPV ERP"

    page.theme_mode = (
        ft.ThemeMode.LIGHT
    )

    page.bgcolor = (
        ft.Colors.GREY_100
    )

    page.vertical_alignment = (
        ft.MainAxisAlignment.CENTER
    )

    page.horizontal_alignment = (
        ft.CrossAxisAlignment.CENTER
    )

    salvando = False

    # ==============================================
    # CAMPOS
    # ==============================================

    txt_user = ft.TextField(

        label="Usuário",

        width=340,

        autofocus=True,

        prefix_icon=ft.Icons.PERSON
    )

    txt_pass = ft.TextField(

        label="Senha",

        width=340,

        password=True,

        can_reveal_password=True,

        prefix_icon=ft.Icons.LOCK
    )

    txt_status = ft.Text(

        "",

        size=14,

        color=ft.Colors.RED
    )

    progress = ft.ProgressRing(

        visible=False
    )

    btn_entrar = ft.ElevatedButton(

        "Entrar",

        icon=ft.Icons.LOGIN,

        width=160
    )

    btn_sair = ft.OutlinedButton(

        "Sair",

        icon=ft.Icons.CLOSE,

        width=160
    )

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
    # LOGIN
    # ==============================================

    def entrar(e=None):

        nonlocal salvando

        if salvando:
            return

        salvando = True

        bloquear_ui(

            True,

            progress,

            btn_entrar,

            btn_sair,

            txt_user,

            txt_pass,

            page
        )

        limpar_status(
            txt_status,
            page
        )

        try:

            usuario_txt = str(

                txt_user.value or ""

            ).strip().upper()

            senha_txt = str(

                txt_pass.value or ""

            )

            # ======================================
            # USER
            # ======================================

            if not usuario_txt:

                status(
                    "Informe o usuário."
                )

                txt_user.focus()

                return

            # ======================================
            # SENHA
            # ======================================

            if not senha_txt:

                status(
                    "Informe a senha."
                )

                txt_pass.focus()

                return

            logging.info(

                "Autenticando usuário %s",

                usuario_txt
            )

            # ======================================
            # AUTH
            # ======================================

            resultado = autenticar(

                usuario_txt,

                senha_txt
            )

            if not resultado:

                raise Exception(
                    "Retorno inválido."
                )

            # ======================================
            # BLOQUEADO
            # ======================================

            if resultado.get(
                "bloqueado"
            ):

                status(
                    "Usuário bloqueado."
                )

                return

            # ======================================
            # INATIVO
            # ======================================

            if not resultado.get(
                "ativo",
                True
            ):

                status(
                    "Usuário inativo."
                )

                return

            # ======================================
            # PERFIL
            # ======================================

            if not resultado.get(
                "perfil_ativo",
                True
            ):

                status(
                    "Perfil inativo."
                )

                return

            # ======================================
            # LOGIN INVÁLIDO
            # ======================================

            if not resultado.get(
                "autenticado"
            ):

                status(
                    "Usuário ou senha inválidos."
                )

                txt_pass.focus()

                return

            # ======================================
            # SESSÃO
            # ======================================

            page.usuario_logado = (
                resultado
            )

            # ======================================
            # TROCA
            # ======================================

            trocar = bool(

                resultado.get(
                    "trocar_senha"
                )

                or

                resultado.get(
                    "senha_expirada"
                )
            )

            # ======================================
            # ALTERAR SENHA
            # ======================================

            if trocar:

                logging.info(
                    "Abrindo alterar senha..."
                )

                from ui.alterar_senha import (
                    alterar_senha_view
                )

                page.clean()

                page.add(
                    alterar_senha_view(page)
                )

                page.update()

            # ======================================
            # DASHBOARD
            # ======================================

            else:

                logging.info(
                    "Abrindo dashboard..."
                )

                from ui.dashboard import (
                    dashboard_view
                )

                dashboard_view(page)

            logging.info(
                "Login concluído."
            )

            exibir_snackbar(

                page,

                (
                    f"Bem-vindo "
                    f"{resultado.get('login')}."
                )
            )

        except Exception as ex:

            logging.exception(
                "LOGIN ERROR"
            )

            status(
                f"Erro no login: {ex}"
            )

        finally:

            salvando = False

            bloquear_ui(

                False,

                progress,

                btn_entrar,

                btn_sair,

                txt_user,

                txt_pass,

                page
            )

    # ==============================================
    # ENTER
    # ==============================================

    txt_user.on_submit = entrar

    txt_pass.on_submit = entrar

    btn_entrar.on_click = entrar

    # ==============================================
    # SAIR
    # ==============================================

    def fechar_sistema(e=None):

        try:

            page.window.visible = False

            page.update()

        except Exception:

            logging.exception(
                "APP CLOSE ERROR"
            )

            exibir_snackbar(

                page,

                "Erro ao fechar sistema.",

                erro=True
            )

    btn_sair.on_click = fechar_sistema

    # ==============================================
    # CARD
    # ==============================================

    card_login = ft.Container(

        content=ft.Column([

            ft.Icon(

                ft.Icons.ACCOUNT_CIRCLE,

                size=80,

                color=ft.Colors.BLUE
            ),

            ft.Text(

                "SMMPV ERP",

                size=34,

                weight="bold"
            ),

            ft.Text(

                "Sistema de Gestão",

                size=16,

                color=ft.Colors.GREY_700
            ),

            ft.Divider(),

            txt_user,

            txt_pass,

            txt_status,

            progress,

            ft.Row([

                btn_entrar,

                btn_sair

            ],

                alignment=(
                    ft.MainAxisAlignment.CENTER
                )
            )

        ],

            spacing=18,

            horizontal_alignment=(
                ft.CrossAxisAlignment.CENTER
            )
        ),

        width=440,

        padding=32,

        border_radius=20,

        bgcolor=ft.Colors.WHITE,

        shadow=ft.BoxShadow(

            blur_radius=20,

            spread_radius=1,

            color=ft.Colors.BLACK12
        )
    )

    # ==============================================
    # LAYOUT
    # ==============================================

    return ft.Container(

        content=card_login,

        expand=True,

        alignment=ft.Alignment(0, 0),

        bgcolor=ft.Colors.GREY_100
    )