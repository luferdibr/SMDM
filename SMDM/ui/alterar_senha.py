
import logging

import flet as ft

from modules.administracao.usuarios.services.user_service import (
    alterar_senha,
    validar_senha
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
    btn_salvar,
    btn_sair,
    txt_nova,
    txt_conf,
    page
):

    progress.visible = status

    btn_salvar.disabled = status

    btn_sair.disabled = status

    txt_nova.disabled = status

    txt_conf.disabled = status

    page.update()


def limpar_campos(
    txt_nova,
    txt_conf
):

    txt_nova.value = ""

    txt_conf.value = ""


# ==================================================
# VIEW
# ==================================================

def alterar_senha_view(page):

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

    obrigatoria = bool(

        usuario.get("trocar_senha")

        or

        usuario.get("senha_expirada")
    )

    login_usuario = str(

        usuario.get("login") or ""

    ).strip().upper()

    salvando = False

    # ==============================================
    # CAMPOS
    # ==============================================

    txt_nova = ft.TextField(

        label="Nova senha",

        password=True,

        can_reveal_password=True,

        width=340,

        autofocus=True,

        prefix_icon=ft.Icons.LOCK
    )

    txt_conf = ft.TextField(

        label="Confirmar senha",

        password=True,

        can_reveal_password=True,

        width=340,

        prefix_icon=ft.Icons.LOCK_RESET
    )

    txt_status = ft.Text(

        "",

        size=14,

        color=ft.Colors.RED
    )

    progress = ft.ProgressRing(

        visible=False
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

        width=160
    )

    btn_sair = ft.OutlinedButton(

        content=ft.Row(
            spacing=6,
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                ft.Icon(ft.Icons.LOGOUT, size=16),
                ft.Text(
                    (
                        "Logout"
                        if obrigatoria
                        else "Voltar"
                    ),
                    size=12,
                ),
            ],
        ),

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
    # SALVAR
    # ==============================================

    def salvar(e=None):

        nonlocal salvando

        if salvando:
            return

        salvando = True

        bloquear_ui(

            True,

            progress,

            btn_salvar,

            btn_sair,

            txt_nova,

            txt_conf,

            page
        )

        txt_status.value = ""

        page.update()

        try:

            usuario_local = get_usuario(
                page
            )

            if not usuario_local:

                raise Exception(
                    "Sessão inválida."
                )

            senha = str(

                txt_nova.value or ""

            ).strip()

            confirmar = str(

                txt_conf.value or ""

            ).strip()

            # ======================================
            # VAZIA
            # ======================================

            if not senha:

                status(
                    "Informe a nova senha."
                )

                txt_nova.focus()

                return

            if not confirmar:

                status(
                    "Confirme a senha."
                )

                txt_conf.focus()

                return

            # ======================================
            # DIFERENTE
            # ======================================

            if senha != confirmar:

                status(
                    "As senhas não conferem."
                )

                txt_conf.focus()

                return

            # ======================================
            # LOGIN
            # ======================================

            if senha.upper() == login_usuario:

                status(
                    "A senha não pode ser igual ao login."
                )

                return

            # ======================================
            # FORÇA
            # ======================================

            if not validar_senha(
                senha
            ):

                status(
                    (
                        "Senha inválida. "
                        "Use letras, números, símbolos "
                        "e mínimo 9 caracteres."
                    )
                )

                return

            # ======================================
            # SERVICE
            # ======================================

            resultado = alterar_senha(

                usuario_local["id"],

                senha
            )

            if not resultado["sucesso"]:

                status(
                    resultado["mensagem"]
                )

                return

            # ======================================
            # FLAGS
            # ======================================

            usuario_local[
                "trocar_senha"
            ] = False

            usuario_local[
                "senha_expirada"
            ] = False

            page.usuario_logado = (
                usuario_local
            )

            limpar_campos(
                txt_nova,
                txt_conf
            )

            logging.info(

                "Senha alterada usuário=%s",

                login_usuario
            )

            exibir_snackbar(

                page,

                "Senha alterada com sucesso."
            )

            # ======================================
            # DASHBOARD
            # ======================================

            from ui.main_layout import (
                carregar_main_layout
            )

            carregar_main_layout(page)

        except Exception:

            logging.exception(
                "CHANGE PASSWORD VIEW ERROR"
            )

            status(
                "Erro interno ao alterar senha."
            )

        finally:

            salvando = False

            bloquear_ui(

                False,

                progress,

                btn_salvar,

                btn_sair,

                txt_nova,

                txt_conf,

                page
            )

    # ==============================================
    # ENTER
    # ==============================================

    txt_nova.on_submit = salvar

    txt_conf.on_submit = salvar

    btn_salvar.on_click = salvar

    # ==============================================
    # SAIR
    # ==============================================

    def sair(e=None):

        try:

            from security.session_service import (
                encerrar_sessao
            )

            from ui.login import (
                login_view
            )

            from ui.main_layout import (
                carregar_main_layout
            )

            # ======================================
            # OBRIGATÓRIA
            # ======================================

            if obrigatoria:

                encerrar_sessao()

                page.clean()

                login_view(page)

                return

            carregar_main_layout(page)

        except Exception:

            logging.exception(
                "PASSWORD EXIT ERROR"
            )

            exibir_snackbar(

                page,

                "Erro ao sair.",

                erro=True
            )

    btn_sair.on_click = sair

    # ==============================================
    # CARD
    # ==============================================

    card = ft.Container(

        content=ft.Column([

            ft.Icon(

                ft.Icons.LOCK_RESET,

                size=72,

                color=ft.Colors.ORANGE
            ),

            ft.Text(

                "Alteração de Senha",

                size=30,

                weight="bold"
            ),

            ft.Text(

                (

                    "Sua senha precisa ser alterada."

                    if obrigatoria

                    else

                    "Defina uma nova senha segura."
                ),

                size=14,

                color=ft.Colors.GREY_700
            ),

            ft.Divider(),

            txt_nova,

            txt_conf,

            ft.Container(

                content=ft.Column([

                    ft.Text(
                        "Requisitos da senha:",
                        weight="bold"
                    ),

                    ft.Text(
                        "• mínimo 9 caracteres"
                    ),

                    ft.Text(
                        "• letras"
                    ),

                    ft.Text(
                        "• números"
                    ),

                    ft.Text(
                        "• símbolos"
                    ),

                    ft.Text(
                        "• diferente do login"
                    )

                ],

                    spacing=2
                ),

                padding=12,

                border_radius=10,

                bgcolor=ft.Colors.GREY_100
            ),

            txt_status,

            progress,

            ft.Row([

                btn_salvar,

                btn_sair

            ],

                alignment=ft.MainAxisAlignment.CENTER
            )

        ],

            spacing=18,

            horizontal_alignment=(
                ft.CrossAxisAlignment.CENTER
            )
        ),

        width=480,

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

        content=card,

        expand=True,

        alignment=ft.Alignment(0, 0),

        bgcolor=ft.Colors.GREY_100
    )
