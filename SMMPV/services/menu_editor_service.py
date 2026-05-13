
import logging

from database.connection import get_connection

from ui.auditoria_service import registrar_evento


# ==================================================
# CONFIG
# ==================================================

ROOT_LEVEL = 100

ADMIN_LEVEL = 50

TIPOS_VALIDOS = {
    "T",
    "M",
    "S"
}

ROTAS_PROTEGIDAS = {

    "dashboard",

    "alterar_senha",

    "usuarios",

    "perfis",

    "menu_config"
}


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


def is_root(usuario):

    return (
        usuario
        and
        int(
            usuario.get(
                "admin_level",
                0
            )
        ) >= ROOT_LEVEL
    )


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

        "tipo": str(
            row[6] or "M"
        ).strip().upper(),

        "sistema": bool(row[7]),

        "admin_level": int(
            row[8] or 0
        )
    }


# ==================================================
# LISTAR
# ==================================================

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

        dados = [

            normalizar_menu(r)
            for r in rows
        ]

        return ok(
            dados=dados
        )

    except Exception as ex:

        logging.exception(
            "MENU LIST ERROR"
        )

        return erro(ex)

    finally:

        try:

            if conn:
                conn.close()
        except:
            pass


# ==================================================
# OBTER
# ==================================================

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

        """, (menu_id,))

        row = cursor.fetchone()

        if not row:

            return erro(
                "Menu não encontrado."
            )

        return ok(
            dados=normalizar_menu(row)
        )

    except Exception as ex:

        logging.exception(
            "MENU GET ERROR"
        )

        return erro(ex)

    finally:

        try:
            if conn:
                conn.close()
        except:
            pass


# ==================================================
# LOOP
# ==================================================

def validar_loop(
    menu_id,
    pai_id,
    lookup
):

    atual = pai_id

    contador = 0

    while atual and contador < 100:

        if atual == menu_id:

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


# ==================================================
# MENU PAI
# ==================================================

def validar_pai(
    dados,
    lookup
):

    pai = dados.get("pai")

    tipo = dados["tipo"]

    if not pai:
        return

    menu_pai = lookup.get(pai)

    if not menu_pai:

        raise Exception(
            "Menu pai inválido."
        )

    if not menu_pai["ativo"]:

        raise Exception(
            "Menu pai inativo."
        )

    if menu_pai["tipo"] == "M":

        raise Exception(
            "Menus do tipo M não podem possuir filhos."
        )

    if tipo == "T":

        raise Exception(
            "Títulos não podem possuir pai."
        )


# ==================================================
# DUPLICIDADE
# ==================================================

def validar_duplicidade(
    cursor,
    dados
):

    nome = dados["nome"]

    rota = dados["rota"]

    menu_id = dados.get("id")

    # ==============================================
    # NOME
    # ==============================================

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

            WHERE UPPER(Nome) = ?

        """, (
            nome.upper(),
        ))

    if cursor.fetchone()[0]:

        raise Exception(
            "Já existe menu com esse nome."
        )

    # ==============================================
    # ROTA
    # ==============================================

    if rota:

        if rota in ROTAS_PROTEGIDAS:

            raise Exception(
                "Rota protegida."
            )

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


# ==================================================
# VALIDAR
# ==================================================

def validar_menu(
    dados,
    lookup=None
):

    dados["nome"] = str(
        dados.get("nome") or ""
    ).strip()

    dados["rota"] = (
        str(
            dados.get("rota")
        ).strip().lower()
        if dados.get("rota")
        else None
    )

    dados["tipo"] = str(
        dados.get("tipo") or "M"
    ).strip().upper()

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

    dados["ordem"] = int(
        dados.get(
            "ordem",
            0
        )
    )

    # ==============================================
    # NOME
    # ==============================================

    if not dados["nome"]:

        raise Exception(
            "Nome obrigatório."
        )

    if len(dados["nome"]) < 2:

        raise Exception(
            "Nome muito curto."
        )

    # ==============================================
    # ORDEM
    # ==============================================

    if dados["ordem"] < 0:

        raise Exception(
            "Ordem inválida."
        )

    # ==============================================
    # TIPO
    # ==============================================

    if dados["tipo"] not in TIPOS_VALIDOS:

        raise Exception(
            "TipoMenu inválido."
        )

    # ==============================================
    # TÍTULO
    # ==============================================

    if dados["tipo"] == "T":

        dados["rota"] = None

        dados["pai"] = None

    # ==============================================
    # SUBMENU
    # ==============================================

    elif dados["tipo"] == "S":

        dados["rota"] = None

    # ==============================================
    # MENU
    # ==============================================

    elif dados["tipo"] == "M":

        if not dados["rota"]:

            raise Exception(
                "Menu precisa de rota."
            )

    # ==============================================
    # AUTO PAI
    # ==============================================

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

    # ==============================================
    # LOOP
    # ==============================================

    if lookup:

        validar_pai(
            dados,
            lookup
        )

        validar_loop(

            dados.get("id"),

            dados.get("pai"),

            lookup
        )

    return dados


# ==================================================
# SEGURANÇA
# ==================================================

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

    # ==============================================
    # ROOT
    # ==============================================

    if usuario_level >= ROOT_LEVEL:
        return

    # ==============================================
    # SISTEMA
    # ==============================================

    if dados.get("sistema"):

        raise Exception(
            "Somente ROOT altera menus estruturais."
        )

    # ==============================================
    # ROOT MENU
    # ==============================================

    if int(
        dados.get(
            "admin_level",
            0
        )
    ) >= ROOT_LEVEL:

        raise Exception(
            "Somente ROOT cria menus ROOT."
        )

    # ==============================================
    # MENU ATUAL
    # ==============================================

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
        ) >= ROOT_LEVEL:

            raise Exception(
                "Menu ROOT protegido."
            )

        if atual.get("rota") in ROTAS_PROTEGIDAS:

            raise Exception(
                "Menu protegido."
            )


# ==================================================
# SALVAR
# ==================================================

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

        # ==========================================
        # UPDATE
        # ==========================================

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

        # ==========================================
        # INSERT
        # ==========================================

        else:

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

        return ok(mensagem)

    except Exception as ex:

        if conn:
            conn.rollback()

        logging.exception(
            "MENU SAVE ERROR"
        )

        return erro(ex)

    finally:

        try:
            if conn:
                conn.close()
        except:
            pass


# ==================================================
# DESATIVAR FILHOS
# ==================================================

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
            AdminLevel,
            Rota

        FROM Menu

        WHERE MenuPaiId = ?

    """, (menu_id,))

    filhos = cursor.fetchall()

    for f in filhos:

        filho_id = f[0]

        sistema = bool(f[1])

        admin_level = int(
            f[2] or 0
        )

        rota = (
            str(f[3]).lower()
            if f[3]
            else None
        )

        # ==========================================
        # PROTEGIDOS
        # ==========================================

        if sistema:
            continue

        if admin_level >= ROOT_LEVEL:
            continue

        if rota in ROTAS_PROTEGIDAS:
            continue

        cursor.execute("""

            UPDATE Menu

            SET Ativo = 0

            WHERE Id = ?

        """, (filho_id,))

        desativar_filhos(
            cursor,
            filho_id,
            visitados
        )


# ==================================================
# EXCLUIR
# ==================================================

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

        if menu.get("rota") in ROTAS_PROTEGIDAS:

            raise Exception(
                "Menu protegido."
            )

        cursor.execute("""

            UPDATE Menu

            SET Ativo = 0

            WHERE Id = ?

        """, (menu_id,))

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

        return ok(
            "Menu desativado."
        )

    except Exception as ex:

        if conn:
            conn.rollback()

        logging.exception(
            "MENU DELETE ERROR"
        )

        return erro(ex)

    finally:

        try:
            if conn:
                conn.close()
        except:
            pass