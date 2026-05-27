
# =========================================================
# ui/components/fields.py
# =========================================================

import flet as ft

from core.themes import (
    TEXTFIELD_BORDER_RADIUS,
)

# =========================================================
# CONFIG
# =========================================================

DEFAULT_HEIGHT = 38

DENSE_HEIGHT = 32

DEFAULT_TEXT_SIZE = 12

# =========================================================
# BASE TEXT FIELD
# =========================================================

def app_textfield(

    label: str = "",

    value: str = "",

    hint_text: str = "",

    prefix_icon=None,

    password=False,

    can_reveal_password=False,

    width=None,

    height=None,

    expand=False,

    multiline=False,

    min_lines=None,

    max_lines=None,

    disabled=False,

    read_only=False,

    visible=True,

    autofocus=False,

    dense=False,

    text_size=DEFAULT_TEXT_SIZE,

    on_change=None,

    on_submit=None,
):

    final_height = (

        height

        if height is not None

        else (
            DENSE_HEIGHT
            if dense
            else DEFAULT_HEIGHT
        )
    )

    return ft.TextField(

        label=label,

        value=value,

        hint_text=hint_text,

        prefix_icon=prefix_icon,

        password=password,

        can_reveal_password=(
            can_reveal_password
        ),

        width=width,

        height=(
            None
            if multiline
            else final_height
        ),

        expand=expand,

        multiline=multiline,

        min_lines=min_lines,

        max_lines=max_lines,

        disabled=disabled,

        read_only=read_only,

        visible=visible,

        autofocus=autofocus,

        border_radius=(
            TEXTFIELD_BORDER_RADIUS
        ),

        filled=True,

        dense=dense,

        text_size=text_size,

        content_padding=(
            ft.Padding(
                10,
                6,
                10,
                6,
            )
            if dense
            else ft.Padding(
                12,
                10,
                12,
                10,
            )
        ),

        on_change=on_change,

        on_submit=on_submit,
    )

# =========================================================
# SEARCH FIELD
# =========================================================

def search_field(
    label="Pesquisar",
    width=240,
    on_change=None,
):

    return app_textfield(

        label=label,

        width=width,

        prefix_icon=ft.Icons.SEARCH,

        dense=True,

        on_change=on_change,
    )

# =========================================================
# PASSWORD FIELD
# =========================================================

def password_field(

    label="Senha",

    width=None,

    expand=False,

    on_submit=None,
):

    return app_textfield(

        label=label,

        password=True,

        can_reveal_password=True,

        prefix_icon=(
            ft.Icons.LOCK_OUTLINE
        ),

        width=width,

        expand=expand,

        dense=True,

        on_submit=on_submit,
    )

# =========================================================
# NUMBER FIELD
# =========================================================

def number_field(

    label="",

    value="",

    width=120,

    on_change=None,
):

    return app_textfield(

        label=label,

        value=value,

        width=width,

        dense=True,

        on_change=on_change,
    )

# =========================================================
# DROPDOWN
# =========================================================

def app_dropdown(

    label=None,

    options=None,

    value=None,

    width=None,

    expand=False,

    dense=True,

    disabled=False,

    text_size=DEFAULT_TEXT_SIZE,

    on_change=None,
):

    options = options or []

    dropdown_options = []

    for item in options:

        # =================================================
        # TUPLA
        # =================================================

        if isinstance(
            item,
            tuple,
        ):

            val, text = item

        # =================================================
        # DICT
        # =================================================

        elif isinstance(
            item,
            dict,
        ):

            val = (

                item.get("value")

                or item.get("id")

                or ""
            )

            text = (

                item.get("label")

                or item.get("nome")

                or str(val)
            )

        # =================================================
        # STRING
        # =================================================

        else:

            val = str(item)

            text = str(item)

        dropdown_options.append(

            ft.dropdown.Option(

                key=str(val),

                text=str(text),
            )
        )

    # =====================================================
    # BUILD
    # =====================================================

    kwargs = dict(

        label=label,

        options=dropdown_options,

        value=(
            str(value)
            if value is not None
            else None
        ),

        width=width,

        expand=expand,

        dense=dense,

        disabled=disabled,

        text_size=text_size,

        content_padding=(
            ft.Padding(
                10,
                4,
                10,
                4,
            )
        ),
    )

    # =====================================================
    # FLET COMPAT
    # =====================================================

    if on_change:

        try:

            kwargs[
                "on_change"
            ] = on_change

            return ft.Dropdown(
                **kwargs
            )

        except TypeError:

            try:

                kwargs.pop(
                    "on_change",
                    None,
                )

                kwargs[
                    "on_select"
                ] = on_change

                return ft.Dropdown(
                    **kwargs
                )

            except TypeError:

                kwargs.pop(
                    "on_select",
                    None,
                )

                kwargs[
                    "on_changed"
                ] = on_change

                return ft.Dropdown(
                    **kwargs
                )

    return ft.Dropdown(
        **kwargs
    )

# =========================================================
# CHECKBOX
# =========================================================

def app_checkbox(

    label: str,

    value=False,

    disabled=False,

    dense=True,

    on_change=None,
):

    return ft.Checkbox(

        label=label,

        value=value,

        disabled=disabled,

        visual_density=(
            ft.VisualDensity.COMPACT
            if dense
            else None
        ),

        on_change=on_change,
    )

# =========================================================
# SWITCH
# =========================================================

def app_switch(

    label: str,

    value=False,

    disabled=False,

    dense=True,

    on_change=None,
):

    return ft.Switch(

        label=label,

        value=value,

        disabled=disabled,

        adaptive=False,

        on_change=on_change,
    )

# =========================================================
# DATE FIELD
# =========================================================

def date_field(
    label="Data",
    width=180,
):

    return app_textfield(

        label=label,

        width=width,

        dense=True,

        prefix_icon=(
            ft.Icons.CALENDAR_MONTH
        ),
    )

# =========================================================
# EMAIL FIELD
# =========================================================

def email_field(

    label="E-mail",

    width=None,

    expand=False,
):

    return app_textfield(

        label=label,

        width=width,

        expand=expand,

        dense=True,

        prefix_icon=(
            ft.Icons.EMAIL_OUTLINED
        ),
    )

# =========================================================
# PHONE FIELD
# =========================================================

def phone_field(
    label="Telefone",
    width=None,
):

    return app_textfield(

        label=label,

        width=width,

        dense=True,

        prefix_icon=ft.Icons.PHONE,
    )

# =========================================================
# URL FIELD
# =========================================================

def url_field(

    label="URL",

    width=None,

    expand=False,
):

    return app_textfield(

        label=label,

        width=width,

        expand=expand,

        dense=True,

        prefix_icon=ft.Icons.LINK,
    )