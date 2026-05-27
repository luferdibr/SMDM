
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

NOMES_RESERVADOS = {

    "ROOT",

    "SYSTEM",

    "SYS"
}


# ==================================================
# LOGGER
# ==================================================

LOGGER = logging.getLogger(
    "MDM_PERFIL_SERVICE"
)


# ==================================================
# HELPERS
# ==================================================

def normalizar_nome(nome):

    return str(
        nome or ""
    ).strip().upper()


def get_admin_level(usuario):

    if not usuario:
        return 0

    return int(
        usuario.get(
            "admin_level",
            0
        )
    )


def is_root(usuario):

    return (

        get_admin_level(usuario)

        >= ROOT_LEVEL
    )


def is_admin(usuario):

    return (
        get_admin_level(usuario)
        >= ADMIN_LEVEL
    )


def validar_operador_admin(usuario_logado):

    if not is_admin(usuario_logado):

        raise Exception(
            "Acesso restrito à administração."
        )


def auditoria_segura(**kwargs):

    try:

        registrar_evento(**kwargs)

    except Exception:

        LOGGER.exception(
            "AUDITORIA ERROR"
        )


def map_perfil(row):

    return {

        "id": row[0],

        "nome": row[1],

        "validade_senha": row[2],

        "ativo": bool(row[3]),

        "admin_level": int(row[4] or 0),

        "sistema": bool(row[5])
    }


def listar_colunas(
    cursor,
    tabela
):

    cursor.execute("""

        SELECT COLUMN_NAME

        FROM INFORMATION_SCHEMA.COLUMNS

        WHERE TABLE_NAME = ?

    """, (tabela,))

    return {
        str(row[0]).strip().lower()
        for row in cursor.fetchall()
    }


def coluna_ou_default(
    colunas,
    nome,
    default_sql
):

    if nome.lower() in colunas:
        return nome

    return default_sql


def perfil_id_eh_identity(
    cursor
):

    cursor.execute("""

        SELECT COLUMNPROPERTY(
            OBJECT_ID('Perfis'),
            'Id',
            'IsIdentity'
        )

    """)

    row = cursor.fetchone()

    return bool(
        row
        and
        row[0]
    )


def obter_proximo_perfil_id(
    cursor
):

    cursor.execute("""

        SELECT ISNULL(MAX(Id), 0) + 1

        FROM Perfis

    """)

    return int(
        cursor.fetchone()[0]
        or 1
    )


# ==================================================
# PERFIL
# ==================================================

def obter_perfil(
    cursor,
    perfil_id
):

    cursor.execute("""

        SELECT
            Id,
            Nome,
            ValidadeSenhaDias,
            Ativo,
            AdminLevel,
            Sistema

        FROM Perfis

        WHERE Id = ?

    """, (perfil_id,))

    row = cursor.fetchone()

    if not row:
        return None

    return map_perfil(row)


# ==================================================
# VALIDAÇÕES
# ==================================================

def validar_nome(nome):

    nome = normalizar_nome(nome)

    if not nome:

        raise Exception(
            "Nome obrigatório."
        )

    if len(nome) < 3:

        raise Exception(
            "Nome muito curto."
        )

    if nome in NOMES_RESERVADOS:

        raise Exception(
            f"Nome reservado: {nome}"
        )

    return nome


def validar_admin_level(admin_level):

    try:

        admin_level = int(
            admin_level or 0
        )

    except Exception:

        raise Exception(
            "Admin level inválido."
        )

    if admin_level < 1:

        raise Exception(
            "Admin level inválido."
        )

    return admin_level


def validar_validade(validade):

    if validade in (
        None,
        "",
        "0"
    ):
        return None

    try:

        validade = int(validade)

    except Exception:

        raise Exception(
            "Validade inválida."
        )

    if validade < 1:

        raise Exception(
            "Validade inválida."
        )

    return validade


def validar_duplicidade(

    cursor,

    nome,

    perfil_id=None
):

    if perfil_id:

        cursor.execute("""

            SELECT COUNT(*)

            FROM Perfis

            WHERE
                UPPER(Nome) = ?
                AND Id <> ?

        """, (

            nome,

            perfil_id
        ))

    else:

        cursor.execute("""

            SELECT COUNT(*)

            FROM Perfis

            WHERE UPPER(Nome) = ?

        """, (nome,))

    if cursor.fetchone()[0]:

        raise Exception(
            "Já existe perfil com esse nome."
        )


def validar_perfil_alvo(

    usuario_logado,

    perfil
):

    if not perfil:

        raise Exception(
            "Perfil inválido."
        )

    validar_operador_admin(
        usuario_logado
    )

    if is_root(usuario_logado):
        return

    usuario_level = get_admin_level(
        usuario_logado
    )

    if perfil["sistema"]:

        raise Exception(
            "Perfil estrutural protegido."
        )

    if perfil["admin_level"] >= usuario_level:

        raise Exception(
            "Sem permissão para este perfil."
        )


def perfil_em_uso(

    cursor,

    perfil_id
):

    cursor.execute("""

        SELECT COUNT(*)

        FROM Usuarios

        WHERE PerfilId = ?

    """, (perfil_id,))

    return cursor.fetchone()[0] > 0


# ==================================================
# LISTAR
# ==================================================

def listar_perfis(filtro=""):

    conn = None

    try:

        conn = get_connection()

        cursor = conn.cursor()

        filtro = str(
            filtro or ""
        ).strip()

        colunas = listar_colunas(
            cursor,
            "Perfis"
        )

        validade_sql = coluna_ou_default(
            colunas,
            "ValidadeSenhaDias",
            "CAST(NULL AS INT)"
        )

        ativo_sql = coluna_ou_default(
            colunas,
            "Ativo",
            "CAST(1 AS BIT)"
        )

        admin_level_sql = coluna_ou_default(
            colunas,
            "AdminLevel",
            "CAST(0 AS INT)"
        )

        sistema_sql = coluna_ou_default(
            colunas,
            "Sistema",
            "CAST(0 AS BIT)"
        )

        query = f"""

            SELECT
                Id,
                Nome,
                {validade_sql},
                {ativo_sql},
                {admin_level_sql},
                {sistema_sql}

            FROM Perfis

        """

        params = []

        if filtro:

            query += """

                WHERE Nome LIKE ?

            """

            params.append(
                f"%{filtro}%"
            )

        query += f"""

            ORDER BY
                {admin_level_sql} DESC,
                Nome

        """

        cursor.execute(
            query,
            tuple(params)
        )

        rows = cursor.fetchall()

        retorno = []

        for row in rows:

            retorno.append(
                map_perfil(row)
            )

        LOGGER.info(
            "Perfis listados: %s",
            len(retorno)
        )

        return retorno

    except Exception:

        LOGGER.exception(
            "LIST PERFIS ERROR"
        )

        raise

    finally:

        try:

            if conn:
                conn.close()

        except Exception:
            pass


# ==================================================
# CRIAR
# ==================================================

def criar_perfil(

    dados,

    usuario_logado
):

    conn = None

    try:

        validar_operador_admin(
            usuario_logado
        )

        nome = validar_nome(
            dados.get("nome")
        )

        validade = validar_validade(
            dados.get(
                "validade_senha"
            )
        )

        admin_level = validar_admin_level(
            dados.get(
                "admin_level"
            )
        )

        ativo = bool(
            dados.get(
                "ativo",
                True
            )
        )

        sistema = bool(
            dados.get(
                "sistema",
                False
            )
        )

        if sistema and not is_root(
            usuario_logado
        ):

            raise Exception(
                "Somente ROOT pode criar perfil sistêmico."
            )

        if (

            admin_level >= ROOT_LEVEL

            and

            not is_root(usuario_logado)
        ):

            raise Exception(
                "Somente ROOT pode criar nível ROOT."
            )

        if (

            not is_root(usuario_logado)

            and

            admin_level >= get_admin_level(usuario_logado)
        ):

            raise Exception(
                "Sem permissão para criar perfil neste nível."
            )

        conn = get_connection()

        cursor = conn.cursor()

        validar_duplicidade(
            cursor,
            nome
        )

        LOGGER.info(
            "Criando perfil: nome=%s admin_level=%s ativo=%s sistema=%s",
            nome,
            admin_level,
            ativo,
            sistema,
        )

        if perfil_id_eh_identity(
            cursor
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

                VALUES (?, ?, ?, ?, ?)

            """, (

                nome,

                validade,

                int(ativo),

                admin_level,

                int(sistema)
            ))

            perfil_id = int(
                cursor.fetchone()[0]
            )

        else:

            perfil_id = obter_proximo_perfil_id(
                cursor
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

                VALUES (?, ?, ?, ?, ?, ?)

            """, (

                perfil_id,

                nome,

                validade,

                int(ativo),

                admin_level,

                int(sistema)
            ))

        conn.commit()

        auditoria_segura(

            usuario_id=usuario_logado.get("id"),

            login=usuario_logado.get("login"),

            acao="CRIAR_PERFIL",

            entidade="Perfis",

            registro_id=perfil_id,

            detalhes=nome
        )

        LOGGER.info(
            "Perfil criado: id=%s nome=%s",
            perfil_id,
            nome,
        )

        return perfil_id

    except Exception:

        if conn:
            conn.rollback()

        LOGGER.exception(
            "CREATE PERFIL ERROR"
        )

        raise

    finally:

        try:

            if conn:
                conn.close()

        except Exception:
            pass


# ==================================================
# UPDATE
# ==================================================

def atualizar_perfil(

    perfil_id,

    dados,

    usuario_logado
):

    conn = None

    try:

        conn = get_connection()

        cursor = conn.cursor()

        perfil = obter_perfil(
            cursor,
            perfil_id
        )

        validar_perfil_alvo(
            usuario_logado,
            perfil
        )

        nome = validar_nome(
            dados.get("nome")
        )

        validade = validar_validade(
            dados.get(
                "validade_senha"
            )
        )

        admin_level = validar_admin_level(
            dados.get(
                "admin_level"
            )
        )

        ativo = bool(
            dados.get(
                "ativo",
                True
            )
        )

        sistema = bool(
            dados.get(
                "sistema",
                False
            )
        )

        if perfil["sistema"]:

            sistema = True

        if (

            admin_level >= ROOT_LEVEL

            and

            not is_root(usuario_logado)
        ):

            raise Exception(
                "Somente ROOT pode alterar nível ROOT."
            )

        if (

            not is_root(usuario_logado)

            and

            admin_level >= get_admin_level(usuario_logado)
        ):

            raise Exception(
                "Sem permissão para definir este nível."
            )

        validar_duplicidade(

            cursor,

            nome,

            perfil_id
        )

        cursor.execute("""

            UPDATE Perfis

            SET
                Nome = ?,
                ValidadeSenhaDias = ?,
                Ativo = ?,
                AdminLevel = ?,
                Sistema = ?

            WHERE Id = ?

        """, (

            nome,

            validade,

            int(ativo),

            admin_level,

            int(sistema),

            perfil_id
        ))

        conn.commit()

        auditoria_segura(

            usuario_id=usuario_logado.get("id"),

            login=usuario_logado.get("login"),

            acao="ALTERAR_PERFIL",

            entidade="Perfis",

            registro_id=perfil_id,

            detalhes=nome
        )

        LOGGER.info(
            f"Perfil atualizado: {nome}"
        )

        return True

    except Exception:

        if conn:
            conn.rollback()

        LOGGER.exception(
            "UPDATE PERFIL ERROR"
        )

        raise

    finally:

        try:

            if conn:
                conn.close()

        except Exception:
            pass


# ==================================================
# DELETE
# ==================================================

def excluir_perfil(

    perfil_id,

    usuario_logado
):

    conn = None

    try:

        conn = get_connection()

        cursor = conn.cursor()

        perfil = obter_perfil(
            cursor,
            perfil_id
        )

        validar_perfil_alvo(
            usuario_logado,
            perfil
        )

        if perfil["admin_level"] >= ROOT_LEVEL:

            raise Exception(
                "Perfil ROOT não pode ser removido."
            )

        if perfil["sistema"]:

            raise Exception(
                "Perfil sistêmico não pode ser removido."
            )

        # ==========================================
        # PERFIL EM USO
        # ==========================================

        if perfil_em_uso(
            cursor,
            perfil_id
        ):

            cursor.execute("""

                UPDATE Perfis

                SET Ativo = 0

                WHERE Id = ?

            """, (perfil_id,))

            conn.commit()

            auditoria_segura(

                usuario_id=usuario_logado.get("id"),

                login=usuario_logado.get("login"),

                acao="DESATIVAR_PERFIL",

                entidade="Perfis",

                registro_id=perfil_id,

                detalhes=perfil["nome"]
            )

            LOGGER.info(
                f"Perfil desativado: "
                f"{perfil['nome']}"
            )

            return True

        # ==========================================
        # REMOVE PERMISSÕES
        # ==========================================

        cursor.execute("""

            DELETE FROM PerfilMenu

            WHERE PerfilId = ?

        """, (perfil_id,))

        # ==========================================
        # REMOVE PERFIL
        # ==========================================

        cursor.execute("""

            DELETE FROM Perfis

            WHERE Id = ?

        """, (perfil_id,))

        conn.commit()

        auditoria_segura(

            usuario_id=usuario_logado.get("id"),

            login=usuario_logado.get("login"),

            acao="EXCLUIR_PERFIL",

            entidade="Perfis",

            registro_id=perfil_id,

            detalhes=perfil["nome"]
        )

        LOGGER.info(
            f"Perfil removido: "
            f"{perfil['nome']}"
        )

        return True

    except Exception:

        if conn:
            conn.rollback()

        LOGGER.exception(
            "DELETE PERFIL ERROR"
        )

        raise

    finally:

        try:

            if conn:
                conn.close()

        except Exception:
            pass
