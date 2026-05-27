# ui/components/permissions.py

# =========================================================
# ADMIN LEVELS
# =========================================================

ADMIN_LEVEL_USER = 10

ADMIN_LEVEL_MANAGER = 50

ADMIN_LEVEL_ADMIN = 90

ADMIN_LEVEL_ROOT = 100

# =========================================================
# GET USER
# =========================================================

def get_user(page):

    usuario = getattr(
        page,
        "usuario_logado",
        None,
    )

    if not usuario:

        return None

    if not isinstance(usuario, dict):

        return None

    return usuario

# =========================================================
# GET ADMIN LEVEL
# =========================================================

def get_admin_level(
    usuario,
):

    if not usuario:

        return 0

    try:

        return int(
            usuario.get(
                "admin_level",
                0,
            )
        )

    except Exception:

        return 0

# =========================================================
# ROOT
# =========================================================

def is_root(
    usuario,
):

    return (
        get_admin_level(usuario)
        >= ADMIN_LEVEL_ROOT
    )

# =========================================================
# ADMIN
# =========================================================

def is_admin(
    usuario,
):

    return (
        get_admin_level(usuario)
        >= ADMIN_LEVEL_ADMIN
    )

# =========================================================
# MANAGER
# =========================================================

def is_manager(
    usuario,
):

    return (
        get_admin_level(usuario)
        >= ADMIN_LEVEL_MANAGER
    )

# =========================================================
# AUTHENTICATED
# =========================================================

def is_authenticated(
    usuario,
):

    return bool(usuario)

# =========================================================
# GET PERMISSION
# =========================================================

def get_permission(
    usuario,
    rota,
):

    if not usuario:

        return {}

    permissoes = usuario.get(
        "permissoes",
        {},
    )

    return permissoes.get(
        rota,
        {},
    )

# =========================================================
# CAN VIEW
# =========================================================

def can_view(
    usuario,
    rota,
):

    if is_root(usuario):

        return True

    permissao = get_permission(
        usuario,
        rota,
    )

    return bool(
        permissao.get("ver")
    )

# =========================================================
# CAN EDIT
# =========================================================

def can_edit(
    usuario,
    rota,
):

    if is_root(usuario):

        return True

    permissao = get_permission(
        usuario,
        rota,
    )

    return bool(
        permissao.get("editar")
    )

# =========================================================
# CAN DELETE
# =========================================================

def can_delete(
    usuario,
    rota,
):

    if is_root(usuario):

        return True

    permissao = get_permission(
        usuario,
        rota,
    )

    return bool(
        permissao.get("excluir")
    )

# =========================================================
# CAN ACCESS
# =========================================================

def can_access(
    usuario,
    rota,
):

    return can_view(
        usuario,
        rota,
    )

# =========================================================
# HIDE IF NO ACCESS
# =========================================================

def visible_if_can_view(
    usuario,
    rota,
):

    return can_view(
        usuario,
        rota,
    )

# =========================================================
# DISABLED IF NO EDIT
# =========================================================

def disabled_if_no_edit(
    usuario,
    rota,
):

    return not can_edit(
        usuario,
        rota,
    )

# =========================================================
# DISABLED IF NO DELETE
# =========================================================

def disabled_if_no_delete(
    usuario,
    rota,
):

    return not can_delete(
        usuario,
        rota,
    )

# =========================================================
# REQUIRE ADMIN
# =========================================================

def require_admin(
    usuario,
):

    return is_admin(usuario)

# =========================================================
# REQUIRE ROOT
# =========================================================

def require_root(
    usuario,
):

    return is_root(usuario)

# =========================================================
# MENU FILTER
# =========================================================

def filter_visible_menus(
    usuario,
    menus,
):

    visiveis = []

    for menu in menus:

        rota = menu.get("rota")

        if not rota:

            visiveis.append(menu)

            continue

        if can_view(
            usuario,
            rota,
        ):

            visiveis.append(menu)

    return visiveis

# =========================================================
# BUTTON ENABLED
# =========================================================

def button_enabled(
    usuario,
    rota,
    action="editar",
):

    if action == "editar":

        return can_edit(
            usuario,
            rota,
        )

    if action == "excluir":

        return can_delete(
            usuario,
            rota,
        )

    return can_view(
        usuario,
        rota,
    )

# =========================================================
# PAGE GUARD
# =========================================================

def page_guard(
    usuario,
    rota,
):

    return can_access(
        usuario,
        rota,
    )
