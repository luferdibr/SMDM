# =========================================================
# main.py
# =========================================================

import logging

import flet as ft

from core.flet_compat import (
    aplicar_compatibilidade_flet,
)

aplicar_compatibilidade_flet()

from services.bootstrap_service import (
    iniciar_sistema,
)

from services.install_service import (
    garantir_instalacao,
)

from ui.login import (
    login_view,
)

# =========================================================
# LOGGING
# =========================================================

logging.basicConfig(

    level=logging.INFO,

    format=(
        "%(asctime)s "
        "[%(levelname)s] "
        "%(message)s"
    ),
)

LOGGER = logging.getLogger(
    "SMDM_MAIN"
)

# =========================================================
# STATUS
# =========================================================

def mostrar_status_validacao(
    page: ft.Page,
):

    page.clean()

    page.add(

        ft.Container(

            expand=True,

            alignment=ft.Alignment(0, 0),

            content=ft.Column(

                horizontal_alignment=ft.CrossAxisAlignment.CENTER,

                alignment=ft.MainAxisAlignment.CENTER,

                spacing=16,

                controls=[

                    ft.ProgressRing(
                        width=42,
                        height=42,
                    ),

                    ft.Text(
                        "Validando a estrutura do sistema",
                        size=22,
                        weight=ft.FontWeight.BOLD,
                    ),

                    ft.Text(
                        "Aguarde enquanto tabelas, menus e dados iniciais são conferidos.",
                        size=13,
                        color=ft.Colors.GREY_700,
                    ),
                ],
            ),
        )
    )

    page.update()

# =========================================================
# MAIN
# =========================================================

def main(
    page: ft.Page,
):

    LOGGER.info(
        "Inicializando SMDM."
    )

    try:

        # =================================================
        # PAGE CONFIG
        # =================================================

        page.title = "SMDM"

        page.bgcolor = (
            ft.Colors.GREY_100
        )

        page.padding = 0

        page.spacing = 0

        page.scroll = (
            ft.ScrollMode.AUTO
        )

        # =================================================
        # WINDOW CONFIG
        # =================================================

        try:

            page.window.width = 1400

            page.window.height = 900

        except Exception:

            LOGGER.warning(
                "Window API indisponível."
            )

        # A instalacao e o bootstrap tambem corrigem dados
        # estruturais ja existentes, como a hierarquia do menu.
        mostrar_status_validacao(
            page
        )

        garantir_instalacao()

        iniciar_sistema()

        # =================================================
        # LOGIN
        # =================================================

        login_view(page)

        LOGGER.info(
            "Login carregado."
        )

    except Exception as ex:

        LOGGER.exception(
            "Erro fatal."
        )

        page.clean()

        page.add(

            ft.Container(

                expand=True,

                alignment=(
                    ft.Alignment(0, 0)
                ),

                content=ft.Column(

                    horizontal_alignment=(
                        ft.CrossAxisAlignment.CENTER
                    ),

                    alignment=(
                        ft.MainAxisAlignment.CENTER
                    ),

                    controls=[

                        ft.Icon(

                            ft.Icons.ERROR,

                            size=72,

                            color=ft.Colors.RED,
                        ),

                        ft.Text(

                            "Erro fatal no sistema",

                            size=24,

                            weight=(
                                ft.FontWeight.BOLD
                            ),
                        ),

                        ft.Text(
                            str(ex)
                        ),
                    ],
                ),
            )
        )

        page.update()

# =========================================================
# START
# =========================================================

if __name__ == "__main__":

    LOGGER.info(
        "Iniciando servidor Flet."
    )

    ft.run(

        main,

        view=ft.AppView.FLET_APP,

        host="127.0.0.1",

        port=8550,
    )
