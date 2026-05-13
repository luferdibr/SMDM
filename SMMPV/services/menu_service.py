
import logging

from database.connection import get_connection


# ==================================================
# CONSTANTES
# ==================================================

ROOT_LEVEL = 100

TIPOS_VALIDOS = {
    "T",
    "S",
    "M"
}


# ==================================================
# NORMALIZAR MENU
# ==================================================

def normalizar_menu(menu):

    tipo = str(
        menu.get("tipo") or "M"
    ).strip().upper()

    if tipo not in TIPOS_VALIDOS:
        tipo = "M"

    return {

        "id": menu.get("id"),

        "nome": str(
            menu.get("nome") or "Menu"
        ).strip(),

        "rota": (
            str(menu.get("rota")).strip()
            if menu.get("rota")
            else None
        ),

        "pai": menu.get("pai"),

        "ordem": (
            menu.get("ordem")
            if menu.get("ordem") is not None
            else 9999
        ),

        "tipo": tipo,

        "sistema": bool(
            menu.get("sistema", 0)
        ),

        "admin_level": int(
            menu.get("admin_level", 0)
        ),

        "filhos": []
    }


# ==================================================
# ORDENAÇÃO
# ==================================================

def ordenar_arvore(menu):

    filhos = menu.get("filhos", [])

    filhos.sort(
        key=lambda x: (
            x.get("ordem", 9999),
            x.get("nome", "")
        )
    )

    for filho in filhos:
        ordenar_arvore(filho)


# ==================================================
# SEGURANÇA MENU
# ==================================================

def pode_acessar_menu(usuario, menu):

    if not usuario:
        return False

    admin_level = int(
        usuario.get("admin_level", 0)
    )

    # ==============================================
    # ROOT
    # ==============================================

    if admin_level >= ROOT_LEVEL:
        return True

    # ==============================================
    # MENU SISTEMA
    # ==============================================

    if bool(menu.get("sistema", 0)):
        return False

    # ==============================================
    # NÍVEL
    # ==============================================

    if admin_level < int(
        menu.get("admin_level", 0)
    ):
        return False

    return True


# ==================================================
# BUSCAR PAIS
# ==================================================

def buscar_pais(cursor, menus):

    ids_existentes = {
        m["id"]
        for m in menus
    }

    while True:

        pais_faltando = {

            m["pai"]

            for m in menus

            if (
                m.get("pai")
                and
                m["pai"] not in ids_existentes
            )
        }

        if not pais_faltando:
            break

        placeholders = ",".join(
            "?"
            for _ in pais_faltando
        )

        sql = f"""

            SELECT
                Id,
                Nome,
                Rota,
                MenuPaiId,
                Ordem,
                TipoMenu,
                Sistema,
                AdminLevel

            FROM Menu

            WHERE
                Ativo = 1
                AND Id IN ({placeholders})

        """

        cursor.execute(
            sql,
            tuple(pais_faltando)
        )

        rows = cursor.fetchall()

        if not rows:
            break

        for r in rows:

            item = normalizar_menu({

                "id": r[0],
                "nome": r[1],
                "rota": r[2],
                "pai": r[3],
                "ordem": r[4],
                "tipo": r[5],
                "sistema": r[6],
                "admin_level": r[7]
            })

            if item["id"] not in ids_existentes:

                menus.append(item)

                ids_existentes.add(
                    item["id"]
                )

    return menus


# ==================================================
# HIERARQUIA
# ==================================================

def montar_hierarquia(menus):

    lookup = {}

    raiz = []

    for m in menus:

        item = normalizar_menu(m)

        lookup[item["id"]] = item

    for item in lookup.values():

        pai = item.get("pai")

        if pai and pai in lookup:

            lookup[pai]["filhos"].append(
                item
            )

        else:

            raiz.append(item)

    for r in raiz:
        ordenar_arvore(r)

    raiz.sort(
        key=lambda x: (
            x.get("ordem", 9999),
            x.get("nome", "")
        )
    )

    return raiz


# ==================================================
# LOG ÁRVORE
# ==================================================

def log_arvore(menus, nivel=0):

    for m in menus:

        logging.info(
            "%sMENU id=%s nome=%s tipo=%s pai=%s sistema=%s level=%s",
            "  " * nivel,
            m.get("id"),
            m.get("nome"),
            m.get("tipo"),
            m.get("pai"),
            m.get("sistema"),
            m.get("admin_level")
        )

        filhos = m.get("filhos", [])

        if filhos:

            log_arvore(
                filhos,
                nivel + 1
            )


# ==================================================
# QUERY ROOT
# ==================================================

def query_root():

    return """

        SELECT
            Id,
            Nome,
            Rota,
            MenuPaiId,
            Ordem,
            TipoMenu,
            Sistema,
            AdminLevel

        FROM Menu

        WHERE
            Ativo = 1

        ORDER BY
            Ordem,
            Nome

    """


# ==================================================
# QUERY PERFIL
# ==================================================

def query_perfil():

    return """

        SELECT
            m.Id,
            m.Nome,
            m.Rota,
            m.MenuPaiId,
            m.Ordem,
            m.TipoMenu,
            m.Sistema,
            m.AdminLevel

        FROM Menu m

        INNER JOIN PerfilMenu pm
            ON pm.MenuId = m.Id

        WHERE
            m.Ativo = 1
            AND pm.PerfilId = ?
            AND pm.PodeVer = 1

        ORDER BY
            m.Ordem,
            m.Nome

    """


# ==================================================
# MENU USUÁRIO
# ==================================================

def get_menu_usuario(usuario):

    if not usuario:

        logging.warning(
            "Usuário inválido."
        )

        return []

    admin_level = int(
        usuario.get("admin_level", 0)
    )

    perfil_id = usuario.get(
        "perfil_id"
    )

    logging.info(
        "Montando menu perfil=%s",
        perfil_id
    )

    conn = None

    try:

        conn = get_connection()

        cursor = conn.cursor()

        # ==========================================
        # ROOT BYPASS
        # ==========================================

        if admin_level >= ROOT_LEVEL:

            logging.info(
                "ROOT BYPASS ATIVADO"
            )

            cursor.execute(
                query_root()
            )

        # ==========================================
        # PERFIL NORMAL
        # ==========================================

        else:

            cursor.execute(
                query_perfil(),
                (perfil_id,)
            )

        rows = cursor.fetchall()

        logging.info(
            "ROWS=%s",
            len(rows)
        )

        menus = []

        for r in rows:

            item = normalizar_menu({

                "id": r[0],
                "nome": r[1],
                "rota": r[2],
                "pai": r[3],
                "ordem": r[4],
                "tipo": r[5],
                "sistema": r[6],
                "admin_level": r[7]
            })

            if not pode_acessar_menu(
                usuario,
                item
            ):
                continue

            menus.append(item)

        menus = buscar_pais(
            cursor,
            menus
        )

        menus = montar_hierarquia(
            menus
        )

        logging.info(
            "ÁRVORE FINAL"
        )

        log_arvore(menus)

        return menus

    except Exception:

        logging.exception(
            "MENU ERROR"
        )

        return []

    finally:

        try:

            if conn:
                conn.close()

        except Exception:
            pass
