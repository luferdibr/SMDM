# =========================================================
# ui/components/notifications.py
# =========================================================

import logging

import flet as ft

from core.state.state import (
    set_temp,
    get_temp,
)

from ui.components.snackbars import (
    show_success,
    show_error,
    show_warning,
    show_info,
)

from ui.components.dialogs import (
    error_dialog,
    info_dialog,
    success_dialog,
)

# =========================================================
# LOGGER
# =========================================================

LOGGER = logging.getLogger(
    "SMDM_NOTIFICATIONS"
)

# =========================================================
# TYPES
# =========================================================

TYPE_SUCCESS = "success"

TYPE_INFO = "info"

TYPE_WARNING = "warning"

TYPE_ERROR = "error"

TYPE_CRITICAL = "critical"

# =========================================================
# STORAGE
# =========================================================

def get_notifications():

    notifications = get_temp(
        "notifications"
    )

    if notifications is None:

        notifications = []

        set_temp(
            "notifications",
            notifications,
        )

    return notifications

# =========================================================
# ADD
# =========================================================

def add_notification(

    notification_type,

    title,

    message,

    persistent=False,
):

    notifications = (
        get_notifications()
    )

    notifications.insert(

        0,

        {

            "type": (
                notification_type
            ),

            "title": title,

            "message": message,

            "persistent": (
                persistent
            ),
        },
    )

    if len(notifications) > 100:

        notifications.pop()

# =========================================================
# BASE
# =========================================================

def notify(

    page: ft.Page,

    notification_type,

    title,

    message,

    persistent=False,
):

    add_notification(

        notification_type=(
            notification_type
        ),

        title=title,

        message=message,

        persistent=persistent,
    )

    LOGGER.info(

        "[NOTIFICATION] "

        f"{notification_type.upper()} "

        f"| {title}"
    )

    # =====================================================
    # SUCCESS
    # =====================================================

    if (
        notification_type
        == TYPE_SUCCESS
    ):

        show_success(
            page,
            message,
        )

        return

    # =====================================================
    # INFO
    # =====================================================

    if (
        notification_type
        == TYPE_INFO
    ):

        show_info(
            page,
            message,
        )

        return

    # =====================================================
    # WARNING
    # =====================================================

    if (
        notification_type
        == TYPE_WARNING
    ):

        show_warning(
            page,
            message,
        )

        return

    # =====================================================
    # ERROR
    # =====================================================

    if (
        notification_type
        == TYPE_ERROR
    ):

        show_error(
            page,
            message,
        )

        return

    # =====================================================
    # CRITICAL
    # =====================================================

    if (
        notification_type
        == TYPE_CRITICAL
    ):

        error_dialog(

            page,

            title,

            message,
        )

# =========================================================
# SUCCESS
# =========================================================

def notify_success(

    page,

    message,

    title="Sucesso",
):

    notify(

        page=page,

        notification_type=(
            TYPE_SUCCESS
        ),

        title=title,

        message=message,
    )

# =========================================================
# INFO
# =========================================================

def notify_info(

    page,

    message,

    title="Informação",
):

    notify(

        page=page,

        notification_type=(
            TYPE_INFO
        ),

        title=title,

        message=message,
    )

# =========================================================
# WARNING
# =========================================================

def notify_warning(

    page,

    message,

    title="Atenção",
):

    notify(

        page=page,

        notification_type=(
            TYPE_WARNING
        ),

        title=title,

        message=message,
    )

# =========================================================
# ERROR
# =========================================================

def notify_error(

    page,

    message,

    title="Erro",
):

    notify(

        page=page,

        notification_type=(
            TYPE_ERROR
        ),

        title=title,

        message=message,
    )

# =========================================================
# CRITICAL
# =========================================================

def notify_critical(

    page,

    message,

    title="Erro Crítico",
):

    notify(

        page=page,

        notification_type=(
            TYPE_CRITICAL
        ),

        title=title,

        message=message,

        persistent=True,
    )

# =========================================================
# CRUD HELPERS
# =========================================================

def notify_save_success(
    page,
):

    notify_success(

        page,

        "Registro salvo com sucesso.",
    )

def notify_delete_success(
    page,
):

    notify_success(

        page,

        "Registro excluído com sucesso.",
    )

def notify_update_success(
    page,
):

    notify_success(

        page,

        "Registro atualizado com sucesso.",
    )

def notify_login(
    page,
):

    notify_info(

        page,

        "Login realizado.",
    )

def notify_logout(
    page,
):

    notify_info(

        page,

        "Logout realizado.",
    )

# =========================================================
# PANEL
# =========================================================

def notification_item(
    item,
):

    return ft.Container(

        padding=10,

        border_radius=10,

        bgcolor=ft.Colors.WHITE,

        border=ft.border.all(
            1,
            ft.Colors.GREY_300,
        ),

        content=ft.Column(

            spacing=4,

            controls=[

                ft.Text(

                    item.get(
                        "title",
                        ""
                    ),

                    weight=(
                        ft.FontWeight.BOLD
                    ),
                ),

                ft.Text(

                    item.get(
                        "message",
                        ""
                    ),

                    size=12,
                ),

                ft.Text(

                    item.get(
                        "type",
                        ""
                    ).upper(),

                    size=10,

                    color=(
                        ft.Colors.GREY_700
                    ),
                ),
            ],
        ),
    )

# =========================================================
# CENTER
# =========================================================

def notification_center():

    notifications = (
        get_notifications()
    )

    if not notifications:

        return ft.Container(

            padding=20,

            alignment=ft.alignment.center,

            content=ft.Text(
                "Nenhuma notificação."
            ),
        )

    return ft.Column(

        spacing=10,

        scroll=ft.ScrollMode.AUTO,

        controls=[

            notification_item(
                item
            )

            for item in notifications
        ],
    )

# =========================================================
# CLEAR
# =========================================================

def clear_notifications():

    set_temp(
        "notifications",
        [],
    )

# =========================================================
# COUNT
# =========================================================

def notification_count():

    return len(
        get_notifications()
    )
