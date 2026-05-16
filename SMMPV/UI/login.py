
import logging

import flet as ft

from services.auth_service import (
    autenticar
)

from services.auditoria_service import (
    registrar_evento
)

from config.settings import (
    APP_CONFIG
)

# ==================================================
# LOGGER
# ==================================================

LOGGER = logging.getLogger(
    "MDM_LOGIN"
)

# ==================================================
# HELPERS
# ==================================================

def show_message(
    page,
    message,
    color=ft.Colors.RED
):

    page.snack_bar = ft.SnackBar(

        content=ft.Text(message),

        bgcolor=color
    )

    page.snack_bar.open = True

    page.update()


def close_app(page):

    LOGGER.info(
        "Minimizando aplicação"
    )

    try:

        # ==========================================
        # MINIMIZA JANELA
        # ==========================================

        page.window.minimized = True

        page.update()

    except Exception:

        LOGGER.exception(
            "MINIMIZE ERROR"
        )



# ==================================================
# LOGIN VIEW
# ==================================================

def login_view(page: ft.Page):

    LOGGER.info(
        "Inicializando login view"
    )

    # ==============================================
    # CAMPOS
    # ==============================================

    txt_user = ft.TextField(

        label="Usuário",

        width=320,

        autofocus=True,

        prefix_icon=ft.Icons.PERSON
    )

    txt_pass = ft.TextField(

        label="Senha",

        password=True,

        can_reveal_password=True,

        width=320,

        prefix_icon=ft.Icons.LOCK
    )

    # ==============================================
    # STATUS
    # ==============================================

    txt_status = ft.Text(

        "",

        color=ft.Colors.RED,

        size=13
    )

    progress = ft.ProgressRing(

        visible=False,

        width=22,

        height=22
    )

    # ==============================================
    # LOGIN
    # ==============================================

    def realizar_login(e):

        try:

            login = (

                txt_user.value or ""

            ).strip().upper()

            senha = (

                txt_pass.value or ""

            ).strip()

            LOGGER.info(
                f"Autenticando usuário {login}"
            )

            # ======================================
            # VALIDACOES
            # ======================================

            if not login:

                txt_status.value = (
                    "Informe o usuário."
                )

                page.update()

                return

            if not senha:

                txt_status.value = (
                    "Informe a senha."
                )

                page.update()

                return

            # ======================================
            # STATUS
            # ======================================

            progress.visible = True

            txt_status.value = ""

            page.update()

            # ======================================
            # AUTH
            # ======================================

            resultado = autenticar(

                login,

                senha
            )

            LOGGER.info(
                f"Resultado auth: {resultado}"
            )

            # ======================================
            # LOGIN INVALIDO
            # ======================================

            if not resultado.get(
                "autenticado"
            ):

                progress.visible = False

                txt_status.value = (

                    resultado.get(
                        "mensagem",
                        "Usuário ou senha inválidos."
                    )
                )

                page.update()

                return

            # ======================================
            # USUARIO
            # ======================================

            usuario = resultado[
                "usuario"
            ]

            LOGGER.info(
                (
                    f"Usuário autenticado: "
                    f"{usuario}"
                )
            )

            # ======================================
            # CONTEXTO PAGE
            # ======================================

            page.usuario_logado = usuario

            # ======================================
            # AUDITORIA
            # ======================================

            registrar_evento(

                usuario_id=usuario["id"],

                login=usuario["login"],

                acao="LOGIN_UI",

                entidade="LOGIN",

                registro_id=usuario["id"],

                detalhes="Login realizado"
            )

            # ======================================
            # LIMPA LOGIN
            # ======================================

            progress.visible = False

            page.clean()

            page.update()

            LOGGER.info(
                "Tela login limpa"
            )

            # ======================================
            # MAIN LAYOUT
            # ======================================

            from ui.main_layout import (
                carregar_main_layout
            )

            LOGGER.info(
                "Carregando main layout"
            )

            carregar_main_layout(
                page,
                usuario
            )

            LOGGER.info(
                "Main layout carregado"
            )

            page.update()

        except Exception as ex:

            LOGGER.exception(
                "LOGIN ERROR"
            )

            progress.visible = False

            txt_status.value = str(ex)

            page.update()

    # ==============================================
    # ENTER
    # ==============================================

    txt_user.on_submit = realizar_login

    txt_pass.on_submit = realizar_login

    # ==============================================
    # BUTTONS
    # ==============================================

    btn_login = ft.ElevatedButton(

        "Entrar",

        width=320,

        height=45,

        icon=ft.Icons.LOGIN,

        on_click=realizar_login
    )

    btn_exit = ft.OutlinedButton(

        "Sair",

        width=320,

        height=45,

        icon=ft.Icons.CLOSE,

        on_click=lambda e: close_app(page)
    )

    # ==============================================
    # CARD
    # ==============================================

    login_card = ft.Card(

        elevation=8,

        content=ft.Container(

            width=420,

            padding=40,

            border_radius=20,

            content=ft.Column(

                [

                    ft.Icon(

                        ft.Icons.ADMIN_PANEL_SETTINGS,

                        size=72,

                        color=ft.Colors.BLUE
                    ),

                    ft.Text(

                        APP_CONFIG["name"],

                        size=30,

                        weight="bold"
                    ),

                    ft.Text(

                        (
                            f"Versão "
                            f"{APP_CONFIG['version']}"
                        ),

                        size=14,

                        color=ft.Colors.GREY_700
                    ),

                    ft.Divider(),

                    txt_user,

                    txt_pass,

                    txt_status,

                    progress,

                    btn_login,

                    btn_exit

                ],

                spacing=18,

                horizontal_alignment=(

                    ft.CrossAxisAlignment.CENTER
                )
            )
        )
    )

    # ==============================================
    # PAGE
    # ==============================================

    return ft.Container(

        expand=True,

        alignment=ft.Alignment(0, 0),

        bgcolor=ft.Colors.GREY_100,

        content=login_card
    )