
import json

import logging

import os

from pathlib import Path

import pyodbc

from config.settings import DB_CONFIG

from config.settings import ADMIN_CONFIG

from config.settings import INITIAL_DATA_FILE

from config.settings import LOC_TIPOS_FILE

from security.password_service import (
    gerar_hash,
)


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

ROOT_LEVEL = 100

ADMIN_LEVEL = 50


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


def adicionar_colunas_se_faltarem(
    cursor,
    tabela,
    colunas,
):

    for coluna, sql in colunas:

        if not coluna_existe(
            cursor,
            tabela,
            coluna
        ):

            LOGGER.info(
                (
                    f"Adicionando coluna "
                    f"{tabela}.{coluna}"
                )
            )

            cursor.execute(sql)


def coluna_eh_identity(
    cursor,
    tabela,
    coluna,
):

    cursor.execute("""

        SELECT COLUMNPROPERTY(
            OBJECT_ID(?),
            ?,
            'IsIdentity'
        )

    """, (
        tabela,
        coluna,
    ))

    row = cursor.fetchone()

    return bool(
        row
        and
        row[0]
    )


def obter_proximo_id(
    cursor,
    tabela,
    coluna,
):

    cursor.execute(f"""

        SELECT ISNULL(MAX({coluna}), 0) + 1

        FROM {tabela}

    """)

    return int(
        cursor.fetchone()[0]
        or 1
    )


def registro_existe(
    cursor,
    tabela,
    coluna,
    valor,
):

    cursor.execute(f"""

        SELECT COUNT(*)

        FROM {tabela}

        WHERE {coluna} = ?

    """, (
        valor,
    ))

    return cursor.fetchone()[0] > 0


def buscar_id(
    cursor,
    tabela,
    coluna_id,
    coluna_busca,
    valor,
):

    cursor.execute(f"""

        SELECT TOP 1 {coluna_id}

        FROM {tabela}

        WHERE {coluna_busca} = ?

        ORDER BY {coluna_id}

    """, (
        valor,
    ))

    row = cursor.fetchone()

    return row[0] if row else None


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
#
# Observacao de instalacao:
# Esta rotina e evolutiva. A cada nova rotina do
# sistema completo, novas tabelas, colunas, indices
# e dados iniciais podem ser necessarios aqui ou nas
# migrations correspondentes.
#
# Observacao de dominio:
# A hierarquia operacional do menu usa:
# - T como pai/agrupador;
# - M como agrupador intermediario;
# - S como item executavel/processo.
#
# Os campos Id, Nome, Rota, TipoMenu, MenuPaiId,
# Ordem e Ativo formam o nucleo atual da montagem.
# Os campos Nivel, Codigo, Modulo, Icone, AdminLevel
# e Sistema permanecem em observacao para uso futuro
# em organizacao visual, auditoria, modulos, regras
# administrativas ou migracoes. Nao remover sem uma
# decisao funcional explicita.

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
# LOCAIS
# ==================================================
#
# Observacao de dominio:
# As tabelas de local ainda estao em evolucao. O
# cadastro de endereco sera padronizado, com campos
# suficientes para CEP, municipio/UF/pais e possivel
# geocodificacao futura para calculo de distancia
# entre o local do evento e as sedes.

def criar_tabela_loc_tipo(cursor):

    if tabela_existe(
        cursor,
        "LocTipo"
    ):
        return

    LOGGER.info(
        "Criando tabela LocTipo"
    )

    cursor.execute("""

        CREATE TABLE LocTipo (

            LocTipoID INT IDENTITY PRIMARY KEY,

            NomeTipo NVARCHAR(100)
                NOT NULL UNIQUE,

            Ativo BIT
                NOT NULL DEFAULT 1
        )

    """)


def criar_tabela_loc_estrutura(cursor):

    if tabela_existe(
        cursor,
        "LocEstrutura"
    ):
        return

    LOGGER.info(
        "Criando tabela LocEstrutura"
    )

    cursor.execute("""

        CREATE TABLE LocEstrutura (

            LocEstruturaID INT IDENTITY PRIMARY KEY,

            NomeEstrutura NVARCHAR(100)
                NOT NULL UNIQUE,

            Ativo BIT
                NOT NULL DEFAULT 1
        )

    """)


def criar_tabela_local_evento(cursor):

    if tabela_existe(
        cursor,
        "LocalEvento"
    ):
        return

    LOGGER.info(
        "Criando tabela LocalEvento"
    )

    cursor.execute("""

        CREATE TABLE LocalEvento (

            LocalEventoID INT IDENTITY PRIMARY KEY,

            NomeCasa NVARCHAR(200)
                NOT NULL UNIQUE,

            NomeFantasia NVARCHAR(200) NULL,

            LocTipoID INT NULL,

            CNPJ NVARCHAR(20) NULL,

            CEP NVARCHAR(20) NULL,

            Logradouro NVARCHAR(200) NULL,

            Numero NVARCHAR(30) NULL,

            Complemento NVARCHAR(100) NULL,

            Bairro NVARCHAR(100) NULL,

            Municipio NVARCHAR(100) NULL,

            UF NVARCHAR(2) NULL,

            Pais NVARCHAR(80)
                NOT NULL DEFAULT 'Brasil',

            Endereco NVARCHAR(700) NULL,

            Responsavel NVARCHAR(200) NULL,

            Contato NVARCHAR(100) NULL,

            Telefone NVARCHAR(30) NULL,

            Celular NVARCHAR(30) NULL,

            Email NVARCHAR(200) NULL,

            Site NVARCHAR(250) NULL,

            Instagram NVARCHAR(250) NULL,

            Facebook NVARCHAR(250) NULL,

            OutrasRedes NVARCHAR(MAX) NULL,

            HorarioFuncionamento NVARCHAR(MAX) NULL,

            Contato1Nome NVARCHAR(200) NULL,

            Contato1Telefone NVARCHAR(30) NULL,

            Contato1Cargo NVARCHAR(120) NULL,

            Contato2Nome NVARCHAR(200) NULL,

            Contato2Telefone NVARCHAR(30) NULL,

            Contato2Cargo NVARCHAR(120) NULL,

            Contato3Nome NVARCHAR(200) NULL,

            Contato3Telefone NVARCHAR(30) NULL,

            Contato3Cargo NVARCHAR(120) NULL,

            QuemIndicou NVARCHAR(200) NULL,

            Latitude DECIMAL(10, 7) NULL,

            Longitude DECIMAL(10, 7) NULL,

            FonteGeo NVARCHAR(50) NULL,

            DataGeo DATETIME NULL,

            PossuiEstacionamento BIT
                NOT NULL DEFAULT 0,

            Observacoes NVARCHAR(MAX) NULL,

            Ativo BIT
                NOT NULL DEFAULT 1,

            CaptadoWeb BIT
                NOT NULL DEFAULT 0,

            ComplementadoWeb BIT
                NOT NULL DEFAULT 0,

            CadastroValidado BIT
                NOT NULL DEFAULT 0,

            PesquisaIncompleta BIT
                NOT NULL DEFAULT 0,

            NecessitaComplemento BIT
                NOT NULL DEFAULT 0,

            NecessitaRevisao BIT
                NOT NULL DEFAULT 0,

            PontuacaoOrigemWeb DECIMAL(5, 2) NULL,

            FonteOrigemWeb NVARCHAR(100) NULL,

            DataOrigemWeb DATETIME NULL,

            LocalPesquisaWebId INT NULL,

            DataValidacaoCadastro DATETIME NULL,

            ObservacaoPesquisa NVARCHAR(MAX) NULL,

            CriadoEm DATETIME
                NOT NULL DEFAULT GETDATE(),

            AtualizadoEm DATETIME NULL,

            FOREIGN KEY (LocTipoID)
                REFERENCES LocTipo(LocTipoID)
        )

    """)

    cursor.execute("""

        CREATE INDEX IX_LocalEvento_NomeCasa
            ON LocalEvento(NomeCasa)

    """)

    cursor.execute("""

        CREATE INDEX IX_LocalEvento_CEP
            ON LocalEvento(CEP)

    """)

    cursor.execute("""

        CREATE UNIQUE INDEX UX_LocalEvento_CNPJ
            ON LocalEvento(CNPJ)
            WHERE CNPJ IS NOT NULL
            AND CNPJ <> ''

    """)


def criar_tabela_local_evento_pesquisa_web(cursor):

    if tabela_existe(
        cursor,
        "LocalEventoPesquisaWeb"
    ):
        return

    LOGGER.info(
        "Criando tabela LocalEventoPesquisaWeb"
    )

    cursor.execute("""

        CREATE TABLE LocalEventoPesquisaWeb (

            LocalPesquisaWebID INT IDENTITY PRIMARY KEY,

            TipoLocalSugerido NVARCHAR(100) NULL,

            NomeCasa NVARCHAR(200)
                NOT NULL,

            NomeFantasia NVARCHAR(200) NULL,

            DescricaoPublica NVARCHAR(MAX) NULL,

            CNPJ NVARCHAR(20) NULL,

            CEP NVARCHAR(20) NULL,

            Logradouro NVARCHAR(200) NULL,

            Numero NVARCHAR(30) NULL,

            Complemento NVARCHAR(100) NULL,

            Bairro NVARCHAR(100) NULL,

            Municipio NVARCHAR(100) NULL,

            UF NVARCHAR(2) NULL,

            Pais NVARCHAR(80)
                NOT NULL DEFAULT 'Brasil',

            Endereco NVARCHAR(700) NULL,

            Latitude DECIMAL(10, 7) NULL,

            Longitude DECIMAL(10, 7) NULL,

            FonteGeo NVARCHAR(50) NULL,

            DataGeo DATETIME NULL,

            Responsavel NVARCHAR(200) NULL,

            Contato NVARCHAR(100) NULL,

            Telefone NVARCHAR(30) NULL,

            Celular NVARCHAR(30) NULL,

            WhatsApp NVARCHAR(30) NULL,

            Email NVARCHAR(200) NULL,

            Site NVARCHAR(250) NULL,

            Instagram NVARCHAR(250) NULL,

            Facebook NVARCHAR(250) NULL,

            OutrasRedes NVARCHAR(MAX) NULL,

            HorarioFuncionamento NVARCHAR(MAX) NULL,

            FontePrincipal NVARCHAR(100) NULL,

            UrlFonte NVARCHAR(500) NULL,

            DadosBrutos NVARCHAR(MAX) NULL,

            PontuacaoConfiabilidade DECIMAL(5, 2)
                NOT NULL DEFAULT 0,

            StatusPesquisa NVARCHAR(30)
                NOT NULL DEFAULT 'PENDENTE_ANALISE',

            PossivelDuplicidade BIT
                NOT NULL DEFAULT 0,

            LocalExistenteId INT NULL,

            Transferido BIT
                NOT NULL DEFAULT 0,

            DataTransferencia DATETIME NULL,

            UsuarioTransferenciaId INT NULL,

            Descartado BIT
                NOT NULL DEFAULT 0,

            DataDescarte DATETIME NULL,

            UsuarioDescarteId INT NULL,

            MotivoDescarte NVARCHAR(MAX) NULL,

            NecessitaComplemento BIT
                NOT NULL DEFAULT 1,

            NecessitaRevisao BIT
                NOT NULL DEFAULT 1,

            DataPesquisa DATETIME
                NOT NULL DEFAULT GETDATE(),

            DataUltimaAtualizacao DATETIME NULL,

            ObservacaoPesquisa NVARCHAR(MAX) NULL,

            FOREIGN KEY (LocalExistenteId)
                REFERENCES LocalEvento(LocalEventoID)
        )

    """)

    cursor.execute("""

        CREATE INDEX IX_LocalEventoPesquisaWeb_Status
            ON LocalEventoPesquisaWeb(StatusPesquisa, Transferido, Descartado)

    """)

    cursor.execute("""

        CREATE INDEX IX_LocalEventoPesquisaWeb_Localidade
            ON LocalEventoPesquisaWeb(Municipio, UF, Bairro)

    """)

    cursor.execute("""

        CREATE INDEX IX_LocalEventoPesquisaWeb_Nome
            ON LocalEventoPesquisaWeb(NomeCasa)

    """)


def criar_tabela_loc_ambientes(cursor):

    if tabela_existe(
        cursor,
        "LocAmbientes"
    ):
        return

    LOGGER.info(
        "Criando tabela LocAmbientes"
    )

    cursor.execute("""

        CREATE TABLE LocAmbientes (

            AmbienteID INT IDENTITY PRIMARY KEY,

            LocalEventoID INT NOT NULL,

            NomeAmbiente NVARCHAR(150)
                NOT NULL,

            TipoEspaco NVARCHAR(20) NULL,

            CapacidadeSentado INT
                NOT NULL DEFAULT 0,

            CapacidadePe INT
                NOT NULL DEFAULT 0,

            Metragem DECIMAL(12, 2)
                NOT NULL DEFAULT 0,

            DimensaoComprimento DECIMAL(12, 2)
                NOT NULL DEFAULT 0,

            DimensaoLargura DECIMAL(12, 2)
                NOT NULL DEFAULT 0,

            PeDireito DECIMAL(12, 2)
                NOT NULL DEFAULT 0,

            ServicosOferecidos NVARCHAR(MAX) NULL,

            ArCondicionado BIT
                NOT NULL DEFAULT 0,

            PrecoBase DECIMAL(18, 2)
                NOT NULL DEFAULT 0,

            SharePointID NVARCHAR(100) NULL,

            Ativo BIT
                NOT NULL DEFAULT 1,

            FOREIGN KEY (LocalEventoID)
                REFERENCES LocalEvento(LocalEventoID)
        )

    """)

    cursor.execute("""

        CREATE INDEX IX_LocAmbientes_Local
            ON LocAmbientes(LocalEventoID)

    """)


def criar_tabela_local_evento_estrutura(cursor):

    if tabela_existe(
        cursor,
        "LocalEventoEstrutura"
    ):
        return

    LOGGER.info(
        "Criando tabela LocalEventoEstrutura"
    )

    cursor.execute("""

        CREATE TABLE LocalEventoEstrutura (

            LocalEventoID INT NOT NULL,

            LocEstruturaID INT NOT NULL,

            PRIMARY KEY (
                LocalEventoID,
                LocEstruturaID
            ),

            FOREIGN KEY (LocalEventoID)
                REFERENCES LocalEvento(LocalEventoID),

            FOREIGN KEY (LocEstruturaID)
                REFERENCES LocEstrutura(LocEstruturaID)
        )

    """)


def criar_tabela_sedes_empresa(cursor):

    if tabela_existe(
        cursor,
        "SedesEmpresa"
    ):
        return

    LOGGER.info(
        "Criando tabela SedesEmpresa"
    )

    cursor.execute("""

        CREATE TABLE SedesEmpresa (

            SedeID INT IDENTITY PRIMARY KEY,

            NomeSede NVARCHAR(150)
                NOT NULL UNIQUE,

            CNPJ NVARCHAR(20) NULL,

            Responsavel NVARCHAR(200) NULL,

            Telefone NVARCHAR(30) NULL,

            Celular NVARCHAR(30) NULL,

            Email NVARCHAR(200) NULL,

            CEP NVARCHAR(20) NULL,

            Logradouro NVARCHAR(200) NULL,

            Numero NVARCHAR(30) NULL,

            Complemento NVARCHAR(100) NULL,

            Bairro NVARCHAR(100) NULL,

            Municipio NVARCHAR(100) NULL,

            UF NVARCHAR(2) NULL,

            Pais NVARCHAR(80)
                NOT NULL DEFAULT 'Brasil',

            Endereco NVARCHAR(700) NULL,

            Latitude DECIMAL(10, 7) NULL,

            Longitude DECIMAL(10, 7) NULL,

            FonteGeo NVARCHAR(50) NULL,

            DataGeo DATETIME NULL,

            Operacional BIT
                NOT NULL DEFAULT 1,

            Fantasma BIT
                NOT NULL DEFAULT 0,

            Observacoes NVARCHAR(MAX) NULL,

            Ativo BIT
                NOT NULL DEFAULT 1,

            CriadoEm DATETIME
                NOT NULL DEFAULT GETDATE(),

            AtualizadoEm DATETIME NULL
        )

    """)

    cursor.execute("""

        CREATE INDEX IX_SedesEmpresa_CEP
            ON SedesEmpresa(CEP)

    """)

    cursor.execute("""

        CREATE UNIQUE INDEX UX_SedesEmpresa_CNPJ
            ON SedesEmpresa(CNPJ)
            WHERE CNPJ IS NOT NULL
            AND CNPJ <> ''

    """)


def criar_tabela_cep_cache(cursor):

    if tabela_existe(
        cursor,
        "CepCache"
    ):
        return

    LOGGER.info(
        "Criando tabela CepCache"
    )

    cursor.execute("""

        CREATE TABLE CepCache (

            CepCacheID INT IDENTITY PRIMARY KEY,

            CEP NVARCHAR(20)
                NOT NULL UNIQUE,

            Logradouro NVARCHAR(200) NULL,

            Bairro NVARCHAR(100) NULL,

            Municipio NVARCHAR(100) NULL,

            UF NVARCHAR(2) NULL,

            Pais NVARCHAR(80)
                NOT NULL DEFAULT 'Brasil',

            Fonte NVARCHAR(50) NULL,

            DadosJson NVARCHAR(MAX) NULL,

            ConsultadoEm DATETIME
                NOT NULL DEFAULT GETDATE()
        )

    """)


def criar_tabela_google_maps_usage(cursor):

    if tabela_existe(
        cursor,
        "GoogleMapsUsage"
    ):
        return

    LOGGER.info(
        "Criando tabela GoogleMapsUsage"
    )

    cursor.execute("""

        CREATE TABLE GoogleMapsUsage (

            Id INT IDENTITY PRIMARY KEY,

            Servico NVARCHAR(80)
                NOT NULL,

            Provedor NVARCHAR(40)
                NOT NULL DEFAULT 'google',

            Consulta NVARCHAR(1000) NULL,

            Status NVARCHAR(80) NULL,

            Sucesso BIT
                NOT NULL DEFAULT 0,

            Detalhes NVARCHAR(2000) NULL,

            ConsultadoEm DATETIME
                NOT NULL DEFAULT GETDATE()
        )

    """)

    cursor.execute("""

        CREATE INDEX IX_GoogleMapsUsage_Mes
            ON GoogleMapsUsage(ConsultadoEm, Servico)

    """)


def criar_tabela_ator(cursor):

    if tabela_existe(
        cursor,
        "Ator"
    ):
        return

    LOGGER.info(
        "Criando tabela Ator"
    )

    cursor.execute("""

        CREATE TABLE Ator (

            AtorID INT IDENTITY PRIMARY KEY,

            Nome NVARCHAR(200)
                NOT NULL,

            NomeProfissional NVARCHAR(200) NULL,

            CEP NVARCHAR(20) NULL,

            Logradouro NVARCHAR(200) NULL,

            Numero NVARCHAR(30) NULL,

            Complemento NVARCHAR(100) NULL,

            Bairro NVARCHAR(100) NULL,

            Municipio NVARCHAR(100) NULL,

            UF NVARCHAR(2) NULL,

            Pais NVARCHAR(80)
                NOT NULL DEFAULT 'Brasil',

            Endereco NVARCHAR(700) NULL,

            Latitude DECIMAL(10, 7) NULL,

            Longitude DECIMAL(10, 7) NULL,

            FonteGeo NVARCHAR(50) NULL,

            DataGeo DATETIME NULL,

            Nacionalidade NVARCHAR(20) NULL,

            Telefone NVARCHAR(30) NULL,

            Celular NVARCHAR(30) NULL,

            DataNascimento DATE NULL,

            CPF NVARCHAR(20) NULL,

            RG NVARCHAR(30) NULL,

            Email NVARCHAR(200) NULL,

            Ensino NVARCHAR(30) NULL,

            Sexo NVARCHAR(20) NULL,

            Ativo BIT
                NOT NULL DEFAULT 1,

            CriadoEm DATETIME
                NOT NULL DEFAULT GETDATE(),

            AtualizadoEm DATETIME NULL
        )

    """)

    cursor.execute("""

        CREATE UNIQUE INDEX UX_Ator_CPF
            ON Ator(CPF)
            WHERE CPF IS NOT NULL
            AND CPF <> ''

    """)


def criar_tabela_cliente(cursor):

    if tabela_existe(
        cursor,
        "Cliente"
    ):
        return

    LOGGER.info(
        "Criando tabela Cliente"
    )

    cursor.execute("""

        CREATE TABLE Cliente (

            ClienteID INT IDENTITY PRIMARY KEY,

            Nome NVARCHAR(200)
                NOT NULL,

            Municipio NVARCHAR(100) NULL,

            UF NVARCHAR(2) NULL,

            Pais NVARCHAR(80)
                NOT NULL DEFAULT 'Brasil',

            Celular NVARCHAR(30) NULL,

            DataNascimento DATE NULL,

            CPF NVARCHAR(20) NULL,

            Email NVARCHAR(200) NULL,

            Sexo NVARCHAR(20) NULL,

            ReceberResumoProgramacao NVARCHAR(20) NULL,

            Profissao NVARCHAR(150) NULL,

            Observacoes NVARCHAR(MAX) NULL,

            PrimeiroCanalContato NVARCHAR(150) NULL,

            Ativo BIT
                NOT NULL DEFAULT 1,

            DataInclusao DATETIME
                NOT NULL DEFAULT GETDATE(),

            AtualizadoEm DATETIME NULL
        )

    """)

    cursor.execute("""

        CREATE UNIQUE INDEX UX_Cliente_CPF
            ON Cliente(CPF)
            WHERE CPF IS NOT NULL
            AND CPF <> ''

    """)


def criar_tabela_cliente_aniversariante(cursor):

    if tabela_existe(
        cursor,
        "ClienteAniversariante"
    ):
        return

    LOGGER.info(
        "Criando tabela ClienteAniversariante"
    )

    cursor.execute("""

        CREATE TABLE ClienteAniversariante (

            ClienteAniversarianteID INT IDENTITY PRIMARY KEY,

            ClienteID INT NOT NULL,

            Relacao NVARCHAR(80) NULL,

            Nome NVARCHAR(200)
                NOT NULL,

            DataNascimento DATE NULL,

            Ativo BIT
                NOT NULL DEFAULT 1,

            CriadoEm DATETIME
                NOT NULL DEFAULT GETDATE(),

            AtualizadoEm DATETIME NULL,

            FOREIGN KEY (ClienteID)
                REFERENCES Cliente(ClienteID)
        )

    """)

    cursor.execute("""

        CREATE INDEX IX_ClienteAniversariante_Cliente
            ON ClienteAniversariante(ClienteID, Nome)

    """)


def criar_tabela_figurino(cursor):

    if tabela_existe(
        cursor,
        "Figurino"
    ):
        return

    LOGGER.info(
        "Criando tabela Figurino"
    )

    cursor.execute("""

        CREATE TABLE Figurino (

            FigurinoID INT IDENTITY PRIMARY KEY,

            NomeLongo NVARCHAR(250)
                NOT NULL,

            NomeCurto NVARCHAR(120) NULL,

            DataAquisicao DATE NULL,

            SedeID INT NULL,

            Disponibilidade NVARCHAR(30)
                NOT NULL DEFAULT 'DISPONIVEL',

            DataUltimoUso DATE NULL,

            UltimoAtorID INT NULL,

            Observacoes NVARCHAR(MAX) NULL,

            Ativo BIT
                NOT NULL DEFAULT 1,

            CriadoEm DATETIME
                NOT NULL DEFAULT GETDATE(),

            AtualizadoEm DATETIME NULL,

            FOREIGN KEY (SedeID)
                REFERENCES SedesEmpresa(SedeID),

            FOREIGN KEY (UltimoAtorID)
                REFERENCES Ator(AtorID)
        )

    """)

    cursor.execute("""

        CREATE INDEX IX_Figurino_Sede
            ON Figurino(SedeID)

    """)

    cursor.execute("""

        CREATE INDEX IX_Figurino_Disponibilidade
            ON Figurino(Disponibilidade)

    """)


def criar_tabela_empresa(cursor):

    if tabela_existe(
        cursor,
        "Empresa"
    ):
        return

    LOGGER.info(
        "Criando tabela Empresa"
    )

    cursor.execute("""

        CREATE TABLE Empresa (

            EmpresaID INT IDENTITY PRIMARY KEY,

            RazaoSocial NVARCHAR(250)
                NOT NULL,

            NomeFantasia NVARCHAR(250) NULL,

            TipoPessoa NVARCHAR(20) NULL,

            Documento NVARCHAR(20) NULL,

            InscricaoEstadual NVARCHAR(50) NULL,

            InscricaoMunicipal NVARCHAR(50) NULL,

            Inscricao NVARCHAR(100) NULL,

            DataFundacao DATE NULL,

            AtividadeEconomica NVARCHAR(250) NULL,

            QuantidadeFuncionarios INT NULL,

            CNAE1 NVARCHAR(30) NULL,

            CNAE2 NVARCHAR(30) NULL,

            CNAE3 NVARCHAR(30) NULL,

            CEP NVARCHAR(20) NULL,

            Logradouro NVARCHAR(200) NULL,

            Numero NVARCHAR(30) NULL,

            Complemento NVARCHAR(100) NULL,

            Bairro NVARCHAR(100) NULL,

            Municipio NVARCHAR(100) NULL,

            UF NVARCHAR(2) NULL,

            Pais NVARCHAR(80)
                NOT NULL DEFAULT 'Brasil',

            Endereco NVARCHAR(700) NULL,

            Latitude DECIMAL(10, 7) NULL,

            Longitude DECIMAL(10, 7) NULL,

            FonteGeo NVARCHAR(50) NULL,

            DataGeo DATETIME NULL,

            Website NVARCHAR(250) NULL,

            Facebook NVARCHAR(250) NULL,

            Twitter NVARCHAR(250) NULL,

            Instagram NVARCHAR(250) NULL,

            Telefone1 NVARCHAR(30) NULL,

            Telefone2 NVARCHAR(30) NULL,

            Telefone3 NVARCHAR(30) NULL,

            Responsavel1Cargo NVARCHAR(120) NULL,
            Responsavel1Nome NVARCHAR(200) NULL,
            Responsavel1Nacionalidade NVARCHAR(50) NULL,
            Responsavel1EstadoCivil NVARCHAR(50) NULL,
            Responsavel1Comerciante BIT NULL,
            Responsavel1RG NVARCHAR(30) NULL,
            Responsavel1CPF NVARCHAR(20) NULL,
            Responsavel1DataNascimento DATE NULL,
            Responsavel1Telefone NVARCHAR(30) NULL,
            Responsavel1Email NVARCHAR(200) NULL,

            Responsavel2Cargo NVARCHAR(120) NULL,
            Responsavel2Nome NVARCHAR(200) NULL,
            Responsavel2Nacionalidade NVARCHAR(50) NULL,
            Responsavel2EstadoCivil NVARCHAR(50) NULL,
            Responsavel2Comerciante BIT NULL,
            Responsavel2RG NVARCHAR(30) NULL,
            Responsavel2CPF NVARCHAR(20) NULL,
            Responsavel2DataNascimento DATE NULL,
            Responsavel2Telefone NVARCHAR(30) NULL,
            Responsavel2Email NVARCHAR(200) NULL,

            Responsavel3Cargo NVARCHAR(120) NULL,
            Responsavel3Nome NVARCHAR(200) NULL,
            Responsavel3Nacionalidade NVARCHAR(50) NULL,
            Responsavel3EstadoCivil NVARCHAR(50) NULL,
            Responsavel3Comerciante BIT NULL,
            Responsavel3RG NVARCHAR(30) NULL,
            Responsavel3CPF NVARCHAR(20) NULL,
            Responsavel3DataNascimento DATE NULL,
            Responsavel3Telefone NVARCHAR(30) NULL,
            Responsavel3Email NVARCHAR(200) NULL,

            ContatoNome NVARCHAR(200) NULL,

            ContatoDepartamento NVARCHAR(120) NULL,

            ContatoCargo NVARCHAR(120) NULL,

            ContatoTelefoneFixo NVARCHAR(30) NULL,

            ContatoCelular NVARCHAR(30) NULL,

            ContatoEmail NVARCHAR(200) NULL,

            QuemIndicou NVARCHAR(200) NULL,

            PrimeiroCanalContato NVARCHAR(200) NULL,

            Observacoes NVARCHAR(MAX) NULL,

            Ativo BIT
                NOT NULL DEFAULT 1,

            DataInclusao DATETIME
                NOT NULL DEFAULT GETDATE(),

            AtualizadoEm DATETIME NULL
        )

    """)

    cursor.execute("""

        CREATE UNIQUE INDEX UX_Empresa_Documento
            ON Empresa(Documento)
            WHERE Documento IS NOT NULL
            AND Documento <> ''

    """)


# ==================================================
# EVOLUCAO SCHEMA
# ==================================================

def atualizar_tabela_system_migration(cursor):

    adicionar_colunas_se_faltarem(

        cursor,

        "SystemMigration",

        [

            (
                "MigrationKey",
                "ALTER TABLE SystemMigration "
                "ADD MigrationKey NVARCHAR(200) NULL"
            ),

            (
                "ExecutadoEm",
                "ALTER TABLE SystemMigration "
                "ADD ExecutadoEm DATETIME "
                "NOT NULL DEFAULT GETDATE()"
            ),
        ],
    )


def atualizar_tabela_perfis(cursor):

    adicionar_colunas_se_faltarem(

        cursor,

        "Perfis",

        [

            (
                "ValidadeSenhaDias",
                "ALTER TABLE Perfis "
                "ADD ValidadeSenhaDias INT NULL"
            ),

            (
                "Ativo",
                "ALTER TABLE Perfis "
                "ADD Ativo BIT "
                "NOT NULL DEFAULT 1"
            ),

            (
                "AdminLevel",
                "ALTER TABLE Perfis "
                "ADD AdminLevel INT "
                "NOT NULL DEFAULT 0"
            ),

            (
                "Sistema",
                "ALTER TABLE Perfis "
                "ADD Sistema BIT "
                "NOT NULL DEFAULT 0"
            ),
        ],
    )


def atualizar_schema_usuarios(cursor):

    adicionar_colunas_se_faltarem(

        cursor,

        "Usuarios",

        [

            (
                "Email",
                "ALTER TABLE Usuarios "
                "ADD Email NVARCHAR(200) NULL"
            ),

            (
                "Ativo",
                "ALTER TABLE Usuarios "
                "ADD Ativo BIT "
                "NOT NULL DEFAULT 1"
            ),

            (
                "Bloqueado",
                "ALTER TABLE Usuarios "
                "ADD Bloqueado BIT "
                "NOT NULL DEFAULT 0"
            ),

            (
                "TentativasLogin",
                "ALTER TABLE Usuarios "
                "ADD TentativasLogin INT "
                "NOT NULL DEFAULT 0"
            ),

            (
                "DeveTrocarSenha",
                "ALTER TABLE Usuarios "
                "ADD DeveTrocarSenha BIT "
                "NOT NULL DEFAULT 0"
            ),

            (
                "SenhaTemporaria",
                "ALTER TABLE Usuarios "
                "ADD SenhaTemporaria BIT "
                "NOT NULL DEFAULT 0"
            ),

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
            ),

            (
                "CriadoEm",
                "ALTER TABLE Usuarios "
                "ADD CriadoEm DATETIME "
                "NOT NULL DEFAULT GETDATE()"
            ),
        ],
    )


def atualizar_tabela_menu(cursor):

    adicionar_colunas_se_faltarem(

        cursor,

        "Menu",

        [

            (
                "Rota",
                "ALTER TABLE Menu "
                "ADD Rota NVARCHAR(100) NULL"
            ),

            (
                "TipoMenu",
                "ALTER TABLE Menu "
                "ADD TipoMenu CHAR(1) "
                "NOT NULL DEFAULT 'S'"
            ),

            (
                "MenuPaiId",
                "ALTER TABLE Menu "
                "ADD MenuPaiId INT NULL"
            ),

            (
                "Ordem",
                "ALTER TABLE Menu "
                "ADD Ordem INT "
                "NOT NULL DEFAULT 0"
            ),

            (
                "Nivel",
                "ALTER TABLE Menu "
                "ADD Nivel INT "
                "NOT NULL DEFAULT 1"
            ),

            (
                "Codigo",
                "ALTER TABLE Menu "
                "ADD Codigo NVARCHAR(50) NULL"
            ),

            (
                "Modulo",
                "ALTER TABLE Menu "
                "ADD Modulo NVARCHAR(50) NULL"
            ),

            (
                "Icone",
                "ALTER TABLE Menu "
                "ADD Icone NVARCHAR(50) NULL"
            ),

            (
                "AdminLevel",
                "ALTER TABLE Menu "
                "ADD AdminLevel INT "
                "NOT NULL DEFAULT 0"
            ),

            (
                "Ativo",
                "ALTER TABLE Menu "
                "ADD Ativo BIT "
                "NOT NULL DEFAULT 1"
            ),

            (
                "Sistema",
                "ALTER TABLE Menu "
                "ADD Sistema BIT "
                "NOT NULL DEFAULT 0"
            ),
        ],
    )


def atualizar_tabela_perfil_menu(cursor):

    adicionar_colunas_se_faltarem(

        cursor,

        "PerfilMenu",

        [

            (
                "PodeVer",
                "ALTER TABLE PerfilMenu "
                "ADD PodeVer BIT "
                "NOT NULL DEFAULT 1"
            ),

            (
                "PodeEditar",
                "ALTER TABLE PerfilMenu "
                "ADD PodeEditar BIT "
                "NOT NULL DEFAULT 0"
            ),

            (
                "PodeExcluir",
                "ALTER TABLE PerfilMenu "
                "ADD PodeExcluir BIT "
                "NOT NULL DEFAULT 0"
            ),
        ],
    )


def atualizar_tabela_auditoria(cursor):

    adicionar_colunas_se_faltarem(

        cursor,

        "Auditoria",

        [

            (
                "UsuarioId",
                "ALTER TABLE Auditoria "
                "ADD UsuarioId INT NULL"
            ),

            (
                "Login",
                "ALTER TABLE Auditoria "
                "ADD Login NVARCHAR(100) NULL"
            ),

            (
                "Acao",
                "ALTER TABLE Auditoria "
                "ADD Acao NVARCHAR(100) NULL"
            ),

            (
                "Entidade",
                "ALTER TABLE Auditoria "
                "ADD Entidade NVARCHAR(100) NULL"
            ),

            (
                "RegistroId",
                "ALTER TABLE Auditoria "
                "ADD RegistroId NVARCHAR(100) NULL"
            ),

            (
                "Detalhes",
                "ALTER TABLE Auditoria "
                "ADD Detalhes NVARCHAR(MAX) NULL"
            ),

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
            ),

            (
                "CriadoEm",
                "ALTER TABLE Auditoria "
                "ADD CriadoEm DATETIME "
                "NOT NULL DEFAULT GETDATE()"
            ),
        ],
    )


def atualizar_tabela_loc_tipo(cursor):

    adicionar_colunas_se_faltarem(

        cursor,

        "LocTipo",

        [

            (
                "NomeTipo",
                "ALTER TABLE LocTipo "
                "ADD NomeTipo NVARCHAR(100) NULL"
            ),

            (
                "Ativo",
                "ALTER TABLE LocTipo "
                "ADD Ativo BIT "
                "NOT NULL DEFAULT 1"
            ),
        ],
    )


def atualizar_tabela_loc_estrutura(cursor):

    adicionar_colunas_se_faltarem(

        cursor,

        "LocEstrutura",

        [

            (
                "NomeEstrutura",
                "ALTER TABLE LocEstrutura "
                "ADD NomeEstrutura NVARCHAR(100) NULL"
            ),

            (
                "Ativo",
                "ALTER TABLE LocEstrutura "
                "ADD Ativo BIT "
                "NOT NULL DEFAULT 1"
            ),
        ],
    )


def atualizar_tabela_local_evento(cursor):

    adicionar_colunas_se_faltarem(

        cursor,

        "LocalEvento",

        [

            (
                "NomeFantasia",
                "ALTER TABLE LocalEvento "
                "ADD NomeFantasia NVARCHAR(200) NULL"
            ),

            (
                "LocTipoID",
                "ALTER TABLE LocalEvento "
                "ADD LocTipoID INT NULL"
            ),

            (
                "CNPJ",
                "ALTER TABLE LocalEvento "
                "ADD CNPJ NVARCHAR(20) NULL"
            ),

            (
                "CEP",
                "ALTER TABLE LocalEvento "
                "ADD CEP NVARCHAR(20) NULL"
            ),

            (
                "Logradouro",
                "ALTER TABLE LocalEvento "
                "ADD Logradouro NVARCHAR(200) NULL"
            ),

            (
                "Numero",
                "ALTER TABLE LocalEvento "
                "ADD Numero NVARCHAR(30) NULL"
            ),

            (
                "Complemento",
                "ALTER TABLE LocalEvento "
                "ADD Complemento NVARCHAR(100) NULL"
            ),

            (
                "Bairro",
                "ALTER TABLE LocalEvento "
                "ADD Bairro NVARCHAR(100) NULL"
            ),

            (
                "Municipio",
                "ALTER TABLE LocalEvento "
                "ADD Municipio NVARCHAR(100) NULL"
            ),

            (
                "UF",
                "ALTER TABLE LocalEvento "
                "ADD UF NVARCHAR(2) NULL"
            ),

            (
                "Pais",
                "ALTER TABLE LocalEvento "
                "ADD Pais NVARCHAR(80) "
                "NOT NULL DEFAULT 'Brasil'"
            ),

            (
                "Endereco",
                "ALTER TABLE LocalEvento "
                "ADD Endereco NVARCHAR(700) NULL"
            ),

            (
                "Responsavel",
                "ALTER TABLE LocalEvento "
                "ADD Responsavel NVARCHAR(200) NULL"
            ),

            (
                "Contato",
                "ALTER TABLE LocalEvento "
                "ADD Contato NVARCHAR(100) NULL"
            ),

            (
                "Telefone",
                "ALTER TABLE LocalEvento "
                "ADD Telefone NVARCHAR(30) NULL"
            ),

            (
                "Celular",
                "ALTER TABLE LocalEvento "
                "ADD Celular NVARCHAR(30) NULL"
            ),

            (
                "Email",
                "ALTER TABLE LocalEvento "
                "ADD Email NVARCHAR(200) NULL"
            ),

            (
                "Site",
                "ALTER TABLE LocalEvento "
                "ADD Site NVARCHAR(250) NULL"
            ),

            (
                "Instagram",
                "ALTER TABLE LocalEvento "
                "ADD Instagram NVARCHAR(250) NULL"
            ),

            (
                "Facebook",
                "ALTER TABLE LocalEvento "
                "ADD Facebook NVARCHAR(250) NULL"
            ),

            (
                "OutrasRedes",
                "ALTER TABLE LocalEvento "
                "ADD OutrasRedes NVARCHAR(MAX) NULL"
            ),

            (
                "HorarioFuncionamento",
                "ALTER TABLE LocalEvento "
                "ADD HorarioFuncionamento NVARCHAR(MAX) NULL"
            ),

            (
                "Contato1Nome",
                "ALTER TABLE LocalEvento "
                "ADD Contato1Nome NVARCHAR(200) NULL"
            ),

            (
                "Contato1Telefone",
                "ALTER TABLE LocalEvento "
                "ADD Contato1Telefone NVARCHAR(30) NULL"
            ),

            (
                "Contato1Cargo",
                "ALTER TABLE LocalEvento "
                "ADD Contato1Cargo NVARCHAR(120) NULL"
            ),

            (
                "Contato2Nome",
                "ALTER TABLE LocalEvento "
                "ADD Contato2Nome NVARCHAR(200) NULL"
            ),

            (
                "Contato2Telefone",
                "ALTER TABLE LocalEvento "
                "ADD Contato2Telefone NVARCHAR(30) NULL"
            ),

            (
                "Contato2Cargo",
                "ALTER TABLE LocalEvento "
                "ADD Contato2Cargo NVARCHAR(120) NULL"
            ),

            (
                "Contato3Nome",
                "ALTER TABLE LocalEvento "
                "ADD Contato3Nome NVARCHAR(200) NULL"
            ),

            (
                "Contato3Telefone",
                "ALTER TABLE LocalEvento "
                "ADD Contato3Telefone NVARCHAR(30) NULL"
            ),

            (
                "Contato3Cargo",
                "ALTER TABLE LocalEvento "
                "ADD Contato3Cargo NVARCHAR(120) NULL"
            ),

            (
                "QuemIndicou",
                "ALTER TABLE LocalEvento "
                "ADD QuemIndicou NVARCHAR(200) NULL"
            ),

            (
                "Latitude",
                "ALTER TABLE LocalEvento "
                "ADD Latitude DECIMAL(10, 7) NULL"
            ),

            (
                "Longitude",
                "ALTER TABLE LocalEvento "
                "ADD Longitude DECIMAL(10, 7) NULL"
            ),

            (
                "FonteGeo",
                "ALTER TABLE LocalEvento "
                "ADD FonteGeo NVARCHAR(50) NULL"
            ),

            (
                "DataGeo",
                "ALTER TABLE LocalEvento "
                "ADD DataGeo DATETIME NULL"
            ),

            (
                "PossuiEstacionamento",
                "ALTER TABLE LocalEvento "
                "ADD PossuiEstacionamento BIT "
                "NOT NULL DEFAULT 0"
            ),

            (
                "Observacoes",
                "ALTER TABLE LocalEvento "
                "ADD Observacoes NVARCHAR(MAX) NULL"
            ),

            (
                "Ativo",
                "ALTER TABLE LocalEvento "
                "ADD Ativo BIT "
                "NOT NULL DEFAULT 1"
            ),

            (
                "CaptadoWeb",
                "ALTER TABLE LocalEvento "
                "ADD CaptadoWeb BIT "
                "NOT NULL DEFAULT 0"
            ),

            (
                "ComplementadoWeb",
                "ALTER TABLE LocalEvento "
                "ADD ComplementadoWeb BIT "
                "NOT NULL DEFAULT 0"
            ),

            (
                "CadastroValidado",
                "ALTER TABLE LocalEvento "
                "ADD CadastroValidado BIT "
                "NOT NULL DEFAULT 0"
            ),

            (
                "PesquisaIncompleta",
                "ALTER TABLE LocalEvento "
                "ADD PesquisaIncompleta BIT "
                "NOT NULL DEFAULT 0"
            ),

            (
                "NecessitaComplemento",
                "ALTER TABLE LocalEvento "
                "ADD NecessitaComplemento BIT "
                "NOT NULL DEFAULT 0"
            ),

            (
                "NecessitaRevisao",
                "ALTER TABLE LocalEvento "
                "ADD NecessitaRevisao BIT "
                "NOT NULL DEFAULT 0"
            ),

            (
                "PontuacaoOrigemWeb",
                "ALTER TABLE LocalEvento "
                "ADD PontuacaoOrigemWeb DECIMAL(5, 2) NULL"
            ),

            (
                "FonteOrigemWeb",
                "ALTER TABLE LocalEvento "
                "ADD FonteOrigemWeb NVARCHAR(100) NULL"
            ),

            (
                "DataOrigemWeb",
                "ALTER TABLE LocalEvento "
                "ADD DataOrigemWeb DATETIME NULL"
            ),

            (
                "LocalPesquisaWebId",
                "ALTER TABLE LocalEvento "
                "ADD LocalPesquisaWebId INT NULL"
            ),

            (
                "DataValidacaoCadastro",
                "ALTER TABLE LocalEvento "
                "ADD DataValidacaoCadastro DATETIME NULL"
            ),

            (
                "ObservacaoPesquisa",
                "ALTER TABLE LocalEvento "
                "ADD ObservacaoPesquisa NVARCHAR(MAX) NULL"
            ),

            (
                "CriadoEm",
                "ALTER TABLE LocalEvento "
                "ADD CriadoEm DATETIME "
                "NOT NULL DEFAULT GETDATE()"
            ),

            (
                "AtualizadoEm",
                "ALTER TABLE LocalEvento "
                "ADD AtualizadoEm DATETIME NULL"
            ),
        ],
    )


def atualizar_tabela_local_evento_pesquisa_web(cursor):

    adicionar_colunas_se_faltarem(

        cursor,

        "LocalEventoPesquisaWeb",

        [

            (
                "TipoLocalSugerido",
                "ALTER TABLE LocalEventoPesquisaWeb "
                "ADD TipoLocalSugerido NVARCHAR(100) NULL"
            ),

            (
                "NomeCasa",
                "ALTER TABLE LocalEventoPesquisaWeb "
                "ADD NomeCasa NVARCHAR(200) NULL"
            ),

            (
                "NomeFantasia",
                "ALTER TABLE LocalEventoPesquisaWeb "
                "ADD NomeFantasia NVARCHAR(200) NULL"
            ),

            (
                "DescricaoPublica",
                "ALTER TABLE LocalEventoPesquisaWeb "
                "ADD DescricaoPublica NVARCHAR(MAX) NULL"
            ),

            (
                "CNPJ",
                "ALTER TABLE LocalEventoPesquisaWeb "
                "ADD CNPJ NVARCHAR(20) NULL"
            ),

            (
                "CEP",
                "ALTER TABLE LocalEventoPesquisaWeb "
                "ADD CEP NVARCHAR(20) NULL"
            ),

            (
                "Logradouro",
                "ALTER TABLE LocalEventoPesquisaWeb "
                "ADD Logradouro NVARCHAR(200) NULL"
            ),

            (
                "Numero",
                "ALTER TABLE LocalEventoPesquisaWeb "
                "ADD Numero NVARCHAR(30) NULL"
            ),

            (
                "Complemento",
                "ALTER TABLE LocalEventoPesquisaWeb "
                "ADD Complemento NVARCHAR(100) NULL"
            ),

            (
                "Bairro",
                "ALTER TABLE LocalEventoPesquisaWeb "
                "ADD Bairro NVARCHAR(100) NULL"
            ),

            (
                "Municipio",
                "ALTER TABLE LocalEventoPesquisaWeb "
                "ADD Municipio NVARCHAR(100) NULL"
            ),

            (
                "UF",
                "ALTER TABLE LocalEventoPesquisaWeb "
                "ADD UF NVARCHAR(2) NULL"
            ),

            (
                "Pais",
                "ALTER TABLE LocalEventoPesquisaWeb "
                "ADD Pais NVARCHAR(80) "
                "NOT NULL DEFAULT 'Brasil'"
            ),

            (
                "Endereco",
                "ALTER TABLE LocalEventoPesquisaWeb "
                "ADD Endereco NVARCHAR(700) NULL"
            ),

            (
                "Latitude",
                "ALTER TABLE LocalEventoPesquisaWeb "
                "ADD Latitude DECIMAL(10, 7) NULL"
            ),

            (
                "Longitude",
                "ALTER TABLE LocalEventoPesquisaWeb "
                "ADD Longitude DECIMAL(10, 7) NULL"
            ),

            (
                "FonteGeo",
                "ALTER TABLE LocalEventoPesquisaWeb "
                "ADD FonteGeo NVARCHAR(50) NULL"
            ),

            (
                "DataGeo",
                "ALTER TABLE LocalEventoPesquisaWeb "
                "ADD DataGeo DATETIME NULL"
            ),

            (
                "Responsavel",
                "ALTER TABLE LocalEventoPesquisaWeb "
                "ADD Responsavel NVARCHAR(200) NULL"
            ),

            (
                "Contato",
                "ALTER TABLE LocalEventoPesquisaWeb "
                "ADD Contato NVARCHAR(100) NULL"
            ),

            (
                "Telefone",
                "ALTER TABLE LocalEventoPesquisaWeb "
                "ADD Telefone NVARCHAR(30) NULL"
            ),

            (
                "Celular",
                "ALTER TABLE LocalEventoPesquisaWeb "
                "ADD Celular NVARCHAR(30) NULL"
            ),

            (
                "WhatsApp",
                "ALTER TABLE LocalEventoPesquisaWeb "
                "ADD WhatsApp NVARCHAR(30) NULL"
            ),

            (
                "Email",
                "ALTER TABLE LocalEventoPesquisaWeb "
                "ADD Email NVARCHAR(200) NULL"
            ),

            (
                "Site",
                "ALTER TABLE LocalEventoPesquisaWeb "
                "ADD Site NVARCHAR(250) NULL"
            ),

            (
                "Instagram",
                "ALTER TABLE LocalEventoPesquisaWeb "
                "ADD Instagram NVARCHAR(250) NULL"
            ),

            (
                "Facebook",
                "ALTER TABLE LocalEventoPesquisaWeb "
                "ADD Facebook NVARCHAR(250) NULL"
            ),

            (
                "OutrasRedes",
                "ALTER TABLE LocalEventoPesquisaWeb "
                "ADD OutrasRedes NVARCHAR(MAX) NULL"
            ),

            (
                "HorarioFuncionamento",
                "ALTER TABLE LocalEventoPesquisaWeb "
                "ADD HorarioFuncionamento NVARCHAR(MAX) NULL"
            ),

            (
                "FontePrincipal",
                "ALTER TABLE LocalEventoPesquisaWeb "
                "ADD FontePrincipal NVARCHAR(100) NULL"
            ),

            (
                "UrlFonte",
                "ALTER TABLE LocalEventoPesquisaWeb "
                "ADD UrlFonte NVARCHAR(500) NULL"
            ),

            (
                "DadosBrutos",
                "ALTER TABLE LocalEventoPesquisaWeb "
                "ADD DadosBrutos NVARCHAR(MAX) NULL"
            ),

            (
                "PontuacaoConfiabilidade",
                "ALTER TABLE LocalEventoPesquisaWeb "
                "ADD PontuacaoConfiabilidade DECIMAL(5, 2) "
                "NOT NULL DEFAULT 0"
            ),

            (
                "StatusPesquisa",
                "ALTER TABLE LocalEventoPesquisaWeb "
                "ADD StatusPesquisa NVARCHAR(30) "
                "NOT NULL DEFAULT 'PENDENTE_ANALISE'"
            ),

            (
                "PossivelDuplicidade",
                "ALTER TABLE LocalEventoPesquisaWeb "
                "ADD PossivelDuplicidade BIT "
                "NOT NULL DEFAULT 0"
            ),

            (
                "LocalExistenteId",
                "ALTER TABLE LocalEventoPesquisaWeb "
                "ADD LocalExistenteId INT NULL"
            ),

            (
                "Transferido",
                "ALTER TABLE LocalEventoPesquisaWeb "
                "ADD Transferido BIT "
                "NOT NULL DEFAULT 0"
            ),

            (
                "DataTransferencia",
                "ALTER TABLE LocalEventoPesquisaWeb "
                "ADD DataTransferencia DATETIME NULL"
            ),

            (
                "UsuarioTransferenciaId",
                "ALTER TABLE LocalEventoPesquisaWeb "
                "ADD UsuarioTransferenciaId INT NULL"
            ),

            (
                "Descartado",
                "ALTER TABLE LocalEventoPesquisaWeb "
                "ADD Descartado BIT "
                "NOT NULL DEFAULT 0"
            ),

            (
                "DataDescarte",
                "ALTER TABLE LocalEventoPesquisaWeb "
                "ADD DataDescarte DATETIME NULL"
            ),

            (
                "UsuarioDescarteId",
                "ALTER TABLE LocalEventoPesquisaWeb "
                "ADD UsuarioDescarteId INT NULL"
            ),

            (
                "MotivoDescarte",
                "ALTER TABLE LocalEventoPesquisaWeb "
                "ADD MotivoDescarte NVARCHAR(MAX) NULL"
            ),

            (
                "NecessitaComplemento",
                "ALTER TABLE LocalEventoPesquisaWeb "
                "ADD NecessitaComplemento BIT "
                "NOT NULL DEFAULT 1"
            ),

            (
                "NecessitaRevisao",
                "ALTER TABLE LocalEventoPesquisaWeb "
                "ADD NecessitaRevisao BIT "
                "NOT NULL DEFAULT 1"
            ),

            (
                "DataPesquisa",
                "ALTER TABLE LocalEventoPesquisaWeb "
                "ADD DataPesquisa DATETIME "
                "NOT NULL DEFAULT GETDATE()"
            ),

            (
                "DataUltimaAtualizacao",
                "ALTER TABLE LocalEventoPesquisaWeb "
                "ADD DataUltimaAtualizacao DATETIME NULL"
            ),

            (
                "ObservacaoPesquisa",
                "ALTER TABLE LocalEventoPesquisaWeb "
                "ADD ObservacaoPesquisa NVARCHAR(MAX) NULL"
            ),
        ],
    )


def atualizar_tabela_loc_ambientes(cursor):

    adicionar_colunas_se_faltarem(

        cursor,

        "LocAmbientes",

        [

            (
                "LocalEventoID",
                "ALTER TABLE LocAmbientes "
                "ADD LocalEventoID INT NULL"
            ),

            (
                "NomeAmbiente",
                "ALTER TABLE LocAmbientes "
                "ADD NomeAmbiente NVARCHAR(150) NULL"
            ),

            (
                "TipoEspaco",
                "ALTER TABLE LocAmbientes "
                "ADD TipoEspaco NVARCHAR(20) NULL"
            ),

            (
                "CapacidadeSentado",
                "ALTER TABLE LocAmbientes "
                "ADD CapacidadeSentado INT "
                "NOT NULL DEFAULT 0"
            ),

            (
                "CapacidadePe",
                "ALTER TABLE LocAmbientes "
                "ADD CapacidadePe INT "
                "NOT NULL DEFAULT 0"
            ),

            (
                "Metragem",
                "ALTER TABLE LocAmbientes "
                "ADD Metragem DECIMAL(12, 2) "
                "NOT NULL DEFAULT 0"
            ),

            (
                "DimensaoComprimento",
                "ALTER TABLE LocAmbientes "
                "ADD DimensaoComprimento DECIMAL(12, 2) "
                "NOT NULL DEFAULT 0"
            ),

            (
                "DimensaoLargura",
                "ALTER TABLE LocAmbientes "
                "ADD DimensaoLargura DECIMAL(12, 2) "
                "NOT NULL DEFAULT 0"
            ),

            (
                "PeDireito",
                "ALTER TABLE LocAmbientes "
                "ADD PeDireito DECIMAL(12, 2) "
                "NOT NULL DEFAULT 0"
            ),

            (
                "ServicosOferecidos",
                "ALTER TABLE LocAmbientes "
                "ADD ServicosOferecidos NVARCHAR(MAX) NULL"
            ),

            (
                "ArCondicionado",
                "ALTER TABLE LocAmbientes "
                "ADD ArCondicionado BIT "
                "NOT NULL DEFAULT 0"
            ),

            (
                "PrecoBase",
                "ALTER TABLE LocAmbientes "
                "ADD PrecoBase DECIMAL(18, 2) "
                "NOT NULL DEFAULT 0"
            ),

            (
                "SharePointID",
                "ALTER TABLE LocAmbientes "
                "ADD SharePointID NVARCHAR(100) NULL"
            ),

            (
                "Ativo",
                "ALTER TABLE LocAmbientes "
                "ADD Ativo BIT "
                "NOT NULL DEFAULT 1"
            ),
        ],
    )


def atualizar_tabela_sedes_empresa(cursor):

    adicionar_colunas_se_faltarem(

        cursor,

        "SedesEmpresa",

        [

            (
                "NomeSede",
                "ALTER TABLE SedesEmpresa "
                "ADD NomeSede NVARCHAR(150) NULL"
            ),

            (
                "CNPJ",
                "ALTER TABLE SedesEmpresa "
                "ADD CNPJ NVARCHAR(20) NULL"
            ),

            (
                "Responsavel",
                "ALTER TABLE SedesEmpresa "
                "ADD Responsavel NVARCHAR(200) NULL"
            ),

            (
                "Telefone",
                "ALTER TABLE SedesEmpresa "
                "ADD Telefone NVARCHAR(30) NULL"
            ),

            (
                "Celular",
                "ALTER TABLE SedesEmpresa "
                "ADD Celular NVARCHAR(30) NULL"
            ),

            (
                "Email",
                "ALTER TABLE SedesEmpresa "
                "ADD Email NVARCHAR(200) NULL"
            ),

            (
                "CEP",
                "ALTER TABLE SedesEmpresa "
                "ADD CEP NVARCHAR(20) NULL"
            ),

            (
                "Logradouro",
                "ALTER TABLE SedesEmpresa "
                "ADD Logradouro NVARCHAR(200) NULL"
            ),

            (
                "Numero",
                "ALTER TABLE SedesEmpresa "
                "ADD Numero NVARCHAR(30) NULL"
            ),

            (
                "Complemento",
                "ALTER TABLE SedesEmpresa "
                "ADD Complemento NVARCHAR(100) NULL"
            ),

            (
                "Bairro",
                "ALTER TABLE SedesEmpresa "
                "ADD Bairro NVARCHAR(100) NULL"
            ),

            (
                "Municipio",
                "ALTER TABLE SedesEmpresa "
                "ADD Municipio NVARCHAR(100) NULL"
            ),

            (
                "UF",
                "ALTER TABLE SedesEmpresa "
                "ADD UF NVARCHAR(2) NULL"
            ),

            (
                "Pais",
                "ALTER TABLE SedesEmpresa "
                "ADD Pais NVARCHAR(80) "
                "NOT NULL DEFAULT 'Brasil'"
            ),

            (
                "Endereco",
                "ALTER TABLE SedesEmpresa "
                "ADD Endereco NVARCHAR(700) NULL"
            ),

            (
                "Latitude",
                "ALTER TABLE SedesEmpresa "
                "ADD Latitude DECIMAL(10, 7) NULL"
            ),

            (
                "Longitude",
                "ALTER TABLE SedesEmpresa "
                "ADD Longitude DECIMAL(10, 7) NULL"
            ),

            (
                "FonteGeo",
                "ALTER TABLE SedesEmpresa "
                "ADD FonteGeo NVARCHAR(50) NULL"
            ),

            (
                "DataGeo",
                "ALTER TABLE SedesEmpresa "
                "ADD DataGeo DATETIME NULL"
            ),

            (
                "Operacional",
                "ALTER TABLE SedesEmpresa "
                "ADD Operacional BIT "
                "NOT NULL DEFAULT 1"
            ),

            (
                "Fantasma",
                "ALTER TABLE SedesEmpresa "
                "ADD Fantasma BIT "
                "NOT NULL DEFAULT 0"
            ),

            (
                "Observacoes",
                "ALTER TABLE SedesEmpresa "
                "ADD Observacoes NVARCHAR(MAX) NULL"
            ),

            (
                "Ativo",
                "ALTER TABLE SedesEmpresa "
                "ADD Ativo BIT "
                "NOT NULL DEFAULT 1"
            ),

            (
                "CriadoEm",
                "ALTER TABLE SedesEmpresa "
                "ADD CriadoEm DATETIME "
                "NOT NULL DEFAULT GETDATE()"
            ),

            (
                "AtualizadoEm",
                "ALTER TABLE SedesEmpresa "
                "ADD AtualizadoEm DATETIME NULL"
            ),
        ],
    )


def atualizar_tabela_cep_cache(cursor):

    adicionar_colunas_se_faltarem(

        cursor,

        "CepCache",

        [

            (
                "CEP",
                "ALTER TABLE CepCache "
                "ADD CEP NVARCHAR(20) NULL"
            ),

            (
                "Logradouro",
                "ALTER TABLE CepCache "
                "ADD Logradouro NVARCHAR(200) NULL"
            ),

            (
                "Bairro",
                "ALTER TABLE CepCache "
                "ADD Bairro NVARCHAR(100) NULL"
            ),

            (
                "Municipio",
                "ALTER TABLE CepCache "
                "ADD Municipio NVARCHAR(100) NULL"
            ),

            (
                "UF",
                "ALTER TABLE CepCache "
                "ADD UF NVARCHAR(2) NULL"
            ),

            (
                "Pais",
                "ALTER TABLE CepCache "
                "ADD Pais NVARCHAR(80) "
                "NOT NULL DEFAULT 'Brasil'"
            ),

            (
                "Fonte",
                "ALTER TABLE CepCache "
                "ADD Fonte NVARCHAR(50) NULL"
            ),

            (
                "DadosJson",
                "ALTER TABLE CepCache "
                "ADD DadosJson NVARCHAR(MAX) NULL"
            ),

            (
                "ConsultadoEm",
                "ALTER TABLE CepCache "
                "ADD ConsultadoEm DATETIME "
                "NOT NULL DEFAULT GETDATE()"
            ),
        ],
    )


def atualizar_tabela_ator(cursor):

    adicionar_colunas_se_faltarem(

        cursor,

        "Ator",

        [

            (
                "Nome",
                "ALTER TABLE Ator "
                "ADD Nome NVARCHAR(200) NULL"
            ),

            (
                "NomeProfissional",
                "ALTER TABLE Ator "
                "ADD NomeProfissional NVARCHAR(200) NULL"
            ),

            (
                "CEP",
                "ALTER TABLE Ator "
                "ADD CEP NVARCHAR(20) NULL"
            ),

            (
                "Logradouro",
                "ALTER TABLE Ator "
                "ADD Logradouro NVARCHAR(200) NULL"
            ),

            (
                "Numero",
                "ALTER TABLE Ator "
                "ADD Numero NVARCHAR(30) NULL"
            ),

            (
                "Complemento",
                "ALTER TABLE Ator "
                "ADD Complemento NVARCHAR(100) NULL"
            ),

            (
                "Bairro",
                "ALTER TABLE Ator "
                "ADD Bairro NVARCHAR(100) NULL"
            ),

            (
                "Municipio",
                "ALTER TABLE Ator "
                "ADD Municipio NVARCHAR(100) NULL"
            ),

            (
                "UF",
                "ALTER TABLE Ator "
                "ADD UF NVARCHAR(2) NULL"
            ),

            (
                "Pais",
                "ALTER TABLE Ator "
                "ADD Pais NVARCHAR(80) "
                "NOT NULL DEFAULT 'Brasil'"
            ),

            (
                "Endereco",
                "ALTER TABLE Ator "
                "ADD Endereco NVARCHAR(700) NULL"
            ),

            (
                "Latitude",
                "ALTER TABLE Ator "
                "ADD Latitude DECIMAL(10, 7) NULL"
            ),

            (
                "Longitude",
                "ALTER TABLE Ator "
                "ADD Longitude DECIMAL(10, 7) NULL"
            ),

            (
                "FonteGeo",
                "ALTER TABLE Ator "
                "ADD FonteGeo NVARCHAR(50) NULL"
            ),

            (
                "DataGeo",
                "ALTER TABLE Ator "
                "ADD DataGeo DATETIME NULL"
            ),

            (
                "Nacionalidade",
                "ALTER TABLE Ator "
                "ADD Nacionalidade NVARCHAR(20) NULL"
            ),

            (
                "Telefone",
                "ALTER TABLE Ator "
                "ADD Telefone NVARCHAR(30) NULL"
            ),

            (
                "Celular",
                "ALTER TABLE Ator "
                "ADD Celular NVARCHAR(30) NULL"
            ),

            (
                "DataNascimento",
                "ALTER TABLE Ator "
                "ADD DataNascimento DATE NULL"
            ),

            (
                "CPF",
                "ALTER TABLE Ator "
                "ADD CPF NVARCHAR(20) NULL"
            ),

            (
                "RG",
                "ALTER TABLE Ator "
                "ADD RG NVARCHAR(30) NULL"
            ),

            (
                "Email",
                "ALTER TABLE Ator "
                "ADD Email NVARCHAR(200) NULL"
            ),

            (
                "Ensino",
                "ALTER TABLE Ator "
                "ADD Ensino NVARCHAR(30) NULL"
            ),

            (
                "Sexo",
                "ALTER TABLE Ator "
                "ADD Sexo NVARCHAR(20) NULL"
            ),

            (
                "Ativo",
                "ALTER TABLE Ator "
                "ADD Ativo BIT "
                "NOT NULL DEFAULT 1"
            ),

            (
                "CriadoEm",
                "ALTER TABLE Ator "
                "ADD CriadoEm DATETIME "
                "NOT NULL DEFAULT GETDATE()"
            ),

            (
                "AtualizadoEm",
                "ALTER TABLE Ator "
                "ADD AtualizadoEm DATETIME NULL"
            ),
        ],
    )


def atualizar_tabela_cliente(cursor):

    adicionar_colunas_se_faltarem(

        cursor,

        "Cliente",

        [

            (
                "Nome",
                "ALTER TABLE Cliente "
                "ADD Nome NVARCHAR(200) NULL"
            ),

            (
                "Municipio",
                "ALTER TABLE Cliente "
                "ADD Municipio NVARCHAR(100) NULL"
            ),

            (
                "UF",
                "ALTER TABLE Cliente "
                "ADD UF NVARCHAR(2) NULL"
            ),

            (
                "Pais",
                "ALTER TABLE Cliente "
                "ADD Pais NVARCHAR(80) "
                "NOT NULL DEFAULT 'Brasil'"
            ),

            (
                "Celular",
                "ALTER TABLE Cliente "
                "ADD Celular NVARCHAR(30) NULL"
            ),

            (
                "DataNascimento",
                "ALTER TABLE Cliente "
                "ADD DataNascimento DATE NULL"
            ),

            (
                "CPF",
                "ALTER TABLE Cliente "
                "ADD CPF NVARCHAR(20) NULL"
            ),

            (
                "Email",
                "ALTER TABLE Cliente "
                "ADD Email NVARCHAR(200) NULL"
            ),

            (
                "Sexo",
                "ALTER TABLE Cliente "
                "ADD Sexo NVARCHAR(20) NULL"
            ),

            (
                "ReceberResumoProgramacao",
                "ALTER TABLE Cliente "
                "ADD ReceberResumoProgramacao NVARCHAR(20) NULL"
            ),

            (
                "Profissao",
                "ALTER TABLE Cliente "
                "ADD Profissao NVARCHAR(150) NULL"
            ),

            (
                "Observacoes",
                "ALTER TABLE Cliente "
                "ADD Observacoes NVARCHAR(MAX) NULL"
            ),

            (
                "PrimeiroCanalContato",
                "ALTER TABLE Cliente "
                "ADD PrimeiroCanalContato NVARCHAR(150) NULL"
            ),

            (
                "Ativo",
                "ALTER TABLE Cliente "
                "ADD Ativo BIT "
                "NOT NULL DEFAULT 1"
            ),

            (
                "DataInclusao",
                "ALTER TABLE Cliente "
                "ADD DataInclusao DATETIME "
                "NOT NULL DEFAULT GETDATE()"
            ),

            (
                "AtualizadoEm",
                "ALTER TABLE Cliente "
                "ADD AtualizadoEm DATETIME NULL"
            ),
        ],
    )


def atualizar_tabela_cliente_aniversariante(cursor):

    adicionar_colunas_se_faltarem(

        cursor,

        "ClienteAniversariante",

        [

            (
                "ClienteID",
                "ALTER TABLE ClienteAniversariante "
                "ADD ClienteID INT NULL"
            ),

            (
                "Relacao",
                "ALTER TABLE ClienteAniversariante "
                "ADD Relacao NVARCHAR(80) NULL"
            ),

            (
                "Nome",
                "ALTER TABLE ClienteAniversariante "
                "ADD Nome NVARCHAR(200) NULL"
            ),

            (
                "DataNascimento",
                "ALTER TABLE ClienteAniversariante "
                "ADD DataNascimento DATE NULL"
            ),

            (
                "Ativo",
                "ALTER TABLE ClienteAniversariante "
                "ADD Ativo BIT "
                "NOT NULL DEFAULT 1"
            ),

            (
                "CriadoEm",
                "ALTER TABLE ClienteAniversariante "
                "ADD CriadoEm DATETIME "
                "NOT NULL DEFAULT GETDATE()"
            ),

            (
                "AtualizadoEm",
                "ALTER TABLE ClienteAniversariante "
                "ADD AtualizadoEm DATETIME NULL"
            ),
        ],
    )


def atualizar_tabela_figurino(cursor):

    adicionar_colunas_se_faltarem(

        cursor,

        "Figurino",

        [

            (
                "NomeLongo",
                "ALTER TABLE Figurino "
                "ADD NomeLongo NVARCHAR(250) NULL"
            ),

            (
                "NomeCurto",
                "ALTER TABLE Figurino "
                "ADD NomeCurto NVARCHAR(120) NULL"
            ),

            (
                "DataAquisicao",
                "ALTER TABLE Figurino "
                "ADD DataAquisicao DATE NULL"
            ),

            (
                "SedeID",
                "ALTER TABLE Figurino "
                "ADD SedeID INT NULL"
            ),

            (
                "Disponibilidade",
                "ALTER TABLE Figurino "
                "ADD Disponibilidade NVARCHAR(30) "
                "NOT NULL DEFAULT 'DISPONIVEL'"
            ),

            (
                "DataUltimoUso",
                "ALTER TABLE Figurino "
                "ADD DataUltimoUso DATE NULL"
            ),

            (
                "UltimoAtorID",
                "ALTER TABLE Figurino "
                "ADD UltimoAtorID INT NULL"
            ),

            (
                "Observacoes",
                "ALTER TABLE Figurino "
                "ADD Observacoes NVARCHAR(MAX) NULL"
            ),

            (
                "Ativo",
                "ALTER TABLE Figurino "
                "ADD Ativo BIT "
                "NOT NULL DEFAULT 1"
            ),

            (
                "CriadoEm",
                "ALTER TABLE Figurino "
                "ADD CriadoEm DATETIME "
                "NOT NULL DEFAULT GETDATE()"
            ),

            (
                "AtualizadoEm",
                "ALTER TABLE Figurino "
                "ADD AtualizadoEm DATETIME NULL"
            ),
        ],
    )


def atualizar_tabela_empresa(cursor):

    adicionar_colunas_se_faltarem(

        cursor,

        "Empresa",

        [
            ("RazaoSocial", "ALTER TABLE Empresa ADD RazaoSocial NVARCHAR(250) NULL"),
            ("NomeFantasia", "ALTER TABLE Empresa ADD NomeFantasia NVARCHAR(250) NULL"),
            ("TipoPessoa", "ALTER TABLE Empresa ADD TipoPessoa NVARCHAR(20) NULL"),
            ("Documento", "ALTER TABLE Empresa ADD Documento NVARCHAR(20) NULL"),
            ("InscricaoEstadual", "ALTER TABLE Empresa ADD InscricaoEstadual NVARCHAR(50) NULL"),
            ("InscricaoMunicipal", "ALTER TABLE Empresa ADD InscricaoMunicipal NVARCHAR(50) NULL"),
            ("Inscricao", "ALTER TABLE Empresa ADD Inscricao NVARCHAR(100) NULL"),
            ("DataFundacao", "ALTER TABLE Empresa ADD DataFundacao DATE NULL"),
            ("AtividadeEconomica", "ALTER TABLE Empresa ADD AtividadeEconomica NVARCHAR(250) NULL"),
            ("QuantidadeFuncionarios", "ALTER TABLE Empresa ADD QuantidadeFuncionarios INT NULL"),
            ("CNAE1", "ALTER TABLE Empresa ADD CNAE1 NVARCHAR(30) NULL"),
            ("CNAE2", "ALTER TABLE Empresa ADD CNAE2 NVARCHAR(30) NULL"),
            ("CNAE3", "ALTER TABLE Empresa ADD CNAE3 NVARCHAR(30) NULL"),
            ("CEP", "ALTER TABLE Empresa ADD CEP NVARCHAR(20) NULL"),
            ("Logradouro", "ALTER TABLE Empresa ADD Logradouro NVARCHAR(200) NULL"),
            ("Numero", "ALTER TABLE Empresa ADD Numero NVARCHAR(30) NULL"),
            ("Complemento", "ALTER TABLE Empresa ADD Complemento NVARCHAR(100) NULL"),
            ("Bairro", "ALTER TABLE Empresa ADD Bairro NVARCHAR(100) NULL"),
            ("Municipio", "ALTER TABLE Empresa ADD Municipio NVARCHAR(100) NULL"),
            ("UF", "ALTER TABLE Empresa ADD UF NVARCHAR(2) NULL"),
            ("Pais", "ALTER TABLE Empresa ADD Pais NVARCHAR(80) NOT NULL DEFAULT 'Brasil'"),
            ("Endereco", "ALTER TABLE Empresa ADD Endereco NVARCHAR(700) NULL"),
            ("Latitude", "ALTER TABLE Empresa ADD Latitude DECIMAL(10, 7) NULL"),
            ("Longitude", "ALTER TABLE Empresa ADD Longitude DECIMAL(10, 7) NULL"),
            ("FonteGeo", "ALTER TABLE Empresa ADD FonteGeo NVARCHAR(50) NULL"),
            ("DataGeo", "ALTER TABLE Empresa ADD DataGeo DATETIME NULL"),
            ("Website", "ALTER TABLE Empresa ADD Website NVARCHAR(250) NULL"),
            ("Facebook", "ALTER TABLE Empresa ADD Facebook NVARCHAR(250) NULL"),
            ("Twitter", "ALTER TABLE Empresa ADD Twitter NVARCHAR(250) NULL"),
            ("Instagram", "ALTER TABLE Empresa ADD Instagram NVARCHAR(250) NULL"),
            ("Telefone1", "ALTER TABLE Empresa ADD Telefone1 NVARCHAR(30) NULL"),
            ("Telefone2", "ALTER TABLE Empresa ADD Telefone2 NVARCHAR(30) NULL"),
            ("Telefone3", "ALTER TABLE Empresa ADD Telefone3 NVARCHAR(30) NULL"),
            ("Responsavel1Cargo", "ALTER TABLE Empresa ADD Responsavel1Cargo NVARCHAR(120) NULL"),
            ("Responsavel1Nome", "ALTER TABLE Empresa ADD Responsavel1Nome NVARCHAR(200) NULL"),
            ("Responsavel1Nacionalidade", "ALTER TABLE Empresa ADD Responsavel1Nacionalidade NVARCHAR(50) NULL"),
            ("Responsavel1EstadoCivil", "ALTER TABLE Empresa ADD Responsavel1EstadoCivil NVARCHAR(50) NULL"),
            ("Responsavel1Comerciante", "ALTER TABLE Empresa ADD Responsavel1Comerciante BIT NULL"),
            ("Responsavel1RG", "ALTER TABLE Empresa ADD Responsavel1RG NVARCHAR(30) NULL"),
            ("Responsavel1CPF", "ALTER TABLE Empresa ADD Responsavel1CPF NVARCHAR(20) NULL"),
            ("Responsavel1DataNascimento", "ALTER TABLE Empresa ADD Responsavel1DataNascimento DATE NULL"),
            ("Responsavel1Telefone", "ALTER TABLE Empresa ADD Responsavel1Telefone NVARCHAR(30) NULL"),
            ("Responsavel1Email", "ALTER TABLE Empresa ADD Responsavel1Email NVARCHAR(200) NULL"),
            ("Responsavel2Cargo", "ALTER TABLE Empresa ADD Responsavel2Cargo NVARCHAR(120) NULL"),
            ("Responsavel2Nome", "ALTER TABLE Empresa ADD Responsavel2Nome NVARCHAR(200) NULL"),
            ("Responsavel2Nacionalidade", "ALTER TABLE Empresa ADD Responsavel2Nacionalidade NVARCHAR(50) NULL"),
            ("Responsavel2EstadoCivil", "ALTER TABLE Empresa ADD Responsavel2EstadoCivil NVARCHAR(50) NULL"),
            ("Responsavel2Comerciante", "ALTER TABLE Empresa ADD Responsavel2Comerciante BIT NULL"),
            ("Responsavel2RG", "ALTER TABLE Empresa ADD Responsavel2RG NVARCHAR(30) NULL"),
            ("Responsavel2CPF", "ALTER TABLE Empresa ADD Responsavel2CPF NVARCHAR(20) NULL"),
            ("Responsavel2DataNascimento", "ALTER TABLE Empresa ADD Responsavel2DataNascimento DATE NULL"),
            ("Responsavel2Telefone", "ALTER TABLE Empresa ADD Responsavel2Telefone NVARCHAR(30) NULL"),
            ("Responsavel2Email", "ALTER TABLE Empresa ADD Responsavel2Email NVARCHAR(200) NULL"),
            ("Responsavel3Cargo", "ALTER TABLE Empresa ADD Responsavel3Cargo NVARCHAR(120) NULL"),
            ("Responsavel3Nome", "ALTER TABLE Empresa ADD Responsavel3Nome NVARCHAR(200) NULL"),
            ("Responsavel3Nacionalidade", "ALTER TABLE Empresa ADD Responsavel3Nacionalidade NVARCHAR(50) NULL"),
            ("Responsavel3EstadoCivil", "ALTER TABLE Empresa ADD Responsavel3EstadoCivil NVARCHAR(50) NULL"),
            ("Responsavel3Comerciante", "ALTER TABLE Empresa ADD Responsavel3Comerciante BIT NULL"),
            ("Responsavel3RG", "ALTER TABLE Empresa ADD Responsavel3RG NVARCHAR(30) NULL"),
            ("Responsavel3CPF", "ALTER TABLE Empresa ADD Responsavel3CPF NVARCHAR(20) NULL"),
            ("Responsavel3DataNascimento", "ALTER TABLE Empresa ADD Responsavel3DataNascimento DATE NULL"),
            ("Responsavel3Telefone", "ALTER TABLE Empresa ADD Responsavel3Telefone NVARCHAR(30) NULL"),
            ("Responsavel3Email", "ALTER TABLE Empresa ADD Responsavel3Email NVARCHAR(200) NULL"),
            ("ContatoNome", "ALTER TABLE Empresa ADD ContatoNome NVARCHAR(200) NULL"),
            ("ContatoDepartamento", "ALTER TABLE Empresa ADD ContatoDepartamento NVARCHAR(120) NULL"),
            ("ContatoCargo", "ALTER TABLE Empresa ADD ContatoCargo NVARCHAR(120) NULL"),
            ("ContatoTelefoneFixo", "ALTER TABLE Empresa ADD ContatoTelefoneFixo NVARCHAR(30) NULL"),
            ("ContatoCelular", "ALTER TABLE Empresa ADD ContatoCelular NVARCHAR(30) NULL"),
            ("ContatoEmail", "ALTER TABLE Empresa ADD ContatoEmail NVARCHAR(200) NULL"),
            ("QuemIndicou", "ALTER TABLE Empresa ADD QuemIndicou NVARCHAR(200) NULL"),
            ("PrimeiroCanalContato", "ALTER TABLE Empresa ADD PrimeiroCanalContato NVARCHAR(200) NULL"),
            ("Observacoes", "ALTER TABLE Empresa ADD Observacoes NVARCHAR(MAX) NULL"),
            ("Ativo", "ALTER TABLE Empresa ADD Ativo BIT NOT NULL DEFAULT 1"),
            ("DataInclusao", "ALTER TABLE Empresa ADD DataInclusao DATETIME NOT NULL DEFAULT GETDATE()"),
            ("AtualizadoEm", "ALTER TABLE Empresa ADD AtualizadoEm DATETIME NULL"),
        ],
    )


# ==================================================
# DADOS INICIAIS
# ==================================================
#
# Regra de implantação:
# Toda tela de atualização/cadastro deve ter sua
# tabela garantida nesta rotina de instalação. Quando
# a rotina depender de registros-base para funcionar
# (perfil, menu, domínio, sede, tipo, estrutura etc.),
# esses registros devem entrar no initial_data.json,
# e não ficar espalhados na tela ou no service.

def valor_bool(
    valor,
    default=False,
):

    if valor is None:
        return default

    if isinstance(valor, bool):
        return valor

    return str(valor).strip().lower() in (
        "1",
        "true",
        "yes",
        "sim",
        "on",
    )


def resolver_arquivo_dados_iniciais():

    caminho = Path(
        INITIAL_DATA_FILE
    )

    candidatos = []

    if caminho.is_absolute():
        candidatos.append(
            caminho
        )

    else:

        candidatos.extend([
            Path.cwd() / caminho,
            Path(__file__).resolve().parents[2] / caminho,
            Path(__file__).resolve().parents[1] / caminho,
        ])

    for candidato in candidatos:

        if candidato.exists():
            return candidato

    return candidatos[0] if candidatos else caminho


def resolver_arquivo_config(caminho_config):

    caminho = Path(
        caminho_config
    )

    candidatos = []

    if caminho.is_absolute():
        candidatos.append(
            caminho
        )

    else:

        candidatos.extend([
            Path.cwd() / caminho,
            Path(__file__).resolve().parents[2] / caminho,
            Path(__file__).resolve().parents[1] / caminho,
        ])

    for candidato in candidatos:

        if candidato.exists():
            return candidato

    return candidatos[0] if candidatos else caminho


def carregar_dados_iniciais():

    caminho = resolver_arquivo_dados_iniciais()

    if not caminho.exists():

        LOGGER.info(
            "Arquivo de dados iniciais não encontrado: %s",
            caminho,
        )

        return None

    try:

        with caminho.open(
            "r",
            encoding="utf-8",
        ) as arquivo:

            dados = json.load(
                arquivo
            )

        LOGGER.info(
            "Dados iniciais carregados: %s",
            caminho,
        )

        return dados

    except Exception:

        LOGGER.exception(
            "Erro lendo dados iniciais: %s",
            caminho,
        )

        return None


def carregar_tipos_local_configurados():

    caminho = resolver_arquivo_config(
        LOC_TIPOS_FILE
    )

    if not caminho.exists():

        LOGGER.info(
            "Arquivo de tipos de local não encontrado: %s",
            caminho,
        )

        return []

    try:

        with caminho.open(
            "r",
            encoding="utf-8",
        ) as arquivo:

            dados = json.load(
                arquivo
            )

        tipos = (
            dados.get("tipos", [])
            if isinstance(dados, dict)
            else dados
        )

        retorno = []

        for tipo in tipos:

            if isinstance(tipo, dict):
                nome = tipo.get("nome")
            else:
                nome = tipo

            nome = str(nome or "").strip()

            if nome:
                retorno.append(nome)

        LOGGER.info(
            "Tipos de local carregados: %s",
            caminho,
        )

        return retorno

    except Exception:

        LOGGER.exception(
            "Erro lendo tipos de local: %s",
            caminho,
        )

        return []


def obter_valor_env_ou_config(
    item,
    chave,
    default=None,
):

    chave_env = item.get(
        f"{chave}_env"
    )

    if chave_env:
        return os.getenv(
            chave_env,
            item.get(
                chave,
                default,
            )
        )

    return item.get(
        chave,
        default,
    )

def inserir_perfil_default(
    cursor,
    nome,
    admin_level,
    sistema,
    validade=90,
):

    perfil_id = buscar_id(
        cursor,
        "Perfis",
        "Id",
        "Nome",
        nome,
    )

    if perfil_id:

        cursor.execute("""

            UPDATE Perfis

            SET
                AdminLevel = ?,
                Sistema = ?,
                Ativo = 1

            WHERE Id = ?

        """, (
            admin_level,
            int(sistema),
            perfil_id,
        ))

        return perfil_id

    if coluna_eh_identity(
        cursor,
        "Perfis",
        "Id",
    ):

        cursor.execute("""

            INSERT INTO Perfis
            (
                Nome,
                ValidadeSenhaDias,
                Ativo,
                AdminLevel,
                Sistema
            )

            OUTPUT INSERTED.Id

            VALUES (?, ?, 1, ?, ?)

        """, (
            nome,
            validade,
            admin_level,
            int(sistema),
        ))

        return int(
            cursor.fetchone()[0]
        )

    perfil_id = obter_proximo_id(
        cursor,
        "Perfis",
        "Id",
    )

    cursor.execute("""

        INSERT INTO Perfis
        (
            Id,
            Nome,
            ValidadeSenhaDias,
            Ativo,
            AdminLevel,
            Sistema
        )

        VALUES (?, ?, ?, 1, ?, ?)

    """, (
        perfil_id,
        nome,
        validade,
        admin_level,
        int(sistema),
    ))

    return perfil_id


def inserir_usuario_default(
    cursor,
    login,
    nome,
    senha,
    perfil_id,
    deve_trocar,
):

    if registro_existe(
        cursor,
        "Usuarios",
        "Login",
        login,
    ):
        return

    senha_hash = gerar_hash(
        senha
    )

    dados = (
        login,
        nome,
        None,
        senha_hash,
        perfil_id,
        1,
        0,
        0,
        int(deve_trocar),
        int(deve_trocar),
    )

    if coluna_eh_identity(
        cursor,
        "Usuarios",
        "Id",
    ):

        cursor.execute("""

            INSERT INTO Usuarios
            (
                Login,
                Nome,
                Email,
                SenhaHash,
                PerfilId,
                Ativo,
                Bloqueado,
                TentativasLogin,
                DeveTrocarSenha,
                SenhaTemporaria,
                DataUltimaTrocaSenha
            )

            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, GETDATE())

        """, dados)

        return

    cursor.execute("""

        INSERT INTO Usuarios
        (
            Id,
            Login,
            Nome,
            Email,
            SenhaHash,
            PerfilId,
            Ativo,
            Bloqueado,
            TentativasLogin,
            DeveTrocarSenha,
            SenhaTemporaria,
            DataUltimaTrocaSenha
        )

        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, GETDATE())

    """, (
        obter_proximo_id(
            cursor,
            "Usuarios",
            "Id",
        ),
        *dados,
    ))


def buscar_menu_por_rota(
    cursor,
    rota,
):

    cursor.execute("""

        SELECT TOP 1 Id

        FROM Menu

        WHERE LOWER(ISNULL(Rota, '')) = ?

        ORDER BY Id

    """, (
        str(rota or "").lower(),
    ))

    row = cursor.fetchone()

    return row[0] if row else None


def buscar_menu_por_nome_tipo(
    cursor,
    nome,
    tipo,
):

    cursor.execute("""

        SELECT TOP 1 Id

        FROM Menu

        WHERE UPPER(Nome) = ?
        AND UPPER(TipoMenu) = ?

        ORDER BY Id

    """, (
        str(nome or "").upper(),
        str(tipo or "").upper(),
    ))

    row = cursor.fetchone()

    return row[0] if row else None


def buscar_menu_por_nome(
    cursor,
    nome,
):

    cursor.execute("""

        SELECT TOP 1 Id

        FROM Menu

        WHERE UPPER(Nome) = ?

        ORDER BY
            Ativo DESC,
            Id

    """, (
        str(nome or "").upper(),
    ))

    row = cursor.fetchone()

    return row[0] if row else None


def inserir_menu_default(
    cursor,
    menu_id,
    nome,
    rota,
    tipo,
    pai_id,
    ordem,
    icone,
    admin_level=0,
    sistema=True,
):

    existente_id = None

    if menu_id:

        cursor.execute("""

            SELECT TOP 1 Id

            FROM Menu

            WHERE Id = ?

        """, (
            menu_id,
        ))

        row = cursor.fetchone()

        existente_id = row[0] if row else None

    if rota and not existente_id:
        existente_id = buscar_menu_por_rota(
            cursor,
            rota,
        )

    if not existente_id:
        existente_id = buscar_menu_por_nome_tipo(
            cursor,
            nome,
            tipo,
        )

    if existente_id:

        cursor.execute("""

            UPDATE Menu

            SET
                Nome = ?,
                Rota = ?,
                TipoMenu = ?,
                MenuPaiId = ?,
                Ordem = ?,
                Icone = ?,
                AdminLevel = ?,
                Ativo = 1,
                Sistema = ?

            WHERE Id = ?

        """, (
            nome,
            rota,
            tipo,
            pai_id,
            ordem,
            icone,
            admin_level,
            int(sistema),
            existente_id,
        ))

        return existente_id

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

            OUTPUT INSERTED.Id

            VALUES (?, ?, ?, ?, ?, 1, NULL, NULL, ?, ?, 1, ?)

        """, (
            nome,
            rota,
            tipo,
            pai_id,
            ordem,
            icone,
            admin_level,
            int(sistema),
        ))

        return int(
            cursor.fetchone()[0]
        )

    if not menu_id:
        menu_id = obter_proximo_id(
            cursor,
            "Menu",
            "Id",
        )

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

        VALUES (?, ?, ?, ?, ?, ?, 1, NULL, NULL, ?, ?, 1, ?)

    """, (
        menu_id,
        nome,
        rota,
        tipo,
        pai_id,
        ordem,
        icone,
        admin_level,
        int(sistema),
    ))

    return menu_id


def inserir_perfil_menu_default(
    cursor,
    perfil_id,
    menu_id,
    ver=1,
    editar=1,
    excluir=1,
):

    cursor.execute("""

        SELECT COUNT(*)

        FROM PerfilMenu

        WHERE PerfilId = ?
        AND MenuId = ?

    """, (
        perfil_id,
        menu_id,
    ))

    if cursor.fetchone()[0]:

        cursor.execute("""

            UPDATE PerfilMenu

            SET
                PodeVer = ?,
                PodeEditar = ?,
                PodeExcluir = ?

            WHERE PerfilId = ?
            AND MenuId = ?

        """, (
            ver,
            editar,
            excluir,
            perfil_id,
            menu_id,
        ))

        return

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
            excluir,
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
        excluir,
    ))


def implantar_perfis_e_usuarios(cursor):

    perfil_root = inserir_perfil_default(
        cursor,
        "ROOT",
        ROOT_LEVEL,
        True,
        validade=None,
    )

    perfil_admin = inserir_perfil_default(
        cursor,
        "ADMIN",
        ADMIN_LEVEL,
        True,
    )

    inserir_perfil_default(
        cursor,
        "OPERADOR",
        10,
        False,
    )

    inserir_usuario_default(
        cursor,
        ADMIN_CONFIG["root_login"],
        ADMIN_CONFIG["root_nome"],
        ADMIN_CONFIG["root_senha"],
        perfil_root,
        deve_trocar=False,
    )

    inserir_usuario_default(
        cursor,
        ADMIN_CONFIG["admin_login"],
        ADMIN_CONFIG["admin_nome"],
        ADMIN_CONFIG["admin_senha"],
        perfil_admin,
        deve_trocar=True,
    )

    return perfil_root, perfil_admin


def implantar_menu_default(cursor):

    dashboard = inserir_menu_default(
        cursor, 1, "Dashboard", "dashboard", "S",
        None, 1, "DASHBOARD", 10, True
    )

    administrativo = inserir_menu_default(
        cursor, 20, "Administrativo", "", "T",
        None, 2, "BUSINESS_CENTER", 10, True
    )

    locais = inserir_menu_default(
        cursor, 101, "Locais de Eventos", "", "M",
        administrativo, 1, "LOCATION_CITY", 10, True
    )

    inserir_menu_default(
        cursor, 201, "Cadastro de Locais", "locais", "S",
        locais, 1, "HOME_WORK", 10, True
    )

    inserir_menu_default(
        cursor, 203, "Tipos de Local", "loc_tipos", "S",
        locais, 2, "CATEGORY", 10, True
    )

    inserir_menu_default(
        cursor, None, "Pesquisa Web", "loc_pesquisa_web", "S",
        locais, 3, "SEARCH", 10, True
    )

    inserir_menu_default(
        cursor, None, "Editar Pesquisados", "loc_pesquisa_web_edicao", "S",
        locais, 4, "EDIT_NOTE", 10, True
    )

    inserir_menu_default(
        cursor, None, "Transferir Pesquisados", "loc_pesquisa_web_transferencia", "S",
        locais, 5, "DRIVE_FILE_MOVE", 10, True
    )

    profissionais = inserir_menu_default(
        cursor, None, "Profissionais", "", "M",
        administrativo, 2, "BADGE", 10, True
    )

    inserir_menu_default(
        cursor, None, "Atores", "atores", "S",
        profissionais, 1, "THEATER_COMEDY", 10, True
    )

    inserir_menu_default(
        cursor, None, "Clientes", "clientes", "S",
        administrativo, 3, "CONTACT_PAGE", 10, True
    )

    inserir_menu_default(
        cursor, None, "Empresas", "empresas", "S",
        administrativo, 4, "BUSINESS", 10, True
    )

    inserir_menu_default(
        cursor, None, "Sedes", "sedes_empresa", "S",
        administrativo, 5, "LOCATION_ON", 10, True
    )

    eventos = inserir_menu_default(
        cursor, 22, "Eventos", "", "M",
        administrativo, 6, "EVENT", 10, True
    )

    inserir_menu_default(
        cursor, 205, "Agenda", "agenda", "S",
        eventos, 1, "CALENDAR_MONTH", 10, True
    )

    inserir_menu_default(
        cursor, 206, "Orçamentos", "orcamentos", "S",
        eventos, 2, "REQUEST_QUOTE", 10, True
    )

    inserir_menu_default(
        cursor, None, "Financeiro", "", "T",
        None, 3, "ACCOUNT_BALANCE", 10, True
    )

    inserir_menu_default(
        cursor, None, "Marketing", "", "T",
        None, 4, "CAMPAIGN", 10, True
    )

    servicos = inserir_menu_default(
        cursor, 30, "Serviços", "", "T",
        None, 5, "MISCELLANEOUS_SERVICES", ADMIN_LEVEL, True
    )

    seguranca = inserir_menu_default(
        cursor, 102, "Segurança", "", "M",
        servicos, 1, "SECURITY", ADMIN_LEVEL, True
    )

    usuarios = inserir_menu_default(
        cursor, 250, "Usuários", "usuarios", "S",
        seguranca, 1, "PEOPLE", ADMIN_LEVEL, True
    )

    perfis = inserir_menu_default(
        cursor, 251, "Perfis", "perfis", "S",
        seguranca, 2, "ADMIN_PANEL_SETTINGS", ADMIN_LEVEL, True
    )

    perfil_menu = inserir_menu_default(
        cursor, None, "Perfil x Menu", "perfil_menu", "S",
        seguranca, 3, "ACCOUNT_TREE", ADMIN_LEVEL, True
    )

    menus = inserir_menu_default(
        cursor, 252, "Menus", "menus", "S",
        seguranca, 4, "MENU", ROOT_LEVEL, True
    )

    sistema = inserir_menu_default(
        cursor, None, "Sistema", "", "M",
        servicos, 90, "SETTINGS", ADMIN_LEVEL, True
    )

    auditoria = inserir_menu_default(
        cursor, None, "Auditoria", "auditoria", "S",
        sistema, 1, "HISTORY", ADMIN_LEVEL, True
    )

    return {
        "dashboard": dashboard,
        "usuarios": usuarios,
        "perfis": perfis,
        "perfil_menu": perfil_menu,
        "menus": menus,
        "auditoria": auditoria,
    }

def inserir_sede_inicial(
    cursor,
    nome,
    municipio,
    uf="RS",
    pais="Brasil",
    fantasma=False,
    operacional=None,
    cnpj=None,
    responsavel=None,
    telefone=None,
    celular=None,
    email=None,
    cep=None,
    logradouro=None,
    numero=None,
    complemento=None,
    bairro=None,
    observacoes=None,
):

    if operacional is None:
        operacional = not fantasma

    if observacoes is None:
        observacoes = (
            "Sede fantasma para recursos em manutenção."
            if fantasma
            else
            "Sede inicial criada pela instalação."
        )

    if registro_existe(
        cursor,
        "SedesEmpresa",
        "NomeSede",
        nome,
    ):

        cursor.execute("""

            UPDATE SedesEmpresa

            SET
                CNPJ = ?,
                Responsavel = ?,
                Telefone = ?,
                Celular = ?,
                Email = ?,
                CEP = ?,
                Logradouro = ?,
                Numero = ?,
                Complemento = ?,
                Bairro = ?,
                Municipio = ?,
                UF = ?,
                Pais = ?,
                Operacional = ?,
                Fantasma = ?,
                Ativo = 1,
                Observacoes = ?,
                AtualizadoEm = GETDATE()

            WHERE NomeSede = ?

        """, (
            cnpj,
            responsavel,
            telefone,
            celular,
            email,
            cep,
            logradouro,
            numero,
            complemento,
            bairro,
            municipio,
            uf,
            pais,
            int(operacional),
            int(fantasma),
            observacoes,
            nome,
        ))

        return

    if coluna_eh_identity(
        cursor,
        "SedesEmpresa",
        "SedeID",
    ):

        cursor.execute("""

            INSERT INTO SedesEmpresa
            (
                NomeSede,
                CNPJ,
                Responsavel,
                Telefone,
                Celular,
                Email,
                CEP,
                Logradouro,
                Numero,
                Complemento,
                Bairro,
                Municipio,
                UF,
                Pais,
                Operacional,
                Fantasma,
                Ativo,
                Observacoes
            )

            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?)

        """, (
            nome,
            cnpj,
            responsavel,
            telefone,
            celular,
            email,
            cep,
            logradouro,
            numero,
            complemento,
            bairro,
            municipio,
            uf,
            pais,
            int(operacional),
            int(fantasma),
            observacoes,
        ))

        return

    cursor.execute("""

        INSERT INTO SedesEmpresa
            (
                SedeID,
                NomeSede,
                CNPJ,
                Responsavel,
                Telefone,
                Celular,
                Email,
                CEP,
                Logradouro,
                Numero,
                Complemento,
                Bairro,
                Municipio,
                UF,
                Pais,
            Operacional,
            Fantasma,
            Ativo,
            Observacoes
        )

        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?)

    """, (
        obter_proximo_id(
            cursor,
            "SedesEmpresa",
            "SedeID",
        ),
        nome,
        cnpj,
        responsavel,
        telefone,
        celular,
        email,
        cep,
        logradouro,
        numero,
        complemento,
        bairro,
        municipio,
        uf,
        pais,
        int(operacional),
        int(fantasma),
        observacoes,
    ))


def inserir_loc_tipo_default(
    cursor,
    nome,
):

    if registro_existe(
        cursor,
        "LocTipo",
        "NomeTipo",
        nome,
    ):
        return

    if coluna_eh_identity(
        cursor,
        "LocTipo",
        "LocTipoID",
    ):

        cursor.execute("""

            INSERT INTO LocTipo
            (
                NomeTipo,
                Ativo
            )

            VALUES (?, 1)

        """, (
            nome,
        ))

        return

    cursor.execute("""

        INSERT INTO LocTipo
        (
            LocTipoID,
            NomeTipo,
            Ativo
        )

        VALUES (?, ?, 1)

    """, (
        obter_proximo_id(
            cursor,
            "LocTipo",
            "LocTipoID",
        ),
        nome,
    ))


def inserir_loc_estrutura_default(
    cursor,
    nome,
):

    if registro_existe(
        cursor,
        "LocEstrutura",
        "NomeEstrutura",
        nome,
    ):
        return

    if coluna_eh_identity(
        cursor,
        "LocEstrutura",
        "LocEstruturaID",
    ):

        cursor.execute("""

            INSERT INTO LocEstrutura
            (
                NomeEstrutura,
                Ativo
            )

            VALUES (?, 1)

        """, (
            nome,
        ))

        return

    cursor.execute("""

        INSERT INTO LocEstrutura
        (
            LocEstruturaID,
            NomeEstrutura,
            Ativo
        )

        VALUES (?, ?, 1)

    """, (
        obter_proximo_id(
            cursor,
            "LocEstrutura",
            "LocEstruturaID",
        ),
        nome,
    ))


def implantar_dados_configurados(cursor, dados):

    perfil_ids = {}

    for perfil in dados.get(
        "perfis",
        [],
    ):

        nome = perfil.get(
            "nome"
        )

        if not nome:
            continue

        perfil_ids[nome.upper()] = inserir_perfil_default(
            cursor,
            nome,
            int(
                perfil.get(
                    "admin_level",
                    0,
                ) or 0
            ),
            valor_bool(
                perfil.get(
                    "sistema"
                ),
                False,
            ),
            validade=perfil.get(
                "validade_senha_dias",
                90,
            ),
        )

    for usuario in dados.get(
        "usuarios",
        [],
    ):

        login = obter_valor_env_ou_config(
            usuario,
            "login",
        )

        nome = obter_valor_env_ou_config(
            usuario,
            "nome",
            login,
        )

        senha = obter_valor_env_ou_config(
            usuario,
            "senha",
        )

        perfil_nome = str(
            usuario.get(
                "perfil",
                "",
            )
        ).upper()

        perfil_id = perfil_ids.get(
            perfil_nome
        )

        if login and senha and perfil_id:

            inserir_usuario_default(
                cursor,
                login,
                nome,
                senha,
                perfil_id,
                valor_bool(
                    usuario.get(
                        "deve_trocar_senha"
                    ),
                    True,
                ),
            )

    menu_ids = {}

    for menu in dados.get(
        "menus",
        [],
    ):

        key = menu.get(
            "key"
        ) or menu.get(
            "rota"
        ) or menu.get(
            "nome"
        )

        pai = menu.get(
            "pai"
        )

        pai_id = None

        if pai:
            pai_id = menu_ids.get(
                str(pai)
            )

        menu_id = inserir_menu_default(
            cursor,
            menu.get(
                "id"
            ),
            menu.get(
                "nome"
            ),
            menu.get(
                "rota",
                "",
            ) or "",
            menu.get(
                "tipo",
                "S",
            ),
            pai_id,
            int(
                menu.get(
                    "ordem",
                    0,
                ) or 0
            ),
            menu.get(
                "icone",
                "",
            ) or "",
            int(
                menu.get(
                    "admin_level",
                    0,
                ) or 0
            ),
            valor_bool(
                menu.get(
                    "sistema"
                ),
                True,
            ),
        )

        if key:
            menu_ids[str(key)] = menu_id

        rota = menu.get(
            "rota"
        )

        if rota:
            menu_ids[str(rota)] = menu_id

    for permissao in dados.get(
        "permissoes",
        [],
    ):

        perfil_id = perfil_ids.get(
            str(
                permissao.get(
                    "perfil",
                    "",
                )
            ).upper()
        )

        if not perfil_id:
            continue

        menus = permissao.get(
            "menus",
            [],
        )

        if menus == "*":

            cursor.execute("""

                SELECT Id

                FROM Menu

                WHERE Ativo = 1

            """)

            menu_alvos = [
                row[0]
                for row in cursor.fetchall()
            ]

        else:

            menu_alvos = []

            for ref in menus:

                menu_id = menu_ids.get(
                    str(ref)
                )

                if menu_id:
                    menu_alvos.append(
                        menu_id
                    )

        for menu_id in menu_alvos:

            inserir_perfil_menu_default(
                cursor,
                perfil_id,
                menu_id,
                int(
                    valor_bool(
                        permissao.get(
                            "ver"
                        ),
                        True,
                    )
                ),
                int(
                    valor_bool(
                        permissao.get(
                            "editar"
                        ),
                        False,
                    )
                ),
                int(
                    valor_bool(
                        permissao.get(
                            "excluir"
                        ),
                        False,
                    )
                ),
            )

    for sede in dados.get(
        "sedes",
        [],
    ):

        inserir_sede_inicial(
            cursor,
            sede.get(
                "nome"
            ),
            sede.get(
                "municipio"
            ),
            uf=sede.get(
                "uf",
                "RS",
            ),
            pais=sede.get(
                "pais",
                "Brasil",
            ),
            fantasma=valor_bool(
                sede.get(
                    "fantasma"
                ),
                False,
            ),
            operacional=valor_bool(
                sede.get(
                    "operacional"
                ),
                True,
            ),
            cnpj=sede.get(
                "cnpj"
            ),
            responsavel=sede.get(
                "responsavel"
            ),
            telefone=sede.get(
                "telefone"
            ),
            celular=sede.get(
                "celular"
            ),
            email=sede.get(
                "email"
            ),
            cep=sede.get(
                "cep"
            ),
            logradouro=sede.get(
                "logradouro"
            ),
            numero=sede.get(
                "numero"
            ),
            complemento=sede.get(
                "complemento"
            ),
            bairro=sede.get(
                "bairro"
            ),
            observacoes=sede.get(
                "observacoes"
            ),
        )

    tipos_local = list(
        dados.get(
            "loc_tipos",
            [],
        )
    )

    tipos_local.extend(
        carregar_tipos_local_configurados()
    )

    for tipo in tipos_local:

        if isinstance(tipo, dict):
            tipo = tipo.get("nome")

        tipo = str(tipo or "").strip()

        if not tipo:
            continue

        inserir_loc_tipo_default(
            cursor,
            tipo,
        )

    for estrutura in dados.get(
        "loc_estruturas",
        [],
    ):

        inserir_loc_estrutura_default(
            cursor,
            estrutura,
        )


def normalizar_menu_atual(cursor):

    LOGGER.info(
        "Normalizando estrutura atual da tabela Menu."
    )

    def atualizar(
        menu_id,
        nome,
        rota,
        tipo,
        pai_id,
        ordem,
        icone,
        admin_level,
        ativo=True,
        sistema=True,
    ):

        if not menu_id:
            return None

        cursor.execute("""

            UPDATE Menu

            SET
                Nome = ?,
                Rota = ?,
                TipoMenu = ?,
                MenuPaiId = ?,
                Ordem = ?,
                Icone = ?,
                AdminLevel = ?,
                Ativo = ?,
                Sistema = ?

            WHERE Id = ?

        """, (
            nome,
            rota,
            tipo,
            pai_id,
            ordem,
            icone,
            admin_level,
            int(ativo),
            int(sistema),
            menu_id,
        ))

        return menu_id

    def obter_grupo(
        nome,
        tipo,
        nome_antigo=None,
    ):

        return (
            buscar_menu_por_nome_tipo(
                cursor,
                nome,
                tipo,
            )
            or (
                buscar_menu_por_nome_tipo(
                    cursor,
                    nome_antigo,
                    tipo,
                )
                if nome_antigo
                else None
            )
        )

    def mover_rota(
        rota,
        pai_id,
        ordem,
        admin_level=10,
    ):

        if not pai_id:
            return

        menu_id = buscar_menu_por_rota(
            cursor,
            rota,
        )

        if not menu_id:
            return

        cursor.execute("""

            UPDATE Menu

            SET
                MenuPaiId = ?,
                Ordem = ?,
                AdminLevel = ?,
                Ativo = 1

            WHERE Id = ?

        """, (
            pai_id,
            ordem,
            admin_level,
            menu_id,
        ))

    def garantir_rota_por_nome(
        nome,
        rota,
        pai_id,
        ordem,
        icone,
        admin_level=10,
    ):

        menu_id = buscar_menu_por_rota(
            cursor,
            rota,
        )

        if not menu_id:
            menu_id = buscar_menu_por_nome(
                cursor,
                nome,
            )

        if not menu_id:
            return None

        atualizar(
            menu_id,
            nome,
            rota,
            "S",
            pai_id,
            ordem,
            icone,
            admin_level,
            True,
            True,
        )

        return menu_id

    def desativar_agrupador_duplicado(
        nome,
        manter_id,
    ):

        if not manter_id:
            return

        cursor.execute("""

            UPDATE Menu

            SET Ativo = 0

            WHERE UPPER(Nome) = ?
            AND Id <> ?
            AND ISNULL(Rota, '') = ''
            AND UPPER(TipoMenu) IN ('T', 'M')

        """, (
            str(nome or "").upper(),
            manter_id,
        ))

    def mover_filhos(
        origem_id,
        destino_id,
    ):

        if not origem_id or not destino_id or origem_id == destino_id:
            return

        cursor.execute("""

            UPDATE Menu

            SET MenuPaiId = ?

            WHERE MenuPaiId = ?

        """, (
            destino_id,
            origem_id,
        ))

    def desativar_substituido(
        nome,
        manter_id,
    ):

        if not manter_id:
            return

        cursor.execute("""

            UPDATE Menu

            SET Ativo = 0

            WHERE UPPER(Nome) = ?
            AND Id <> ?
            AND ISNULL(Rota, '') = ''
            AND UPPER(TipoMenu) IN ('T', 'M')

        """, (
            str(nome or "").upper(),
            manter_id,
        ))

    def desativar_rotas_integradas(rotas):

        if not rotas:
            return

        marcadores = ", ".join(
            "?"
            for _ in rotas
        )

        cursor.execute(f"""

            UPDATE Menu

            SET
                Ativo = 0,
                Sistema = 0

            WHERE Rota IN ({marcadores})

        """, tuple(rotas))

    administrativo = (
        obter_grupo(
            "Administrativo",
            "T",
            "Cadastros",
        )
        or inserir_menu_default(
            cursor,
            20,
            "Administrativo",
            "",
            "T",
            None,
            2,
            "BUSINESS_CENTER",
            10,
            True,
        )
    )

    atualizar(
        administrativo,
        "Administrativo",
        "",
        "T",
        None,
        2,
        "BUSINESS_CENTER",
        10,
    )

    financeiro = (
        obter_grupo(
            "Financeiro",
            "T",
        )
        or inserir_menu_default(
            cursor,
            None,
            "Financeiro",
            "",
            "T",
            None,
            3,
            "ACCOUNT_BALANCE",
            10,
            True,
        )
    )

    atualizar(
        financeiro,
        "Financeiro",
        "",
        "T",
        None,
        3,
        "ACCOUNT_BALANCE",
        10,
    )

    marketing = (
        obter_grupo(
            "Marketing",
            "T",
        )
        or inserir_menu_default(
            cursor,
            None,
            "Marketing",
            "",
            "T",
            None,
            4,
            "CAMPAIGN",
            10,
            True,
        )
    )

    atualizar(
        marketing,
        "Marketing",
        "",
        "T",
        None,
        4,
        "CAMPAIGN",
        10,
    )

    servicos = (
        obter_grupo(
            "Serviços",
            "T",
            "Administração",
        )
        or buscar_menu_por_nome(
            cursor,
            "Administracao",
        )
        or inserir_menu_default(
            cursor,
            30,
            "Serviços",
            "",
            "T",
            None,
            5,
            "MISCELLANEOUS_SERVICES",
            ADMIN_LEVEL,
            True,
        )
    )

    atualizar(
        servicos,
        "Serviços",
        "",
        "T",
        None,
        5,
        "MISCELLANEOUS_SERVICES",
        ADMIN_LEVEL,
    )

    locais = (
        obter_grupo(
            "Locais de Eventos",
            "M",
            "Locais",
        )
        or inserir_menu_default(
            cursor,
            101,
            "Locais de Eventos",
            "",
            "M",
            administrativo,
            1,
            "LOCATION_CITY",
            10,
            True,
        )
    )

    atualizar(
        locais,
        "Locais de Eventos",
        "",
        "M",
        administrativo,
        1,
        "LOCATION_CITY",
        10,
    )

    profissionais = (
        obter_grupo(
            "Profissionais",
            "M",
        )
        or inserir_menu_default(
            cursor,
            None,
            "Profissionais",
            "",
            "M",
            administrativo,
            2,
            "BADGE",
            10,
            True,
        )
    )

    atualizar(
        profissionais,
        "Profissionais",
        "",
        "M",
        administrativo,
        2,
        "BADGE",
        10,
    )

    eventos = (
        obter_grupo(
            "Eventos",
            "M",
        )
        or obter_grupo(
            "Eventos",
            "T",
        )
        or inserir_menu_default(
            cursor,
            22,
            "Eventos",
            "",
            "M",
            administrativo,
            6,
            "EVENT",
            10,
            True,
        )
    )

    atualizar(
        eventos,
        "Eventos",
        "",
        "M",
        administrativo,
        6,
        "EVENT",
        10,
    )

    seguranca = (
        obter_grupo(
            "Segurança",
            "M",
        )
        or inserir_menu_default(
            cursor,
            102,
            "Segurança",
            "",
            "M",
            servicos,
            1,
            "SECURITY",
            ADMIN_LEVEL,
            True,
        )
    )

    atualizar(
        seguranca,
        "Segurança",
        "",
        "M",
        servicos,
        1,
        "SECURITY",
        ADMIN_LEVEL,
    )

    sistema = (
        obter_grupo(
            "Sistema",
            "M",
        )
        or inserir_menu_default(
            cursor,
            None,
            "Sistema",
            "",
            "M",
            servicos,
            90,
            "SETTINGS",
            ADMIN_LEVEL,
            True,
        )
    )

    atualizar(
        sistema,
        "Sistema",
        "",
        "M",
        servicos,
        90,
        "SETTINGS",
        ADMIN_LEVEL,
    )

    mover_rota("locais", locais, 1)
    mover_rota("loc_tipos", locais, 2)
    garantir_rota_por_nome(
        "Pesquisa Web",
        "loc_pesquisa_web",
        locais,
        3,
        "SEARCH",
        10,
    )
    garantir_rota_por_nome(
        "Editar Pesquisados",
        "loc_pesquisa_web_edicao",
        locais,
        4,
        "EDIT_NOTE",
        10,
    )
    garantir_rota_por_nome(
        "Transferir Pesquisados",
        "loc_pesquisa_web_transferencia",
        locais,
        5,
        "DRIVE_FILE_MOVE",
        10,
    )
    desativar_rotas_integradas((
        "loc_ambientes",
        "loc_estruturas",
    ))
    mover_rota("atores", profissionais, 1)
    garantir_rota_por_nome(
        "Figurinos",
        "figurinos",
        profissionais,
        2,
        "CHECKROOM",
        10,
    )
    clientes = garantir_rota_por_nome(
        "Clientes",
        "clientes",
        administrativo,
        3,
        "CONTACT_PAGE",
        10,
    )
    empresas = garantir_rota_por_nome(
        "Empresas",
        "empresas",
        administrativo,
        4,
        "BUSINESS",
        10,
    )
    sedes = garantir_rota_por_nome(
        "Sedes",
        "sedes_empresa",
        administrativo,
        5,
        "LOCATION_ON",
        10,
    )
    mover_rota("agenda", eventos, 1)
    mover_rota("orcamentos", eventos, 2)
    mover_rota("usuarios", seguranca, 1, ADMIN_LEVEL)
    mover_rota("perfis", seguranca, 2, ADMIN_LEVEL)
    perfil_menu = garantir_rota_por_nome(
        "Perfil x Menu",
        "perfil_menu",
        seguranca,
        3,
        "ACCOUNT_TREE",
        ADMIN_LEVEL,
    )
    mover_rota("menus", seguranca, 4, ROOT_LEVEL)
    mover_rota("menu_config", seguranca, 4, ROOT_LEVEL)
    mover_rota("auditoria", sistema, 1, ADMIN_LEVEL)

    desativar_agrupador_duplicado(
        "Clientes",
        clientes,
    )

    desativar_agrupador_duplicado(
        "Empresas",
        empresas,
    )

    desativar_agrupador_duplicado(
        "Sedes",
        sedes,
    )

    for nome_antigo in (
        "Cadastros",
        "Administração",
        "Administracao",
    ):

        antigo = buscar_menu_por_nome(
            cursor,
            nome_antigo,
        )

        destino = (
            administrativo
            if nome_antigo == "Cadastros"
            else servicos
        )

        mover_filhos(
            antigo,
            destino,
        )

        desativar_substituido(
            nome_antigo,
            destino,
        )

    evento_antigo = buscar_menu_por_nome_tipo(
        cursor,
        "Eventos",
        "T",
    )

    mover_filhos(
        evento_antigo,
        eventos,
    )

    desativar_substituido(
        "Eventos",
        eventos,
    )

    cursor.execute("""

        UPDATE Menu

        SET Nivel =
            CASE
                WHEN MenuPaiId IS NULL THEN 0
                WHEN UPPER(TipoMenu) = 'M' THEN 1
                ELSE 2
            END

    """)


def implantar_dados_iniciais(cursor):

    dados = carregar_dados_iniciais()

    if dados:

        implantar_dados_configurados(
            cursor,
            dados,
        )

        return

    perfil_root, perfil_admin = (
        implantar_perfis_e_usuarios(
            cursor
        )
    )

    menus_default = implantar_menu_default(
        cursor
    )

    cursor.execute("""

        SELECT Id

        FROM Menu

        WHERE Ativo = 1

    """)

    for row in cursor.fetchall():

        inserir_perfil_menu_default(
            cursor,
            perfil_root,
            row[0],
            1,
            1,
            1,
        )

    for rota in (
        "dashboard",
        "usuarios",
        "perfis",
        "perfil_menu",
        "auditoria",
    ):

        menu_id = menus_default.get(
            rota
        )

        if menu_id:

            inserir_perfil_menu_default(
                cursor,
                perfil_admin,
                menu_id,
                1,
                1,
                1,
            )

    inserir_sede_inicial(
        cursor,
        "Porto Alegre",
        "Porto Alegre",
    )

    inserir_sede_inicial(
        cursor,
        "Santa Cruz do Sul",
        "Santa Cruz do Sul",
    )

    inserir_sede_inicial(
        cursor,
        "Manutenção",
        "Porto Alegre",
        fantasma=True,
    )

    tipos_default = carregar_tipos_local_configurados()

    if not tipos_default:

        tipos_default = (
            "Não informado",
            "Centro de Convenções",
            "Auditório",
            "Teatro",
            "Sala de Treinamento",
            "Coworking",
            "Espaço de Festas",
            "Sítio",
            "Rooftop",
            "Espaço VIP",
            "Local Histórico",
            "Museu",
            "Arena",
            "Estádio",
            "Hotel",
            "Estúdio",
            "Espaço Virtual",
        )

    for tipo in tipos_default:

        inserir_loc_tipo_default(
            cursor,
            tipo,
        )

    for estrutura in (
        "Banheiros",
        "Cozinha",
        "Estacionamento",
        "Palco",
    ):

        inserir_loc_estrutura_default(
            cursor,
            estrutura,
        )


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

        criar_tabela_loc_tipo(cursor)

        criar_tabela_loc_estrutura(cursor)

        criar_tabela_local_evento(cursor)

        criar_tabela_local_evento_pesquisa_web(cursor)

        criar_tabela_loc_ambientes(cursor)

        criar_tabela_local_evento_estrutura(cursor)

        criar_tabela_sedes_empresa(cursor)

        criar_tabela_cep_cache(cursor)

        criar_tabela_google_maps_usage(cursor)

        criar_tabela_ator(cursor)

        criar_tabela_cliente(cursor)

        criar_tabela_cliente_aniversariante(cursor)

        criar_tabela_figurino(cursor)

        criar_tabela_empresa(cursor)

        atualizar_tabela_system_migration(
            cursor
        )

        atualizar_tabela_perfis(
            cursor
        )

        atualizar_schema_usuarios(
            cursor
        )

        atualizar_tabela_menu(
            cursor
        )

        atualizar_tabela_perfil_menu(
            cursor
        )

        atualizar_tabela_auditoria(
            cursor
        )

        atualizar_tabela_loc_tipo(
            cursor
        )

        atualizar_tabela_loc_estrutura(
            cursor
        )

        atualizar_tabela_local_evento(
            cursor
        )

        atualizar_tabela_local_evento_pesquisa_web(
            cursor
        )

        atualizar_tabela_loc_ambientes(
            cursor
        )

        atualizar_tabela_sedes_empresa(
            cursor
        )

        atualizar_tabela_cep_cache(
            cursor
        )

        atualizar_tabela_ator(
            cursor
        )

        atualizar_tabela_cliente(
            cursor
        )

        atualizar_tabela_cliente_aniversariante(
            cursor
        )

        atualizar_tabela_figurino(
            cursor
        )

        atualizar_tabela_empresa(
            cursor
        )

        implantar_dados_iniciais(
            cursor
        )

        normalizar_menu_atual(
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
