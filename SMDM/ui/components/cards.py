# =========================================================
# ui/components/cards.py
# =========================================================

import flet as ft

from core.themes import (

    SURFACE_COLOR,

    BACKGROUND_COLOR,

    TEXT_PRIMARY,

    TEXT_SECONDARY,

    BORDER_COLOR,

    CARD_RADIUS,

    CARD_PADDING,
)

# =========================================================
# APP CARD
# =========================================================

def app_card(

    content,

    title=None,

    subtitle=None,

    padding=CARD_PADDING,

    bgcolor=SURFACE_COLOR,

    elevation=1,

    margin=10,

    expand=False,
):

    controls = []

    # =====================================================
    # HEADER
    # =====================================================

    if title:

        controls.append(

            ft.Text(

                title,

                size=18,

                weight=(
                    ft.FontWeight.BOLD
                ),

                color=TEXT_PRIMARY,
            )
        )

    if subtitle:

        controls.append(

            ft.Text(

                subtitle,

                size=12,

                color=TEXT_SECONDARY,
            )
        )

    if title or subtitle:

        controls.append(
            ft.Divider(height=1)
        )

    # =====================================================
    # CONTENT
    # =====================================================

    controls.append(content)

    return ft.Card(

        expand=expand,

        elevation=elevation,

        margin=margin,

        content=ft.Container(

            bgcolor=bgcolor,

            padding=padding,

            border_radius=CARD_RADIUS,

            expand=expand,

            content=ft.Column(

                controls=controls,

                spacing=10,
            ),
        ),
    )

# =========================================================
# MESSAGE CARD
# =========================================================

def message_card(

    title,

    message,

    icon=None,
):

    controls = []

    if icon:

        controls.append(

            ft.Icon(
                icon,
                size=48,
            )
        )

    controls.extend(

        [

            ft.Text(

                title,

                size=20,

                weight=(
                    ft.FontWeight.BOLD
                ),
            ),

            ft.Text(
                message
            ),
        ]
    )

    return app_card(

        content=ft.Column(

            controls=controls,

            horizontal_alignment=(
                ft.CrossAxisAlignment.CENTER
            ),

            spacing=12,
        ),

        padding=30,
    )

# =========================================================
# ERROR CARD
# =========================================================

def error_card(
    message,
):

    return message_card(

        title="Erro",

        message=message,

        icon=ft.Icons.ERROR,
    )

# =========================================================
# SUCCESS CARD
# =========================================================

def success_card(
    message,
):

    return message_card(

        title="Sucesso",

        message=message,

        icon=ft.Icons.CHECK_CIRCLE,
    )

# =========================================================
# WARNING CARD
# =========================================================

def warning_card(
    message,
):

    return message_card(

        title="Aviso",

        message=message,

        icon=ft.Icons.WARNING,
    )

# =========================================================
# INFO CARD
# =========================================================

def info_card(
    message,
):

    return message_card(

        title="Informação",

        message=message,

        icon=ft.Icons.INFO,
    )


# =========================================================
# EMPTY CARD
# =========================================================

def empty_card(

    message="Nenhum registro encontrado.",
):

    return app_card(

        content=ft.Container(

            padding=20,

            alignment=ft.Alignment(0, 0),

            content=ft.Text(

                message,

                size=13,

                color=TEXT_SECONDARY,
            ),
        )
    )


# =========================================================
# SECTION CARD
# =========================================================

def section_card(

    title,

    subtitle=None,

    icon=None,

    content=None,

    expand=False,
):

    header_controls = []

    if icon:

        header_controls.append(

            ft.Icon(
                icon,
                size=18,
                color=TEXT_SECONDARY,
            )
        )

    header_controls.append(

        ft.Column(

            spacing=0,

            expand=True,

            controls=[

                ft.Text(
                    title,
                    size=14,
                    weight=ft.FontWeight.BOLD,
                    color=TEXT_PRIMARY,
                ),

                ft.Text(
                    subtitle or "",
                    size=11,
                    color=TEXT_SECONDARY,
                    visible=bool(subtitle),
                ),
            ],
        )
    )

    return app_card(

        expand=expand,

        content=ft.Column(

            expand=expand,

            spacing=10,

            controls=[

                ft.Row(
                    spacing=8,
                    controls=header_controls,
                    vertical_alignment=(
                        ft.CrossAxisAlignment.CENTER
                    ),
                ),

                ft.Divider(height=1),

                content or ft.Container(),
            ],
        ),
    )

# =========================================================
# PAGE CONTAINER
# =========================================================

def page_container(

    content,

    padding=20,

    expand=True,
):

    return ft.Container(

        expand=expand,

        padding=padding,

        bgcolor=BACKGROUND_COLOR,

        content=content,
    )
