
import logging

from database.connection import (
    get_connection
)

from services.auditoria_service import (
    registrar_evento
)


# ==================================================
# CONFIG
# ==================================================

ROOT_LEVEL = 100

ADMIN_LEVEL = 50

ROTAS_OBRIGATORIAS = {

    "dashboard",

    "alterar_senha"
}


# ==================================================
# HELPERS
# ==================================================

def retorno(
    sucesso,
    mensagem="",
    dados=None
):

    return {

        "sucesso": bool(sucesso),

        "mensagem": str(mensagem),

        "dados": dados
    }


def permissao_vazia():

    return {

        "ver": 0,

        "editar": 0,

        "excluir": 0
    }


def auditoria_segura(**kwargs):

    try:

        registrar_evento(**kwargs)

    except Exception:

        logging.exception(
            "AUDITORIA ERROR"
        )


def is_root(usuario):

    return bool(
        usuario
        and
        int(
            usuario.get(
                "admin_level",
                0
            )
        ) >= ROOT_LEVEL
    )


def possui_nivel(
    usuario,
    nivel
):

    return bool(
        usuario
        and
        int(
            usuario.get(
                "admin_level",
                0
            )
        ) >= int(nivel)
    )


# ==================================================
# PERFIL
# ==================================================

def get_dados_perfil(
    cursor,
    perfil_id
):

    cursor.execute("""

        SELECT
            Id,
            Nome,
            Ativo,
            Sistema,
            AdminLevel

        FROM Perfis

        WHERE Id = ?

    """, (perfil_id,))

    row = cursor.fetchone()

    if not row:
        return None

    return {

        "id": row[0],

        "nome": row[1],

        "ativo": bool(row[2]),

        "sistema": bool(row[3]),

        "admin_level": int(row[4] or 0)
    }


# ==================================================
# MENU
# ==================================================

def get_dados_menu(
    cursor,
    menu_id
):

    cursor.execute("""

        SELECT
            Id,
            Nome,
            Rota,
            MenuPaiId,
            Sistema,
            AdminLevel,
            Ativo

        FROM Menu

        WHERE Id = ?

    """, (menu_id,))

    row = cursor.fetchone()

    if not row:
        return None

    return {

        "id": row[0],

        "nome": row[1],

        "rota": row[2],

        "pai": row[3],

        "sistema": bool(row[4]),

        "admin_level": int(row[5] or 0),

        "ativo": bool(row[6])
    }


# ==================================================
# SEGURANÇA PERFIL
# ==================================================

def validar_perfil(
    usuario,
    perfil
):

    if not usuario:

        raise Exception(
            "Usuário inválido."
        )

    if not perfil:

        raise Exception(
            "Perfil inválido."
        )

    if not perfil["ativo"]:

        raise Exception(
            "Perfil inativo."
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
    # PERFIL SISTEMA
    # ==============================================

    if perfil["sistema"]:

        raise Exception(
            "Perfil estrutural protegido."
        )

    # ==============================================
    # AUTO ELEVAÇÃO
    # ==============================================

    if perfil["admin_level"] >= usuario_level:

        raise Exception(
            "Sem permissão para alterar este perfil."
        )


# ==================================================
# VALIDAR MENU
# ==================================================

def validar_menu(
    usuario,
    menu
):

    if not menu:
        raise Exception(
            "Menu inválido."
        )

    if not menu["ativo"]:

        raise Exception(
            "Menu inativo."
        )

    # ==============================================
    # ROOT
    # ==============================================

    if is_root(usuario):
        return

    # ==============================================
    # SISTEMA
    # ==============================================

    if menu["sistema"]:

        raise Exception(
            f"Menu estrutural protegido: {menu['nome']}"
        )

    # ==============================================
    # NÍVEL
    # ==============================================

    if int(
        usuario.get(
            "admin_level",
            0
        )
    ) < int(menu["admin_level"]):

        raise Exception(
            f"Menu protegido: {menu['nome']}"
        )


# ==================================================
# PAIS
# ==================================================

def expandir_pais(
    cursor,
    permissoes
):

    resultado = []

    lookup = {}

    # ==============================================
    # BASE
    # ==============================================

    for p in permissoes:

        menu_id = p.get("menu_id")

        if not menu_id:
            continue

        item = {

            "menu_id": menu_id,

            "ver": int(bool(
                p.get("ver", 0)
            )),

            "editar": int(bool(
                p.get("editar", 0)
            )),

            "excluir": int(bool(
                p.get("excluir", 0)
            ))
        }

        resultado.append(item)

        lookup[menu_id] = item

    # ==============================================
    # SUBIR HIERARQUIA
    # ==============================================

    alterou = True

    while alterou:

        alterou = False

        atuais = resultado.copy()

        for item in atuais:

            menu = get_dados_menu(
                cursor,
                item["menu_id"]
            )

            if not menu:
                continue

            pai = menu.get("pai")

            if not pai:
                continue

            if pai in lookup:
                continue

            novo = {

                "menu_id": pai,

                "ver": 1,

                "editar": 0,

                "excluir": 0
            }

            resultado.append(novo)

            lookup[pai] = novo

            alterou = True

    return resultado


# ==================================================
# MENUS OBRIGATÓRIOS
# ==================================================

def validar_menus_obrigatorios(
    cursor,
    permissoes
):

    cursor.execute("""

        SELECT
            Id,
            Rota

        FROM Menu

        WHERE
            Ativo = 1
            AND Rota IS NOT NULL

    """)

    rows = cursor.fetchall()

    rotas = {
        r[0]: r[1]
        for r in rows
    }

    liberadas = set()

    for p in permissoes:

        if not p.get("ver"):
            continue

        rota = rotas.get(
            p["menu_id"]
        )

        if rota:
            liberadas.add(rota)

    faltando = (
        ROTAS_OBRIGATORIAS
        - liberadas
    )

    if faltando:

        raise Exception(
            "Menus obrigatórios ausentes: "
            + ", ".join(sorted(faltando))
        )


# ==================================================
# SEGURANÇA MENUS
# ==================================================

def validar_menus_seguranca(
    cursor,
    usuario,
    permissoes
):

    for p in permissoes:

        menu_id = p.get("menu_id")

        if not menu_id:
            continue

        menu = get_dados_menu(
            cursor,
            menu_id
        )

        validar_menu(
            usuario,
            menu
        )


# ==================================================
# LISTAR MENUS
# ==================================================

def listar_menus_com_permissao(
    usuario,
    perfil_id
):

    conn = None

    try:

        conn = get_connection()

        cursor = conn.cursor()

        perfil = get_dados_perfil(
            cursor,
            perfil_id
        )

        validar_perfil(
            usuario,
            perfil
        )

        usuario_level = int(
            usuario.get(
                "admin_level",
                0
            )
        )

        cursor.execute("""

            SELECT
                m.Id,
                m.Nome,
                m.Rota,
                m.MenuPaiId,
                m.Ordem,
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

        """, (perfil_id,))

        rows = cursor.fetchall()

        menus = []

        for r in rows:

            sistema = bool(r[6])

            admin_level = int(r[7] or 0)

            # ======================================
            # SEGURANÇA
            # ======================================

            if not is_root(usuario):

                if sistema:
                    continue

                if admin_level >= ROOT_LEVEL:
                    continue

                if admin_level > usuario_level:
                    continue

            menus.append({

                "id": r[0],

                "nome": r[1],

                "rota": r[2],

                "pai": r[3],

                "ordem": r[4],

                "tipo": r[5],

                "sistema": sistema,

                "admin_level": admin_level,

                "ver": bool(r[8]),

                "editar": bool(r[9]),

                "excluir": bool(r[10])
            })

        return retorno(
            True,
            dados=menus
        )

    except Exception as ex:

        logging.exception(
            "MENU ADMIN LIST ERROR"
        )

        return retorno(
            False,
            str(ex),
            []
        )

    finally:

        try:

            if conn:
                conn.close()

        except Exception:
            pass


# ==================================================
# SALVAR
# ==================================================

def salvar_permissoes(
    usuario,
    perfil_id,
    permissoes
):

    conn = None

    try:

        conn = get_connection()

        cursor = conn.cursor()

        perfil = get_dados_perfil(
            cursor,
            perfil_id
        )

        validar_perfil(
            usuario,
            perfil
        )

        # ==========================================
        # EXPANDIR
        # ==========================================

        permissoes = expandir_pais(
            cursor,
            permissoes
        )

        # ==========================================
        # VALIDAR
        # ==========================================

        validar_menus_obrigatorios(
            cursor,
            permissoes
        )

        validar_menus_seguranca(
            cursor,
            usuario,
            permissoes
        )

        # ==========================================
        # LIMPAR
        # ==========================================

        cursor.execute("""

            DELETE FROM PerfilMenu

            WHERE PerfilId = ?

        """, (perfil_id,))

        # ==========================================
        # INSERIR
        # ==========================================

        processados = set()

        for p in permissoes:

            menu_id = p.get("menu_id")

            if not menu_id:
                continue

            if menu_id in processados:
                continue

            processados.add(
                menu_id
            )

            ver = int(bool(
                p.get("ver", 0)
            ))

            editar = int(bool(
                p.get("editar", 0)
            ))

            excluir = int(bool(
                p.get("excluir", 0)
            ))

            # ======================================
            # AJUSTE
            # ======================================

            if editar or excluir:
                ver = 1

            if not (
                ver
                or editar
                or excluir
            ):
                continue

            menu = get_dados_menu(
                cursor,
                menu_id
            )

            validar_menu(
                usuario,
                menu
            )

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

        conn.commit()

        auditoria_segura(

            usuario_id=usuario.get("id"),

            login=usuario.get("login"),

            acao="SALVAR_PERMISSOES",

            entidade="PerfilMenu",

            registro_id=perfil_id
        )

        return retorno(
            True,
            "Permissões atualizadas."
        )

    except Exception as ex:

        if conn:
            conn.rollback()

        logging.exception(
            "MENU SAVE ERROR"
        )

        return retorno(
            False,
            str(ex)
        )

    finally:

        try:

            if conn:
                conn.close()

        except Exception:
            pass


# ==================================================
# COPIAR
# ==================================================

def copiar_permissoes(
    usuario,
    perfil_origem_id,
    perfil_destino_id
):

    conn = None

    try:

        conn = get_connection()

        cursor = conn.cursor()

        perfil_origem = get_dados_perfil(
            cursor,
            perfil_origem_id
        )

        perfil_destino = get_dados_perfil(
            cursor,
            perfil_destino_id
        )

        validar_perfil(
            usuario,
            perfil_origem
        )

        validar_perfil(
            usuario,
            perfil_destino
        )

        cursor.execute("""

            DELETE FROM PerfilMenu

            WHERE PerfilId = ?

        """, (perfil_destino_id,))

        # ==========================================
        # ROOT
        # ==========================================

        if is_root(usuario):

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
                perfil_destino_id,
                perfil_origem_id
            ))

        # ==========================================
        # ADMIN
        # ==========================================

        else:

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
                    pm.MenuId,
                    pm.PodeVer,
                    pm.PodeEditar,
                    pm.PodeExcluir

                FROM PerfilMenu pm

                INNER JOIN Menu m
                    ON m.Id = pm.MenuId

                WHERE
                    pm.PerfilId = ?
                    AND m.Sistema = 0
                    AND m.AdminLevel < ?

            """, (

                perfil_destino_id,

                perfil_origem_id,

                ROOT_LEVEL
            ))

        conn.commit()

        auditoria_segura(

            usuario_id=usuario.get("id"),

            login=usuario.get("login"),

            acao="COPIAR_PERMISSOES",

            entidade="PerfilMenu",

            detalhes=(
                f"{perfil_origem_id} -> "
                f"{perfil_destino_id}"
            )
        )

        return retorno(
            True,
            "Permissões copiadas."
        )

    except Exception as ex:

        if conn:
            conn.rollback()

        logging.exception(
            "MENU COPY ERROR"
        )

        return retorno(
            False,
            str(ex)
        )

    finally:

        try:

            if conn:
                conn.close()

        except Exception:
            pass


# ==================================================
# PERMISSÕES USUÁRIO
# ==================================================

def get_permissoes_usuario(
    usuario,
    rota
):

    if not usuario:
        return permissao_vazia()

    # ==============================================
    # ROOT
    # ==============================================

    if is_root(usuario):

        return {

            "ver": 1,

            "editar": 1,

            "excluir": 1
        }

    if not rota:
        return permissao_vazia()

    conn = None

    try:

        conn = get_connection()

        cursor = conn.cursor()

        cursor.execute("""

            SELECT
                pm.PodeVer,
                pm.PodeEditar,
                pm.PodeExcluir,

                m.Sistema,
                m.AdminLevel,
                m.Ativo

            FROM Menu m

            INNER JOIN PerfilMenu pm
                ON pm.MenuId = m.Id

            WHERE
                pm.PerfilId = ?
                AND m.Rota = ?
                AND m.Ativo = 1

        """, (

            usuario["perfil_id"],

            rota
        ))

        row = cursor.fetchone()

        if not row:
            return permissao_vazia()

        sistema = bool(row[3])

        admin_level = int(row[4] or 0)

        ativo = bool(row[5])

        # ==========================================
        # VALIDAÇÕES
        # ==========================================

        if not ativo:
            return permissao_vazia()

        if sistema:
            return permissao_vazia()

        if int(
            usuario.get(
                "admin_level",
                0
            )
        ) < admin_level:

            return permissao_vazia()

        return {

            "ver": bool(row[0]),

            "editar": bool(row[1]),

            "excluir": bool(row[2])
        }

    except Exception:

        logging.exception(
            "MENU PERMISSION ERROR"
        )

        return permissao_vazia()

    finally:

        try:

            if conn:
                conn.close()

        except Exception:
            pass