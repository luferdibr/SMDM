
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


# ==================================================
# LOGGER
# ==================================================

LOGGER = logging.getLogger(
    "MDM_MIGRATION"
)


# ==================================================
# HELPERS
# ==================================================

def auditoria_segura(**kwargs):

    try:

        registrar_evento(**kwargs)

    except Exception:

        LOGGER.exception(
            "AUDITORIA ERROR"
        )


def migration_executada(
    cursor,
    key
):

    cursor.execute("""

        SELECT COUNT(*)

        FROM SystemMigration

        WHERE MigrationKey = ?

    """, (key,))

    return cursor.fetchone()[0] > 0


def registrar_migration(
    cursor,
    key
):

    if coluna_eh_identity(
        cursor,
        "SystemMigration",
        "Id",
    ):

        cursor.execute("""

            INSERT INTO SystemMigration (

                MigrationKey

            )

            VALUES (?)

        """, (key,))

        return

    cursor.execute("""

        INSERT INTO SystemMigration (

            Id,
            MigrationKey

        )

        VALUES (?, ?)

    """, (
        obter_proximo_id(
            cursor,
            "SystemMigration",
            "Id",
        ),
        key,
    ))


def coluna_existe(
    cursor,
    tabela,
    coluna
):

    cursor.execute("""

        SELECT COUNT(*)

        FROM INFORMATION_SCHEMA.COLUMNS

        WHERE
            TABLE_NAME = ?
            AND COLUMN_NAME = ?

    """, (

        tabela,
        coluna
    ))

    return cursor.fetchone()[0] > 0


# ==================================================
# USERS SECURITY
# ==================================================

def migration_usuarios_security_v2(cursor):

    migration_key = (
        "USUARIOS_SECURITY_V2"
    )

    if migration_executada(
        cursor,
        migration_key
    ):
        return

    LOGGER.info(
        migration_key
    )

    alteracoes = [

        (
            "UltimoLogin",

            """
            ALTER TABLE Usuarios
            ADD UltimoLogin DATETIME NULL
            """
        ),

        (
            "DataUltimaTrocaSenha",

            """
            ALTER TABLE Usuarios
            ADD DataUltimaTrocaSenha
                DATETIME NULL
            """
        ),

        (
            "BloqueadoAte",

            """
            ALTER TABLE Usuarios
            ADD BloqueadoAte DATETIME NULL
            """
        ),

        (
            "NivelBloqueio",

            """
            ALTER TABLE Usuarios
            ADD NivelBloqueio INT
                NOT NULL DEFAULT 0
            """
        ),

        (
            "BloqueioTotal",

            """
            ALTER TABLE Usuarios
            ADD BloqueioTotal BIT
                NOT NULL DEFAULT 0
            """
        )
    ]

    for coluna, sql in alteracoes:

        if not coluna_existe(
            cursor,
            "Usuarios",
            coluna
        ):

            LOGGER.info(
                f"Adicionando coluna "
                f"{coluna}"
            )

            cursor.execute(sql)

    registrar_migration(
        cursor,
        migration_key
    )


# ==================================================
# AUDITORIA
# ==================================================

def migration_auditoria_v2(cursor):

    migration_key = (
        "AUDITORIA_V2"
    )

    ja_executada = migration_executada(
        cursor,
        migration_key
    )

    LOGGER.info(
        migration_key
    )

    alteracoes = [

        (
            "UsuarioId",

            """
            ALTER TABLE Auditoria
            ADD UsuarioId INT NULL
            """
        ),

        (
            "Login",

            """
            ALTER TABLE Auditoria
            ADD Login NVARCHAR(100) NULL
            """
        ),

        (
            "Acao",

            """
            ALTER TABLE Auditoria
            ADD Acao NVARCHAR(100) NULL
            """
        ),

        (
            "Entidade",

            """
            ALTER TABLE Auditoria
            ADD Entidade NVARCHAR(100) NULL
            """
        ),

        (
            "RegistroId",

            """
            ALTER TABLE Auditoria
            ADD RegistroId NVARCHAR(100) NULL
            """
        ),

        (
            "Detalhes",

            """
            ALTER TABLE Auditoria
            ADD Detalhes NVARCHAR(MAX) NULL
            """
        ),

        (
            "Severidade",

            """
            ALTER TABLE Auditoria
            ADD Severidade NVARCHAR(20)
                NULL
            """
        ),

        (
            "Sucesso",

            """
            ALTER TABLE Auditoria
            ADD Sucesso BIT
                NOT NULL DEFAULT 1
            """
        ),

        (
            "CriadoEm",

            """
            ALTER TABLE Auditoria
            ADD CriadoEm DATETIME
                NOT NULL DEFAULT GETDATE()
            """
        )
    ]

    for coluna, sql in alteracoes:

        if not coluna_existe(
            cursor,
            "Auditoria",
            coluna
        ):

            LOGGER.info(
                f"Adicionando coluna "
                f"{coluna}"
            )

            cursor.execute(sql)

    if not ja_executada:

        registrar_migration(
            cursor,
            migration_key
        )

# ==================================================
# MENU ENTERPRISE
# ==================================================

def migration_menu_enterprise_v2(cursor):

    migration_key = (
        "MENU_ENTERPRISE_V2"
    )

    if migration_executada(
        cursor,
        migration_key
    ):
        return

    LOGGER.info(
        migration_key
    )

    # ==============================================
    # RESET METADADOS
    # ==============================================

    cursor.execute("""

        UPDATE Menu

        SET

            TipoMenu = 'T',

            Nivel = 1,

            Codigo = NULL,

            Modulo = NULL

    """)

    # ==============================================
    # SEGURANCA RAIZ
    # ==============================================

    cursor.execute("""

        UPDATE Menu

        SET MenuPaiId = NULL

        WHERE Id = 101

    """)

    # ==============================================
    # NIVEL 1
    # ==============================================

    cursor.execute("""

        UPDATE Menu

        SET Nivel = 1

        WHERE MenuPaiId IS NULL

    """)

    # ==============================================
    # NIVEL 2
    # ==============================================

    cursor.execute("""

        UPDATE Menu

        SET Nivel = 2

        WHERE MenuPaiId IN (

            SELECT Id
            FROM Menu
            WHERE Nivel = 1

        )

    """)

    # ==============================================
    # NIVEL 3
    # ==============================================

    cursor.execute("""

        UPDATE Menu

        SET Nivel = 3

        WHERE MenuPaiId IN (

            SELECT Id
            FROM Menu
            WHERE Nivel = 2

        )

    """)

    # ==============================================
    # FOLHAS = T
    # ==============================================

    cursor.execute("""

        UPDATE Menu

        SET TipoMenu = 'T'

        WHERE Id NOT IN (

            SELECT DISTINCT MenuPaiId

            FROM Menu

            WHERE MenuPaiId IS NOT NULL

        )

    """)

    # ==============================================
    # COM FILHOS = M
    # ==============================================

    cursor.execute("""

        UPDATE Menu

        SET TipoMenu = 'M'

        WHERE Id IN (

            SELECT DISTINCT MenuPaiId

            FROM Menu

            WHERE MenuPaiId IS NOT NULL

        )

    """)

    # ==============================================
    # OVERRIDES
    # ==============================================

    cursor.execute("""

        UPDATE Menu

        SET

            TipoMenu = 'T',

            Codigo = 'DASHBOARD',

            Modulo = 'CORE'

        WHERE Id = 1

    """)

    cursor.execute("""

        UPDATE Menu

        SET

            TipoMenu = 'M',

            Codigo = 'SEGURANCA',

            Modulo = 'CORE',

            Ordem = 100

        WHERE Id = 101

    """)

    cursor.execute("""

        UPDATE Menu

        SET TipoMenu = 'S'

        WHERE Id IN (
            20,
            22
        )

    """)

    # ==============================================
    # ENTERPRISE
    # ==============================================

    cursor.execute("""

        UPDATE Menu

        SET

            TipoMenu = 'T',

            Modulo = 'CORE'

        WHERE Id IN (
            201,
            202,
            203
        )

    """)

    cursor.execute("""

        UPDATE Menu
        SET Codigo = 'USUARIOS'
        WHERE Id = 201

    """)

    cursor.execute("""

        UPDATE Menu
        SET Codigo = 'PERFIS'
        WHERE Id = 202

    """)

    cursor.execute("""

        UPDATE Menu
        SET Codigo = 'MENUS'
        WHERE Id = 203

    """)

   

    # ==============================================
    # PERFILMENU
    # ==============================================

    migracoes = [

        (8, 201),
        (11, 202),
        (12, 203)

    ]

    for antigo, novo in migracoes:

        # ==========================================
        # REMOVE DUPLICADOS
        # ==========================================

        cursor.execute("""

            DELETE PM

            FROM PerfilMenu PM

            WHERE PM.MenuId = ?

            AND EXISTS (

                SELECT 1

                FROM PerfilMenu X

                WHERE
                    X.PerfilId = PM.PerfilId
                    AND X.MenuId = ?

            )

        """, (

            antigo,
            novo

        ))

        # ==========================================
        # MIGRA
        # ==========================================

        cursor.execute("""

            UPDATE PerfilMenu

            SET MenuId = ?

            WHERE MenuId = ?

        """, (

            novo,
            antigo

        ))

    # ==============================================
    # LEGADOS
    # ==============================================

    cursor.execute("""

        UPDATE Menu

        SET Ativo = 0

        WHERE Id IN (
            8,
            11,
            12
        )

    """)

    registrar_migration(
        cursor,
        migration_key
    )


# ==================================================
# CLEANUP
# ==================================================

def migration_cleanup_legado(cursor):

    migration_key = (
        "CLEANUP_LEGADO_V1"
    )

    if migration_executada(
        cursor,
        migration_key
    ):
        return

    LOGGER.info(
        migration_key
    )

    cursor.execute("""

        DELETE FROM SystemMigration

        WHERE MigrationKey IN (

            'MENU_REORDER_V1',
            'LEGACY_SECURITY',
            'PERFIS_V1_OLD'

        )

    """)

    registrar_migration(
        cursor,
        migration_key
    )


# ==================================================
# EXECUCAO
# ==================================================

def executar_migracoes():

    conn = None

    try:

        LOGGER.info(
            "Inicializando migrations..."
        )

        conn = get_connection()

        cursor = conn.cursor()

        # ==========================================
        # USERS
        # ==========================================

        migration_usuarios_security_v2(
            cursor
        )

        # ==========================================
        # AUDITORIA
        # ==========================================

        migration_auditoria_v2(
            cursor
        )

        # ==========================================
        # MENU
        # ==========================================

        migration_menu_enterprise_v2(
            cursor
        )

        # ==========================================
        # CLEANUP
        # ==========================================

        migration_cleanup_legado(
            cursor
        )

        conn.commit()

        auditoria_segura(

            login="SYSTEM",

            acao="MIGRATIONS_OK",

            entidade="SYSTEM"
        )

        LOGGER.info(
            "Migrations concluídas."
        )

        return True

    except Exception:

        if conn:
            conn.rollback()

        LOGGER.exception(
            "MIGRATION ERROR"
        )

        auditoria_segura(

            login="SYSTEM",

            acao="MIGRATIONS_ERROR",

            entidade="SYSTEM"
        )

        raise

    finally:

        try:

            if conn:
                conn.close()

        except Exception:
            pass
