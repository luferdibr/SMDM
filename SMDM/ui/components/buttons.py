# =========================================================
# ui/components/buttons.py
# =========================================================

import flet as ft

from core.themes import (

    PRIMARY_COLOR,

    SUCCESS_COLOR,

    WARNING_COLOR,

    ERROR_COLOR,

    TEXT_ON_PRIMARY,

    BUTTON_HEIGHT,

    BUTTON_RADIUS,
)

# =========================================================
# BUTTON CONTENT
# =========================================================

def button_content(

    text,

    icon=None,
):

    controls = []

    if icon:

        controls.append(

            ft.Icon(

                icon,

                size=16,

                color=TEXT_ON_PRIMARY,
            )
        )

    controls.append(

        ft.Text(

            text,

            color=TEXT_ON_PRIMARY,
        )
    )

    return ft.Row(

        controls=controls,

        spacing=8,

        alignment=(
            ft.MainAxisAlignment.CENTER
        ),
    )

# =========================================================
# BASE BUTTON
# =========================================================

def app_button(

    text,

    on_click=None,

    icon=None,

    width=None,

    height=BUTTON_HEIGHT,

    bgcolor=PRIMARY_COLOR,

    disabled=False,
):

    return ft.FilledButton(

        content=button_content(
            text,
            icon,
        ),

        width=width,

        height=height,

        disabled=disabled,

        style=ft.ButtonStyle(

            bgcolor=bgcolor,

            shape=ft.RoundedRectangleBorder(

                radius=BUTTON_RADIUS
            ),
        ),

        on_click=on_click,
    )

# =========================================================
# PRIMARY BUTTON
# =========================================================

def primary_button(

    text,

    on_click=None,

    icon=None,

    width=None,
):

    return app_button(

        text=text,

        on_click=on_click,

        icon=icon,

        width=width,

        bgcolor=PRIMARY_COLOR,
    )

# =========================================================
# SUCCESS BUTTON
# =========================================================

def success_button(

    text,

    on_click=None,

    icon=None,

    width=None,
):

    return app_button(

        text=text,

        on_click=on_click,

        icon=icon,

        width=width,

        bgcolor=SUCCESS_COLOR,
    )

# =========================================================
# WARNING BUTTON
# =========================================================

def warning_button(

    text,

    on_click=None,

    icon=None,

    width=None,
):

    return app_button(

        text=text,

        on_click=on_click,

        icon=icon,

        width=width,

        bgcolor=WARNING_COLOR,
    )

# =========================================================
# DANGER BUTTON
# =========================================================

def danger_button(

    text,

    on_click=None,

    icon=None,

    width=None,
):

    return app_button(

        text=text,

        on_click=on_click,

        icon=icon,

        width=width,

        bgcolor=ERROR_COLOR,
    )

# =========================================================
# SAVE BUTTON
# =========================================================

def save_button(

    on_click=None,

    width=None,
):

    return success_button(

        text="Salvar",

        icon=ft.Icons.SAVE,

        width=width,

        on_click=on_click,
    )

# =========================================================
# NEW BUTTON
# =========================================================

def new_button(

    on_click=None,

    width=None,
):

    return primary_button(

        text="Novo",

        icon=ft.Icons.ADD,

        width=width,

        on_click=on_click,
    )

# =========================================================
# CANCEL BUTTON
# =========================================================

def cancel_button(

    on_click=None,

    width=None,
):

    return warning_button(

        text="Cancelar",

        icon=ft.Icons.CANCEL,

        width=width,

        on_click=on_click,
    )

# =========================================================
# DELETE BUTTON
# =========================================================

def delete_button(

    on_click=None,

    width=None,
):

    return danger_button(

        text="Excluir",

        icon=ft.Icons.DELETE,

        width=width,

        on_click=on_click,
    )

# =========================================================
# EDIT BUTTON
# =========================================================

def edit_button(

    on_click=None,

    width=None,
):

    return primary_button(

        text="Editar",

        icon=ft.Icons.EDIT,

        width=width,

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

    icon_size=None,

    disabled=False,
):

    return ft.IconButton(

        icon=icon,

        tooltip=tooltip,

        icon_color=icon_color,

        icon_size=icon_size,

        disabled=disabled,

        on_click=on_click,
    )

# =========================================================
# LOADING BUTTON
# =========================================================

class LoadingButton:

    def __init__(

        self,

        text="Salvar",

        icon=None,

        width=None,

        on_click=None,
    ):

        self.button_text = text

        self.button_icon = icon

        self.button_width = width

        self.user_on_click = (
            on_click
        )

        self.loading = False

        self.button = ft.FilledButton(

            content=button_content(

                self.button_text,

                self.button_icon,
            ),

            width=self.button_width,

            disabled=False,

            on_click=self.handle_click,
        )

    # =====================================================
    # SAFE UPDATE
    # =====================================================

    def safe_update(
        self,
    ):

        try:

            if self.button.page:

                self.button.update()

        except Exception:

            pass

    # =====================================================
    # CLICK
    # =====================================================

    def handle_click(

        self,

        e,
    ):

        if self.loading:

            return

        if self.user_on_click:

            self.user_on_click(e)

    # =====================================================
    # START LOADING
    # =====================================================

    def start_loading(
        self,
    ):

        self.loading = True

        self.button.disabled = True

        self.button.content = ft.Row(

            controls=[

                ft.ProgressRing(

                    width=16,

                    height=16,

                    stroke_width=2,
                ),

                ft.Text(
                    "Processando..."
                ),
            ],

            spacing=10,

            alignment=(
                ft.MainAxisAlignment.CENTER
            ),
        )

        self.safe_update()

    # =====================================================
    # STOP LOADING
    # =====================================================

    def stop_loading(
        self,
    ):

        self.loading = False

        self.button.disabled = False

        self.button.content = button_content(

            self.button_text,

            self.button_icon,
        )

        self.safe_update()

    # =====================================================
    # CONTROL
    # =====================================================

    @property
    def control(
        self,
    ):

        return self.button
