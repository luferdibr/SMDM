# =========================================================
# core/state/state.py
# =========================================================

# =========================================================
# GLOBAL STATE
# =========================================================

APP_STATE = {

    # =====================================================
    # AUTH
    # =====================================================

    "usuario": None,

    "autenticado": False,

    # =====================================================
    # NAVIGATION
    # =====================================================

    "current_route": "dashboard",

    "previous_route": None,

    "current_view": None,

    "last_view": None,

    # =====================================================
    # UI
    # =====================================================

    "theme_mode": "light",

    "sidebar_expanded": True,

    "fullscreen": False,

    "loading": False,

    # =====================================================
    # OPERATIONAL
    # =====================================================

    "operational_mode": False,

    "selected_record": None,

    "selected_module": None,

    # =====================================================
    # CACHE
    # =====================================================

    "cache": {

        "menus": None,

        "permissions": None,
    },

    # =====================================================
    # FILTERS
    # =====================================================

    "filters": {},

    # =====================================================
    # SETTINGS
    # =====================================================

    "settings": {},

    # =====================================================
    # TEMP
    # =====================================================

    "temp": {},
}

# =========================================================
# USER
# =========================================================

def set_user(
    usuario,
):

    APP_STATE["usuario"] = usuario

    APP_STATE["autenticado"] = bool(
        usuario
    )

def get_user():

    return APP_STATE.get(
        "usuario"
    )

def clear_user():

    APP_STATE["usuario"] = None

    APP_STATE["autenticado"] = False

# =========================================================
# AUTH
# =========================================================

def is_authenticated():

    return bool(

        APP_STATE.get(
            "autenticado"
        )
    )

# =========================================================
# ROUTE
# =========================================================

def set_route(
    route,
):

    APP_STATE[
        "previous_route"
    ] = APP_STATE.get(
        "current_route"
    )

    APP_STATE[
        "current_route"
    ] = route

def get_route():

    return APP_STATE.get(
        "current_route"
    )

def get_previous_route():

    return APP_STATE.get(
        "previous_route"
    )

# =========================================================
# VIEW
# =========================================================

def set_current_view(
    view_name,
):

    APP_STATE[
        "last_view"
    ] = APP_STATE.get(
        "current_view"
    )

    APP_STATE[
        "current_view"
    ] = view_name

def get_current_view():

    return APP_STATE.get(
        "current_view"
    )

def get_last_view():

    return APP_STATE.get(
        "last_view"
    )

# =========================================================
# SIDEBAR
# =========================================================

def set_sidebar_expanded(
    expanded: bool,
):

    APP_STATE[
        "sidebar_expanded"
    ] = expanded

def is_sidebar_expanded():

    return bool(

        APP_STATE.get(
            "sidebar_expanded"
        )
    )

def expand_sidebar():

    set_sidebar_expanded(
        True
    )

def collapse_sidebar():

    set_sidebar_expanded(
        False
    )

def toggle_sidebar():

    atual = is_sidebar_expanded()

    set_sidebar_expanded(
        not atual
    )

# =========================================================
# FULLSCREEN
# =========================================================

def set_fullscreen(
    value: bool,
):

    APP_STATE[
        "fullscreen"
    ] = value

def is_fullscreen():

    return bool(

        APP_STATE.get(
            "fullscreen"
        )
    )

# =========================================================
# OPERATIONAL MODE
# =========================================================

def set_operational_mode(
    value: bool,
):

    APP_STATE[
        "operational_mode"
    ] = value

def is_operational_mode():

    return bool(

        APP_STATE.get(
            "operational_mode"
        )
    )

# =========================================================
# MODULE
# =========================================================

def set_selected_module(
    module_name,
):

    APP_STATE[
        "selected_module"
    ] = module_name

def get_selected_module():

    return APP_STATE.get(
        "selected_module"
    )

# =========================================================
# RECORD
# =========================================================

def set_selected_record(
    record,
):

    APP_STATE[
        "selected_record"
    ] = record

def get_selected_record():

    return APP_STATE.get(
        "selected_record"
    )

def clear_selected_record():

    APP_STATE[
        "selected_record"
    ] = None

# =========================================================
# THEME
# =========================================================

def set_theme_mode(
    mode: str,
):

    APP_STATE[
        "theme_mode"
    ] = mode

def get_theme_mode():

    return APP_STATE.get(
        "theme_mode",
        "light",
    )

def is_dark_mode():

    return (
        get_theme_mode()
        == "dark"
    )

def toggle_theme():

    if is_dark_mode():

        set_theme_mode(
            "light"
        )

    else:

        set_theme_mode(
            "dark"
        )

# =========================================================
# LOADING
# =========================================================

def set_loading(
    value: bool,
):

    APP_STATE[
        "loading"
    ] = value

def is_loading():

    return bool(

        APP_STATE.get(
            "loading"
        )
    )

# =========================================================
# CACHE
# =========================================================

def set_cache(
    key,
    value,
):

    APP_STATE[
        "cache"
    ][key] = value

def get_cache(
    key,
    default=None,
):

    return APP_STATE[
        "cache"
    ].get(
        key,
        default,
    )

def remove_cache(
    key,
):

    APP_STATE[
        "cache"
    ].pop(
        key,
        None,
    )

def clear_cache():

    APP_STATE[
        "cache"
    ] = {}

# =========================================================
# FILTERS
# =========================================================

def set_filter(
    key,
    value,
):

    APP_STATE[
        "filters"
    ][key] = value

def get_filter(
    key,
    default=None,
):

    return APP_STATE[
        "filters"
    ].get(
        key,
        default,
    )

def clear_filters():

    APP_STATE[
        "filters"
    ] = {}

# =========================================================
# SETTINGS
# =========================================================

def set_setting(
    key,
    value,
):

    APP_STATE[
        "settings"
    ][key] = value

def get_setting(
    key,
    default=None,
):

    return APP_STATE[
        "settings"
    ].get(
        key,
        default,
    )

# =========================================================
# TEMP
# =========================================================

def set_temp(
    key,
    value,
):

    APP_STATE[
        "temp"
    ][key] = value

def get_temp(
    key,
    default=None,
):

    return APP_STATE[
        "temp"
    ].get(
        key,
        default,
    )

def clear_temp():

    APP_STATE[
        "temp"
    ] = {}

# =========================================================
# RESET OPERATIONAL
# =========================================================

def reset_operational_state():

    APP_STATE[
        "operational_mode"
    ] = False

    APP_STATE[
        "selected_record"
    ] = None

    APP_STATE[
        "selected_module"
    ] = None

    APP_STATE[
        "fullscreen"
    ] = False

# =========================================================
# RESET
# =========================================================

def reset_state():

    clear_user()

    clear_cache()

    clear_filters()

    clear_temp()

    reset_operational_state()

    APP_STATE[
        "loading"
    ] = False

    APP_STATE[
        "current_route"
    ] = "dashboard"

    APP_STATE[
        "previous_route"
    ] = None

    APP_STATE[
        "current_view"
    ] = None

    APP_STATE[
        "last_view"
    ] = None

# =========================================================
# DEBUG
# =========================================================

def dump_state():

    return APP_STATE.copy()