# =========================================================
# core/themes.py
# =========================================================

import flet as ft

# =========================================================
# BRAND
# =========================================================

PRIMARY_COLOR = ft.Colors.BLUE_700

PRIMARY_LIGHT = ft.Colors.BLUE_50

PRIMARY_DARK = ft.Colors.BLUE_900

SECONDARY_COLOR = ft.Colors.INDIGO_400

ACCENT_COLOR = ft.Colors.CYAN_500

# =========================================================
# SEMANTIC COLORS
# =========================================================

SUCCESS_COLOR = ft.Colors.GREEN_600

WARNING_COLOR = ft.Colors.ORANGE_700

ERROR_COLOR = ft.Colors.RED_600

INFO_COLOR = ft.Colors.BLUE_600

# =========================================================
# SURFACES
# =========================================================

BACKGROUND_COLOR = ft.Colors.GREY_100

CONTENT_BG = BACKGROUND_COLOR

SURFACE_COLOR = ft.Colors.WHITE

SURFACE_VARIANT = ft.Colors.BLUE_GREY_50

SURFACE_HOVER = ft.Colors.BLUE_GREY_100

SURFACE_SELECTED = ft.Colors.BLUE_50

# =========================================================
# TEXT
# =========================================================

TEXT_PRIMARY = ft.Colors.BLACK87

TEXT_SECONDARY = ft.Colors.GREY_700

TEXT_DISABLED = ft.Colors.GREY_500

TEXT_ON_PRIMARY = ft.Colors.WHITE

# =========================================================
# BORDERS
# =========================================================

BORDER_COLOR = ft.Colors.GREY_300

DIVIDER_COLOR = BORDER_COLOR

# =========================================================
# SIDEBAR
# =========================================================

SIDEBAR_BG = SURFACE_COLOR

SIDEBAR_BORDER = BORDER_COLOR

SIDEBAR_TEXT = TEXT_PRIMARY

SIDEBAR_ACTIVE_BG = PRIMARY_LIGHT

SIDEBAR_ACTIVE_TEXT = PRIMARY_COLOR

ACTIVE_BG = SIDEBAR_ACTIVE_BG

ACTIVE_COLOR = SIDEBAR_ACTIVE_TEXT

SIDEBAR_WIDTH = 260

SIDEBAR_COLLAPSED_WIDTH = 72

# =========================================================
# TOPBAR
# =========================================================

TOPBAR_BG = SURFACE_COLOR

TOPBAR_BORDER = BORDER_COLOR

TOPBAR_HEIGHT = 56

# =========================================================
# TABLES
# =========================================================

TABLE_HEADER_BG = ft.Colors.BLUE_GREY_50

TABLE_ROW_BG = SURFACE_COLOR

TABLE_ROW_HOVER = ft.Colors.BLUE_50

TABLE_ROW_SELECTED = ft.Colors.BLUE_100

# =========================================================
# DIALOGS
# =========================================================

DIALOG_BG = SURFACE_COLOR

# =========================================================
# TYPOGRAPHY
# =========================================================

FONT_FAMILY = "Segoe UI"

TEXT_SIZE_XS = 10

TEXT_SIZE_SM = 11

TEXT_SIZE_MD = 12

TEXT_SIZE_LG = 14

TEXT_SIZE_XL = 18

TEXT_SIZE_TITLE = 24

TEXT_SIZE_HERO = 32

# =========================================================
# RADIUS
# =========================================================

RADIUS_XS = 4

RADIUS_SM = 8

RADIUS_MD = 12

RADIUS_LG = 16

RADIUS_XL = 20

# =========================================================
# SPACING
# =========================================================

SPACING_XS = 4

SPACING_SM = 8

SPACING_MD = 12

SPACING_LG = 16

SPACING_XL = 24

SPACING_XXL = 32

# =========================================================
# BUTTONS
# =========================================================

BUTTON_HEIGHT = 36

BUTTON_RADIUS = RADIUS_MD

BUTTON_PADDING = 16

FILLED_BUTTON_STYLE = ft.ButtonStyle(

    bgcolor=PRIMARY_COLOR,

    color=TEXT_ON_PRIMARY,

    shape=ft.RoundedRectangleBorder(
        radius=BUTTON_RADIUS
    ),

    padding=BUTTON_PADDING,
)

OUTLINED_BUTTON_STYLE = ft.ButtonStyle(

    color=PRIMARY_COLOR,

    shape=ft.RoundedRectangleBorder(
        radius=BUTTON_RADIUS
    ),

    padding=BUTTON_PADDING,
)

# =========================================================
# INPUTS
# =========================================================

INPUT_HEIGHT = 42

INPUT_RADIUS = RADIUS_MD

TEXTFIELD_BORDER_RADIUS = INPUT_RADIUS

# =========================================================
# CARDS
# =========================================================

CARD_RADIUS = RADIUS_LG

CARD_ELEVATION = 1

CARD_PADDING = 20

# =========================================================
# TOOLBAR
# =========================================================

TOOLBAR_HEIGHT = 48

# =========================================================
# SHADOWS
# =========================================================

DEFAULT_SHADOW = ft.BoxShadow(

    blur_radius=10,

    spread_radius=1,

    color=ft.Colors.BLACK12,
)

# =========================================================
# ANIMATION
# =========================================================

ANIMATION_DURATION = 250

# =========================================================
# ERP THEME
# =========================================================

ERP_THEME = ft.Theme(

    color_scheme_seed=PRIMARY_COLOR,

    font_family=FONT_FAMILY,
)

# =========================================================
# ERP DARK THEME
# =========================================================

ERP_DARK_THEME = ft.Theme(

    color_scheme_seed=PRIMARY_COLOR,

    font_family=FONT_FAMILY,
)

# =========================================================
# APPLY THEME
# =========================================================

def apply_theme(
    page,
):

    page.theme = ERP_THEME

    page.dark_theme = ERP_DARK_THEME

    page.theme_mode = (
        ft.ThemeMode.LIGHT
    )

    page.bgcolor = (
        BACKGROUND_COLOR
    )

    return page

# =========================================================
# LEGACY COMPATIBILITY
# =========================================================

APP_BG = BACKGROUND_COLOR

CARD_BG = SURFACE_COLOR

MENU_BG = SIDEBAR_BG

MENU_ACTIVE_BG = SIDEBAR_ACTIVE_BG

MENU_ACTIVE_TEXT = SIDEBAR_ACTIVE_TEXT
