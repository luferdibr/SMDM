
import logging

import flet as ft

from config.settings import (
    APP_CONFIG,
    DB_CONFIG
)

from services.install_service import (
    garantir_instalacao
)

from services.migration_service import (
    executar_migracoes
)

from services.bootstrap_service import (
    iniciar_sistema
)

from services.auditoria_service import (
    registrar_evento
)

from ui.login import (
    login_view
)


# ==================================================
# LOGGER
# ==================================================

logging.basicConfig(

    level=logging.INFO,

    format=(
        "%(asctime)s "
        "[%(levelname)s] "
        "%(message)s"
    )
)

LOGGER = logging.getLogger(
    "MDM_MAIN"
)


# ==================================================
# HELPERS
# ==================================================

def auditoria_segura(**kwargs):

    try:

        registrar_evento(**kwargs)

    except Exception:

        LOGGER.exception(
            "AUDITORIA ERROR"
        )


# ==================================================
# ERRO FATAL
# ==================================================

def exibir_erro_fatal(
    page,
    erro
):

    LOGGER.exception(
        "FATAL STARTUP ERROR"
    )

    page.clean()

    page.add(

        ft.Container(

            expand=True,

            bgcolor=ft.Colors.RED_50,

            alignment=(
                ft.Alignment(0, 0)
            ),

            content=ft.Column(

                [

                    ft.Icon(

                        ft.Icons.ERROR,

                        size=90,

                        color=ft.Colors.RED
                    ),

                    ft.Text(

                        "Erro fatal na aplicação",

                        size=28,

                        weight="bold",

                        color=ft.Colors.RED
                    ),

                    ft.Text(

                        str(erro),

                        size=15
                    )

                ],

                spacing=20,

                horizontal_alignment=(
                    ft.CrossAxisAlignment.CENTER
                )
            )
        )
    )

    page.update()


# ==================================================
# STARTUP
# ==================================================

def startup_install():

    LOGGER.info(
        "Validando instalação..."
    )

    garantir_instalacao()

    LOGGER.info(
        "Instalação validada."
    )


def startup_migrations():

    LOGGER.info(
        "Executando migrations..."
    )

    executar_migracoes()

    LOGGER.info(
        "Migrations concluídas."
    )


def startup_bootstrap():

    LOGGER.info(
        "Inicializando bootstrap..."
    )

    iniciar_sistema()

    LOGGER.info(
        "Bootstrap validado."
    )


# ==================================================
# APP
# ==================================================

def inicializar_sistema(page):

    LOGGER.info(
        "Inicializando aplicação."
    )

    startup_install()

    startup_migrations()

    startup_bootstrap()

    auditoria_segura(

        login="SYSTEM",

        acao="SYSTEM_BOOT",

        entidade="SYSTEM"
    )

    LOGGER.info(
        "Aplicação pronta."
    )


# ==================================================
# MAIN VIEW
# ==================================================

def main(page: ft.Page):

    try:

        LOGGER.info(
            "Iniciando aplicação..."
        )

        # ==========================================
        # PAGE
        # ==========================================

        page.title = APP_CONFIG[
            "name"
        ]

        page.theme_mode = (
            ft.ThemeMode.LIGHT
        )

        page.window.width = 1280

        page.window.height = 850

        page.window.min_width = 1000

        page.window.min_height = 700

        page.padding = 0

        page.spacing = 0

        page.bgcolor = (
            ft.Colors.GREY_100
        )

        page.scroll = (
            ft.ScrollMode.AUTO
        )

        page.vertical_alignment = (
            ft.MainAxisAlignment.START
        )

        page.horizontal_alignment = (
            ft.CrossAxisAlignment.START
        )

        # ==========================================
        # LOGS
        # ==========================================

        LOGGER.info(

            f"Ambiente: "
            f"{APP_CONFIG['environment']}"
        )

        LOGGER.info(

            f"Aplicação: "
            f"{APP_CONFIG['name']}"
        )

        LOGGER.info(

            f"SQL Server: "
            f"{DB_CONFIG['server']}"
        )

        # ==========================================
        # STARTUP
        # ==========================================

        inicializar_sistema(page)

        # ==========================================
        # LOGIN
        # ==========================================

        page.clean()

        page.add(
            login_view(page)
        )

        page.update()

    except Exception as ex:

        exibir_erro_fatal(
            page,
            ex
        )


# ==================================================
# RUN
# ==================================================

if __name__ == "__main__":

    LOGGER.info(
        "Inicializando aplicação..."
    )

    ft.run(main)