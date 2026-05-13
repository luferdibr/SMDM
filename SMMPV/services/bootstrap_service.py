
import logging

from database.connection import get_connection

from services.auth_service import gerar_hash

from services.auditoria_service import registrar_evento

from config.settings import ADMIN_CONFIG


# ==================================================
# CONFIG
# ==================================================

LOGIN_ADMIN = ADMIN_CONFIG["login"]

SENHA_ADMIN = ADMIN_CONFIG["password"]

FORCAR_TROCA_ADMIN = bool(
    ADMIN_CONFIG["force_change"]
)

ROOT_LEVEL = 100

ADMIN_LEVEL = 50


# ==================================================
# HELPERS
# ==================================================

def tabela_existe(cursor, tabela):

    cursor.execute("""

        SELECT COUNT(*)

        FROM INFORMATION_SCHEMA.TABLES

        WHERE TABLE_NAME = ?

    """, (tabela,))

    return cursor.fetchone()[0] > 0


# ==================================================
# VALIDAR ESTRUTURA
# ==================================================

def validar_estrutura(cursor):

    tabelas = [

        "Perfis",

        "Usuarios",

        "Menu",

        "PerfilMenu",

        "Auditoria"
    ]

    for tabela in tabelas:

        if not tabela_existe(
            cursor,
            tabela
        ):

            raise Exception(
                f"Tabela obrigatória ausente: {tabela}"
            )


# ==================================================
# VALIDAR PERFIS
# ==================================================

def validar_perfis(cursor):

    cursor.execute("""

        SELECT
            Id,
            Nome,
            AdminLevel,
            Sistema

        FROM Perfis

        ORDER BY Id

    """)

    rows = cursor.fetchall()

    if not rows:

        raise Exception(
            "Nenhum perfil encontrado."
        )

    perfis = {}

    for r in rows:

        perfis[r[0]] = {

            "nome": r[1],

            "level": int(r[2]),

            "sistema": bool(r[3])
        }

    # ==============================================
    # ROOT
    # ==============================================

    root = perfis.get(1)

    if not root:

        raise Exception(
            "Perfil ROOT inexistente."
        )

    if root["nome"] != "ROOT":

        raise Exception(
            "Perfil 1 deve ser ROOT."
        )

    if root["level"] < ROOT_LEVEL:

        raise Exception(
            "ROOT inválido."
        )

    if not root["sistema"]:

        raise Exception(
            "ROOT deve ser estrutural."
        )

    # ==============================================
    # ADMIN
    # ==============================================

    admin = perfis.get(2)

    if not admin:

        raise Exception(
            "Perfil ADMIN inexistente."
        )

    if admin["nome"] != "ADMIN":

        raise Exception(
            "Perfil 2 deve ser ADMIN."
        )

    if admin["level"] < ADMIN_LEVEL:

        raise Exception(
            "ADMIN inválido."
        )


# ==================================================
# VALIDAR MENUS
# ==================================================

def validar_menus(cursor):

    cursor.execute("""

        SELECT COUNT(*)

        FROM Menu

        WHERE Ativo = 1

    """)

    total = cursor.fetchone()[0]

    if total <= 0:

        raise Exception(
            "Nenhum menu ativo encontrado."
        )


# ==================================================
# GARANTIR ROOT
# ==================================================

def garantir_root(cursor):

    cursor.execute("""

        SELECT
            Id

        FROM Usuarios

        WHERE UPPER(Login) = 'ROOT'

    """)

    row = cursor.fetchone()

    if row:

        return row[0]

    logging.warning(
        "Usuário ROOT inexistente."
    )

    senha_hash = gerar_hash(
        SENHA_ADMIN
    )

    cursor.execute("""

        INSERT INTO Usuarios
        (
            Login,
            Nome,
            SenhaHash,
            PerfilId,
            Ativo,
            Bloqueado,
            TentativasLogin,
            DeveTrocarSenha,
            SenhaTemporaria,
            SenhaMigrada
        )

        VALUES
        (
            'ROOT',
            'ROOT',
            ?,
            1,
            1,
            0,
            0,
            ?,
            ?,
            0
        )

    """, (

        senha_hash,

        int(FORCAR_TROCA_ADMIN),

        int(FORCAR_TROCA_ADMIN)
    ))

    registrar_evento(

        login="BOOTSTRAP",

        acao="CRIAR_ROOT",

        entidade="Usuarios",

        detalhes="Usuário ROOT criado automaticamente"
    )

    logging.info(
        "Usuário ROOT criado."
    )

    return True


# ==================================================
# GARANTIR ADMIN
# ==================================================

def garantir_admin(cursor):

    cursor.execute("""

        SELECT
            Id

        FROM Usuarios

        WHERE UPPER(Login) = UPPER(?)

    """, (LOGIN_ADMIN,))

    row = cursor.fetchone()

    if row:

        return row[0]

    logging.warning(
        "Usuário ADMIN inexistente."
    )

    senha_hash = gerar_hash(
        SENHA_ADMIN
    )

    cursor.execute("""

        INSERT INTO Usuarios
        (
            Login,
            Nome,
            SenhaHash,
            PerfilId,
            Ativo,
            Bloqueado,
            TentativasLogin,
            DeveTrocarSenha,
            SenhaTemporaria,
            SenhaMigrada
        )

        VALUES
        (
            ?, ?,
            ?,
            2,
            1,
            0,
            0,
            ?,
            ?,
            0
        )

    """, (

        LOGIN_ADMIN,

        LOGIN_ADMIN,

        senha_hash,

        int(FORCAR_TROCA_ADMIN),

        int(FORCAR_TROCA_ADMIN)
    ))

    registrar_evento(

        login="BOOTSTRAP",

        acao="CRIAR_ADMIN",

        entidade="Usuarios",

        detalhes="Usuário ADMIN criado automaticamente"
    )

    logging.info(
        "Usuário ADMIN criado."
    )

    return True


# ==================================================
# VALIDAR ROOT USER
# ==================================================

def validar_root_usuario(cursor):

    cursor.execute("""

        SELECT
            u.Id,
            u.PerfilId,
            p.AdminLevel,
            p.Sistema

        FROM Usuarios u

        INNER JOIN Perfis p
            ON p.Id = u.PerfilId

        WHERE UPPER(u.Login) = 'ROOT'

    """)

    row = cursor.fetchone()

    if not row:

        raise Exception(
            "Usuário ROOT inexistente."
        )

    perfil_id = row[1]

    level = int(row[2])

    sistema = bool(row[3])

    if perfil_id != 1:

        raise Exception(
            "ROOT deve usar PerfilId=1."
        )

    if level < ROOT_LEVEL:

        raise Exception(
            "ROOT inválido."
        )

    if not sistema:

        raise Exception(
            "ROOT não estrutural."
        )


# ==================================================
# INICIAR SISTEMA
# ==================================================

def iniciar_sistema():

    conn = None

    try:

        logging.info(
            "Inicializando bootstrap..."
        )

        conn = get_connection()

        cursor = conn.cursor()

        # ==========================================
        # ESTRUTURA
        # ==========================================

        validar_estrutura(cursor)

        # ==========================================
        # PERFIS
        # ==========================================

        validar_perfis(cursor)

        # ==========================================
        # MENUS
        # ==========================================

        validar_menus(cursor)

        # ==========================================
        # ROOT
        # ==========================================

        garantir_root(cursor)

        # ==========================================
        # ADMIN
        # ==========================================

        garantir_admin(cursor)

        # ==========================================
        # VALIDAR ROOT
        # ==========================================

        validar_root_usuario(cursor)

        conn.commit()

        logging.info(
            "Bootstrap validado."
        )

    except Exception:

        if conn:

            conn.rollback()

        logging.exception(
            "BOOTSTRAP ERROR"
        )

        raise

    finally:

        try:

            if conn:
                conn.close()

        except Exception:
            pass