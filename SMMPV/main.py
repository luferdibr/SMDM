
import logging
import traceback
from datetime import datetime

import flet as ft

from ui.login import login_view

from services.install_service import (
    garantir_instalacao
)

from services.bootstrap_service import (
    iniciar_sistema
)

from services.auditoria_service import (
    registrar_evento,
    registrar_erro
)

from config.settings import (

    APP_NAME,

    APP_VERSION
)


# ==================================================
# LOGGER CENTRAL
# ==================================================

LOGGER = logging.getLogger("SMMPV")


def configurar_logging():

    if LOGGER.handlers:
        return

    LOGGER.setLevel(logging.INFO)

    formatter = logging.Formatter(

        (
            "%(asctime)s "
            "[%(levelname)s] "
            "%(message)s"
        )
    )

    console = logging.StreamHandler()

    console.setFormatter(formatter)

    LOGGER.addHandler(console)


# ==================================================
# HELPERS
# ==================================================

def limpar_page(page):

    try:

        page.clean()

    except Exception:

        LOGGER.exception(
            "PAGE CLEAN ERROR"
        )


def mostrar_erro(
    page,
    titulo,
    mensagem
):

    limpar_page(page)

    page.add(

        ft.Container(

            content=ft.Column([

                ft.Icon(

                    ft.Icons.ERROR,

                    size=90,

                    color=ft.Colors.RED
                ),

                ft.Text(

                    titulo,

                    size=28,

                    weight="bold",

                    color=ft.Colors.RED
                ),

                ft.Container(

                    content=ft.Text(

                        str(mensagem),

                        selectable=True,

                        size=15
                    ),

                    padding=15,

                    border_radius=10,

                    bgcolor=ft.Colors.RED_50
                )

            ],

                spacing=20,

                horizontal_alignment=(
                    ft.CrossAxisAlignment.CENTER
                )
            ),

            expand=True,

            alignment=ft.Alignment(0, 0),

            padding=30
        )
    )

    page.update()


def mostrar_loading(
    page,
    titulo,
    mensagem
):

    limpar_page(page)

    page.add(

        ft.Container(

            content=ft.Column([

                ft.ProgressRing(),

                ft.Text(

                    titulo,

                    size=24,

                    weight="bold"
                ),

                ft.Text(
                    mensagem,
                    size=15
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


# ==================================================
# PAGE CONFIG
# ==================================================

def configurar_pagina(page: ft.Page):

    page.title = (
        f"{APP_NAME} "
        f"{APP_VERSION}"
    )

    # ==============================================
    # THEME
    # ==============================================

    page.theme_mode = ft.ThemeMode.LIGHT

    page.theme = ft.Theme(

        color_scheme_seed=ft.Colors.BLUE
    )

    page.bgcolor = ft.Colors.GREY_100

    # ==============================================
    # LAYOUT
    # ==============================================

    page.padding = 0

    page.spacing = 0

    page.scroll = ft.ScrollMode.AUTO

    page.horizontal_alignment = (
        ft.CrossAxisAlignment.START
    )

    page.vertical_alignment = (
        ft.MainAxisAlignment.START
    )

    # ==============================================
    # WINDOW
    # ==============================================

    page.window_width = 1440

    page.window_height = 920

    page.window_min_width = 1200

    page.window_min_height = 700

    # ==============================================
    # APP STATE
    # ==============================================

    page.usuario_logado = None

    page.menu_cache = None

    page.rota_atual = None

    page.conteudo = None

    page.app_inicializada = False

    page.app_bootstrap = False

    page.start_time = datetime.now()

    # ==============================================
    # LIMPAR
    # ==============================================

    limpar_page(page)


# ==================================================
# FECHAR APP
# ==================================================

def fechar_aplicacao(page):

    try:

        LOGGER.info(
            "Encerrando aplicação..."
        )

        # ==========================================
        # LIMPAR ESTADO
        # ==========================================

        page.usuario_logado = None

        page.menu_cache = None

        page.rota_atual = None

        page.conteudo = None

        # ==========================================
        # FECHAR
        # ==========================================

        page.window.close()

    except Exception:

        LOGGER.exception(
            "APP CLOSE ERROR"
        )


# ==================================================
# ERROR HANDLER
# ==================================================

def tratar_erro_global(
    page,
    erro,
    contexto="APP"
):

    LOGGER.exception(
        f"GLOBAL ERROR {contexto}"
    )

    try:

        registrar_erro(

            erro,

            modulo=contexto
        )

    except Exception:
        pass

    mostrar_erro(

        page,

        "Erro interno do sistema",

        (
            f"{erro}\n\n"
            f"{traceback.format_exc()}"
        )
    )


# ==================================================
# STARTUP INSTALL
# ==================================================

def startup_instalacao(page):

    mostrar_loading(

        page,

        "Validando instalação",

        (
            "Preparando estrutura "
            "do banco de dados..."
        )
    )

    garantir_instalacao()

    LOGGER.info(
        "Instalação validada."
    )


# ==================================================
# STARTUP BOOTSTRAP
# ==================================================

def startup_bootstrap(page):

    mostrar_loading(

        page,

        "Inicializando sistema",

        (
            "Carregando serviços "
            "principais..."
        )
    )

    iniciar_sistema()

    LOGGER.info(
        "Bootstrap validado."
    )


# ==================================================
# STARTUP LOGIN
# ==================================================

def startup_login(page):

    mostrar_loading(

        page,

        "Carregando login",

        (
            "Inicializando "
            "interface..."
        )
    )

    limpar_page(page)

    page.add(
        login_view(page)
    )

    page.update()


# ==================================================
# MAIN
# ==================================================

def main(page: ft.Page):

    LOGGER.info(
        "Inicializando aplicação."
    )

    try:

        # ==========================================
        # CONFIG
        # ==========================================

        configurar_pagina(page)

        # ==========================================
        # INSTALL
        # ==========================================

        startup_instalacao(page)

        # ==========================================
        # BOOTSTRAP
        # ==========================================

        startup_bootstrap(page)

        # ==========================================
        # LOGIN
        # ==========================================

        startup_login(page)

        # ==========================================
        # STATE
        # ==========================================

        page.app_inicializada = True

        page.app_bootstrap = True

        # ==========================================
        # AUDITORIA
        # ==========================================

        registrar_evento(

            evento="SYSTEM_BOOT",

            descricao=(
                "Sistema inicializado."
            ),

            modulo="main"
        )

        LOGGER.info(
            "Aplicação pronta."
        )

    except Exception as ex:

        tratar_erro_global(

            page,

            ex,

            contexto="MAIN"
        )


# ==================================================
# STARTUP
# ==================================================

if __name__ == "__main__":

    configurar_logging()

    try:

        LOGGER.info(
            "Iniciando aplicação..."
        )

        ft.run(main)

    except KeyboardInterrupt:

        LOGGER.info(
            "Aplicação encerrada."
        )

    except Exception as ex:

        LOGGER.exception(
            "FATAL APP ERROR"
        )

        try:

            registrar_erro(

                ex,

                modulo="startup"
            )

        except Exception:
            pass

        raise