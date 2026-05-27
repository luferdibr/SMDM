# ui/components/loading.py

import flet as ft

from core.themes import (
    BACKGROUND_COLOR,
    SURFACE_COLOR,
    PRIMARY_COLOR,
)

# =========================================================
# INLINE LOADING
# =========================================================

def inline_loading(
    visible=True,
    size=22,
):

    return ft.ProgressRing(
        visible=visible,
        width=size,
        height=size,
        stroke_width=3,
        color=PRIMARY_COLOR,
    )

# =========================================================
# CENTER LOADING
# =========================================================

def center_loading(
    message="Carregando...",
):

    return ft.Container(
        expand=True,
        alignment=ft.Alignment(x=0, y=0),
        content=ft.Column(
            controls=[
                ft.ProgressRing(
                    width=42,
                    height=42,
                    stroke_width=4,
                    color=PRIMARY_COLOR,
                ),

                ft.Text(
                    message,
                    size=16,
                ),
            ],
            spacing=20,
            horizontal_alignment=(
                ft.CrossAxisAlignment.CENTER
            ),
        ),
    )

# =========================================================
# PAGE LOADING
# =========================================================

def page_loading(
    message="Carregando página...",
):

    return ft.Container(
        expand=True,
        bgcolor=BACKGROUND_COLOR,
        alignment=ft.Alignment(x=0, y=0),
        content=ft.Column(
            controls=[
                ft.ProgressRing(
                    width=48,
                    height=48,
                    stroke_width=4,
                    color=PRIMARY_COLOR,
                ),

                ft.Text(
                    message,
                    size=16,
                ),
            ],
            spacing=24,
            horizontal_alignment=(
                ft.CrossAxisAlignment.CENTER
            ),
        ),
    )

# =========================================================
# CARD LOADING
# =========================================================

def card_loading(
    height=180,
):

    return ft.Container(
        height=height,
        border_radius=16,
        bgcolor=SURFACE_COLOR,
        alignment=ft.Alignment(x=0, y=0),
        content=ft.ProgressRing(
            width=36,
            height=36,
            stroke_width=4,
            color=PRIMARY_COLOR,
        ),
    )

# =========================================================
# TABLE LOADING
# =========================================================

def table_loading():

    return ft.Container(
        padding=40,
        alignment=ft.Alignment(x=0, y=0),
        content=ft.ProgressRing(
            width=36,
            height=36,
            stroke_width=4,
            color=PRIMARY_COLOR,
        ),
    )

# =========================================================
# BUTTON LOADING
# =========================================================

def button_loading(
    text="Processando...",
):

    return ft.Row(
        controls=[
            ft.ProgressRing(
                width=16,
                height=16,
                stroke_width=2,
                color=ft.Colors.WHITE,
            ),

            ft.Text(
                text,
                color=ft.Colors.WHITE,
            ),
        ],
        spacing=10,
        tight=True,
    )

# =========================================================
# LOADING OVERLAY
# =========================================================

def loading_overlay(
    visible=False,
    message="Processando...",
):

    overlay = ft.Container(
        visible=visible,
        expand=True,
        bgcolor=ft.Colors.with_opacity(
            0.6,
            ft.Colors.BLACK,
        ),
        alignment=ft.Alignment(x=0, y=0),
        content=ft.Container(
            width=260,
            padding=24,
            border_radius=20,
            bgcolor=SURFACE_COLOR,
            content=ft.Column(
                controls=[
                    ft.ProgressRing(
                        width=42,
                        height=42,
                        stroke_width=4,
                        color=PRIMARY_COLOR,
                    ),

                    ft.Text(
                        message,
                        size=16,
                        text_align=(
                            ft.TextAlign.CENTER
                        ),
                    ),
                ],
                spacing=20,
                horizontal_alignment=(
                    ft.CrossAxisAlignment.CENTER
                ),
                tight=True,
            ),
        ),
    )

    return overlay

# =========================================================
# SHOW OVERLAY
# =========================================================

def show_overlay(
    overlay,
    page: ft.Page,
):

    overlay.visible = True

    page.update()

# =========================================================
# HIDE OVERLAY
# =========================================================

def hide_overlay(
    overlay,
    page: ft.Page,
):

    overlay.visible = False

    page.update()

# =========================================================
# LOADING DIALOG
# =========================================================

def loading_dialog(
    page: ft.Page,
    message="Processando...",
):

    dlg = ft.AlertDialog(
        modal=True,
        content=ft.Row(
            controls=[
                ft.ProgressRing(
                    width=24,
                    height=24,
                    stroke_width=3,
                    color=PRIMARY_COLOR,
                ),

                ft.Text(message),
            ],
            spacing=20,
            tight=True,
        ),
    )

    page.dialog = dlg

    dlg.open = True

    page.update()

    return dlg

# =========================================================
# CLOSE LOADING DIALOG
# =========================================================

def close_loading_dialog(
    page: ft.Page,
    dialog,
):

    dialog.open = False

    page.update()
