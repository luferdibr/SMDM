# =========================================================
# ui/components/snackbars.py
# =========================================================

import flet as ft

from core.state.state import (
    set_temp,
    get_temp,
)

from core.themes import (
    SUCCESS_COLOR,
    ERROR_COLOR,
    WARNING_COLOR,
    INFO_COLOR,
    TEXT_ON_PRIMARY,
)

# =========================================================
# CONFIG
# =========================================================

DEFAULT_DURATION = 3000

MAX_STACK = 5

# =========================================================
# TYPES
# =========================================================

TYPE_SUCCESS = "success"

TYPE_ERROR = "error"

TYPE_WARNING = "warning"

TYPE_INFO = "info"

# =========================================================
# COLORS
# =========================================================

TYPE_COLORS = {

    TYPE_SUCCESS: SUCCESS_COLOR,

    TYPE_ERROR: ERROR_COLOR,

    TYPE_WARNING: WARNING_COLOR,

    TYPE_INFO: INFO_COLOR,
}

# =========================================================
# ICONS
# =========================================================

TYPE_ICONS = {

    TYPE_SUCCESS: ft.Icons.CHECK_CIRCLE,

    TYPE_ERROR: ft.Icons.ERROR,

    TYPE_WARNING: (
        ft.Icons.WARNING_AMBER
    ),

    TYPE_INFO: ft.Icons.INFO,
}

# =========================================================
# QUEUE
# =========================================================

def get_snackbar_queue():

    queue = get_temp(
        "snackbar_queue"
    )

    if queue is None:

        queue = []

        set_temp(
            "snackbar_queue",
            queue,
        )

    return queue

# =========================================================
# BASE
# =========================================================

def build_snackbar(

    message,

    snackbar_type=TYPE_INFO,

    duration=DEFAULT_DURATION,

    action=None,
):

    color = TYPE_COLORS.get(
        snackbar_type,
        INFO_COLOR,
    )

    icon = TYPE_ICONS.get(
        snackbar_type,
        ft.Icons.INFO,
    )

    return ft.SnackBar(

        behavior=(
            ft.SnackBarBehavior
            .FLOATING
        ),

        duration=duration,

        bgcolor=color,

        margin=12,

        content=ft.Row(

            spacing=12,

            controls=[

                ft.Icon(

                    icon,

                    color=(
                        TEXT_ON_PRIMARY
                    ),
                ),

                ft.Text(

                    str(message),

                    color=(
                        TEXT_ON_PRIMARY
                    ),

                    expand=True,
                ),
            ],
        ),

        action=action,
    )

# =========================================================
# SHOW
# =========================================================

def show_snackbar(

    page: ft.Page,

    message,

    snackbar_type=TYPE_INFO,

    duration=DEFAULT_DURATION,

    action=None,
):

    queue = get_snackbar_queue()

    snackbar = build_snackbar(

        message=message,

        snackbar_type=(
            snackbar_type
        ),

        duration=duration,

        action=action,
    )

    queue.append(
        snackbar
    )

    if len(queue) > MAX_STACK:

        queue.pop(0)

    page.snack_bar = snackbar

    snackbar.open = True

    page.update()

# =========================================================
# SUCCESS
# =========================================================

def show_success(

    page,

    message,

    duration=DEFAULT_DURATION,
):

    show_snackbar(

        page=page,

        message=message,

        snackbar_type=(
            TYPE_SUCCESS
        ),

        duration=duration,
    )

# =========================================================
# ERROR
# =========================================================

def show_error(

    page,

    message,

    duration=DEFAULT_DURATION,
):

    show_snackbar(

        page=page,

        message=message,

        snackbar_type=(
            TYPE_ERROR
        ),

        duration=duration,
    )

# =========================================================
# WARNING
# =========================================================

def show_warning(

    page,

    message,

    duration=DEFAULT_DURATION,
):

    show_snackbar(

        page=page,

        message=message,

        snackbar_type=(
            TYPE_WARNING
        ),

        duration=duration,
    )

# =========================================================
# INFO
# =========================================================

def show_info(

    page,

    message,

    duration=DEFAULT_DURATION,
):

    show_snackbar(

        page=page,

        message=message,

        snackbar_type=(
            TYPE_INFO
        ),

        duration=duration,
    )

# =========================================================
# CRUD HELPERS
# =========================================================

def show_save_success(
    page,
):

    show_success(

        page,

        "Registro salvo com sucesso.",
    )

def show_delete_success(
    page,
):

    show_success(

        page,

        "Registro excluído com sucesso.",
    )

def show_update_success(
    page,
):

    show_success(

        page,

        "Registro atualizado com sucesso.",
    )

def show_operation_error(

    page,

    error=None,
):

    mensagem = (
        "Erro durante operação."
    )

    if error:

        mensagem = (
            f"{mensagem}\n{str(error)}"
        )

    show_error(
        page,
        mensagem,
    )

# =========================================================
# CLOSE
# =========================================================

def close_snackbar(
    page,
):

    if page.snack_bar:

        page.snack_bar.open = False

        page.update()

# =========================================================
# CLEAR QUEUE
# =========================================================

def clear_snackbar_queue():

    set_temp(
        "snackbar_queue",
        [],
    )