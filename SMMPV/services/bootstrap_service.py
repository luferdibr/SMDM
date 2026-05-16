
import logging

from config.settings import (
    ADMIN_CONFIG
)

from database.connection import (
    get_connection
)

from security.password_service import (
    gerar_hash
)

from services.auditoria_service import (
    registrar_evento_sistema
)


# ==================================================
# CONFIG
# ==================================================

ROOT_LEVEL = 100

ADMIN_LEVEL = 50


# ==================================================
# ROOT
# ==================================================

LOGIN_ROOT = ADMIN_CONFIG[
    "root_login"
]

NOME_ROOT = ADMIN_CONFIG[
    "root_nome"
]

SENHA_ROOT = ADMIN_CONFIG[
    "root_senha"
]


# ==================================================
# ADMIN
# ==================================================

LOGIN_ADMIN = ADMIN_CONFIG[
    "admin_login"
]

NOME_ADMIN = ADMIN_CONFIG[
    "admin_nome"
]

SENHA_ADMIN = ADMIN_CONFIG[
    "admin_senha"
]


# ==================================================
# LOGGER
# ==================================================

LOGGER = logging.getLogger(
    "MDM_BOOTSTRAP"
)


# ==================================================
# HELPERS
# ==================================================

def existe_tabela(

    cursor,

    tabela
):

    cursor.execute("""

        SELECT COUNT(*)

        FROM INFORMATION_SCHEMA.TABLES

        WHERE TABLE_NAME = ?

    """, (tabela,))

    return cursor.fetchone()[0] > 0


def existe_registro(

    cursor,

    tabela,

    campo,

    valor
):

    cursor.execute(f"""

        SELECT COUNT(*)

        FROM {tabela}

        WHERE {campo} = ?

    """, (valor,))

    return cursor.fetchone()[0] > 0


# ==================================================
# PERFIS
# ==================================================

def garantir_perfis(cursor):

    perfis = [

        {

            "nome": "ROOT",

            "admin_level": ROOT_LEVEL,

            "sistema": 1
        },

        {

            "nome": "ADMIN",

            "admin_level": ADMIN_LEVEL,

            "sistema": 1
        },

        {

            "nome": "OPERADOR",

            "admin_level": 10,

            "sistema": 1
        }
    ]

    for perfil in perfis:

        if existe_registro(

            cursor,

            "Perfis",

            "Nome",

            perfil["nome"]
        ):

            continue

        cursor.execute("""

            INSERT INTO Perfis
            (
                Nome,
                AdminLevel,
                Sistema,
                Ativo,
                ValidadeSenhaDias
            )

            VALUES (?, ?, ?, 1, 90)

        """, (

            perfil["nome"],

            perfil["admin_level"],

            perfil["sistema"]
        ))

        LOGGER.info(

            (
                f"Perfil criado: "
                f"{perfil['nome']}"
            )
        )


# ==================================================
# GET PERFIL
# ==================================================

def get_perfil_id(

    cursor,

    nome
):

    cursor.execute("""

        SELECT TOP 1 Id

        FROM Perfis

        WHERE Nome = ?

    """, (nome,))

    row = cursor.fetchone()

    if not row:

        raise Exception(
            f"Perfil não encontrado: {nome}"
        )

    return row[0]


# ==================================================
# USERS
# ==================================================

def garantir_root(cursor):

    if existe_registro(

        cursor,

        "Usuarios",

        "Login",

        LOGIN_ROOT
    ):

        return

    perfil_id = get_perfil_id(

        cursor,

        "ROOT"
    )

    senha_hash = gerar_hash(
        SENHA_ROOT
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
            SenhaTemporaria
        )

        VALUES
        (
            ?, ?, ?, ?,
            1, 0, 0, 0, 0
        )

    """, (

        LOGIN_ROOT,

        NOME_ROOT,

        senha_hash,

        perfil_id
    ))

    LOGGER.info(
        "Usuário ROOT criado."
    )


def garantir_admin(cursor):

    if existe_registro(

        cursor,

        "Usuarios",

        "Login",

        LOGIN_ADMIN
    ):

        return

    perfil_id = get_perfil_id(

        cursor,

        "ADMIN"
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
            SenhaTemporaria
        )

        VALUES
        (
            ?, ?, ?, ?,
            1, 0, 0, 1, 1
        )

    """, (

        LOGIN_ADMIN,

        NOME_ADMIN,

        senha_hash,

        perfil_id
    ))

    LOGGER.info(
        "Usuário ADMIN criado."
    )


# ==================================================
# MENUS
# ==================================================


def garantir_menus(cursor):

    # ==========================================
    # LIMPEZA CONTROLADA
    # ==========================================

    cursor.execute("""

        DELETE FROM PerfilMenu

    """)

    cursor.execute("""

        DELETE FROM Menu

    """)

    # ==========================================
    # MENUS OFICIAIS
    # ==========================================

    menus = [

        # ======================================
        # TITULOS (T)
        # ======================================

        (
            1,
            "Dashboard",
            "dashboard",
            "T",
            None,
            1,
            1,
            "DASHBOARD",
            "CORE",
            "dashboard",
            10
        ),

        (
            20,
            "Cadastros",
            None,
            "T",
            None,
            2,
            1,
            "CADASTROS",
            "CORE",
            "folder",
            10
        ),

        (
            22,
            "Eventos",
            None,
            "T",
            None,
            3,
            1,
            "EVENTOS",
            "CORE",
            "event",
            10
        ),

        (
            30,
            "Administração",
            None,
            "T",
            None,
            99,
            1,
            "ADMIN",
            "CORE",
            "admin_panel_settings",
            ADMIN_LEVEL
        ),

        # ======================================
        # MENUS (M)
        # ======================================

        (
            101,
            "Locais",
            None,
            "M",
            20,
            1,
            2,
            "LOCAIS",
            "CORE",
            "location_city",
            10
        ),

        (
            102,
            "Segurança",
            None,
            "M",
            30,
            1,
            2,
            "SEGURANCA",
            "CORE",
            "security",
            ADMIN_LEVEL
        ),

        # ======================================
        # SUBMENUS (S)
        # ======================================

        (
            201,
            "Cadastro de Locais",
            "locais",
            "S",
            101,
            1,
            3,
            "LOC_CAD",
            "CORE",
            "home_work",
            10
        ),

        (
            202,
            "Ambientes",
            "loc_ambientes",
            "S",
            101,
            2,
            3,
            "LOC_AMB",
            "CORE",
            "meeting_room",
            10
        ),

        (
            203,
            "Tipos de Local",
            "loc_tipos",
            "S",
            101,
            3,
            3,
            "LOC_TIPOS",
            "CORE",
            "category",
            10
        ),

        (
            204,
            "Estruturas",
            "loc_estruturas",
            "S",
            101,
            4,
            3,
            "LOC_ESTRUT",
            "CORE",
            "account_tree",
            10
        ),

        (
            205,
            "Agenda",
            "agenda",
            "S",
            22,
            1,
            2,
            "AGENDA",
            "CORE",
            "calendar_month",
            10
        ),

        (
            206,
            "Orçamentos",
            "orcamentos",
            "S",
            22,
            2,
            2,
            "ORCAMENTOS",
            "CORE",
            "request_quote",
            10
        ),

        (
            250,
            "Usuários",
            "usuarios",
            "S",
            102,
            1,
            3,
            "USUARIOS",
            "CORE",
            "people",
            ADMIN_LEVEL
        ),

        (
            251,
            "Perfis",
            "perfis",
            "S",
            102,
            2,
            3,
            "PERFIS",
            "CORE",
            "admin_panel_settings",
            ADMIN_LEVEL
        ),

        (
            252,
            "Menus",
            "menu_config",
            "S",
            102,
            3,
            3,
            "MENUS",
            "CORE",
            "menu",
            ROOT_LEVEL
        )
    ]

    # ==========================================
    # INSERT
    # ==========================================

    for menu in menus:

        cursor.execute("""

            INSERT INTO Menu
            (
                Id,
                Nome,
                Rota,
                TipoMenu,
                MenuPaiId,
                Ordem,
                Nivel,
                Codigo,
                Modulo,
                Icone,
                AdminLevel,
                Ativo,
                Sistema
            )

            VALUES
            (
                ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?,
                ?, 1, 1
            )

        """, menu)

        LOGGER.info(

            (
                f"Menu criado: "
                f"{menu[1]}"
            )
        )


# ==================================================
# PERMISSOES
# ==================================================

def garantir_permissoes(cursor):

    cursor.execute("""

        SELECT
            p.Id,
            p.AdminLevel,
            m.Id,
            m.AdminLevel

        FROM Perfis p

        CROSS JOIN Menu m

    """)

    rows = cursor.fetchall()

    for row in rows:

        perfil_id = row[0]

        perfil_level = int(row[1])

        menu_id = row[2]

        menu_level = int(row[3])

        pode_ver = (
            perfil_level >= menu_level
        )

        if not pode_ver:
            continue

        cursor.execute("""

            SELECT COUNT(*)

            FROM PerfilMenu

            WHERE
                PerfilId = ?
                AND
                MenuId = ?

        """, (

            perfil_id,

            menu_id
        ))

        existe = (
            cursor.fetchone()[0] > 0
        )

        if existe:
            continue

        pode_editar = (
            perfil_level >= ADMIN_LEVEL
        )

        pode_excluir = (
            perfil_level >= ROOT_LEVEL
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

            int(pode_ver),

            int(pode_editar),

            int(pode_excluir)
        ))


# ==================================================
# BOOTSTRAP
# ==================================================

def iniciar_sistema():

    conn = None

    try:

        LOGGER.info(
            "Inicializando bootstrap..."
        )

        conn = get_connection()

        cursor = conn.cursor()

        # ==========================================
        # VALIDA
        # ==========================================

        tabelas = [

            "Perfis",

            "Usuarios",

            "Menu",

            "PerfilMenu"
        ]

        for tabela in tabelas:

            if not existe_tabela(

                cursor,

                tabela
            ):

                raise Exception(

                    (
                        f"Tabela não encontrada: "
                        f"{tabela}"
                    )
                )

        # ==========================================
        # PERFIS
        # ==========================================

        garantir_perfis(cursor)

        # ==========================================
        # USERS
        # ==========================================

        garantir_root(cursor)

        garantir_admin(cursor)

        # ==========================================
        # MENUS
        # ==========================================

        garantir_menus(cursor)

        # ==========================================
        # PERMISSOES
        # ==========================================

        garantir_permissoes(cursor)

        conn.commit()

        registrar_evento_sistema(

            "BOOTSTRAP_OK",

            "Bootstrap executado."
        )

        LOGGER.info(
            "Bootstrap concluído."
        )

        return True

    except Exception as ex:

        if conn:
            conn.rollback()

        LOGGER.exception(
            "BOOTSTRAP ERROR"
        )

        raise Exception(

            (
                "Erro bootstrap.\n\n"
                f"{str(ex)}"
            )
        )

    finally:

        try:

            if conn:
                conn.close()

        except Exception:
            pass