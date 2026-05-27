# services/menu_admin_service.py

import logging

from database.connection import (
    get_connection
)

from services.auditoria_service import (
    registrar_evento
)

from services.identity_service import (
    coluna_eh_identity,
    obter_proximo_id,
)

from core.menu_constants import (
    ADMIN_LEVEL_ADMIN,
    ADMIN_LEVEL_ROOT,
)

ADMIN_EDIT_ROUTES = {
    "usuarios",
    "perfis",
    "perfil_menu",
    "perfilmenu",
}

ROOT_ONLY_ROUTES = {
    "menus",
    "menu",
    "menu_admin",
    "menu_config",
}


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


def is_admin(usuario):

    return (
        get_admin_level(usuario)
        >= ADMIN_LEVEL_ADMIN
    )


def validar_operador_admin(usuario):

    if not is_admin(usuario):

        raise Exception(
            "Acesso restrito à administração."
        )


def obter_perfil(
    cursor,
    perfil_id
):

    cursor.execute("""

        SELECT
            Id,
            Nome,
            AdminLevel,
            Sistema,
            Ativo

        FROM Perfis

        WHERE Id = ?

    """, (
        perfil_id,
    ))

    row = cursor.fetchone()

    if not row:

        raise Exception(
            "Perfil inválido."
        )

    return {

        "id": row[0],

        "nome": row[1],

        "admin_level": int(row[2] or 0),

        "sistema": bool(row[3]),

        "ativo": bool(row[4]),
    }


def validar_perfil_alvo(
    usuario,
    perfil
):

    validar_operador_admin(
        usuario
    )

    if is_root(usuario):

        return

    if perfil["admin_level"] > get_admin_level(usuario):

        raise Exception(
            "Sem permissão para este perfil."
        )


def validar_menu_permissao(
    cursor,
    menu_id
):

    cursor.execute("""

        SELECT COUNT(*)

        FROM Menu

        WHERE Id = ?
        AND Ativo = 1

    """, (
        menu_id,
    ))

    if not cursor.fetchone()[0]:

        raise Exception(
            f"Menu inválido: {menu_id}"
        )


def inserir_perfil_menu(
    cursor,
    perfil_id,
    menu_id,
    ver,
    editar,
    excluir,
):

    if coluna_eh_identity(
        cursor,
        "PerfilMenu",
        "Id",
    ):

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

        return

    cursor.execute("""

        INSERT INTO PerfilMenu
        (
            Id,
            PerfilId,
            MenuId,
            PodeVer,
            PodeEditar,
            PodeExcluir
        )

        VALUES (?, ?, ?, ?, ?, ?)

    """, (

        obter_proximo_id(
            cursor,
            "PerfilMenu",
            "Id",
        ),
        perfil_id,
        menu_id,
        ver,
        editar,
        excluir
    ))


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

        rota = str(
            rota or ""
        ).strip().lower()

        # ==========================================
        # ROOT
        # ==========================================

        if is_root(usuario):

            return {

                "ver": True,
                "editar": True,
                "excluir": True
            }

        if is_admin(usuario):

            if rota in ADMIN_EDIT_ROUTES:

                return {

                    "ver": True,
                    "editar": True,
                    "excluir": True
                }

            if rota in ROOT_ONLY_ROUTES:

                return {

                    "ver": False,
                    "editar": False,
                    "excluir": False
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

        permissoes = (
            permissoes
            or []
        )

        conn = get_connection()

        cursor = conn.cursor()

        perfil = obter_perfil(
            cursor,
            perfil_id
        )

        validar_perfil_alvo(
            usuario,
            perfil
        )

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

            if editar or excluir:

                ver = 1

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

            validar_menu_permissao(
                cursor,
                menu_id
            )

            inserir_perfil_menu(
                cursor,
                perfil_id,
                menu_id,
                ver,
                editar,
                excluir,
            )

        registrar_evento(

            evento="MENU_PERMISSION_SAVE",

            descricao=(
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

        perfil_destino_dados = obter_perfil(
            cursor,
            perfil_destino
        )

        validar_perfil_alvo(
            usuario,
            perfil_destino_dados
        )

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

            SELECT
                MenuId,
                PodeVer,
                PodeEditar,
                PodeExcluir

            FROM PerfilMenu

            WHERE PerfilId = ?

        """, (
            perfil_origem,
        ))

        for row in cursor.fetchall():

            inserir_perfil_menu(
                cursor,
                perfil_destino,
                row[0],
                int(bool(row[1])),
                int(bool(row[2])),
                int(bool(row[3])),
            )

        registrar_evento(

            evento="MENU_PERMISSION_COPY",

            descricao=(
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
