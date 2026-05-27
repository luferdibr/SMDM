# =========================================================
# services/bootstrap_service.py
# =========================================================

import logging

from config.settings import (
    ADMIN_CONFIG,
)

from database.connection import (
    get_connection,
)

from security.password_service import (
    gerar_hash,
)

from services.auditoria_service import (
    registrar_evento_sistema,
)

from services.identity_service import (
    coluna_eh_identity,
    obter_proximo_id,
)

from modules.administracao.menus.services.menu_service import (
    invalidate_menu_cache,
)

# =========================================================
# LOGGER
# =========================================================

LOGGER = logging.getLogger(
    "SMDM_BOOTSTRAP"
)

# =========================================================
# VERSION
# =========================================================

SCHEMA_VERSION = 1

# =========================================================
# LEVELS
# =========================================================

ROOT_LEVEL = 100

ADMIN_LEVEL = 50

# =========================================================
# ROOT
# =========================================================

LOGIN_ROOT = ADMIN_CONFIG[
    "root_login"
]

NOME_ROOT = ADMIN_CONFIG[
    "root_nome"
]

SENHA_ROOT = ADMIN_CONFIG[
    "root_senha"
]

# =========================================================
# ADMIN
# =========================================================

LOGIN_ADMIN = ADMIN_CONFIG[
    "admin_login"
]

NOME_ADMIN = ADMIN_CONFIG[
    "admin_nome"
]

SENHA_ADMIN = ADMIN_CONFIG[
    "admin_senha"
]

# =========================================================
# HELPERS
# =========================================================

def existe_tabela(
    cursor,
    tabela,
):

    cursor.execute(

        """

        SELECT COUNT(*)

        FROM INFORMATION_SCHEMA.TABLES

        WHERE TABLE_NAME = ?

        """,

        (tabela,),
    )

    return (
        cursor.fetchone()[0]
        > 0
    )

# =========================================================
# REGISTRO
# =========================================================

def existe_registro(
    cursor,
    tabela,
    campo,
    valor,
):

    cursor.execute(

        f"""

        SELECT COUNT(*)

        FROM {tabela}

        WHERE {campo} = ?

        """,

        (valor,),
    )

    return (
        cursor.fetchone()[0]
        > 0
    )

# =========================================================
# SCHEMA VERSION
# =========================================================

def garantir_schema_version(
    cursor,
):

    if not existe_tabela(
        cursor,
        "SchemaVersion",
    ):

        cursor.execute(

            """

            CREATE TABLE SchemaVersion (

                Id INT IDENTITY(1,1)
                PRIMARY KEY,

                Versao INT NOT NULL,

                DataExecucao DATETIME
                DEFAULT GETDATE()
            )

            """
        )

        LOGGER.info(
            "SchemaVersion criada."
        )

# =========================================================
# GET VERSION
# =========================================================

def get_schema_version(
    cursor,
):

    garantir_schema_version(
        cursor
    )

    cursor.execute(

        """

        SELECT TOP 1 Versao

        FROM SchemaVersion

        ORDER BY Id DESC

        """
    )

    row = cursor.fetchone()

    if not row:

        return 0

    return int(row[0])

# =========================================================
# SET VERSION
# =========================================================

def set_schema_version(
    cursor,
    version,
):

    cursor.execute(

        """

        INSERT INTO SchemaVersion
        (
            Versao
        )

        VALUES (?)

        """,

        (version,),
    )


def perfil_id_eh_identity(
    cursor,
):

    cursor.execute(

        """

        SELECT COLUMNPROPERTY(
            OBJECT_ID('Perfis'),
            'Id',
            'IsIdentity'
        )

        """
    )

    row = cursor.fetchone()

    return bool(
        row
        and
        row[0]
    )


def obter_proximo_perfil_id(
    cursor,
):

    cursor.execute(

        """

        SELECT ISNULL(MAX(Id), 0) + 1

        FROM Perfis

        """
    )

    return int(
        cursor.fetchone()[0]
        or 1
    )


def inserir_perfil_inicial(
    cursor,
    perfil,
):

    if perfil_id_eh_identity(
        cursor
    ):

        cursor.execute(

            """

            INSERT INTO Perfis (

                Nome,
                AdminLevel,
                Sistema,
                Ativo,
                ValidadeSenhaDias

            )

            VALUES (?, ?, ?, 1, 90)

            """,

            (
                perfil["nome"],
                perfil["admin_level"],
                1 if perfil["sistema"] else 0,
            ),
        )

        return

    cursor.execute(

        """

        INSERT INTO Perfis (

            Id,
            Nome,
            AdminLevel,
            Sistema,
            Ativo,
            ValidadeSenhaDias

        )

        VALUES (?, ?, ?, ?, 1, 90)

        """,

        (
            obter_proximo_perfil_id(
                cursor
            ),
            perfil["nome"],
            perfil["admin_level"],
            1 if perfil["sistema"] else 0,
        ),
    )


def inserir_perfil_menu(
    cursor,
    perfil_id,
    menu_id,
    ver=1,
    editar=1,
    excluir=1,
):

    cursor.execute(

        """

        SELECT COUNT(*)

        FROM PerfilMenu

        WHERE PerfilId = ?
        AND MenuId = ?

        """,

        (
            perfil_id,
            menu_id,
        ),
    )

    if cursor.fetchone()[0]:
        return

    if coluna_eh_identity(
        cursor,
        "PerfilMenu",
        "Id",
    ):

        cursor.execute(

            """

            INSERT INTO PerfilMenu
            (
                PerfilId,
                MenuId,
                PodeVer,
                PodeEditar,
                PodeExcluir
            )

            VALUES (?, ?, ?, ?, ?)

            """,

            (
                perfil_id,
                menu_id,
                ver,
                editar,
                excluir,
            ),
        )

        return

    cursor.execute(

        """

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

        """,

        (
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
        ),
    )

# =========================================================
# PERFIS
# =========================================================

def garantir_perfis(
    cursor,
):

    perfis = [

        {
            "nome": "ROOT",
            "admin_level": ROOT_LEVEL,
            "sistema": True,
        },

        {
            "nome": "ADMIN",
            "admin_level": ADMIN_LEVEL,
            "sistema": True,
        },

        {
            "nome": "OPERADOR",
            "admin_level": 10,
            "sistema": False,
        },
    ]

    for perfil in perfis:

        if existe_registro(

            cursor,
            "Perfis",
            "Nome",
            perfil["nome"],
        ):

            cursor.execute(

                """

                UPDATE Perfis

                SET
                    AdminLevel = ?,
                    Sistema = ?

                WHERE Nome = ?

                """,

                (
                    perfil["admin_level"],
                    1 if perfil["sistema"] else 0,
                    perfil["nome"],
                ),
            )

            continue

        inserir_perfil_inicial(
            cursor,
            perfil,
        )

        LOGGER.info(

            (
                "Perfil criado: "
                f"{perfil['nome']}"
            )
        )

# =========================================================
# PERFIL ID
# =========================================================

def get_perfil_id(
    cursor,
    nome,
):

    cursor.execute(

        """

        SELECT TOP 1 Id

        FROM Perfis

        WHERE Nome = ?

        """,

        (nome,),
    )

    row = cursor.fetchone()

    if not row:

        raise Exception(

            (
                "Perfil não encontrado: "
                f"{nome}"
            )
        )

    return row[0]

# =========================================================
# ROOT USER
# =========================================================
#
# Observacao de seguranca:
# A senha ROOT deve ser informada no processo de
# instalacao/implantacao. O usuario ROOT nao recebe
# flag de troca obrigatoria no primeiro acesso, pois
# representa a conta maxima de recuperacao e controle
# do sistema.

def garantir_root(
    cursor,
):

    if existe_registro(

        cursor,
        "Usuarios",
        "Login",
        LOGIN_ROOT,
    ):

        return

    perfil_id = get_perfil_id(
        cursor,
        "ROOT",
    )

    senha_hash = gerar_hash(
        SENHA_ROOT
    )

    if coluna_eh_identity(
        cursor,
        "Usuarios",
        "Id",
    ):

        cursor.execute(

            """

            INSERT INTO Usuarios (

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

            VALUES (

                ?, ?, ?, ?,
                1, 0, 0, 0, 0

            )

            """,

            (
                LOGIN_ROOT,
                NOME_ROOT,
                senha_hash,
                perfil_id,
            ),
        )

    else:

        cursor.execute(

            """

            INSERT INTO Usuarios (

                Id,
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

            VALUES (

                ?, ?, ?, ?, ?,
                1, 0, 0, 0, 0

            )

            """,

            (
                obter_proximo_id(
                    cursor,
                    "Usuarios",
                    "Id",
                ),
                LOGIN_ROOT,
                NOME_ROOT,
                senha_hash,
                perfil_id,
            ),
        )

    LOGGER.info(
        "ROOT criado."
    )

# =========================================================
# ADMIN USER
# =========================================================
#
# Observacao de seguranca:
# O usuario ADMIN e criado como conta administrativa
# operacional. Diferente do ROOT, ele recebe senha
# temporaria e deve trocar a senha no primeiro acesso.

def garantir_admin(
    cursor,
):

    if existe_registro(

        cursor,
        "Usuarios",
        "Login",
        LOGIN_ADMIN,
    ):

        return

    perfil_id = get_perfil_id(
        cursor,
        "ADMIN",
    )

    senha_hash = gerar_hash(
        SENHA_ADMIN
    )

    if coluna_eh_identity(
        cursor,
        "Usuarios",
        "Id",
    ):

        cursor.execute(

            """

            INSERT INTO Usuarios (

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

            VALUES (

                ?, ?, ?, ?,
                1, 0, 0, 1, 1

            )

            """,

            (
                LOGIN_ADMIN,
                NOME_ADMIN,
                senha_hash,
                perfil_id,
            ),
        )

    else:

        cursor.execute(

            """

            INSERT INTO Usuarios (

                Id,
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

            VALUES (

                ?, ?, ?, ?, ?,
                1, 0, 0, 1, 1

            )

            """,

            (
                obter_proximo_id(
                    cursor,
                    "Usuarios",
                    "Id",
                ),
                LOGIN_ADMIN,
                NOME_ADMIN,
                senha_hash,
                perfil_id,
            ),
        )

    LOGGER.info(
        "ADMIN criado."
    )


# =========================================================
# ROOT UNICO
# =========================================================

def garantir_root_unico(
    cursor,
):

    perfil_root = get_perfil_id(
        cursor,
        "ROOT",
    )

    perfil_admin = get_perfil_id(
        cursor,
        "ADMIN",
    )

    cursor.execute(

        """

        UPDATE Usuarios

        SET PerfilId = ?

        WHERE PerfilId = ?
        AND UPPER(Login) <> ?

        """,

        (
            perfil_admin,
            perfil_root,
            str(LOGIN_ROOT).upper(),
        ),
    )

    LOGGER.info(
        "Unicidade ROOT validada."
    )

# =========================================================
# VALIDAR TABELAS
# =========================================================

def validar_tabelas(
    cursor,
):

    tabelas = [

        "Perfis",
        "Usuarios",
        "Menu",
        "PerfilMenu",
    ]

    for tabela in tabelas:

        if not existe_tabela(
            cursor,
            tabela,
        ):

            raise Exception(

                (
                    "Tabela não encontrada: "
                    f"{tabela}"
                )
            )

# =========================================================
# MENU
# =========================================================
#
# Observacao de implantacao:
# Este bootstrap acompanha a evolucao do sistema. A
# cada implementacao de novas rotinas, podem surgir
# novos dados iniciais, perfis, permissoes e ajustes
# de menu a serem implantados aqui ou via migrations.
#
# Observacao de dominio:
# A tabela Menu pode conter campos de apoio ainda em
# observacao, criados pela rotina de instalacao para
# possivel uso futuro. A carga inicial e a ACL devem
# considerar como regra funcional vigente:
# - T agrupa menus de nivel superior;
# - M agrupa itens abaixo de T;
# - S representa a opcao executavel/processo;
# - PerfilMenu define o que cada perfil enxerga.
#
# Nao remover nem assumir obrigatoriedade dos campos
# excedentes sem revisao funcional.

def validar_menu(
    cursor,
):

    cursor.execute(

        """

        SELECT COUNT(*)

        FROM Menu

        """
    )

    total = cursor.fetchone()[0]

    if total <= 0:

        LOGGER.warning(
            "Tabela Menu vazia."
        )

    else:

        LOGGER.info(

            (
                "Menus encontrados: "
                f"{total}"
            )
        )


def obter_proximo_menu_id(
    cursor,
):

    cursor.execute(

        """

        SELECT ISNULL(MAX(Id), 0) + 1

        FROM Menu

        """
    )

    return int(
        cursor.fetchone()[0]
    )


def menu_id_eh_identity(
    cursor,
):

    cursor.execute(

        """

        SELECT COLUMNPROPERTY(
            OBJECT_ID('Menu'),
            'Id',
            'IsIdentity'
        )

        """
    )

    row = cursor.fetchone()

    return bool(
        row
        and
        row[0]
    )


def buscar_menu_por_rota(
    cursor,
    rota,
):

    cursor.execute(

        """

        SELECT TOP 1 Id

        FROM Menu

        WHERE LOWER(ISNULL(Rota, '')) = ?

        """,

        (
            str(rota or "").lower(),
        ),
    )

    row = cursor.fetchone()

    return row[0] if row else None


def buscar_menu_por_nome(
    cursor,
    nome,
):

    cursor.execute(

        """

        SELECT TOP 1 Id

        FROM Menu

        WHERE UPPER(Nome) = ?

        ORDER BY Id

        """,

        (
            str(nome or "").upper(),
        ),
    )

    row = cursor.fetchone()

    return row[0] if row else None


def buscar_menu_por_nome_tipo(
    cursor,
    nome,
    tipo,
):

    cursor.execute(

        """

        SELECT TOP 1 Id

        FROM Menu

        WHERE UPPER(Nome) = ?
        AND UPPER(TipoMenu) = ?

        ORDER BY Id

        """,

        (
            str(nome or "").upper(),
            str(tipo or "").upper(),
        ),
    )

    row = cursor.fetchone()

    return row[0] if row else None


def inserir_menu(
    cursor,
    nome,
    rota,
    tipo,
    pai_id,
    ordem,
    icone,
    admin_level=0,
    sistema=True,
):

    if menu_id_eh_identity(
        cursor
    ):

        cursor.execute(

            """

            INSERT INTO Menu (

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

            VALUES (

                ?, ?, ?, ?, ?, 1, NULL, NULL,
                ?, ?, 1, ?

            )

            """,

            (
                nome,
                rota,
                tipo,
                pai_id,
                ordem,
                icone,
                admin_level,
                1 if sistema else 0,
            ),
        )

        menu_id = int(
            cursor.fetchone()[0]
        )

    else:

        menu_id = obter_proximo_menu_id(
            cursor
        )

        cursor.execute(

            """

            INSERT INTO Menu (

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

            VALUES (

                ?, ?, ?, ?, ?, ?, 1, NULL, NULL,
                ?, ?, 1, ?

            )

            """,

            (
                menu_id,
                nome,
                rota,
                tipo,
                pai_id,
                ordem,
                icone,
                admin_level,
                1 if sistema else 0,
            ),
        )

    LOGGER.info(
        "Menu criado: %s",
        nome,
    )

    return menu_id


def atualizar_menu_auditoria(
    cursor,
    menu_id,
    pai_id,
):

    cursor.execute(

        """

        UPDATE Menu

        SET
            Nome = 'Auditoria',
            Rota = 'auditoria',
            TipoMenu = 'S',
            MenuPaiId = ?,
            Ordem = 900,
            Icone = 'HISTORY',
            AdminLevel = ?,
            Ativo = 1,
            Sistema = 1

        WHERE Id = ?

        """,

        (
            pai_id,
            ADMIN_LEVEL,
            menu_id,
        ),
    )


def garantir_menu_auditoria(
    cursor,
):

    servicos_id = (
        buscar_menu_por_nome(
            cursor,
            "SERVIÇOS",
        )
        or
        buscar_menu_por_nome(
            cursor,
            "SERVICOS",
        )
    )

    if not servicos_id:

        servicos_id = inserir_menu(
            cursor=cursor,
            nome="Serviços",
            rota="",
            tipo="T",
            pai_id=None,
            ordem=5,
            icone="MISCELLANEOUS_SERVICES",
            admin_level=ADMIN_LEVEL,
            sistema=True,
        )

    sistema_id = (
        buscar_menu_por_nome_tipo(
            cursor,
            "SISTEMA",
            "M",
        )
        or
        buscar_menu_por_nome_tipo(
            cursor,
            "Sistema",
            "M",
        )
    )

    if not sistema_id:

        sistema_id = inserir_menu(
            cursor=cursor,
            nome="Sistema",
            rota="",
            tipo="M",
            pai_id=servicos_id,
            ordem=90,
            icone="SETTINGS",
            admin_level=ADMIN_LEVEL,
            sistema=True,
        )

    else:

        cursor.execute(

            """

            UPDATE Menu

            SET
                MenuPaiId = ?,
                Ordem = 90,
                Icone = 'SETTINGS',
                AdminLevel = ?,
                Ativo = 1,
                Sistema = 1

            WHERE Id = ?

            """,

            (
                servicos_id,
                ADMIN_LEVEL,
                sistema_id,
            ),
        )

    menu_id = buscar_menu_por_rota(
        cursor,
        "auditoria",
    )

    if menu_id:

        atualizar_menu_auditoria(
            cursor,
            menu_id,
            sistema_id,
        )

        LOGGER.info(
            "Menu Auditoria atualizado."
        )

        return

    inserir_menu(
        cursor=cursor,
        nome="Auditoria",
        rota="auditoria",
        tipo="S",
        pai_id=sistema_id,
        ordem=900,
        icone="HISTORY",
        admin_level=ADMIN_LEVEL,
        sistema=True,
    )

# =========================================================
# ACL ROOT
# =========================================================

def sincronizar_acl_root(
    cursor,
):

    perfil_root = get_perfil_id(
        cursor,
        "ROOT",
    )

    cursor.execute(

        """

        SELECT Id

        FROM Menu

        WHERE Ativo = 1

        ORDER BY
            ISNULL(MenuPaiId, Id),
            Ordem,
            Id

        """
    )

    for row in cursor.fetchall():

        inserir_perfil_menu(
            cursor,
            perfil_root,
            row[0],
            1,
            1,
            1,
        )

    LOGGER.info(
        "ACL ROOT sincronizada."
    )


# =========================================================
# ACL ADMIN
# =========================================================

def sincronizar_acl_admin(
    cursor,
):

    perfil_admin = get_perfil_id(
        cursor,
        "ADMIN",
    )

    rotas_admin = (
        "usuarios",
        "perfis",
        "menus",
        "auditoria",
    )

    for rota in rotas_admin:

        cursor.execute(

            """

            SELECT TOP 1 Id

            FROM Menu

            WHERE LOWER(Rota) = ?
            AND Ativo = 1

            """,

            (rota,),
        )

        row = cursor.fetchone()

        if not row:

            LOGGER.warning(
                "Menu ADMIN não encontrado: %s",
                rota,
            )

            continue

        menu_id = row[0]

        inserir_perfil_menu(
            cursor,
            perfil_admin,
            menu_id,
            1,
            1,
            1,
        )

    LOGGER.info(
        "ACL ADMIN sincronizada."
    )

# =========================================================
# REPAIR
# =========================================================

def repair_database(
    cursor,
):

    LOGGER.info(
        "Repair database."
    )

    validar_tabelas(
        cursor
    )

    garantir_perfis(
        cursor
    )

    garantir_root(
        cursor
    )

    garantir_admin(
        cursor
    )

    garantir_root_unico(
        cursor
    )

    validar_menu(
        cursor
    )

    garantir_menu_auditoria(
        cursor
    )

    invalidate_menu_cache()

    sincronizar_acl_root(
        cursor
    )

    sincronizar_acl_admin(
        cursor
    )

# =========================================================
# MIGRATION
# =========================================================

def executar_migrations(
    cursor,
):

    versao_atual = (
        get_schema_version(
            cursor
        )
    )

    LOGGER.info(

        (
            "Schema version atual: "
            f"{versao_atual}"
        )
    )

    if versao_atual >= SCHEMA_VERSION:

        return

    LOGGER.info(
        "Executando migrations."
    )

    # ==============================================
    # FUTURAS MIGRATIONS
    # ==============================================

    set_schema_version(

        cursor,

        SCHEMA_VERSION,
    )

# =========================================================
# BOOTSTRAP
# =========================================================

def iniciar_sistema():

    conn = None

    try:

        LOGGER.info(
            "Inicializando bootstrap."
        )

        conn = get_connection()

        cursor = conn.cursor()

        # ==========================================
        # MIGRATIONS
        # ==========================================

        executar_migrations(
            cursor
        )

        # ==========================================
        # REPAIR
        # ==========================================

        repair_database(
            cursor
        )

        # ==========================================
        # CACHE
        # ==========================================

        invalidate_menu_cache()

        conn.commit()

        registrar_evento_sistema(

            "BOOTSTRAP_OK",

            "Bootstrap executado.",
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
