# ui/components/buttons.py

import flet as ft

from core.themes import (
    PRIMARY_COLOR,
    ERROR_COLOR,
    FILLED_BUTTON_STYLE,
    OUTLINED_BUTTON_STYLE,
)

# =========================================================
# BUTTON CONTENT
# =========================================================

def _button_content(
    text,
    icon=None,
    color=None,
):

    controls = []

    if icon:

        controls.append(
            ft.Icon(
                icon,
                size=16,
                color=color,
            )
        )

    controls.append(
        ft.Text(
            text,
            size=12,
            color=color,
        )
    )

    return ft.Row(
        spacing=6,
        alignment=ft.MainAxisAlignment.CENTER,
        controls=controls,
    )

# =========================================================
# PRIMARY BUTTON
# =========================================================

def primary_button(
    text: str,
    on_click=None,
    icon=None,
    width=None,
    height=44,
    disabled=False,
    expand=False,
):

    return ft.FilledButton(
        content=_button_content(
            text,
            icon,
            ft.Colors.WHITE,
        ),
        width=width,
        height=height,
        disabled=disabled,
        expand=expand,
        style=FILLED_BUTTON_STYLE,
        on_click=on_click,
    )

# =========================================================
# SECONDARY BUTTON
# =========================================================

def secondary_button(
    text: str,
    on_click=None,
    icon=None,
    width=None,
    height=44,
    disabled=False,
    expand=False,
):

    return ft.OutlinedButton(
        content=_button_content(
            text,
            icon,
            PRIMARY_COLOR,
        ),
        width=width,
        height=height,
        disabled=disabled,
        expand=expand,
        style=OUTLINED_BUTTON_STYLE,
        on_click=on_click,
    )

# =========================================================
# TEXT BUTTON
# =========================================================

def text_button(
    text: str,
    on_click=None,
    icon=None,
    disabled=False,
):

    return ft.TextButton(
        content=_button_content(
            text,
            icon,
            PRIMARY_COLOR,
        ),
        disabled=disabled,
        on_click=on_click,
    )

# =========================================================
# DANGER BUTTON
# =========================================================

def danger_button(
    text: str,
    on_click=None,
    icon=ft.Icons.DELETE_OUTLINE,
    width=None,
    height=44,
    disabled=False,
):

    return ft.FilledButton(
        content=_button_content(
            text,
            icon,
            ft.Colors.WHITE,
        ),
        width=width,
        height=height,
        disabled=disabled,
        style=ft.ButtonStyle(
            bgcolor=ERROR_COLOR,
            color=ft.Colors.WHITE,
            shape=ft.RoundedRectangleBorder(
                radius=12
            ),
            padding=16,
        ),
        on_click=on_click,
    )

# =========================================================
# ICON BUTTON
# =========================================================

def icon_button(
    icon,
    on_click=None,
    tooltip=None,
    icon_color=None,
    selected=False,
):

    return ft.IconButton(
        icon=icon,
        tooltip=tooltip,
        icon_color=icon_color,
        selected=selected,
        on_click=on_click,
    )

# =========================================================
# SAVE BUTTON
# =========================================================

def save_button(
    on_click=None,
    disabled=False,
):

    return primary_button(
        text="Salvar",
        icon=ft.Icons.SAVE_OUTLINED,
        on_click=on_click,
        disabled=disabled,
    )

# =========================================================
# NEW BUTTON
# =========================================================

def new_button(
    on_click=None,
):

    return secondary_button(
        text="Novo",
        icon=ft.Icons.ADD,
        on_click=on_click,
    )

# =========================================================
# DELETE BUTTON
# =========================================================

def delete_button(
    on_click=None,
    disabled=False,
):

    return danger_button(
        text="Excluir",
        icon=ft.Icons.DELETE_OUTLINE,
        on_click=on_click,
        disabled=disabled,
    )

# =========================================================
# BACK BUTTON
# =========================================================

def back_button(
    on_click=None,
):

    return text_button(
        text="Voltar",
        icon=ft.Icons.ARROW_BACK,
        on_click=on_click,
    )

# =========================================================
# REFRESH BUTTON
# =========================================================

def refresh_button(
    on_click=None,
):

    return icon_button(
        icon=ft.Icons.REFRESH,
        tooltip="Atualizar",
        on_click=on_click,
    )
