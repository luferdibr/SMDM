# =========================================================
# modules/administracao/menus/services/menu_service.py
# =========================================================

import logging

from typing import Optional

from database.connection import (
    get_connection,
)

from core.menu_constants import (
    ADMIN_LEVEL_ROOT,
    tipo_existe,
)

from core.state.state import (
    remove_cache,
)

from modules.administracao.menus.services.menu_tree_service import (
    build_menu_tree,
    flatten_tree,
)

# =========================================================
# LOGGER
# =========================================================

LOGGER = logging.getLogger(
    "SMDM_MENU_SERVICE"
)

# =========================================================
# CACHE KEYS
# =========================================================

CACHE_MENU_ALL = (
    "MENU_ALL"
)

CACHE_MENU_TREE = (
    "MENU_TREE"
)

# =========================================================
# SQL BASE
# =========================================================

BASE_SELECT = """

    SELECT

        m.Id,
        m.Nome,
        m.Rota,
        m.Ordem,
        m.MenuPaiId,
        m.TipoMenu,
        ISNULL(m.Icone, ''),
        ISNULL(m.AdminLevel, 0),
        ISNULL(m.Ativo, 1)

    FROM Menu m

"""

# =========================================================
# CACHE
# =========================================================

def invalidate_menu_cache():

    remove_cache(
        CACHE_MENU_ALL
    )

    remove_cache(
        CACHE_MENU_TREE
    )

    LOGGER.info(
        "Menu cache invalidado."
    )

# =========================================================
# USER
# =========================================================

def normalizar_usuario(
    usuario,
):

    if not usuario:

        return {}

    return {

        "id": (
            usuario.get("id")
            or usuario.get("Id")
        ),

        "login": (
            usuario.get("login")
            or usuario.get("Login")
        ),

        "perfil_id": (
            usuario.get("perfil_id")
            or usuario.get("PerfilId")
        ),

        "admin_level": int(

            usuario.get(
                "admin_level"
            )

            or

            usuario.get(
                "AdminLevel"
            )

            or 0
        ),
    }

# =========================================================
# ADMIN LEVEL
# =========================================================

def get_admin_level(
    usuario,
):

    usuario = normalizar_usuario(
        usuario
    )

    return int(

        usuario.get(
            "admin_level",
            0,
        )
    )

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


def usuario_ativo(
    cursor,
    usuario,
):

    usuario = normalizar_usuario(
        usuario
    )

    usuario_id = usuario.get(
        "id"
    )

    if not usuario_id:

        return False

    cursor.execute(

        """

        SELECT COUNT(*)

        FROM Usuarios

        WHERE Id = ?
        AND Ativo = 1
        AND Bloqueado = 0

        """,

        (usuario_id,),
    )

    return (
        cursor.fetchone()[0]
        > 0
    )


def perfil_ativo(
    cursor,
    usuario,
):

    usuario = normalizar_usuario(
        usuario
    )

    perfil_id = usuario.get(
        "perfil_id"
    )

    if not perfil_id:

        return False

    cursor.execute(

        """

        SELECT COUNT(*)

        FROM Perfis

        WHERE Id = ?
        AND Ativo = 1

        """,

        (perfil_id,),
    )

    return (
        cursor.fetchone()[0]
        > 0
    )

# =========================================================
# NORMALIZE
# =========================================================

def normalize_menu_data(
    registro,
):

    tipo = str(

        registro.get(
            "tipo",
            "S",
        )

    ).strip().upper()

    if not tipo_existe(tipo):

        tipo = "S"

    nome = str(

        registro.get(
            "nome",
            "",
        )

        or ""

    ).strip()

    rota = str(

        registro.get(
            "rota",
            "",
        )

        or ""

    ).strip().lower()

    icone = str(

        registro.get(
            "icone",
            "",
        )

        or ""

    ).strip()

    menu_pai = registro.get(
        "menu_pai"
    )

    if menu_pai in (
        "",
        "0",
        0,
        None,
    ):

        menu_pai = None

    else:

        menu_pai = int(
            menu_pai
        )

    try:

        ordem = int(

            registro.get(
                "ordem",
                0,
            )

            or 0
        )

    except Exception:

        ordem = 0

    try:

        admin_level = int(

            registro.get(
                "admin_level",
                0,
            )

            or 0
        )

    except Exception:

        admin_level = 0

    if tipo in ("T", "M"):

        rota = ""

    return {

        "id": (
            int(registro.get("id"))
            if registro.get("id")
            else None
        ),

        "nome": nome,

        "rota": rota,

        "ordem": ordem,

        "menu_pai": menu_pai,

        "tipo": tipo,

        "icone": icone,

        "admin_level": admin_level,

        "ativo": bool(
            registro.get(
                "ativo",
                True,
            )
        ),
    }

# =========================================================
# MAP
# =========================================================

def map_menu(
    row,
):

    return {

        "id": row[0],

        "nome": str(
            row[1] or ""
        ).strip(),

        "rota": (

            str(row[2]).strip()

            if row[2]

            else ""
        ),

        "ordem": int(
            row[3] or 0
        ),

        "menu_pai": row[4],

        "tipo": str(
            row[5] or "S"
        ).strip(),

        "icone": str(
            row[6] or ""
        ).strip(),

        "admin_level": int(
            row[7] or 0
        ),

        "ativo": bool(
            row[8]
        ),
    }

# =========================================================
# ALL MENUS
# =========================================================

def get_all_menus_flat():

    conn = None

    try:

        conn = get_connection()

        cursor = conn.cursor()

        cursor.execute(

            f"""

            {BASE_SELECT}

            WHERE
                m.Ativo = 1

            ORDER BY

                ISNULL(
                    m.MenuPaiId,
                    0
                ),

                m.Ordem,

                m.Nome

            """
        )

        rows = cursor.fetchall()

        menus = [

            map_menu(row)

            for row in rows
        ]

        return menus

    finally:

        try:

            if conn:

                conn.close()

        except Exception:

            pass

# =========================================================
# GET MENU
# =========================================================

def get_menu(
    menu_id,
):

    menus = get_all_menus_flat()

    for item in menus:

        if item["id"] == menu_id:

            return item

    return None

# =========================================================
# VALIDAR HIERARQUIA
# =========================================================

def validar_hierarquia(
    registro,
):

    tipo = registro["tipo"]

    menu_pai = registro[
        "menu_pai"
    ]

    if (
        registro.get("id")
        and
        menu_pai
        and
        int(registro["id"]) == int(menu_pai)
    ):

        raise Exception(
            "Menu não pode ser pai dele mesmo."
        )

    if tipo == "T":

        if menu_pai:

            raise Exception(
                "T não pode ter pai."
            )

        return

    if tipo == "M":

        if not menu_pai:

            raise Exception(
                "M requer T pai."
            )

        pai = get_menu(
            menu_pai
        )

        if not pai:

            raise Exception(
                "Pai inválido."
            )

        if pai["tipo"] != "T":

            raise Exception(
                "M requer pai T."
            )

        return

    if tipo == "S":

        if not menu_pai:

            raise Exception(
                "S requer pai."
            )

        pai = get_menu(
            menu_pai
        )

        if not pai:

            raise Exception(
                "Pai inválido."
            )

        if pai["tipo"] not in (
            "T",
            "M",
        ):

            raise Exception(
                "S requer pai T ou M."
            )

        if not registro["rota"]:

            raise Exception(
                "S requer rota."
            )


def obter_proximo_menu_id(
    cursor,
):

    cursor.execute(

        """

        SELECT ISNULL(MAX(Id), 0) + 1

        FROM Menu

        """
    )

    return int(
        cursor.fetchone()[0]
    )


def menu_id_eh_identity(
    cursor,
):

    cursor.execute(

        """

        SELECT COLUMNPROPERTY(
            OBJECT_ID('Menu'),
            'Id',
            'IsIdentity'
        )

        """
    )

    row = cursor.fetchone()

    return bool(
        row
        and
        row[0]
    )


def validar_duplicidade_menu(
    cursor,
    registro,
):

    menu_id = registro.get(
        "id"
    )

    cursor.execute(

        """

        SELECT COUNT(*)

        FROM Menu

        WHERE
            UPPER(Nome) = ?
            AND ISNULL(MenuPaiId, 0) = ISNULL(?, 0)
            AND Id <> ISNULL(?, -1)

        """,

        (
            registro["nome"].upper(),
            registro["menu_pai"],
            menu_id,
        ),
    )

    if cursor.fetchone()[0]:

        raise Exception(
            "Já existe menu com esse nome neste nível."
        )

    if registro["tipo"] != "S":

        return

    cursor.execute(

        """

        SELECT COUNT(*)

        FROM Menu

        WHERE
            LOWER(Rota) = ?
            AND Id <> ISNULL(?, -1)

        """,

        (
            registro["rota"].lower(),
            menu_id,
        ),
    )

    if cursor.fetchone()[0]:

        raise Exception(
            "Já existe item executável com essa rota."
        )

# =========================================================
# CHILDREN
# =========================================================

def possui_filhos(
    menu_id,
):

    menus = get_all_menus_flat()

    for item in menus:

        if item.get(
            "menu_pai"
        ) == menu_id:

            return True

    return False

# =========================================================
# PERFILMENU
# =========================================================

def menu_em_perfil(
    menu_id,
):

    conn = None

    try:

        conn = get_connection()

        cursor = conn.cursor()

        cursor.execute(

            """

            SELECT COUNT(*)

            FROM PerfilMenu

            WHERE MenuId = ?

            """,

            (menu_id,),
        )

        return (
            cursor.fetchone()[0]
            > 0
        )

    finally:

        try:

            if conn:

                conn.close()

        except Exception:

            pass

# =========================================================
# DELETE PROFILE LINKS
# =========================================================

def excluir_vinculos_perfil_menu(
    cursor,
    menu_id,
):

    cursor.execute(

        """

        DELETE FROM PerfilMenu

        WHERE MenuId = ?

        """,

        (menu_id,),
    )

# =========================================================
# LISTAR
# =========================================================

def listar_menus():

    menus = build_menu_tree(
        get_all_menus_flat()
    )

    return menus

# =========================================================
# USER MENUS
# =========================================================

def listar_menus_usuario(
    usuario,
):

    conn = None

    try:

        usuario = normalizar_usuario(
            usuario
        )

        admin_level = get_admin_level(
            usuario
        )

        perfil_id = usuario.get(
            "perfil_id"
        )

        if not perfil_id:

            return []

        conn = get_connection()

        cursor = conn.cursor()

        if not usuario_ativo(
            cursor,
            usuario,
        ):

            return []

        if not perfil_ativo(
            cursor,
            usuario,
        ):

            LOGGER.warning(
                (
                    "Perfil inativo. "
                    "Menu operacional bloqueado."
                )
            )

            return []

        menus = flatten_tree(
            listar_menus()
        )

        if is_root(usuario):

            return build_menu_tree(
                menus
            )

        cursor.execute(

            """

            SELECT MenuId

            FROM PerfilMenu

            WHERE PerfilId = ?
            AND PodeVer = 1

            """,

            (perfil_id,),
        )

        permitidos_ids = {

            row[0]

            for row in cursor.fetchall()
        }

        if not permitidos_ids:

            return []

        menus_por_id = {

            item["id"]: item

            for item in menus
        }

        ids_com_ancestrais = set(
            permitidos_ids
        )

        for menu_id in list(
            permitidos_ids
        ):

            atual = menus_por_id.get(
                menu_id
            )

            while atual:

                pai_id = atual.get(
                    "menu_pai"
                )

                if not pai_id:

                    break

                ids_com_ancestrais.add(
                    pai_id
                )

                atual = menus_por_id.get(
                    pai_id
                )

        permitidos = []

        for item in menus:

            if not item.get(
                "ativo",
                True,
            ):

                continue

            if int(

                item.get(
                    "admin_level",
                    0,
                )

            ) > admin_level:

                continue

            if item.get("id") not in ids_com_ancestrais:

                continue

            permitidos.append(
                item
            )

        return build_menu_tree(
            permitidos
        )

    except Exception:

        LOGGER.exception(
            "Erro menus usuário."
        )

        return []

    finally:

        try:

            if conn:

                conn.close()

        except Exception:

            pass

# =========================================================
# ROUTE
# =========================================================

def get_menu_by_route(
    usuario,
    rota,
) -> Optional[dict]:

    menus = listar_menus_usuario(
        usuario
    )

    flat = flatten_tree(
        menus
    )

    rota = str(
        rota or ""
    ).strip().lower()

    for item in flat:

        if (

            str(
                item.get(
                    "rota",
                    ""
                )
            ).strip().lower()

            == rota
        ):

            return item

    return None

# =========================================================
# SAVE
# =========================================================

def salvar_menu(
    registro,
):

    conn = None

    try:

        LOGGER.info(
            "[SALVAR_MENU_SERVICE] Recebido: %s",
            registro,
        )

        registro = normalize_menu_data(
            registro
        )

        LOGGER.info(
            "[SALVAR_MENU_SERVICE] Normalizado: %s",
            registro,
        )

        validar_hierarquia(
            registro
        )

        LOGGER.info(
            "[SALVAR_MENU_SERVICE] Hierarquia OK."
        )

        conn = get_connection()

        cursor = conn.cursor()

        validar_duplicidade_menu(
            cursor,
            registro
        )

        LOGGER.info(
            "[SALVAR_MENU_SERVICE] Duplicidade OK."
        )

        menu_id = registro.get(
            "id"
        )

        dados = (

            registro["nome"],

            registro["rota"],

            registro["ordem"],

            registro["menu_pai"],

            registro["tipo"],

            registro["icone"],

            registro["admin_level"],

            1 if registro[
                "ativo"
            ] else 0,
        )

        if menu_id:

            LOGGER.info(
                "[SALVAR_MENU_SERVICE] Atualizando Id=%s.",
                menu_id,
            )

            cursor.execute(

                """

                UPDATE Menu

                SET

                    Nome = ?,
                    Rota = ?,
                    Ordem = ?,
                    MenuPaiId = ?,
                    TipoMenu = ?,
                    Icone = ?,
                    AdminLevel = ?,
                    Ativo = ?

                WHERE Id = ?

                """,

                (
                    *dados,
                    menu_id,
                ),
            )

        else:

            if menu_id_eh_identity(
                cursor
            ):

                LOGGER.info(
                    (
                        "[SALVAR_MENU_SERVICE] "
                        "Inserindo com Id IDENTITY."
                    )
                )

                cursor.execute(

                    """

                    INSERT INTO Menu (

                        Nome,
                        Rota,
                        Ordem,
                        MenuPaiId,
                        TipoMenu,
                        Icone,
                        AdminLevel,
                        Ativo

                    )

                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)

                    """,

                    dados,
                )

            else:

                menu_id = obter_proximo_menu_id(
                    cursor
                )

                LOGGER.info(
                    "[SALVAR_MENU_SERVICE] Inserindo Id=%s.",
                    menu_id,
                )

                cursor.execute(

                    """

                    INSERT INTO Menu (

                        Id,
                        Nome,
                        Rota,
                        Ordem,
                        MenuPaiId,
                        TipoMenu,
                        Icone,
                        AdminLevel,
                        Ativo

                    )

                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)

                    """,

                    (
                        menu_id,
                        *dados,
                    ),
                )

        LOGGER.info(
            "[SALVAR_MENU_SERVICE] Rowcount=%s.",
            cursor.rowcount,
        )

        conn.commit()

        LOGGER.info(
            "[SALVAR_MENU_SERVICE] Commit OK."
        )

        invalidate_menu_cache()

        LOGGER.info(
            "Menu salvo."
        )

        return True

    except Exception as ex:

        if conn:

            conn.rollback()

        LOGGER.exception(
            "Erro salvar."
        )

        raise Exception(str(ex))

    finally:

        try:

            if conn:

                conn.close()

        except Exception:

            pass

# =========================================================
# DELETE
# =========================================================

def excluir_menu(
    menu_id,
):

    conn = None

    try:

        LOGGER.info(
            f"Excluindo menu: {menu_id}"
        )

        if possui_filhos(
            menu_id
        ):

            raise Exception(

                "Menu possui "
                "itens subordinados."
            )

        conn = get_connection()

        cursor = conn.cursor()

        excluir_vinculos_perfil_menu(
            cursor,
            menu_id,
        )

        cursor.execute(

            """

            DELETE FROM Menu

            WHERE Id = ?

            """,

            (menu_id,),
        )

        conn.commit()

        invalidate_menu_cache()

        LOGGER.info(
            "Menu excluído."
        )

        return True

    except Exception as ex:

        if conn:

            conn.rollback()

        LOGGER.exception(
            "Erro excluir."
        )

        raise Exception(str(ex))

    finally:

        try:

            if conn:

                conn.close()

        except Exception:

            pass
