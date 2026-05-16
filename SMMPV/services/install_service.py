
import logging

import pyodbc

from config.settings import DB_CONFIG


# ==================================================
# LOGGER
# ==================================================

LOGGER = logging.getLogger(
    "MDM_INSTALL"
)

if not LOGGER.handlers:

    logging.basicConfig(

        level=logging.INFO,

        format=(
            "%(asctime)s "
            "[%(levelname)s] "
            "%(message)s"
        )
    )


# ==================================================
# CONFIG
# ==================================================

DATABASE_NAME = DB_CONFIG[
    "database"
]


# ==================================================
# CONNECTION STRING
# ==================================================

def build_conn_str(database=None):

    server = str(
        DB_CONFIG["server"]
    ).strip()

    port = str(
        DB_CONFIG.get(
            "port",
            ""
        )
    ).strip()

    server_str = server

    if port:

        server_str = (
            f"{server},{port}"
        )

    encrypt = (

        "yes"

        if DB_CONFIG.get(
            "encrypt"
        )

        else "no"
    )

    trust_cert = (

        "yes"

        if DB_CONFIG.get(
            "trust_cert"
        )

        else "no"
    )

    conn = (

        f"DRIVER="
        f"{{{DB_CONFIG['driver']}}};"

        f"SERVER={server_str};"

        f"UID={DB_CONFIG['user']};"

        f"PWD={DB_CONFIG['password']};"

        f"Encrypt={encrypt};"

        f"TrustServerCertificate="
        f"{trust_cert};"

        "MARS_Connection=yes;"

        "MultipleActiveResultSets=True;"
    )

    if database:

        conn += (
            f"DATABASE={database};"
        )

    return conn


# ==================================================
# ENCODING
# ==================================================

def configurar_encoding(conn):

    conn.setdecoding(

        pyodbc.SQL_CHAR,

        encoding="latin1"
    )

    conn.setdecoding(

        pyodbc.SQL_WCHAR,

        encoding="utf-16le"
    )

    conn.setencoding(

        encoding="latin1"
    )


# ==================================================
# CONNECTIONS
# ==================================================

def get_master_connection():

    conn = pyodbc.connect(

        build_conn_str(),

        autocommit=True,

        timeout=DB_CONFIG.get(
            "timeout",
            30
        )
    )

    configurar_encoding(conn)

    return conn


def get_database_connection():

    conn = pyodbc.connect(

        build_conn_str(
            DATABASE_NAME
        ),

        timeout=DB_CONFIG.get(
            "timeout",
            30
        )
    )

    configurar_encoding(conn)

    return conn


# ==================================================
# HELPERS
# ==================================================

def tabela_existe(
    cursor,
    tabela
):

    cursor.execute("""

        SELECT COUNT(*)

        FROM INFORMATION_SCHEMA.TABLES

        WHERE TABLE_NAME = ?

    """, (tabela,))

    return cursor.fetchone()[0] > 0


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


def banco_existe(cursor):

    cursor.execute("""

        SELECT db_id(?)

    """, (DATABASE_NAME,))

    row = cursor.fetchone()

    return row[0] is not None


# ==================================================
# DATABASE
# ==================================================

def criar_database(cursor):

    LOGGER.info(

        "Criando database %s",

        DATABASE_NAME
    )

    cursor.execute(f"""

        CREATE DATABASE {DATABASE_NAME}

    """)


# ==================================================
# SYSTEM MIGRATION
# ==================================================

def criar_tabela_system_migration(cursor):

    if tabela_existe(
        cursor,
        "SystemMigration"
    ):
        return

    LOGGER.info(
        "Criando tabela SystemMigration"
    )

    cursor.execute("""

        CREATE TABLE SystemMigration (

            Id INT IDENTITY PRIMARY KEY,

            MigrationKey NVARCHAR(200)
                NOT NULL UNIQUE,

            ExecutadoEm DATETIME
                NOT NULL DEFAULT GETDATE()
        )

    """)


# ==================================================
# PERFIS
# ==================================================

def criar_tabela_perfis(cursor):

    if tabela_existe(cursor, "Perfis"):
        return

    LOGGER.info(
        "Criando tabela Perfis"
    )

    cursor.execute("""

        CREATE TABLE Perfis (

            Id INT IDENTITY PRIMARY KEY,

            Nome NVARCHAR(100)
                NOT NULL UNIQUE,

            ValidadeSenhaDias INT NULL,

            Ativo BIT
                NOT NULL DEFAULT 1,

            AdminLevel INT
                NOT NULL DEFAULT 0,

            Sistema BIT
                NOT NULL DEFAULT 0
        )

    """)


# ==================================================
# USUARIOS
# ==================================================

def criar_tabela_usuarios(cursor):

    if tabela_existe(cursor, "Usuarios"):
        return

    LOGGER.info(
        "Criando tabela Usuarios"
    )

    cursor.execute("""

        CREATE TABLE Usuarios (

            Id INT IDENTITY PRIMARY KEY,

            Login NVARCHAR(50)
                NOT NULL UNIQUE,

            Nome NVARCHAR(200)
                NOT NULL,

            Email NVARCHAR(200)
                NULL,

            SenhaHash NVARCHAR(500)
                NOT NULL,

            PerfilId INT
                NOT NULL,

            Ativo BIT
                NOT NULL DEFAULT 1,

            Bloqueado BIT
                NOT NULL DEFAULT 0,

            TentativasLogin INT
                NOT NULL DEFAULT 0,

            DeveTrocarSenha BIT
                NOT NULL DEFAULT 0,

            SenhaTemporaria BIT
                NOT NULL DEFAULT 0,

            UltimoLogin DATETIME NULL,

            DataUltimaTrocaSenha
                DATETIME NULL,

            BloqueadoAte DATETIME NULL,

            NivelBloqueio INT
                NOT NULL DEFAULT 0,

            BloqueioTotal BIT
                NOT NULL DEFAULT 0,

            CriadoEm DATETIME
                NOT NULL DEFAULT GETDATE(),

            FOREIGN KEY (PerfilId)
                REFERENCES Perfis(Id)
        )

    """)

    cursor.execute("""

        CREATE INDEX IX_Usuarios_Login
            ON Usuarios(Login)

    """)

    cursor.execute("""

        CREATE INDEX IX_Usuarios_Perfil
            ON Usuarios(PerfilId)

    """)


# ==================================================
# MENU
# ==================================================

def criar_tabela_menu(cursor):

    if tabela_existe(cursor, "Menu"):
        return

    LOGGER.info(
        "Criando tabela Menu"
    )

    cursor.execute("""

        CREATE TABLE Menu (

            Id INT PRIMARY KEY,

            Nome NVARCHAR(100)
                NOT NULL,

            Rota NVARCHAR(100)
                NULL,

            TipoMenu CHAR(1)
                NOT NULL,

            MenuPaiId INT NULL,

            Ordem INT
                NOT NULL DEFAULT 0,

            Nivel INT
                NOT NULL DEFAULT 1,

            Codigo NVARCHAR(50)
                NULL,

            Modulo NVARCHAR(50)
                NULL,

            Icone NVARCHAR(50)
                NULL,

            AdminLevel INT
                NOT NULL DEFAULT 0,

            Ativo BIT
                NOT NULL DEFAULT 1,

            Sistema BIT
                NOT NULL DEFAULT 0,

            FOREIGN KEY (MenuPaiId)
                REFERENCES Menu(Id)
        )

    """)


# ==================================================
# PERFIL MENU
# ==================================================

def criar_tabela_perfil_menu(cursor):

    if tabela_existe(
        cursor,
        "PerfilMenu"
    ):
        return

    LOGGER.info(
        "Criando tabela PerfilMenu"
    )

    cursor.execute("""

        CREATE TABLE PerfilMenu (

            Id INT IDENTITY PRIMARY KEY,

            PerfilId INT NOT NULL,

            MenuId INT NOT NULL,

            PodeVer BIT
                NOT NULL DEFAULT 0,

            PodeEditar BIT
                NOT NULL DEFAULT 0,

            PodeExcluir BIT
                NOT NULL DEFAULT 0,

            FOREIGN KEY (PerfilId)
                REFERENCES Perfis(Id),

            FOREIGN KEY (MenuId)
                REFERENCES Menu(Id)
        )

    """)


# ==================================================
# AUDITORIA
# ==================================================

def criar_tabela_auditoria(cursor):

    if tabela_existe(
        cursor,
        "Auditoria"
    ):
        return

    LOGGER.info(
        "Criando tabela Auditoria"
    )

    cursor.execute("""

        CREATE TABLE Auditoria (

            Id INT IDENTITY PRIMARY KEY,

            UsuarioId INT NULL,

            Login NVARCHAR(100)
                NULL,

            Acao NVARCHAR(100)
                NOT NULL,

            Entidade NVARCHAR(100)
                NULL,

            RegistroId NVARCHAR(100)
                NULL,

            Detalhes NVARCHAR(MAX)
                NULL,

            Severidade NVARCHAR(20)
                NULL,

            Sucesso BIT
                NOT NULL DEFAULT 1,

            CriadoEm DATETIME
                NOT NULL DEFAULT GETDATE()
        )

    """)


# ==================================================
# EVOLUCAO SCHEMA
# ==================================================

def atualizar_schema_usuarios(cursor):

    colunas = [

        (
            "UltimoLogin",
            "ALTER TABLE Usuarios "
            "ADD UltimoLogin DATETIME NULL"
        ),

        (
            "DataUltimaTrocaSenha",
            "ALTER TABLE Usuarios "
            "ADD DataUltimaTrocaSenha DATETIME NULL"
        ),

        (
            "BloqueadoAte",
            "ALTER TABLE Usuarios "
            "ADD BloqueadoAte DATETIME NULL"
        ),

        (
            "NivelBloqueio",
            "ALTER TABLE Usuarios "
            "ADD NivelBloqueio INT "
            "NOT NULL DEFAULT 0"
        ),

        (
            "BloqueioTotal",
            "ALTER TABLE Usuarios "
            "ADD BloqueioTotal BIT "
            "NOT NULL DEFAULT 0"
        )
    ]

    for coluna, sql in colunas:

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


def atualizar_tabela_auditoria(cursor):

    colunas = [

        (
            "Severidade",
            "ALTER TABLE Auditoria "
            "ADD Severidade NVARCHAR(20) NULL"
        ),

        (
            "Sucesso",
            "ALTER TABLE Auditoria "
            "ADD Sucesso BIT "
            "NOT NULL DEFAULT 1"
        )
    ]

    for coluna, sql in colunas:

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


# ==================================================
# INSTALL
# ==================================================

def garantir_instalacao():

    conn = None

    try:

        LOGGER.info(
            "Validando instalação..."
        )

        master_conn = get_master_connection()

        master_cursor = master_conn.cursor()

        if not banco_existe(
            master_cursor
        ):

            criar_database(
                master_cursor
            )

        master_conn.close()

        conn = get_database_connection()

        cursor = conn.cursor()

        criar_tabela_system_migration(
            cursor
        )

        criar_tabela_perfis(cursor)

        criar_tabela_usuarios(cursor)

        criar_tabela_menu(cursor)

        criar_tabela_perfil_menu(cursor)

        criar_tabela_auditoria(cursor)

        atualizar_schema_usuarios(
            cursor
        )

        atualizar_tabela_auditoria(
            cursor
        )

        conn.commit()

        LOGGER.info(
            "Instalação validada."
        )

        return True

    except Exception:

        if conn:
            conn.rollback()

        LOGGER.exception(
            "INSTALL ERROR"
        )

        raise

    finally:

        try:

            if conn:
                conn.close()

        except Exception:
            pass