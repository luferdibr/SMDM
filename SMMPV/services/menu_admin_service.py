# services/menu_admin_service.py

import logging

from database.connection import (
    get_connection
)

from services.auditoria_service import (
    registrar_evento
)

from core.menu_constants import (
    ADMIN_LEVEL_ROOT
)


# ==================================================
# LOGGER
# ==================================================

LOGGER = logging.getLogger(
    "MDM_MENU_ADMIN_SERVICE"
)


# ==================================================
# HELPERS
# ==================================================

def ok(
    mensagem="OK",
    dados=None
):

    return {

        "sucesso": True,

        "mensagem": mensagem,

        "dados": dados
    }


def erro(mensagem):

    return {

        "sucesso": False,

        "mensagem": str(mensagem),

        "dados": None
    }


def get_admin_level(usuario):

    if not usuario:
        return 0

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
# NORMALIZA MENU
# ==================================================

def normalizar_menu(row):

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

        "pai": row[3],

        "ordem": int(
            row[4] or 0
        ),

        "ativo": bool(row[5]),

        "tipo_menu": str(
            row[6] or "M"
        ).strip().upper(),

        "sistema": bool(row[7]),

        "admin_level": int(
            row[8] or 0
        )
    }


# ==================================================
# NORMALIZA PERMISSÃO
# ==================================================

def normalizar_permissao(row):

    return {

        "menu_id": row[0],

        "ver": bool(row[1]),

        "editar": bool(row[2]),

        "excluir": bool(row[3])
    }


# ==================================================
# GET PERMISSÕES
# ==================================================

def get_permissoes_usuario(
    usuario,
    rota
):

    conn = None

    try:

        if not usuario:

            return {

                "ver": False,
                "editar": False,
                "excluir": False
            }

        # ==========================================
        # ROOT
        # ==========================================

        if is_root(usuario):

            return {

                "ver": True,
                "editar": True,
                "excluir": True
            }

        perfil_id = usuario.get(
            "perfil_id"
        )

        if not perfil_id:

            return {

                "ver": False,
                "editar": False,
                "excluir": False
            }

        rota = str(
            rota or ""
        ).strip().lower()

        conn = get_connection()

        cursor = conn.cursor()

        cursor.execute("""

            SELECT
                pm.PodeVer,
                pm.PodeEditar,
                pm.PodeExcluir

            FROM PerfilMenu pm

            INNER JOIN Menu m
                ON m.Id = pm.MenuId

            WHERE
                pm.PerfilId = ?
                AND LOWER(m.Rota) = ?
                AND m.Ativo = 1

        """, (
            perfil_id,
            rota
        ))

        row = cursor.fetchone()

        if not row:

            return {

                "ver": False,
                "editar": False,
                "excluir": False
            }

        return {

            "ver": bool(row[0]),

            "editar": bool(row[1]),

            "excluir": bool(row[2])
        }

    except Exception:

        LOGGER.exception(
            "GET PERMISSION ERROR"
        )

        return {

            "ver": False,
            "editar": False,
            "excluir": False
        }

    finally:

        try:
            if conn:
                conn.close()
        except:
            pass


# ==================================================
# LISTAR MENUS + PERMISSÕES
# ==================================================

def listar_menus_com_permissao(
    perfil_id
):

    conn = None

    try:

        conn = get_connection()

        cursor = conn.cursor()

        cursor.execute("""

            SELECT

                m.Id,
                m.Nome,
                m.Rota,
                m.MenuPaiId,
                m.Ordem,
                m.Ativo,
                m.TipoMenu,
                m.Sistema,
                m.AdminLevel,

                ISNULL(pm.PodeVer, 0),
                ISNULL(pm.PodeEditar, 0),
                ISNULL(pm.PodeExcluir, 0)

            FROM Menu m

            LEFT JOIN PerfilMenu pm
                ON pm.MenuId = m.Id
                AND pm.PerfilId = ?

            WHERE
                m.Ativo = 1

            ORDER BY
                ISNULL(m.MenuPaiId, m.Id),
                m.Ordem,
                m.Nome

        """, (
            perfil_id,
        ))

        rows = cursor.fetchall()

        retorno = []

        for row in rows:

            menu = normalizar_menu(row)

            menu["ver"] = bool(row[9])

            menu["editar"] = bool(row[10])

            menu["excluir"] = bool(row[11])

            retorno.append(menu)

        LOGGER.info(
            (
                f"Menus permissão: "
                f"{len(retorno)}"
            )
        )

        return retorno

    except Exception:

        LOGGER.exception(
            "LIST MENU PERMISSION ERROR"
        )

        return []

    finally:

        try:
            if conn:
                conn.close()
        except:
            pass


# ==================================================
# SALVAR PERMISSÕES
# ==================================================

def salvar_permissoes(
    perfil_id,
    permissoes,
    usuario
):

    conn = None

    try:

        if not perfil_id:

            raise Exception(
                "Perfil inválido."
            )

        if not permissoes:

            raise Exception(
                "Nenhuma permissão."
            )

        conn = get_connection()

        cursor = conn.cursor()

        # ==========================================
        # REMOVE
        # ==========================================

        cursor.execute("""

            DELETE FROM PerfilMenu

            WHERE PerfilId = ?

        """, (
            perfil_id,
        ))

        # ==========================================
        # INSERT
        # ==========================================

        for item in permissoes:

            menu_id = item["menu_id"]

            ver = int(
                bool(
                    item.get(
                        "ver"
                    )
                )
            )

            editar = int(
                bool(
                    item.get(
                        "editar"
                    )
                )
            )

            excluir = int(
                bool(
                    item.get(
                        "excluir"
                    )
                )
            )

            # ======================================
            # IGNORA VAZIOS
            # ======================================

            if not (
                ver
                or
                editar
                or
                excluir
            ):
                continue

            cursor.execute("""

                INSERT INTO PerfilMenu
                (
                    PerfilId,
                    MenuId,
                    PodeVer,
                    PodeEditar,
                    PodeExcluir
                )

                VALUES (?, ?, ?, ?, ?)

            """, (

                perfil_id,

                menu_id,

                ver,

                editar,

                excluir
            ))

        registrar_evento(

            usuario,

            "MENU_PERMISSION_SAVE",

            (
                f"Permissões perfil "
                f"{perfil_id}"
            )
        )

        conn.commit()

        return ok(
            "Permissões salvas."
        )

    except Exception as ex:

        if conn:
            conn.rollback()

        LOGGER.exception(
            "SAVE MENU PERMISSION ERROR"
        )

        return erro(ex)

    finally:

        try:
            if conn:
                conn.close()
        except:
            pass


# ==================================================
# COPIAR PERMISSÕES
# ==================================================

def copiar_permissoes(
    perfil_origem,
    perfil_destino,
    usuario
):

    conn = None

    try:

        if perfil_origem == perfil_destino:

            raise Exception(
                "Perfis iguais."
            )

        conn = get_connection()

        cursor = conn.cursor()

        # ==========================================
        # REMOVE DESTINO
        # ==========================================

        cursor.execute("""

            DELETE FROM PerfilMenu

            WHERE PerfilId = ?

        """, (
            perfil_destino,
        ))

        # ==========================================
        # COPIA
        # ==========================================

        cursor.execute("""

            INSERT INTO PerfilMenu
            (
                PerfilId,
                MenuId,
                PodeVer,
                PodeEditar,
                PodeExcluir
            )

            SELECT
                ?,
                MenuId,
                PodeVer,
                PodeEditar,
                PodeExcluir

            FROM PerfilMenu

            WHERE PerfilId = ?

        """, (

            perfil_destino,
            perfil_origem
        ))

        registrar_evento(

            usuario,

            "MENU_PERMISSION_COPY",

            (
                f"{perfil_origem} -> "
                f"{perfil_destino}"
            )
        )

        conn.commit()

        return ok(
            "Permissões copiadas."
        )

    except Exception as ex:

        if conn:
            conn.rollback()

        LOGGER.exception(
            "COPY MENU PERMISSION ERROR"
        )

        return erro(ex)

    finally:

        try:
            if conn:
                conn.close()
        except:
            pass