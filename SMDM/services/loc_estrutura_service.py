from database.connection import get_connection

from services.identity_service import (
    coluna_eh_identity,
    obter_proximo_id,
)


# ==================================================
# CRUD ESTRUTURA
# ==================================================

def listar_loc_estruturas():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            LocEstruturaID,
            NomeEstrutura,
            Ativo
        FROM LocEstrutura
        ORDER BY NomeEstrutura
    """)

    rows = cursor.fetchall()

    conn.close()

    return rows


def obter_loc_estrutura(estrutura_id):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            LocEstruturaID,
            NomeEstrutura,
            Ativo
        FROM LocEstrutura
        WHERE LocEstruturaID = ?
    """, (estrutura_id,))

    row = cursor.fetchone()

    conn.close()

    return row


# ==================================================
# VALIDAR DUPLICIDADE
# ==================================================

def existe_nome(nome, estrutura_id=None):

    conn = get_connection()

    cursor = conn.cursor()

    if estrutura_id:

        cursor.execute("""
            SELECT COUNT(*)
            FROM LocEstrutura
            WHERE
                NomeEstrutura = ?
                AND LocEstruturaID <> ?
        """, (

            nome,

            estrutura_id
        ))

    else:

        cursor.execute("""
            SELECT COUNT(*)
            FROM LocEstrutura
            WHERE NomeEstrutura = ?
        """, (nome,))

    total = cursor.fetchone()[0]

    conn.close()

    return total > 0


# ==================================================
# SALVAR ESTRUTURA
# ==================================================

def salvar_loc_estrutura(dados):

    nome = dados["nome"].strip()

    if not nome:

        raise Exception(
            "Informe o nome."
        )

    if existe_nome(

        nome,

        dados.get("id")
    ):

        raise Exception(
            "Já existe uma estrutura com esse nome."
        )

    conn = get_connection()

    cursor = conn.cursor()

    ativo = int(

        bool(
            dados["ativo"]
        )
    )

    try:

        # ==========================================
        # UPDATE
        # ==========================================

        if dados.get("id"):

            cursor.execute("""
                UPDATE LocEstrutura
                SET
                    NomeEstrutura = ?,
                    Ativo = ?
                WHERE LocEstruturaID = ?
            """, (

                nome,

                ativo,

                dados["id"]
            ))

        # ==========================================
        # INSERT
        # ==========================================

        else:

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
                    VALUES (?, ?)
                """, (

                    nome,

                    ativo
                ))

            else:

                cursor.execute("""
                    INSERT INTO LocEstrutura
                    (
                        LocEstruturaID,
                        NomeEstrutura,
                        Ativo
                    )
                    VALUES (?, ?, ?)
                """, (

                    obter_proximo_id(
                        cursor,
                        "LocEstrutura",
                        "LocEstruturaID",
                    ),

                    nome,

                    ativo
                ))

        conn.commit()

    except Exception as e:

        conn.rollback()

        print(
            "Erro ao salvar estrutura:",
            e
        )

        raise

    finally:

        conn.close()


# ==================================================
# VALIDAR USO
# ==================================================

def estrutura_em_uso(estrutura_id):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM LocalEventoEstrutura
        WHERE LocEstruturaID = ?
    """, (estrutura_id,))

    total = cursor.fetchone()[0]

    conn.close()

    return total > 0


# ==================================================
# EXCLUIR
# ==================================================

def excluir_loc_estrutura(estrutura_id):

    if estrutura_em_uso(estrutura_id):

        raise Exception(
            "Estrutura vinculada a locais cadastrados."
        )

    conn = get_connection()

    cursor = conn.cursor()

    try:

        cursor.execute("""
            DELETE FROM LocEstrutura
            WHERE LocEstruturaID = ?
        """, (estrutura_id,))

        conn.commit()

    except Exception as e:

        conn.rollback()

        print(
            "Erro ao excluir estrutura:",
            e
        )

        raise

    finally:

        conn.close()


# ==================================================
# LISTAR ESTRUTURAS DO LOCAL
# ==================================================

def listar_estruturas_local(local_id):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            le.LocEstruturaID
        FROM LocalEventoEstrutura le
        WHERE le.LocalEventoID = ?
    """, (local_id,))

    rows = cursor.fetchall()

    conn.close()

    return [r[0] for r in rows]


# ==================================================
# SALVAR ESTRUTURAS DO LOCAL
# ==================================================

def salvar_estruturas_local(local_id, estruturas):

    conn = get_connection()

    cursor = conn.cursor()

    try:

        # ==========================================
        # REMOVE ANTIGAS
        # ==========================================

        cursor.execute("""
            DELETE FROM LocalEventoEstrutura
            WHERE LocalEventoID = ?
        """, (local_id,))

        # ==========================================
        # INSERE NOVAS
        # ==========================================

        for estrutura_id in estruturas:

            cursor.execute("""
                INSERT INTO LocalEventoEstrutura
                (
                    LocalEventoID,
                    LocEstruturaID
                )
                VALUES (?, ?)
            """, (

                local_id,

                estrutura_id
            ))

        conn.commit()

    except Exception as e:

        conn.rollback()

        print(
            "Erro ao salvar estruturas:",
            e
        )

        raise

    finally:

        conn.close()


# ==================================================
# REMOVER ESTRUTURAS DO LOCAL
# ==================================================

def remover_estruturas_local(local_id):

    conn = get_connection()

    cursor = conn.cursor()

    try:

        cursor.execute("""
            DELETE FROM LocalEventoEstrutura
            WHERE LocalEventoID = ?
        """, (local_id,))

        conn.commit()

    except Exception as e:

        conn.rollback()

        print(
            "Erro ao remover estruturas:",
            e
        )

        raise

    finally:

        conn.close()
