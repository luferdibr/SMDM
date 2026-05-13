
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


def auditoria_segura(**kwargs):

    try:

        registrar_evento(**kwargs)

    except Exception:

        logging.exception(
            "AUDITORIA ERROR"
        )


def normalizar_nome(nome):

    return str(
        nome or ""
    ).strip().upper()


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


def get_admin_level(usuario):

    if not usuario:
        return 0

    return int(
        usuario.get(
            "admin_level",
            0
        )
    )


# ==================================================
# PERFIL
# ==================================================

def map_perfil(row):

    return {

        "id": row[0],

        "nome": row[1],

        "validade": row[2],

        "ativo": bool(row[3]),

        "admin_level": int(row[4] or 0),

        "sistema": bool(row[5])
    }


def get_perfil(
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
# VALIDADE
# ==================================================

def tratar_validade(
    admin_level,
    validade
):

    admin_level = int(
        admin_level or 0
    )

    # ==============================================
    # ROOT NÃO EXPIRA
    # ==============================================

    if admin_level >= ROOT_LEVEL:
        return None

    if validade in (
        None,
        "",
        "0"
    ):
        return None

    try:

        validade = int(validade)

        if validade < 1:
            return None

        return validade

    except Exception:

        return None


# ==================================================
# VALIDAR NOME
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


# ==================================================
# VALIDAR DUPLICIDADE
# ==================================================

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


# ==================================================
# SEGURANÇA
# ==================================================

def validar_permissao_perfil(
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

    usuario_level = get_admin_level(
        usuario
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
    # NÍVEL
    # ==============================================

    if perfil["admin_level"] >= usuario_level:

        raise Exception(
            "Sem permissão para alterar este perfil."
        )


def validar_nivel(
    usuario,
    admin_level
):

    admin_level = int(
        admin_level or 0
    )

    usuario_level = get_admin_level(
        usuario
    )

    # ==============================================
    # ROOT
    # ==============================================

    if usuario_level >= ROOT_LEVEL:
        return

    if admin_level >= usuario_level:

        raise Exception(
            "Nível administrativo inválido."
        )


# ==================================================
# PERFIL EM USO
# ==================================================

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

def listar_perfis(usuario):

    conn = None

    try:

        conn = get_connection()

        cursor = conn.cursor()

        usuario_level = get_admin_level(
            usuario
        )

        cursor.execute("""

            SELECT
                Id,
                Nome,
                ValidadeSenhaDias,
                Ativo,
                AdminLevel,
                Sistema

            FROM Perfis

            ORDER BY
                AdminLevel DESC,
                Nome

        """)

        rows = cursor.fetchall()

        perfis = []

        for row in rows:

            perfil = map_perfil(row)

            # ======================================
            # ROOT
            # ======================================

            if not is_root(usuario):

                if perfil["sistema"]:
                    continue

                if perfil["admin_level"] >= ROOT_LEVEL:
                    continue

                if perfil["admin_level"] >= usuario_level:
                    continue

            perfis.append(perfil)

        return retorno(
            True,
            dados=perfis
        )

    except Exception as ex:

        logging.exception(
            "PERFIL LIST ERROR"
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
# CRIAR
# ==================================================

def criar_perfil(
    usuario,
    nome,
    validade,
    admin_level,
    ativo=1,
    sistema=0
):

    conn = None

    try:

        nome = validar_nome(
            nome
        )

        admin_level = int(
            admin_level or 0
        )

        ativo = int(bool(ativo))

        sistema = int(bool(sistema))

        validar_nivel(
            usuario,
            admin_level
        )

        # ==========================================
        # ROOT
        # ==========================================

        if not is_root(usuario):

            sistema = 0

        validade = tratar_validade(
            admin_level,
            validade
        )

        conn = get_connection()

        cursor = conn.cursor()

        validar_duplicidade(
            cursor,
            nome
        )

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
            ativo,
            admin_level,
            sistema
        ))

        perfil_id = cursor.fetchone()[0]

        conn.commit()

        auditoria_segura(

            usuario_id=usuario.get("id"),

            login=usuario.get("login"),

            acao="CRIAR_PERFIL",

            entidade="Perfis",

            registro_id=perfil_id,

            detalhes=(
                f"nome={nome};"
                f"level={admin_level};"
                f"sistema={sistema}"
            )
        )

        return retorno(
            True,
            "Perfil criado.",
            perfil_id
        )

    except Exception as ex:

        if conn:
            conn.rollback()

        logging.exception(
            "PERFIL CREATE ERROR"
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
# ATUALIZAR
# ==================================================

def atualizar_perfil(
    usuario,
    perfil_id,
    nome,
    validade,
    admin_level,
    ativo=1,
    sistema=0
):

    conn = None

    try:

        if not perfil_id:

            raise Exception(
                "Perfil inválido."
            )

        nome = validar_nome(
            nome
        )

        admin_level = int(
            admin_level or 0
        )

        ativo = int(bool(ativo))

        sistema = int(bool(sistema))

        conn = get_connection()

        cursor = conn.cursor()

        perfil = get_perfil(
            cursor,
            perfil_id
        )

        validar_permissao_perfil(
            usuario,
            perfil
        )

        validar_nivel(
            usuario,
            admin_level
        )

        # ==========================================
        # ROOT
        # ==========================================

        if perfil_id == 1:

            raise Exception(
                "ROOT não pode ser alterado."
            )

        # ==========================================
        # PERFIL SISTEMA
        # ==========================================

        if perfil["sistema"]:

            raise Exception(
                "Perfil estrutural protegido."
            )

        # ==========================================
        # ADMIN
        # ==========================================

        if not is_root(usuario):

            sistema = 0

        validade = tratar_validade(
            admin_level,
            validade
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
            ativo,
            admin_level,
            sistema,
            perfil_id
        ))

        conn.commit()

        auditoria_segura(

            usuario_id=usuario.get("id"),

            login=usuario.get("login"),

            acao="ATUALIZAR_PERFIL",

            entidade="Perfis",

            registro_id=perfil_id
        )

        return retorno(
            True,
            "Perfil atualizado."
        )

    except Exception as ex:

        if conn:
            conn.rollback()

        logging.exception(
            "PERFIL UPDATE ERROR"
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
# EXCLUIR
# ==================================================

def excluir_perfil(
    usuario,
    perfil_id
):

    conn = None

    try:

        if not perfil_id:

            raise Exception(
                "Perfil inválido."
            )

        if perfil_id == 1:

            raise Exception(
                "ROOT não pode ser removido."
            )

        conn = get_connection()

        cursor = conn.cursor()

        perfil = get_perfil(
            cursor,
            perfil_id
        )

        validar_permissao_perfil(
            usuario,
            perfil
        )

        # ==========================================
        # SISTEMA
        # ==========================================

        if perfil["sistema"]:

            raise Exception(
                "Perfil estrutural protegido."
            )

        # ==========================================
        # EM USO
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

            mensagem = (
                "Perfil em uso. "
                "Perfil desativado."
            )

        else:

            cursor.execute("""

                DELETE FROM PerfilMenu

                WHERE PerfilId = ?

            """, (perfil_id,))

            cursor.execute("""

                DELETE FROM Perfis

                WHERE Id = ?

            """, (perfil_id,))

            mensagem = (
                "Perfil removido."
            )

        conn.commit()

        auditoria_segura(

            usuario_id=usuario.get("id"),

            login=usuario.get("login"),

            acao="EXCLUIR_PERFIL",

            entidade="Perfis",

            registro_id=perfil_id
        )

        return retorno(
            True,
            mensagem
        )

    except Exception as ex:

        if conn:
            conn.rollback()

        logging.exception(
            "PERFIL DELETE ERROR"
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