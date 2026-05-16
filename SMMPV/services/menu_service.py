# services/menu_service.py

import logging

from database.connection import (
    get_connection
)

from core.menu_constants import (

    ADMIN_LEVEL_ROOT,

    tipo_existe
)


# ==================================================
# LOGGER
# ==================================================

LOGGER = logging.getLogger(
    "MDM_MENU_SERVICE"
)


# ==================================================
# HELPERS
# ==================================================

def normalizar_usuario(usuario):

    if not usuario:

        return {}

    return {

        "id": (
            usuario.get("id")
            or
            usuario.get("Id")
        ),

        "login": (
            usuario.get("login")
            or
            usuario.get("Login")
        ),

        "perfil_id": (
            usuario.get("perfil_id")
            or
            usuario.get("PerfilId")
        ),

        "admin_level": int(

            usuario.get("admin_level")

            or

            usuario.get("AdminLevel")

            or 0
        )
    }


def get_admin_level(usuario):

    usuario = normalizar_usuario(
        usuario
    )

    return int(
        usuario.get(
            "admin_level",
            0
        )
    )


def is_root(usuario):

    return (
        get_admin_level(usuario)
        >=
        ADMIN_LEVEL_ROOT
    )


# ==================================================
# MAP MENU
# ==================================================

def map_menu(row):

    tipo = str(
        row[5] or "M"
    ).strip().upper()

    if not tipo_existe(tipo):

        LOGGER.warning(
            (
                f"TipoMenu inválido: "
                f"{tipo}"
            )
        )

        tipo = "M"

    return {

        "id": row[0],

        "nome": str(
            row[1] or ""
        ).strip(),

        "rota": (
            str(row[2]).strip().lower()
            if row[2]
            else None
        ),

        "ordem": int(
            row[3] or 0
        ),

        "menu_pai": row[4],

        "tipo": tipo,

        "icone": (
            str(row[6] or "")
            .strip()
        ),

        "admin_level": int(
            row[7] or 0
        ),

        "filhos": []
    }


# ==================================================
# SORT MENUS
# ==================================================

def sort_menus(menus):

    return sorted(

        menus,

        key=lambda x: (

            int(
                x.get(
                    "ordem",
                    0
                )
            ),

            str(
                x.get(
                    "nome",
                    ""
                )
            ).upper()
        )
    )


# ==================================================
# BUILD TREE
# ==================================================

def build_tree(menus):

    LOGGER.info(
        (
            f"Montando árvore: "
            f"{len(menus)} menus"
        )
    )

    mapa = {}

    raiz = []

    # ==============================================
    # INDEX
    # ==============================================

    for menu in menus:

        menu["filhos"] = []

        mapa[
            menu["id"]
        ] = menu

    # ==============================================
    # VINCULAÇÃO
    # ==============================================

    for menu in menus:

        pai = menu.get(
            "menu_pai"
        )

        # ==========================================
        # RAIZ
        # ==========================================

        if pai is None:

            raiz.append(menu)

            LOGGER.info(
                (
                    f"RAIZ: "
                    f"{menu['nome']} "
                    f"[{menu['tipo']}]"
                )
            )

            continue

        # ==========================================
        # PAI NÃO ENCONTRADO
        # ==========================================

        if pai not in mapa:

            LOGGER.warning(
                (
                    f"Pai não encontrado | "
                    f"menu={menu['nome']} "
                    f"pai={pai}"
                )
            )

            raiz.append(menu)

            continue

        # ==========================================
        # FILHO
        # ==========================================

        mapa[pai][
            "filhos"
        ].append(menu)

        LOGGER.info(
            (
                f"Vinculado: "
                f"{menu['nome']} -> "
                f"{mapa[pai]['nome']}"
            )
        )

    # ==============================================
    # SORT RECURSIVO
    # ==============================================

    def ordenar(items):

        items = sort_menus(items)

        for item in items:

            filhos = item.get(
                "filhos",
                []
            )

            if filhos:

                item["filhos"] = ordenar(
                    filhos
                )

        return items

    arvore = ordenar(raiz)

    LOGGER.info(
        (
            f"Árvore final: "
            f"{len(arvore)} raízes"
        )
    )

    return arvore


# ==================================================
# SQL BASE
# ==================================================

def get_sql_root():

    return """

        SELECT
            m.Id,
            m.Nome,
            m.Rota,
            m.Ordem,
            m.MenuPaiId,
            m.TipoMenu,
            ISNULL(m.Icone, ''),
            m.AdminLevel

        FROM Menu m

        WHERE
            m.Ativo = 1

        ORDER BY
            ISNULL(m.MenuPaiId, 0),
            m.Ordem,
            m.Nome

    """


def get_sql_perfil():

    return """

        SELECT
            m.Id,
            m.Nome,
            m.Rota,
            m.Ordem,
            m.MenuPaiId,
            m.TipoMenu,
            ISNULL(m.Icone, ''),
            m.AdminLevel

        FROM PerfilMenu pm

        INNER JOIN Menu m
            ON m.Id = pm.MenuId

        WHERE
            pm.PerfilId = ?
            AND pm.PodeVer = 1
            AND m.Ativo = 1
            AND m.AdminLevel <= ?

        ORDER BY
            ISNULL(m.MenuPaiId, 0),
            m.Ordem,
            m.Nome

    """


# ==================================================
# LISTAR MENUS
# ==================================================

def listar_menus_usuario(usuario):

    conn = None

    try:

        usuario = normalizar_usuario(
            usuario
        )

        LOGGER.info(
            (
                f"Usuário normalizado: "
                f"{usuario}"
            )
        )

        perfil_id = usuario.get(
            "perfil_id"
        )

        admin_level = get_admin_level(
            usuario
        )

        LOGGER.info(
            (
                f"Carregando menus | "
                f"perfil={perfil_id} | "
                f"admin_level={admin_level}"
            )
        )

        if not perfil_id:

            LOGGER.warning(
                "Usuário sem perfil."
            )

            return []

        conn = get_connection()

        cursor = conn.cursor()

        # ==========================================
        # ROOT
        # ==========================================

        if is_root(usuario):

            LOGGER.info(
                "Carregamento ROOT"
            )

            cursor.execute(
                get_sql_root()
            )

        # ==========================================
        # PERFIL
        # ==========================================

        else:

            LOGGER.info(
                "Carregamento PerfilMenu"
            )

            cursor.execute(

                get_sql_perfil(),

                (
                    perfil_id,
                    admin_level
                )
            )

        rows = cursor.fetchall()

        LOGGER.info(
            (
                f"Menus SQL: "
                f"{len(rows)}"
            )
        )

        menus = []

        for row in rows:

            menu = map_menu(row)

            menus.append(menu)

            LOGGER.info(
                (
                    f"MENU: "
                    f"{menu['id']} | "
                    f"{menu['nome']} | "
                    f"tipo={menu['tipo']} | "
                    f"pai={menu['menu_pai']}"
                )
            )

        return build_tree(
            menus
        )

    except Exception:

        LOGGER.exception(
            "MENU LOAD ERROR"
        )

        return []

    finally:

        try:

            if conn:
                conn.close()

        except Exception:

            pass


# ==================================================
# MENU POR ROTA
# ==================================================

def get_menu_by_route(
    usuario,
    rota
):

    conn = None

    try:

        usuario = normalizar_usuario(
            usuario
        )

        perfil_id = usuario.get(
            "perfil_id"
        )

        admin_level = get_admin_level(
            usuario
        )

        rota = str(
            rota or ""
        ).strip().lower()

        conn = get_connection()

        cursor = conn.cursor()

        # ==========================================
        # ROOT
        # ==========================================

        if is_root(usuario):

            cursor.execute(
                """

                SELECT
                    Id,
                    Nome,
                    Rota,
                    Ordem,
                    MenuPaiId,
                    TipoMenu,
                    ISNULL(Icone, ''),
                    AdminLevel

                FROM Menu

                WHERE
                    LOWER(Rota) = ?
                    AND Ativo = 1

                """,

                (rota,)
            )

        # ==========================================
        # PERFIL
        # ==========================================

        else:

            cursor.execute(
                """

                SELECT
                    m.Id,
                    m.Nome,
                    m.Rota,
                    m.Ordem,
                    m.MenuPaiId,
                    m.TipoMenu,
                    ISNULL(m.Icone, ''),
                    m.AdminLevel

                FROM PerfilMenu pm

                INNER JOIN Menu m
                    ON m.Id = pm.MenuId

                WHERE
                    pm.PerfilId = ?
                    AND pm.PodeVer = 1
                    AND LOWER(m.Rota) = ?
                    AND m.Ativo = 1
                    AND m.AdminLevel <= ?

                """,

                (
                    perfil_id,
                    rota,
                    admin_level
                )
            )

        row = cursor.fetchone()

        if not row:

            LOGGER.warning(
                (
                    f"Menu não encontrado "
                    f"rota={rota}"
                )
            )

            return None

        menu = map_menu(row)

        LOGGER.info(
            (
                f"Menu localizado: "
                f"{menu['nome']}"
            )
        )

        return menu

    except Exception:

        LOGGER.exception(
            "MENU ROUTE ERROR"
        )

        return None

    finally:

        try:

            if conn:
                conn.close()

        except Exception:

            pass


# ==================================================
# FLATTEN TREE
# ==================================================

def flatten_menu_tree(menus):

    retorno = []

    def processar(items):

        items = sort_menus(items)

        for item in items:

            retorno.append(item)

            filhos = item.get(
                "filhos",
                []
            )

            if filhos:

                processar(filhos)

    processar(menus)

    LOGGER.info(
        (
            f"Flatten tree: "
            f"{len(retorno)} itens"
        )
    )

    return retorno