# core/menu_constants.py

"""
=========================================================
DOMÍNIO CENTRAL DE MENUS
=========================================================

Objetivos:
- eliminar hardcode
- centralizar regras estruturais
- centralizar metadados
- desacoplar UI
- suportar crescimento futuro
- suportar múltiplos frontends
- suportar renderização dinâmica
"""

from dataclasses import dataclass
from typing import Optional


# =========================================================
# ADMIN LEVELS
# =========================================================

ADMIN_LEVEL_USER = 10

ADMIN_LEVEL_ADMIN = 50

ADMIN_LEVEL_ROOT = 100


# =========================================================
# TIPOS
# =========================================================

TIPO_TITULO = "T"

TIPO_MENU = "M"

TIPO_SUBMENU = "S"


# =========================================================
# UI CONFIG
# =========================================================

MENU_UI_CONFIG = {

    "indent_size": 20,

    "compact_height": 56,

    "dense_spacing": 4,

    "border_radius": 8,

    "icon_size": 16,

    "font_size": 13,

    "sub_font_size": 10,

    "max_depth": 10,

    "padding_x": 8,

    "padding_y": 4
}


# =========================================================
# TREE CONFIG
# =========================================================

TREE_CONFIG = {

    "max_depth": 10,

    "allow_orphans": False,

    "sort_case_insensitive": True,

    "auto_fix_missing_parent": True
}


# =========================================================
# FEATURE FLAGS
# =========================================================

FEATURE_FLAGS = {

    "lazy_render": False,

    "virtual_scroll": False,

    "dynamic_loading": False,

    "cache_enabled": True
}


# =========================================================
# MENU TYPE
# =========================================================

@dataclass(frozen=True)
class MenuTipo:

    codigo: str

    label: str

    descricao: str

    icone: str

    cor: str

    permite_rota: bool

    permite_pai: bool

    permite_filhos: bool

    pais_validos: list[str]

    ordem_default: int = 10

    admin_level_minimo: int = (
        ADMIN_LEVEL_USER
    )

    estrutural: bool = False

    expandable: bool = True

    bold: bool = False

    uppercase: bool = False


# =========================================================
# MENU TYPES
# =========================================================

MENU_TIPOS = {

    # =====================================================
    # TÍTULO
    # =====================================================

    TIPO_TITULO:

        MenuTipo(

            codigo=TIPO_TITULO,

            label="Título",

            descricao=(
                "Agrupador estrutural."
            ),

            icone="folder",

            cor="BLUE_50",

            permite_rota=False,

            permite_pai=False,

            permite_filhos=True,

            pais_validos=[],

            ordem_default=10,

            expandable=True,

            bold=True
        ),

    # =====================================================
    # MENU
    # =====================================================

    TIPO_MENU:

        MenuTipo(

            codigo=TIPO_MENU,

            label="Menu",

            descricao=(
                "Menu navegável."
            ),

            icone="menu",

            cor="GREY_100",

            permite_rota=True,

            permite_pai=True,

            permite_filhos=True,

            pais_validos=[
                TIPO_TITULO
            ],

            ordem_default=20,

            expandable=True
        ),

    # =====================================================
    # SUBMENU
    # =====================================================

    TIPO_SUBMENU:

        MenuTipo(

            codigo=TIPO_SUBMENU,

            label="Submenu",

            descricao=(
                "Subitem operacional."
            ),

            icone="web",

            cor="WHITE",

            permite_rota=False,

            permite_pai=True,

            permite_filhos=False,

            pais_validos=[
                TIPO_TITULO,
                TIPO_MENU
            ],

            ordem_default=30,

            expandable=False
        )
}


# =========================================================
# SCREEN REGISTRY
# =========================================================
#
# OBS:
# Layout usa este mapa para resolver views.
# Futuramente pode migrar para:
# ui/screen_registry.py
# =========================================================

SCREEN_ROUTE_MAP = {

    "dashboard": "dashboard_view",

    "menu": "menu_admin_view",

    "menu_admin": "menu_admin_view",

    "menu_config": "menu_admin_view",

    "menus": "menu_admin_view",

    "menu_editor": "menu_editor_view",

    "menus_editor": "menu_editor_view",

    "editor_menu": "menu_editor_view",

    "usuarios": "usuarios_view",

    "perfis": "perfis_view"
}


# =========================================================
# UI ICON MAP
# =========================================================
#
# Mapeamento abstrato.
# UI decide como traduzir.
# =========================================================

MENU_ICON_MAP = {

    "folder": "FOLDER",

    "menu": "MENU",

    "web": "WEB",

    "help": "HELP"
}


# =========================================================
# HELPERS
# =========================================================

def tipos_menu():

    return list(
        MENU_TIPOS.keys()
    )


def tipo_existe(tipo):

    return (
        str(tipo).upper()
        in
        MENU_TIPOS
    )


def get_tipo(tipo):

    return MENU_TIPOS.get(
        str(tipo).upper()
    )


def get_label(tipo):

    obj = get_tipo(tipo)

    if not obj:
        return "Desconhecido"

    return obj.label


def get_descricao(tipo):

    obj = get_tipo(tipo)

    if not obj:
        return ""

    return obj.descricao


def get_icone(tipo):

    obj = get_tipo(tipo)

    if not obj:
        return "help"

    return obj.icone


def get_cor(tipo):

    obj = get_tipo(tipo)

    if not obj:
        return "WHITE"

    return obj.cor


def get_icon_ui(tipo):

    icone = get_icone(tipo)

    return MENU_ICON_MAP.get(
        icone,
        "HELP"
    )


def permite_rota(tipo):

    obj = get_tipo(tipo)

    if not obj:
        return False

    return obj.permite_rota


def permite_pai(tipo):

    obj = get_tipo(tipo)

    if not obj:
        return False

    return obj.permite_pai


def permite_filhos(tipo):

    obj = get_tipo(tipo)

    if not obj:
        return False

    return obj.permite_filhos


def get_pais_validos(tipo):

    obj = get_tipo(tipo)

    if not obj:
        return []

    return obj.pais_validos


def get_ordem_default(tipo):

    obj = get_tipo(tipo)

    if not obj:
        return 10

    return obj.ordem_default


def get_admin_level_minimo(tipo):

    obj = get_tipo(tipo)

    if not obj:
        return ADMIN_LEVEL_USER

    return obj.admin_level_minimo


def is_expandable(tipo):

    obj = get_tipo(tipo)

    if not obj:
        return False

    return obj.expandable


def is_bold(tipo):

    obj = get_tipo(tipo)

    if not obj:
        return False

    return obj.bold


def is_uppercase(tipo):

    obj = get_tipo(tipo)

    if not obj:
        return False

    return obj.uppercase


def is_root_tipo(tipo):

    return not permite_pai(
        tipo
    )


def is_leaf_tipo(tipo):

    return not permite_filhos(
        tipo
    )


def validar_hierarquia(

    tipo_filho,

    tipo_pai=None
):

    tipo_filho = str(
        tipo_filho or ""
    ).upper()

    tipo_pai = (

        str(tipo_pai).upper()

        if tipo_pai

        else None
    )

    # =====================================================
    # FILHO INVÁLIDO
    # =====================================================

    if not tipo_existe(
        tipo_filho
    ):

        return False

    # =====================================================
    # SEM PAI
    # =====================================================

    if not tipo_pai:

        return not permite_pai(
            tipo_filho
        )

    # =====================================================
    # PAI INVÁLIDO
    # =====================================================

    if not tipo_existe(
        tipo_pai
    ):

        return False

    return (

        tipo_pai

        in

        get_pais_validos(
            tipo_filho
        )
    )


# =========================================================
# TREE HELPERS
# =========================================================

def get_indent(nivel):

    return int(
        nivel
    ) * int(
        MENU_UI_CONFIG[
            "indent_size"
        ]
    )


def get_max_depth():

    return int(
        TREE_CONFIG[
            "max_depth"
        ]
    )


def allows_orphans():

    return bool(
        TREE_CONFIG[
            "allow_orphans"
        ]
    )


def auto_fix_missing_parent():

    return bool(
        TREE_CONFIG[
            "auto_fix_missing_parent"
        ]
    )


# =========================================================
# SCREEN HELPERS
# =========================================================

def get_screen_view(rota):

    return SCREEN_ROUTE_MAP.get(
        str(rota or "")
        .strip()
        .lower()
    )


# =========================================================
# SERIALIZAÇÃO
# =========================================================

def serializar_tipo(tipo):

    obj = get_tipo(tipo)

    if not obj:
        return None

    return {

        "codigo": obj.codigo,

        "label": obj.label,

        "descricao": obj.descricao,

        "icone": obj.icone,

        "cor": obj.cor,

        "permite_rota":
            obj.permite_rota,

        "permite_pai":
            obj.permite_pai,

        "permite_filhos":
            obj.permite_filhos,

        "pais_validos":
            obj.pais_validos,

        "ordem_default":
            obj.ordem_default,

        "admin_level_minimo":
            obj.admin_level_minimo,

        "estrutural":
            obj.estrutural,

        "expandable":
            obj.expandable,

        "bold":
            obj.bold,

        "uppercase":
            obj.uppercase
    }


def serializar_tipos():

    return {

        codigo: serializar_tipo(
            codigo
        )

        for codigo in MENU_TIPOS
    }


# =========================================================
# EXPORTS
# =========================================================

__all__ = [

    # LEVELS
    "ADMIN_LEVEL_USER",
    "ADMIN_LEVEL_ADMIN",
    "ADMIN_LEVEL_ROOT",

    # TIPOS
    "TIPO_TITULO",
    "TIPO_MENU",
    "TIPO_SUBMENU",

    # CONFIG
    "MENU_UI_CONFIG",
    "TREE_CONFIG",
    "FEATURE_FLAGS",

    # TYPES
    "MENU_TIPOS",

    # SCREEN
    "SCREEN_ROUTE_MAP",

    # ICONS
    "MENU_ICON_MAP",

    # HELPERS
    "tipos_menu",
    "tipo_existe",
    "get_tipo",
    "get_label",
    "get_descricao",
    "get_icone",
    "get_cor",
    "get_icon_ui",
    "permite_rota",
    "permite_pai",
    "permite_filhos",
    "get_pais_validos",
    "get_ordem_default",
    "get_admin_level_minimo",
    "is_expandable",
    "is_bold",
    "is_uppercase",
    "is_root_tipo",
    "is_leaf_tipo",
    "validar_hierarquia",

    # TREE
    "get_indent",
    "get_max_depth",
    "allows_orphans",
    "auto_fix_missing_parent",

    # SCREEN
    "get_screen_view",

    # SERIALIZE
    "serializar_tipo",
    "serializar_tipos"
]
