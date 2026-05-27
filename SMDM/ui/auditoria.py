# =========================================================
# ui/auditoria.py
# =========================================================

import logging

import flet as ft

from database.connection import (
    get_connection,
)

from ui.components.base_view import (
    base_view,
)

from ui.components.cards import (
    section_card,
)

from ui.components.tables import (
    simple_table,
    table_row,
    text_cell,
)

from utils.error_formatter import (
    format_error_message,
)

# =========================================================
# LOGGER
# =========================================================

LOGGER = logging.getLogger(
    "SMDM_AUDITORIA_VIEW"
)

# =========================================================
# DATA
# =========================================================

def listar_auditoria(
    limite=100,
):

    conn = None

    try:

        conn = get_connection()

        cursor = conn.cursor()

        cursor.execute(

            """

            SELECT TOP (?)

                Id,
                CriadoEm,
                Login,
                Acao,
                Entidade,
                RegistroId,
                Severidade,
                Sucesso,
                Detalhes

            FROM Auditoria

            ORDER BY Id DESC

            """,

            (
                int(limite),
            ),
        )

        return cursor.fetchall()

    finally:

        try:

            if conn:

                conn.close()

        except Exception:

            pass

# =========================================================
# VIEW
# =========================================================

def auditoria_view(
    page: ft.Page,
):

    LOGGER.info(
        "Carregando auditoria."
    )

    try:

        rows = []

        for item in listar_auditoria():

            sucesso = (
                "Sim"
                if bool(item[7])
                else "Não"
            )

            rows.append(

                table_row(

                    controls=[

                        text_cell(
                            item[0],
                            width=55,
                        ),

                        text_cell(
                            item[1],
                            width=140,
                        ),

                        text_cell(
                            item[2],
                            width=90,
                        ),

                        text_cell(
                            item[3],
                            width=110,
                        ),

                        text_cell(
                            item[4],
                            width=110,
                        ),

                        text_cell(
                            item[5],
                            width=80,
                        ),

                        text_cell(
                            item[6],
                            width=80,
                        ),

                        text_cell(
                            sucesso,
                            width=55,
                        ),

                        text_cell(
                            item[8],
                            expand=True,
                        ),
                    ]
                )
            )

        content = section_card(

            title="Auditoria",

            subtitle="Últimos registros do sistema",

            icon=ft.Icons.HISTORY,

            content=simple_table(

                dense=True,

                columns=[

                    {
                        "label": "ID",
                        "width": 55,
                    },

                    {
                        "label": "Data",
                        "width": 140,
                    },

                    {
                        "label": "Login",
                        "width": 90,
                    },

                    {
                        "label": "Ação",
                        "width": 110,
                    },

                    {
                        "label": "Entidade",
                        "width": 110,
                    },

                    {
                        "label": "Registro",
                        "width": 80,
                    },

                    {
                        "label": "Nível",
                        "width": 80,
                    },

                    {
                        "label": "OK",
                        "width": 55,
                    },

                    {
                        "label": "Detalhes",
                        "expand": True,
                    },
                ],

                rows=rows,
            ),
        )

        return base_view(

            title="Auditoria",

            subtitle="Eventos recentes do sistema",

            content_controls=[
                content,
            ],
        )

    except Exception as ex:

        LOGGER.exception(
            "Erro auditoria view."
        )

        return base_view(

            title="Auditoria",

            subtitle="Erro carregando auditoria",

            content_controls=[

                ft.Container(

                    padding=20,

                    content=ft.Text(
                        format_error_message(ex),
                        selectable=True,
                        color=ft.Colors.RED,
                    ),
                )
            ],
        )
