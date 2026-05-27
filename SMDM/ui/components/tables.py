# =========================================================
# ui/components/tables.py
# =========================================================

import math

import flet as ft

from core.state.state import (
    get_selected_record,
    set_selected_record,
)

from core.themes import (
    SPACING_LG,
    TEXT_SECONDARY,
)

from ui.components.cards import (
    app_card,
    empty_card,
)

# =========================================================
# CONFIG
# =========================================================

HEADER_HEIGHT = 32

ROW_HEIGHT = 30

TEXT_SIZE = 11

PAGE_SIZE = 20

# =========================================================
# ALIGN
# =========================================================

ALIGN_LEFT = ft.Alignment(-1, 0)

ALIGN_CENTER = ft.Alignment(0, 0)

ALIGN_RIGHT = ft.Alignment(1, 0)

# =========================================================
# COLORS
# =========================================================

HEADER_BG = ft.Colors.BLUE_GREY_50

ROW_BG = ft.Colors.WHITE

ROW_SELECTED_BG = ft.Colors.BLUE_50

ROW_HOVER_BG = ft.Colors.BLUE_100

# =========================================================
# TEXT CELL
# =========================================================

def text_cell(

    value,

    width=None,

    expand=False,

    size=TEXT_SIZE,

    bold=False,

    color=None,
):

    return ft.Container(

        width=width,

        expand=expand,

        alignment=ALIGN_LEFT,

        content=ft.Text(

            "" if value is None
            else str(value),

            size=size,

            color=color,

            weight=(

                ft.FontWeight.BOLD
                if bold
                else ft.FontWeight.W_400
            ),

            max_lines=1,

            overflow=(
                ft.TextOverflow
                .ELLIPSIS
            ),
        ),
    )

# =========================================================
# ACTION CELL
# =========================================================

def action_cell(
    controls,
    width=100,
):

    return ft.Container(

        width=width,

        alignment=ALIGN_RIGHT,

        content=ft.Row(

            controls=controls,

            spacing=2,

            alignment=(
                ft.MainAxisAlignment.END
            ),
        ),
    )

# =========================================================
# STATUS CHIP
# =========================================================

def status_chip(
    label,
    color=ft.Colors.BLUE,
):

    return ft.Container(

        padding=ft.Padding(
            8,
            2,
            8,
            2,
        ),

        border_radius=20,

        bgcolor=color,

        content=ft.Text(

            str(label),

            size=10,

            color=ft.Colors.WHITE,
        ),
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
                color=ft.Colors.WHITE,
            )
        )

    controls.append(
        ft.Text(
            text,
            size=12,
            color=ft.Colors.WHITE,
        )
    )

    return ft.Row(
        spacing=6,
        alignment=ft.MainAxisAlignment.CENTER,
        controls=controls,
    )

# =========================================================
# HEADER
# =========================================================

def table_header(
    columns,
):

    controls = []

    for column in columns:

        controls.append(

            ft.Container(

                width=column.get(
                    "width"
                ),

                expand=column.get(
                    "expand",
                    False,
                ),

                alignment=ALIGN_LEFT,

                content=ft.Text(

                    column.get(
                        "label",
                        ""
                    ),

                    size=TEXT_SIZE,

                    weight=(
                        ft.FontWeight.BOLD
                    ),
                ),
            )
        )

    return ft.Container(

        height=HEADER_HEIGHT,

        padding=ft.Padding(
            8,
            0,
            8,
            0,
        ),

        bgcolor=HEADER_BG,

        border_radius=6,

        alignment=ALIGN_LEFT,

        content=ft.Row(

            controls=controls,

            spacing=8,

            vertical_alignment=(
                ft.CrossAxisAlignment.CENTER
            ),
        ),
    )

# =========================================================
# TABLE ROW
# =========================================================

def table_row(

    controls,

    record=None,

    selected=False,

    on_click=None,
):

    bgcolor = (

        ROW_SELECTED_BG
        if selected
        else ROW_BG
    )

    return ft.Container(

        height=ROW_HEIGHT,

        bgcolor=bgcolor,

        border_radius=6,

        padding=ft.Padding(
            8,
            0,
            8,
            0,
        ),

        ink=True,

        on_click=on_click,

        content=ft.Row(

            controls=controls,

            spacing=8,

            vertical_alignment=(
                ft.CrossAxisAlignment.CENTER
            ),
        ),
    )

# =========================================================
# PAGINATION
# =========================================================

def pagination_bar(

    page_number,

    total_pages,

    on_previous=None,

    on_next=None,
):

    return ft.Row(

        spacing=6,

        alignment=(
            ft.MainAxisAlignment.END
        ),

        controls=[

            ft.IconButton(

                icon=(
                    ft.Icons.ARROW_BACK
                ),

                tooltip="Anterior",

                disabled=(
                    page_number <= 1
                ),

                on_click=on_previous,
            ),

            ft.Text(

                (
                    f"Página "
                    f"{page_number} "
                    f"de "
                    f"{total_pages}"
                ),

                size=TEXT_SIZE,

                color=TEXT_SECONDARY,
            ),

            ft.IconButton(

                icon=(
                    ft.Icons.ARROW_FORWARD
                ),

                tooltip="Próxima",

                disabled=(
                    page_number >= total_pages
                ),

                on_click=on_next,
            ),
        ],
    )

# =========================================================
# TOOLBAR
# =========================================================

def table_toolbar(

    title=None,

    on_new=None,

    on_refresh=None,

    search_field=None,

    extra_actions=None,
):

    extra_actions = (
        extra_actions or []
    )

    controls = []

    if search_field:

        controls.append(
            search_field
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

    if on_new:

        controls.append(

            ft.FilledButton(

                content=button_content(
                    "Novo",
                    ft.Icons.ADD,
                ),

                height=34,

                on_click=on_new,
            )
        )

    controls.extend(
        extra_actions
    )

    return ft.Row(

        alignment=(
            ft.MainAxisAlignment
            .SPACE_BETWEEN
        ),

        vertical_alignment=(
            ft.CrossAxisAlignment.CENTER
        ),

        controls=[

            ft.Text(

                title or "",

                size=15,

                weight=(
                    ft.FontWeight.BOLD
                ),
            ),

            ft.Row(

                spacing=4,

                controls=controls,
            ),
        ],
    )

# =========================================================
# TABLE LOADING
# =========================================================

def table_loading():

    return ft.Container(

        padding=20,

        alignment=ALIGN_CENTER,

        content=ft.ProgressRing(

            width=28,

            height=28,

            stroke_width=3,
        ),
    )

# =========================================================
# DATA TABLE
# =========================================================

def data_table(

    columns,

    rows,

    title=None,

    empty_message=(
        "Nenhum registro encontrado."
    ),

    toolbar=None,

    pagination=None,
):

    if not rows:

        return empty_card(
            message=empty_message
        )

    content = [

        table_header(columns),

        *rows,
    ]

    controls = []

    if toolbar:

        controls.append(
            toolbar
        )

    controls.append(

        ft.Container(

            expand=True,

            content=ft.Column(

                scroll=(
                    ft.ScrollMode.AUTO
                ),

                spacing=2,

                tight=True,

                controls=content,
            ),
        )
    )

    if pagination:

        controls.append(
            pagination
        )

    return app_card(

        content=ft.Column(

            expand=True,

            spacing=SPACING_LG,

            controls=controls,
        )
    )


def simple_table(

    columns,

    rows,

    dense=False,
):

    spacing = 1 if dense else 4

    return ft.Column(

        expand=True,

        spacing=spacing,

        scroll=ft.ScrollMode.AUTO,

        controls=[

            table_header(columns),

            *rows,
        ],
    )

# =========================================================
# SEARCH FIELD
# =========================================================

def search_field(
    hint="Pesquisar...",
    on_change=None,
):

    return ft.TextField(

        hint_text=hint,

        dense=True,

        height=34,

        width=260,

        prefix_icon=(
            ft.Icons.SEARCH
        ),

        on_change=on_change,
    )

# =========================================================
# GRID ENGINE
# =========================================================

class DataGrid:

    def __init__(

        self,

        page,

        records,

        build_row,

        columns,

        title=None,
    ):

        self.page = page

        self.records = (
            records or []
        )

        self.filtered = (
            self.records.copy()
        )

        self.build_row = build_row

        self.columns = columns

        self.title = title

        self.page_number = 1

        self.page_size = PAGE_SIZE

        self.search_text = ""

    # =====================================================
    # FILTER
    # =====================================================

    def apply_filter(
        self,
    ):

        texto = (

            self.search_text
            .strip()
            .lower()
        )

        if not texto:

            self.filtered = (
                self.records.copy()
            )

            return

        resultado = []

        for item in self.records:

            texto_item = str(
                item
            ).lower()

            if texto in texto_item:

                resultado.append(
                    item
                )

        self.filtered = resultado

    # =====================================================
    # PAGE
    # =====================================================

    def total_pages(
        self,
    ):

        if not self.filtered:

            return 1

        return max(

            1,

            math.ceil(

                len(self.filtered)
                / self.page_size
            ),
        )

    def page_items(
        self,
    ):

        inicio = (

            (self.page_number - 1)
            * self.page_size
        )

        fim = (
            inicio
            + self.page_size
        )

        return self.filtered[
            inicio:fim
        ]

    # =====================================================
    # SEARCH
    # =====================================================

    def on_search(
        self,
        e,
    ):

        self.search_text = (
            e.control.value or ""
        )

        self.page_number = 1

        self.apply_filter()

        self.refresh()

    # =====================================================
    # PAGINATION
    # =====================================================

    def next_page(
        self,
        e,
    ):

        if (

            self.page_number
            < self.total_pages()
        ):

            self.page_number += 1

            self.refresh()

    def previous_page(
        self,
        e,
    ):

        if self.page_number > 1:

            self.page_number -= 1

            self.refresh()

    # =====================================================
    # REFRESH
    # =====================================================

    def refresh(
        self,
    ):

        self.container.content = (
            self.build()
        )

        self.page.update()

    # =====================================================
    # BUILD ROWS
    # =====================================================

    def build_rows(
        self,
    ):

        rows = []

        selecionado = (
            get_selected_record()
        )

        for item in self.page_items():

            row = self.build_row(
                item
            )

            rows.append(

                table_row(

                    controls=row,

                    record=item,

                    selected=(
                        selecionado
                        == item
                    ),

                    on_click=lambda e,
                    r=item: (
                        set_selected_record(
                            r
                        ),
                        self.refresh(),
                    ),
                )
            )

        return rows

    # =====================================================
    # BUILD
    # =====================================================

    def build(
        self,
    ):

        self.apply_filter()

        toolbar = table_toolbar(

            title=self.title,

            search_field=search_field(
                on_change=self.on_search
            ),
        )

        pagination = pagination_bar(

            page_number=(
                self.page_number
            ),

            total_pages=(
                self.total_pages()
            ),

            on_previous=(
                self.previous_page
            ),

            on_next=self.next_page,
        )

        return data_table(

            columns=self.columns,

            rows=self.build_rows(),

            toolbar=toolbar,

            pagination=pagination,
        )

    # =====================================================
    # RENDER
    # =====================================================

    def render(
        self,
    ):

        self.container = ft.Container(
            expand=True,
        )

        self.container.content = (
            self.build()
        )

        return self.container

# =========================================================
# RESPONSIVE TABLE
# =========================================================

def responsive_table(
    cards,
):

    return ft.ResponsiveRow(

        controls=cards,

        spacing=8,

        run_spacing=8,
    )
