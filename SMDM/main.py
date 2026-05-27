# =========================================================
# main.py
# =========================================================

import logging

import flet as ft

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

            page.window.center()

        except Exception:

            LOGGER.warning(
                "Window API indisponível."
            )

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

    ft.app(

        target=main,

        view=ft.AppView.FLET_APP,

        host="127.0.0.1",

        port=8550,
    )