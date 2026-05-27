# services/menu_editor_service.py

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

    ADMIN_LEVEL_ROOT,

    tipo_existe,

    validar_hierarquia,

    permite_rota,

    permite_pai,

    get_ordem_default,

    is_leaf_tipo,

    is_root_tipo
)


# =========================================================
# LOGGER
# =========================================================

LOGGER = logging.getLogger(
    "MDM_MENU_EDITOR_SERVICE"
)


# =========================================================
# HELPERS
# =========================================================

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


def is_root(usuario):

    return (

        usuario

        and

        int(
            usuario.get(
                "admin_level",
                0
            )
        ) >= ADMIN_LEVEL_ROOT
    )


# =========================================================
# NORMALIZAR
# =========================================================

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

        "tipo": (

            str(row[6]).strip().upper()

            if row[6]

            else None
        ),

        "sistema": bool(row[7]),

        "admin_level": int(
            row[8] or 0
        )
    }


# =========================================================
# LISTAR
# =========================================================

def listar_menus():

    conn = None

    try:

        conn = get_connection()

        cursor = conn.cursor()

        cursor.execute("""

            SELECT
                Id,
                Nome,
                Rota,
                MenuPaiId,
                Ordem,
                Ativo,
                TipoMenu,
                Sistema,
                AdminLevel

            FROM Menu

            ORDER BY
                ISNULL(MenuPaiId, Id),
                Ordem,
                Nome

        """)

        rows = cursor.fetchall()

        retorno = [

            normalizar_menu(r)

            for r in rows
        ]

        LOGGER.info(
            (
                f"LIST_MENU "
                f"{len(retorno)}"
            )
        )

        return ok(
            dados=retorno
        )

    except Exception as ex:

        LOGGER.exception(
            "LIST_MENU_ERROR"
        )

        return erro(ex)

    finally:

        try:

            if conn:
                conn.close()

        except Exception:

            pass


# =========================================================
# GET
# =========================================================

def obter_menu(menu_id):

    conn = None

    try:

        conn = get_connection()

        cursor = conn.cursor()

        cursor.execute("""

            SELECT
                Id,
                Nome,
                Rota,
                MenuPaiId,
                Ordem,
                Ativo,
                TipoMenu,
                Sistema,
                AdminLevel

            FROM Menu

            WHERE Id = ?

        """, (
            menu_id,
        ))

        row = cursor.fetchone()

        if not row:

            return erro(
                "Menu não encontrado."
            )

        return ok(
            dados=normalizar_menu(row)
        )

    except Exception as ex:

        LOGGER.exception(
            "GET_MENU_ERROR"
        )

        return erro(ex)

    finally:

        try:

            if conn:
                conn.close()

        except Exception:

            pass


# =========================================================
# LOOP
# =========================================================

def validar_loop(

    menu_id,

    pai_id,

    lookup
):

    atual = pai_id

    contador = 0

    while atual and contador < 100:

        if atual == menu_id:

            LOGGER.warning(
                (
                    f"LOOP_DETECTED "
                    f"{menu_id}"
                )
            )

            raise Exception(
                "Loop hierárquico detectado."
            )

        menu = lookup.get(atual)

        if not menu:
            break

        atual = menu["pai"]

        contador += 1

    if contador >= 100:

        raise Exception(
            "Hierarquia inválida."
        )


# =========================================================
# HIERARQUIA
# =========================================================

def validar_hierarquia_menu(

    dados,

    lookup
):

    tipo = dados["tipo"]

    pai = dados.get(
        "pai"
    )

    # =====================================================
    # ROOT TYPE
    # =====================================================

    if is_root_tipo(tipo):

        if pai:

            raise Exception(
                "Tipo raiz não pode possuir pai."
            )

        return

    # =====================================================
    # OBRIGATÓRIO
    # =====================================================

    if permite_pai(tipo):

        if not pai:

            raise Exception(
                "Menu pai obrigatório."
            )

    menu_pai = lookup.get(pai)

    if not menu_pai:

        raise Exception(
            "Menu pai inválido."
        )

    tipo_pai = menu_pai["tipo"]

    # =====================================================
    # LEAF
    # =====================================================

    if is_leaf_tipo(tipo_pai):

        raise Exception(
            "Menu pai não aceita filhos."
        )

    # =====================================================
    # DOMÍNIO CENTRAL
    # =====================================================

    if not validar_hierarquia(

        tipo,

        tipo_pai
    ):

        raise Exception(
            (
                f"Hierarquia inválida "
                f"{tipo} -> {tipo_pai}"
            )
        )


# =========================================================
# DUPLICIDADE
# =========================================================

def validar_duplicidade(

    cursor,

    dados
):

    nome = dados["nome"]

    rota = dados["rota"]

    menu_id = dados.get(
        "id"
    )

    # =====================================================
    # NOME
    # =====================================================

    if menu_id:

        cursor.execute("""

            SELECT COUNT(*)

            FROM Menu

            WHERE
                UPPER(Nome) = ?
                AND Id <> ?

        """, (

            nome.upper(),

            menu_id
        ))

    else:

        cursor.execute("""

            SELECT COUNT(*)

            FROM Menu

            WHERE
                UPPER(Nome) = ?

        """, (
            nome.upper(),
        ))

    if cursor.fetchone()[0]:

        raise Exception(
            "Já existe menu com esse nome."
        )

    # =====================================================
    # ROTA
    # =====================================================

    if rota:

        if menu_id:

            cursor.execute("""

                SELECT COUNT(*)

                FROM Menu

                WHERE
                    LOWER(Rota) = ?
                    AND Id <> ?

            """, (

                rota,

                menu_id
            ))

        else:

            cursor.execute("""

                SELECT COUNT(*)

                FROM Menu

                WHERE LOWER(Rota) = ?

            """, (
                rota,
            ))

        if cursor.fetchone()[0]:

            raise Exception(
                "Já existe menu com essa rota."
            )


# =========================================================
# VALIDAR
# =========================================================

def validar_menu(

    dados,

    lookup=None
):

    dados["nome"] = str(
        dados.get("nome") or ""
    ).strip()

    dados["rota"] = (

        str(
            dados.get(
                "rota"
            )
        ).strip().lower()

        if dados.get("rota")

        else None
    )

    dados["tipo"] = str(
        dados.get("tipo") or ""
    ).strip().upper()

    # =====================================================
    # TIPO
    # =====================================================

    if not tipo_existe(
        dados["tipo"]
    ):

        raise Exception(
            "TipoMenu inválido."
        )

    # =====================================================
    # ORDEM
    # =====================================================

    dados["ordem"] = int(

        dados.get(

            "ordem",

            get_ordem_default(
                dados["tipo"]
            )
        )
    )

    dados["admin_level"] = int(

        dados.get(
            "admin_level",
            10
        )
    )

    dados["sistema"] = int(

        bool(
            dados.get(
                "sistema",
                0
            )
        )
    )

    # =====================================================
    # NOME
    # =====================================================

    if not dados["nome"]:

        raise Exception(
            "Nome obrigatório."
        )

    if len(dados["nome"]) < 2:

        raise Exception(
            "Nome muito curto."
        )

    # =====================================================
    # ROOT TYPE
    # =====================================================

    if is_root_tipo(
        dados["tipo"]
    ):

        dados["pai"] = None

    # =====================================================
    # ROTA
    # =====================================================

    if not permite_rota(
        dados["tipo"]
    ):

        dados["rota"] = None

    else:

        if not dados["rota"]:

            raise Exception(
                "Rota obrigatória."
            )

    # =====================================================
    # PAI
    # =====================================================

    if not permite_pai(
        dados["tipo"]
    ):

        dados["pai"] = None

    # =====================================================
    # AUTO PAI
    # =====================================================

    if (

        dados.get("id")

        and

        dados.get("pai")

        and

        dados["id"] == dados["pai"]
    ):

        raise Exception(
            "Menu não pode ser pai dele mesmo."
        )

    # =====================================================
    # LOOP
    # =====================================================

    if lookup:

        validar_hierarquia_menu(

            dados,

            lookup
        )

        validar_loop(

            dados.get("id"),

            dados.get("pai"),

            lookup
        )

    return dados


# =========================================================
# SEGURANÇA
# =========================================================

def validar_seguranca(

    usuario,

    dados,

    atual=None
):

    if not usuario:

        raise Exception(
            "Usuário inválido."
        )

    usuario_level = int(
        usuario.get(
            "admin_level",
            0
        )
    )

    # =====================================================
    # ROOT
    # =====================================================

    if usuario_level >= ADMIN_LEVEL_ROOT:
        return

    # =====================================================
    # SISTEMA
    # =====================================================

    if dados.get("sistema"):

        raise Exception(
            "Somente ROOT altera menus estruturais."
        )

    # =====================================================
    # ROOT MENU
    # =====================================================

    if int(
        dados.get(
            "admin_level",
            0
        )
    ) >= ADMIN_LEVEL_ROOT:

        raise Exception(
            "Somente ROOT cria menus ROOT."
        )

    # =====================================================
    # MENU ATUAL
    # =====================================================

    if atual:

        if atual.get("sistema"):

            raise Exception(
                "Menu estrutural protegido."
            )

        if int(
            atual.get(
                "admin_level",
                0
            )
        ) >= ADMIN_LEVEL_ROOT:

            raise Exception(
                "Menu ROOT protegido."
            )


# =========================================================
# SAVE
# =========================================================

def salvar_menu(

    usuario,

    dados
):

    conn = None

    try:

        conn = get_connection()

        cursor = conn.cursor()

        resultado = listar_menus()

        if not resultado["sucesso"]:

            raise Exception(
                resultado["mensagem"]
            )

        menus = resultado["dados"]

        lookup = {

            m["id"]: m

            for m in menus
        }

        dados = validar_menu(

            dados,

            lookup
        )

        atual = None

        if dados.get("id"):

            resultado_menu = obter_menu(
                dados["id"]
            )

            if not resultado_menu["sucesso"]:

                raise Exception(
                    resultado_menu["mensagem"]
                )

            atual = resultado_menu[
                "dados"
            ]

        validar_seguranca(

            usuario,

            dados,

            atual
        )

        validar_duplicidade(

            cursor,

            dados
        )

        ativo = int(

            bool(
                dados.get(
                    "ativo",
                    1
                )
            )
        )

        # =================================================
        # UPDATE
        # =================================================

        if dados.get("id"):

            cursor.execute("""

                UPDATE Menu

                SET
                    Nome = ?,
                    Rota = ?,
                    MenuPaiId = ?,
                    Ordem = ?,
                    Ativo = ?,
                    TipoMenu = ?,
                    Sistema = ?,
                    AdminLevel = ?

                WHERE Id = ?

            """, (

                dados["nome"],

                dados["rota"],

                dados["pai"],

                dados["ordem"],

                ativo,

                dados["tipo"],

                dados["sistema"],

                dados["admin_level"],

                dados["id"]
            ))

            registrar_evento(

                usuario,

                "MENU_UPDATE",

                (
                    f"Menu atualizado "
                    f"ID={dados['id']}"
                )
            )

            mensagem = "Menu atualizado."

        # =================================================
        # INSERT
        # =================================================

        else:

            if coluna_eh_identity(
                cursor,
                "Menu",
                "Id",
            ):

                cursor.execute("""

                    INSERT INTO Menu
                    (
                        Nome,
                        Rota,
                        MenuPaiId,
                        Ordem,
                        Ativo,
                        TipoMenu,
                        Sistema,
                        AdminLevel
                    )

                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)

                """, (

                    dados["nome"],

                    dados["rota"],

                    dados["pai"],

                    dados["ordem"],

                    ativo,

                    dados["tipo"],

                    dados["sistema"],

                    dados["admin_level"]
                ))

            else:

                cursor.execute("""

                    INSERT INTO Menu
                    (
                        Id,
                        Nome,
                        Rota,
                        MenuPaiId,
                        Ordem,
                        Ativo,
                        TipoMenu,
                        Sistema,
                        AdminLevel
                    )

                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)

                """, (

                    obter_proximo_id(
                        cursor,
                        "Menu",
                        "Id",
                    ),

                    dados["nome"],

                    dados["rota"],

                    dados["pai"],

                    dados["ordem"],

                    ativo,

                    dados["tipo"],

                    dados["sistema"],

                    dados["admin_level"]
                ))

            registrar_evento(

                usuario,

                "MENU_CREATE",

                (
                    f"Menu criado "
                    f"{dados['nome']}"
                )
            )

            mensagem = "Menu criado."

        conn.commit()

        LOGGER.info(
            mensagem
        )

        return ok(
            mensagem
        )

    except Exception as ex:

        if conn:
            conn.rollback()

        LOGGER.exception(
            "SAVE_MENU_ERROR"
        )

        return erro(ex)

    finally:

        try:

            if conn:
                conn.close()

        except Exception:

            pass


# =========================================================
# DESATIVAR FILHOS
# =========================================================

def desativar_filhos(

    cursor,

    menu_id,

    visitados=None
):

    if visitados is None:

        visitados = set()

    if menu_id in visitados:
        return

    visitados.add(menu_id)

    cursor.execute("""

        SELECT
            Id,
            Sistema,
            AdminLevel

        FROM Menu

        WHERE MenuPaiId = ?

    """, (
        menu_id,
    ))

    filhos = cursor.fetchall()

    for f in filhos:

        filho_id = f[0]

        sistema = bool(f[1])

        admin_level = int(
            f[2] or 0
        )

        # =================================================
        # PROTEGIDOS
        # =================================================

        if sistema:
            continue

        if admin_level >= ADMIN_LEVEL_ROOT:
            continue

        LOGGER.info(
            (
                f"DISABLE_CHILD "
                f"{filho_id}"
            )
        )

        cursor.execute("""

            UPDATE Menu

            SET Ativo = 0

            WHERE Id = ?

        """, (
            filho_id,
        ))

        desativar_filhos(

            cursor,

            filho_id,

            visitados
        )


# =========================================================
# DELETE
# =========================================================

def excluir_menu(

    usuario,

    menu_id
):

    conn = None

    try:

        conn = get_connection()

        cursor = conn.cursor()

        resultado = obter_menu(
            menu_id
        )

        if not resultado["sucesso"]:

            raise Exception(
                resultado["mensagem"]
            )

        menu = resultado["dados"]

        validar_seguranca(

            usuario,

            menu,

            menu
        )

        cursor.execute("""

            UPDATE Menu

            SET Ativo = 0

            WHERE Id = ?

        """, (
            menu_id,
        ))

        desativar_filhos(

            cursor,

            menu_id
        )

        registrar_evento(

            usuario,

            "MENU_DELETE",

            (
                f"Menu desativado "
                f"ID={menu_id}"
            )
        )

        conn.commit()

        LOGGER.info(
            (
                f"DELETE_MENU "
                f"{menu_id}"
            )
        )

        return ok(
            "Menu desativado."
        )

    except Exception as ex:

        if conn:
            conn.rollback()

        LOGGER.exception(
            "DELETE_MENU_ERROR"
        )

        return erro(ex)

    finally:

        try:

            if conn:
                conn.close()

        except Exception:

            pass
