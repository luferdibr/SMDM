# =========================================================
# ui/components/dialogs.py
# =========================================================

import traceback

import flet as ft

from core.state.state import (
    set_operational_mode,
    set_temp,
    get_temp,
)

from core.themes import (
    ERROR_COLOR,
    PRIMARY_COLOR,
    SUCCESS_COLOR,
)

# =========================================================
# CONFIG
# =========================================================

DIALOG_WIDTH = 420

FULLSCREEN_PADDING = 16

# =========================================================
# STACK
# =========================================================

def get_dialog_stack(
    page,
):

    stack = get_temp(
        "dialog_stack"
    )

    if stack is None:

        stack = []

        set_temp(
            "dialog_stack",
            stack,
        )

    return stack

# =========================================================
# OPEN
# =========================================================

def open_dialog(
    page: ft.Page,
    dialog,
):

    stack = get_dialog_stack(
        page
    )

    if dialog not in page.overlay:

        page.overlay.append(
            dialog
        )

    if dialog not in stack:

        stack.append(dialog)

    dialog.open = True

    set_operational_mode(
        True
    )

    page.update()

# =========================================================
# CLOSE
# =========================================================

def close_dialog(
    page: ft.Page,
    dialog,
):

    dialog.open = False

    stack = get_dialog_stack(
        page
    )

    if dialog in stack:

        stack.remove(dialog)

    if not stack:

        set_operational_mode(
            False
        )

    page.update()

# =========================================================
# CLOSE ALL
# =========================================================

def close_all_dialogs(
    page,
):

    stack = get_dialog_stack(
        page
    )

    for dlg in stack:

        dlg.open = False

    stack.clear()

    set_operational_mode(
        False
    )

    page.update()

# =========================================================
# BUTTONS
# =========================================================

def dialog_button_content(

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

def dialog_text_button(
    text,
    on_click=None,
    icon=None,
):

    return ft.TextButton(

        content=dialog_button_content(
            text,
        ),

        on_click=on_click,
    )

def dialog_filled_button(

    text,

    on_click=None,

    bgcolor=None,

    icon=None,
):

    return ft.FilledButton(

        content=dialog_button_content(
            text,
            icon,
            ft.Colors.WHITE,
        ),

        style=ft.ButtonStyle(

            bgcolor=(

                bgcolor
                or PRIMARY_COLOR
            ),
        ),

        on_click=on_click,
    )

# =========================================================
# BASE DIALOG
# =========================================================

def base_dialog(

    title,

    content,

    actions=None,

    modal=True,

    width=DIALOG_WIDTH,
):

    actions = actions or []

    return ft.AlertDialog(

        modal=modal,

        title=ft.Text(

            title,

            size=18,

            weight=(
                ft.FontWeight.BOLD
            ),
        ),

        content=ft.Container(

            width=width,

            content=content,
        ),

        actions_alignment=(
            ft.MainAxisAlignment.END
        ),

        actions=actions,
    )

# =========================================================
# CONFIRM
# =========================================================

def confirm_dialog(

    page: ft.Page,

    title: str,

    message: str,

    on_confirm=None,

    confirm_text="Confirmar",

    cancel_text="Cancelar",
):

    dlg = None

    def cancelar(e):

        close_dialog(
            page,
            dlg,
        )

    def confirmar(e):

        close_dialog(
            page,
            dlg,
        )

        if on_confirm:

            on_confirm(e)

    dlg = base_dialog(

        title=title,

        content=ft.Text(
            message,
            size=13,
        ),

        actions=[

            dialog_text_button(

                cancel_text,

                icon=(
                    ft.Icons.CLOSE
                ),

                on_click=cancelar,
            ),

            dialog_filled_button(

                confirm_text,

                icon=(
                    ft.Icons.CHECK
                ),

                on_click=confirmar,
            ),
        ],
    )

    open_dialog(
        page,
        dlg,
    )

# =========================================================
# INFO
# =========================================================

def info_dialog(
    page,
    title,
    message,
):

    dlg = None

    def fechar(e):

        close_dialog(
            page,
            dlg,
        )

    dlg = base_dialog(

        title=title,

        content=ft.Text(
            message,
            size=13,
        ),

        actions=[

            dialog_filled_button(

                "OK",

                icon=(
                    ft.Icons.CHECK
                ),

                on_click=fechar,
            )
        ],
    )

    open_dialog(
        page,
        dlg,
    )

# =========================================================
# SUCCESS
# =========================================================

def success_dialog(
    page,
    message,
):

    dlg = None

    def fechar(e):

        close_dialog(
            page,
            dlg,
        )

    dlg = ft.AlertDialog(

        modal=True,

        title=ft.Row(

            spacing=10,

            controls=[

                ft.Icon(

                    ft.Icons
                    .CHECK_CIRCLE,

                    color=(
                        SUCCESS_COLOR
                    ),
                ),

                ft.Text(

                    "Sucesso",

                    weight=(

                        ft.FontWeight
                        .BOLD
                    ),
                ),
            ],
        ),

        content=ft.Container(

            width=DIALOG_WIDTH,

            content=ft.Text(
                message
            ),
        ),

        actions=[

            dialog_filled_button(

                "OK",

                on_click=fechar,
            )
        ],
    )

    open_dialog(
        page,
        dlg,
    )

# =========================================================
# ERROR
# =========================================================

def error_dialog(

    page: ft.Page,

    message: str,

    exception=None,
):

    detalhes = ""

    if exception:

        detalhes = traceback.format_exc()

    dlg = None

    def fechar(e):

        close_dialog(
            page,
            dlg,
        )

    controls = [

        ft.Text(
            message
        )
    ]

    if detalhes:

        controls.append(

            ft.Container(

                margin=ft.Margin(
                    0,
                    10,
                    0,
                    0,
                ),

                padding=10,

                bgcolor=(
                    ft.Colors
                    .GREY_100
                ),

                border_radius=6,

                content=ft.Text(

                    detalhes,

                    size=10,

                    selectable=True,
                ),
            )
        )

    dlg = ft.AlertDialog(

        modal=True,

        title=ft.Row(

            spacing=10,

            controls=[

                ft.Icon(

                    ft.Icons.ERROR,

                    color=(
                        ERROR_COLOR
                    ),
                ),

                ft.Text(

                    "Erro",

                    weight=(

                        ft.FontWeight
                        .BOLD
                    ),
                ),
            ],
        ),

        content=ft.Container(

            width=DIALOG_WIDTH,

            content=ft.Column(
                controls=controls
            ),
        ),

        actions=[

            dialog_text_button(

                "Fechar",

                icon=(
                    ft.Icons.CLOSE
                ),

                on_click=fechar,
            )
        ],
    )

    open_dialog(
        page,
        dlg,
    )

# =========================================================
# LOADING
# =========================================================

def loading_dialog(

    page,

    message="Processando...",
):

    dlg = ft.AlertDialog(

        modal=True,

        content=ft.Container(

            width=280,

            padding=20,

            content=ft.Column(

                tight=True,

                spacing=16,

                horizontal_alignment=(

                    ft.CrossAxisAlignment
                    .CENTER
                ),

                controls=[

                    ft.ProgressRing(

                        width=32,

                        height=32,

                        stroke_width=3,
                    ),

                    ft.Text(

                        message,

                        size=13,
                    ),
                ],
            ),
        ),
    )

    open_dialog(
        page,
        dlg,
    )

    return dlg

# =========================================================
# FULLSCREEN
# =========================================================

def fullscreen_dialog(

    page,

    title,

    content,

    on_close=None,
):

    dlg = ft.AlertDialog(

        modal=True,

        inset_padding=0,

        content_padding=0,

        shape=ft.RoundedRectangleBorder(
            radius=0
        ),

        content=ft.Container(

            expand=True,

            padding=FULLSCREEN_PADDING,

            content=ft.Column(

                expand=True,

                spacing=16,

                controls=[

                    ft.Row(

                        alignment=(

                            ft.MainAxisAlignment
                            .SPACE_BETWEEN
                        ),

                        controls=[

                            ft.Text(

                                title,

                                size=22,

                                weight=(

                                    ft.FontWeight
                                    .BOLD
                                ),
                            ),

                            ft.IconButton(

                                icon=(
                                    ft.Icons.CLOSE
                                ),

                                on_click=lambda e: (

                                    close_dialog(
                                        page,
                                        dlg,
                                    ),

                                    on_close()
                                    if on_close
                                    else None
                                ),
                            ),
                        ],
                    ),

                    ft.Divider(height=1),

                    ft.Container(

                        expand=True,

                        content=content,
                    ),
                ],
            ),
        ),
    )

    open_dialog(
        page,
        dlg,
    )

    return dlg

# =========================================================
# FORM
# =========================================================

def form_dialog(

    page,

    title,

    content,

    on_save=None,

    on_cancel=None,

    width=560,
):

    dlg = None

    def cancelar(e):

        close_dialog(
            page,
            dlg,
        )

        if on_cancel:

            on_cancel()

    def salvar(e):

        if on_save:

            on_save(e)

    dlg = base_dialog(

        title=title,

        width=width,

        content=content,

        actions=[

            dialog_text_button(

                "Cancelar",

                icon=(
                    ft.Icons.CLOSE
                ),

                on_click=cancelar,
            ),

            dialog_filled_button(

                "Salvar",

                icon=(
                    ft.Icons.SAVE
                ),

                on_click=salvar,
            ),
        ],
    )

    open_dialog(
        page,
        dlg,
    )

    return dlg
