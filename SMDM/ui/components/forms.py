# =========================================================
# ui/components/forms.py
# =========================================================

import flet as ft

from core.state.state import (
    is_loading,
    set_temp,
    get_temp,
)

from ui.components.cards import (
    app_card,
)

from ui.components.buttons import (
    save_button,
    cancel_button,
)

# =========================================================
# CONFIG
# =========================================================

FIELD_HEIGHT = 42

FIELD_SPACING = 12

SECTION_SPACING = 18

FORM_PADDING = 20

# =========================================================
# HELPERS
# =========================================================

def field_error(
    message,
):

    return ft.Text(

        message,

        size=11,

        color=ft.Colors.RED_700,
    )

# =========================================================
# LABEL
# =========================================================

def field_label(
    text,
    required=False,
):

    return ft.Row(

        spacing=2,

        controls=[

            ft.Text(

                text,

                size=12,

                weight=(
                    ft.FontWeight.W_500
                ),
            ),

            ft.Text(

                "*",

                color=ft.Colors.RED,

                visible=required,
            ),
        ],
    )

# =========================================================
# TEXT FIELD
# =========================================================

def text_field(

    label,

    value=None,

    required=False,

    password=False,

    multiline=False,

    read_only=False,

    on_change=None,

    hint=None,
):

    return ft.TextField(

        label=label,

        value=value,

        password=password,

        multiline=multiline,

        read_only=read_only,

        dense=True,

        height=(
            90
            if multiline
            else FIELD_HEIGHT
        ),

        hint_text=hint,

        disabled=is_loading(),

        on_change=on_change,
    )

# =========================================================
# NUMBER FIELD
# =========================================================

def number_field(

    label,

    value=None,

    required=False,

    decimals=False,

    on_change=None,
):

    return ft.TextField(

        label=label,

        value=value,

        dense=True,

        height=FIELD_HEIGHT,

        keyboard_type=(

            ft.KeyboardType.NUMBER
        ),

        input_filter=(

            ft.NumbersOnlyInputFilter()
        ),

        disabled=is_loading(),

        on_change=on_change,
    )

# =========================================================
# PASSWORD FIELD
# =========================================================

def password_field(

    label,

    value=None,

    required=False,
):

    return text_field(

        label=label,

        value=value,

        required=required,

        password=True,
    )

# =========================================================
# DROPDOWN FIELD
# =========================================================

def dropdown_field(

    label,

    options,

    value=None,

    required=False,

    on_change=None,
):

    return ft.Dropdown(

        label=label,

        value=value,

        dense=True,

        height=FIELD_HEIGHT,

        disabled=is_loading(),

        options=[

            ft.dropdown.Option(

                key=str(item[0]),

                text=str(item[1]),
            )

            for item in options
        ],

        on_change=on_change,
    )

# =========================================================
# SWITCH FIELD
# =========================================================

def switch_field(

    label,

    value=False,

    on_change=None,
):

    return ft.Switch(

        label=label,

        value=value,

        disabled=is_loading(),

        on_change=on_change,
    )

# =========================================================
# CHECKBOX FIELD
# =========================================================

def checkbox_field(

    label,

    value=False,

    on_change=None,
):

    return ft.Checkbox(

        label=label,

        value=value,

        disabled=is_loading(),

        on_change=on_change,
    )

# =========================================================
# DATE FIELD
# =========================================================

def date_field(

    label,

    value=None,

    on_change=None,
):

    return ft.TextField(

        label=label,

        value=value,

        dense=True,

        height=FIELD_HEIGHT,

        hint_text="dd/mm/aaaa",

        disabled=is_loading(),

        on_change=on_change,
    )

# =========================================================
# FIELD CONTAINER
# =========================================================

def field_container(

    control,

    xs=12,

    sm=6,

    md=4,

    lg=3,
):

    return ft.Container(

        col={

            "xs": xs,

            "sm": sm,

            "md": md,

            "lg": lg,
        },

        content=control,
    )

# =========================================================
# FORM GRID
# =========================================================

def form_grid(
    controls,
):

    return ft.ResponsiveRow(

        controls=controls,

        spacing=FIELD_SPACING,

        run_spacing=FIELD_SPACING,
    )

# =========================================================
# FORM SECTION
# =========================================================

def form_section(

    title,

    controls,

    subtitle=None,
):

    return app_card(

        content=ft.Column(

            spacing=SECTION_SPACING,

            controls=[

                ft.Column(

                    spacing=2,

                    controls=[

                        ft.Text(

                            title,

                            size=18,

                            weight=(
                                ft.FontWeight.BOLD
                            ),
                        ),

                        ft.Text(

                            subtitle or "",

                            size=12,

                            color=(
                                ft.Colors.GREY_700
                            ),

                            visible=bool(
                                subtitle
                            ),
                        ),
                    ],
                ),

                ft.Divider(height=1),

                *controls,
            ],
        )
    )

# =========================================================
# VALIDATORS
# =========================================================

def required_validator(
    value,
):

    if value is None:

        return False

    if str(value).strip() == "":

        return False

    return True

def min_length_validator(
    value,
    length,
):

    return len(

        str(value or "")
    ) >= length

# =========================================================
# FORM STATE
# =========================================================

class FormState:

    def __init__(
        self,
        form_name,
    ):

        self.form_name = (
            form_name
        )

        self.values = {}

        self.errors = {}

        self.dirty = False

    # =====================================================
    # VALUE
    # =====================================================

    def set_value(
        self,
        field,
        value,
    ):

        self.values[field] = value

        self.dirty = True

    def get_value(
        self,
        field,
        default=None,
    ):

        return self.values.get(
            field,
            default,
        )

    # =====================================================
    # ERRORS
    # =====================================================

    def set_error(
        self,
        field,
        message,
    ):

        self.errors[field] = (
            message
        )

    def get_error(
        self,
        field,
    ):

        return self.errors.get(
            field
        )

    def clear_errors(
        self,
    ):

        self.errors = {}

    # =====================================================
    # DIRTY
    # =====================================================

    def is_dirty(
        self,
    ):

        return self.dirty

    def reset_dirty(
        self,
    ):

        self.dirty = False

# =========================================================
# ERP FORM
# =========================================================

class ERPForm:

    def __init__(

        self,

        form_name,

        sections,

        on_save=None,

        on_cancel=None,
    ):

        self.form_name = (
            form_name
        )

        self.sections = sections

        self.on_save = on_save

        self.on_cancel = on_cancel

        self.state = FormState(
            form_name
        )

        set_temp(
            f"form:{form_name}",
            self.state,
        )

    # =====================================================
    # VALIDATE
    # =====================================================

    def validate(
        self,
    ):

        self.state.clear_errors()

        return True

    # =====================================================
    # SAVE
    # =====================================================

    def save(
        self,
        e,
    ):

        if not self.validate():

            return

        if self.on_save:

            self.on_save(e)

        self.state.reset_dirty()

    # =====================================================
    # CANCEL
    # =====================================================

    def cancel(
        self,
        e,
    ):

        if self.on_cancel:

            self.on_cancel(e)

    # =====================================================
    # BUILD
    # =====================================================

    def build(
        self,
    ):

        controls = []

        controls.extend(
            self.sections
        )

        controls.append(

            ft.Divider(height=1)
        )

        controls.append(

            ft.Row(

                spacing=8,

                controls=[

                    save_button(
                        on_click=self.save
                    ),

                    cancel_button(
                        on_click=self.cancel
                    ),
                ],
            )
        )

        return ft.Container(

            padding=FORM_PADDING,

            content=ft.Column(

                spacing=SECTION_SPACING,

                scroll=(
                    ft.ScrollMode.AUTO
                ),

                controls=controls,
            ),
        )

# =========================================================
# SEARCH SECTION
# =========================================================

def search_section(

    search_field,

    actions=None,
):

    return app_card(

        content=ft.Row(

            spacing=12,

            vertical_alignment=(

                ft.CrossAxisAlignment
                .CENTER
            ),

            controls=[

                search_field,

                ft.Container(
                    expand=True
                ),

                *(actions or []),
            ],
        )
    )

# =========================================================
# FILTER SECTION
# =========================================================

def filter_section(
    controls,
):

    return app_card(

        content=form_grid(
            controls
        )
    )

# =========================================================
# COLLAPSIBLE SECTION
# =========================================================

def collapsible_section(

    title,

    content,

    initially_expanded=True,
):

    return ft.ExpansionTile(

        title=ft.Text(

            title,

            weight=(
                ft.FontWeight.BOLD
            ),
        ),

        initially_expanded=(
            initially_expanded
        ),

        controls=[

            ft.Container(

                padding=16,

                content=content,
            )
        ],
    )

# =========================================================
# TABS
# =========================================================

def form_tabs(
    tabs,
):

    return ft.Tabs(

        expand=True,

        animation_duration=200,

        tabs=tabs,
    )

# =========================================================
# TAB
# =========================================================

def form_tab(

    text,

    content,

    icon=None,
):

    return ft.Tab(

        text=text,

        icon=icon,

        content=content,
    )
