# =========================================================
# ui/components/base_view.py
# =========================================================

import flet as ft

from core.state.state import (
    set_current_view,
    set_operational_mode,
    set_selected_module,
)

from ui.components.cards import (
    app_card,
    page_container,
)

# =========================================================
# CONFIG
# =========================================================

PAGE_SPACING = 18

SECTION_SPACING = 12

TOOLBAR_HEIGHT = 42

# =========================================================
# COLORS
# =========================================================

TEXT_SECONDARY = (
    ft.Colors.GREY_700
)

TOOLBAR_BG = (
    ft.Colors.WHITE
)

BREADCRUMB_COLOR = (
    ft.Colors.BLUE_700
)

# =========================================================
# BUTTON CONTENT
# =========================================================

def toolbar_button_content(

    text,

    icon=None,
):

    controls = []

    if icon:

        controls.append(

            ft.Icon(
                icon,
                size=16,
            )
        )

    controls.append(

        ft.Text(
            text,
            size=12,
        )
    )

    return ft.Row(

        spacing=6,

        alignment=ft.MainAxisAlignment.CENTER,

        controls=controls,
    )

# =========================================================
# BREADCRUMB
# =========================================================

def breadcrumb(
    items,
):

    controls = []

    total = len(items)

    for idx, item in enumerate(items):

        controls.append(

            ft.Text(

                str(item),

                size=11,

                color=BREADCRUMB_COLOR,

                weight=(
                    ft.FontWeight.W_500
                ),
            )
        )

        if idx < (total - 1):

            controls.append(

                ft.Icon(

                    ft.Icons
                    .CHEVRON_RIGHT,

                    size=14,

                    color=(
                        ft.Colors.GREY_500
                    ),
                )
            )

    return ft.Row(

        spacing=2,

        controls=controls,
    )

# =========================================================
# PAGE HEADER
# =========================================================

def page_header(

    title,

    subtitle=None,

    actions=None,

    breadcrumbs=None,
):

    actions = actions or []

    return ft.Column(

        spacing=8,

        controls=[

            breadcrumb(
                breadcrumbs
            )

            if breadcrumbs
            else ft.Container(),

            ft.Row(

                alignment=(

                    ft.MainAxisAlignment
                    .SPACE_BETWEEN
                ),

                vertical_alignment=(

                    ft.CrossAxisAlignment
                    .CENTER
                ),

                controls=[

                    ft.Column(

                        spacing=2,

                        expand=True,

                        controls=[

                            ft.Text(

                                title,

                                size=24,

                                weight=(
                                    ft.FontWeight.BOLD
                                ),
                            ),

                            ft.Text(

                                subtitle or "",

                                size=12,

                                color=(
                                    TEXT_SECONDARY
                                ),

                                visible=bool(
                                    subtitle
                                ),
                            ),
                        ],
                    ),

                    ft.Row(

                        spacing=6,

                        controls=actions,
                    ),
                ],
            ),
        ],
    )

# =========================================================
# TOOLBAR
# =========================================================

def operational_toolbar(

    on_new=None,

    on_edit=None,

    on_delete=None,

    on_refresh=None,

    on_back=None,

    extra_actions=None,
):

    extra_actions = (
        extra_actions or []
    )

    controls = []

    if on_back:

        controls.append(

            ft.OutlinedButton(

                content=toolbar_button_content(
                    "Voltar",
                    ft.Icons.ARROW_BACK,
                ),

                height=34,

                on_click=on_back,
            )
        )

    if on_new:

        controls.append(

            ft.FilledButton(

                content=toolbar_button_content(
                    "Novo",
                    ft.Icons.ADD,
                ),

                height=34,

                on_click=on_new,
            )
        )

    if on_edit:

        controls.append(

            ft.OutlinedButton(

                content=toolbar_button_content(
                    "Editar",
                    ft.Icons.EDIT,
                ),

                height=34,

                on_click=on_edit,
            )
        )

    if on_delete:

        controls.append(

            ft.OutlinedButton(

                content=toolbar_button_content(
                    "Excluir",
                    ft.Icons.DELETE,
                ),

                height=34,

                on_click=on_delete,
            )
        )

    if on_refresh:

        controls.append(

            ft.IconButton(

                icon=(
                    ft.Icons.REFRESH
                ),

                tooltip="Atualizar",

                on_click=on_refresh,
            )
        )

    controls.extend(
        extra_actions
    )

    return ft.Container(

        height=TOOLBAR_HEIGHT,

        padding=ft.Padding(
            10,
            4,
            10,
            4,
        ),

        bgcolor=TOOLBAR_BG,

        border_radius=8,

        content=ft.Row(

            spacing=6,

            controls=controls,
        ),
    )

# =========================================================
# CONTENT SECTION
# =========================================================

def content_section(
    content,
):

    return app_card(
        content=content
    )

# =========================================================
# LOADING VIEW
# =========================================================

def loading_view(
    message="Carregando...",
):

    return page_container(

        content=ft.Column(

            expand=True,

            alignment=(
                ft.MainAxisAlignment.CENTER
            ),

            horizontal_alignment=(
                ft.CrossAxisAlignment.CENTER
            ),

            spacing=18,

            controls=[

                ft.ProgressRing(

                    width=36,

                    height=36,

                    stroke_width=3,
                ),

                ft.Text(

                    message,

                    size=14,
                ),
            ],
        )
    )

# =========================================================
# ERROR VIEW
# =========================================================

def error_view(
    title="Erro interno",
    subtitle=None,
):

    return page_empty(

        title=title,

        subtitle=subtitle,

        icon=ft.Icons.ERROR,
    )

# =========================================================
# SUCCESS VIEW
# =========================================================

def success_view(
    title,
    subtitle=None,
):

    return page_empty(

        title=title,

        subtitle=subtitle,

        icon=ft.Icons.CHECK_CIRCLE,
    )

# =========================================================
# CONSTRUCTION VIEW
# =========================================================

def construction_view(
    rotina,
):

    return page_empty(

        title="Rotina em construção",

        subtitle=(

            f"A rotina "

            f"'{rotina}' "

            f"ainda não foi implementada."
        ),

        icon=(
            ft.Icons.CONSTRUCTION
        ),
    )

# =========================================================
# BASE VIEW
# =========================================================

def base_view(

    title,

    subtitle=None,

    content_controls=None,

    actions=None,

    toolbar=None,

    breadcrumbs=None,

    module_name=None,

    operational=False,

    scroll=ft.ScrollMode.AUTO,
):

    content_controls = (
        content_controls or []
    )

    if module_name:

        set_current_view(
            module_name
        )

        set_selected_module(
            module_name
        )

    set_operational_mode(
        operational
    )

    controls = [

        page_header(

            title=title,

            subtitle=subtitle,

            actions=actions,

            breadcrumbs=breadcrumbs,
        ),
    ]

    if toolbar:

        controls.append(
            toolbar
        )

    controls.extend(
        content_controls
    )

    return page_container(

        content=ft.Column(

            expand=True,

            spacing=PAGE_SPACING,

            scroll=scroll,

            controls=controls,
        )
    )

# =========================================================
# DASHBOARD LAYOUT
# =========================================================

def dashboard_view_layout(

    title,

    subtitle,

    cards,
):

    return base_view(

        title=title,

        subtitle=subtitle,

        content_controls=[
            cards
        ],

        breadcrumbs=[
            "Dashboard"
        ],

        module_name="dashboard",
    )

# =========================================================
# EMPTY PAGE
# =========================================================

def page_empty(

    title,

    subtitle=None,

    icon=ft.Icons.INFO_OUTLINE,
):

    return page_container(

        content=ft.Column(

            expand=True,

            alignment=(

                ft.MainAxisAlignment
                .CENTER
            ),

            horizontal_alignment=(

                ft.CrossAxisAlignment
                .CENTER
            ),

            spacing=20,

            controls=[

                ft.Icon(

                    icon,

                    size=72,

                    color=(
                        ft.Colors.GREY_500
                    ),
                ),

                ft.Text(

                    title,

                    size=24,

                    weight=(
                        ft.FontWeight.BOLD
                    ),
                ),

                ft.Text(

                    subtitle or "",

                    size=13,

                    color=(
                        ft.Colors.GREY_700
                    ),

                    text_align=(
                        ft.TextAlign.CENTER
                    ),

                    visible=bool(
                        subtitle
                    ),
                ),
            ],
        )
    )

# =========================================================
# PAGE DIVIDER
# =========================================================

def page_divider():

    return ft.Divider(
        height=1
    )

# =========================================================
# PAGE SECTION
# =========================================================

def page_section(

    title,

    content,
):

    return ft.Column(

        spacing=SECTION_SPACING,

        controls=[

            ft.Text(

                title,

                size=16,

                weight=(
                    ft.FontWeight.BOLD
                ),
            ),

            content,
        ],
    )

# =========================================================
# FULLSCREEN VIEW
# =========================================================

def fullscreen_view(
    content,
):

    return ft.Container(

        expand=True,

        padding=0,

        margin=0,

        content=content,
    )

# =========================================================
# LIFECYCLE
# =========================================================

class ViewLifecycle:

    def __init__(
        self,
    ):

        self.on_open = None

        self.on_close = None

        self.on_refresh = None

        self.on_back = None

    def open(
        self,
    ):

        if self.on_open:

            self.on_open()

    def close(
        self,
    ):

        if self.on_close:

            self.on_close()

    def refresh(
        self,
    ):

        if self.on_refresh:

            self.on_refresh()

    def back(
        self,
    ):

        if self.on_back:

            self.on_back()
