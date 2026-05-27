# ui/themes.py

import flet as ft

# =========================================================
# COLORS
# =========================================================

PRIMARY_COLOR = ft.Colors.BLUE_700

SECONDARY_COLOR = ft.Colors.BLUE_400

BACKGROUND_COLOR = ft.Colors.GREY_100

SURFACE_COLOR = ft.Colors.WHITE

ERROR_COLOR = ft.Colors.RED_400

SUCCESS_COLOR = ft.Colors.GREEN_600

TEXT_COLOR = ft.Colors.BLACK87

TEXT_SECONDARY = ft.Colors.GREY_700

BORDER_COLOR = ft.Colors.GREY_300

# =========================================================
# BORDER RADIUS
# =========================================================

RADIUS_SMALL = 8

RADIUS_MEDIUM = 12

RADIUS_LARGE = 16

RADIUS_XL = 20

# =========================================================
# SPACING
# =========================================================

SPACING_XS = 4

SPACING_SM = 8

SPACING_MD = 12

SPACING_LG = 16

SPACING_XL = 24

# =========================================================
# BUTTON STYLE
# =========================================================

BUTTON_STYLE = ft.ButtonStyle(
    shape=ft.RoundedRectangleBorder(
        radius=RADIUS_MEDIUM
    ),
    padding=16,
)

# =========================================================
# FILLED BUTTON STYLE
# =========================================================

FILLED_BUTTON_STYLE = ft.ButtonStyle(
    shape=ft.RoundedRectangleBorder(
        radius=RADIUS_MEDIUM
    ),
    padding=16,
    bgcolor=PRIMARY_COLOR,
    color=ft.Colors.WHITE,
)

# =========================================================
# OUTLINED BUTTON STYLE
# =========================================================

OUTLINED_BUTTON_STYLE = ft.ButtonStyle(
    shape=ft.RoundedRectangleBorder(
        radius=RADIUS_MEDIUM
    ),
    padding=16,
)

# =========================================================
# TEXTFIELD STYLE
# =========================================================

TEXTFIELD_BORDER_RADIUS = RADIUS_MEDIUM

# =========================================================
# CARD STYLE
# =========================================================

CARD_ELEVATION = 2

CARD_RADIUS = RADIUS_LARGE

# =========================================================
# SNACKBAR
# =========================================================

def show_snackbar(
    page: ft.Page,
    message: str,
    error: bool = False,
):

    page.snack_bar = ft.SnackBar(
        content=ft.Text(message),
        bgcolor=(
            ERROR_COLOR
            if error
            else SUCCESS_COLOR
        ),
        behavior=(
            ft.SnackBarBehavior.FLOATING
        ),
        show_close_icon=True,
        duration=3000,
    )

    page.snack_bar.open = True

    page.update()

# =========================================================
# LIGHT THEME
# =========================================================

LIGHT_THEME = ft.Theme(
    color_scheme_seed=PRIMARY_COLOR,
    use_material3=True,
)

# =========================================================
# DARK THEME
# =========================================================

DARK_THEME = ft.Theme(
    color_scheme_seed=PRIMARY_COLOR,
    use_material3=True,
)

# =========================================================
# APP THEME
# =========================================================

APP_THEME = {
    "mode": ft.ThemeMode.LIGHT,
    "theme": LIGHT_THEME,
    "dark_theme": DARK_THEME,
    "bgcolor": BACKGROUND_COLOR,
}

# =========================================================
# APPLY THEME
# =========================================================

def apply_theme(page: ft.Page):

    page.theme_mode = APP_THEME["mode"]

    page.theme = APP_THEME["theme"]

    page.dark_theme = APP_THEME["dark_theme"]

    page.bgcolor = APP_THEME["bgcolor"]

    page.update()
