from database.connection import get_connection

from services.identity_service import (
    coluna_eh_identity,
    obter_proximo_id,
)


# ==================================================
# HELPERS
# ==================================================

def to_int(valor):

    try:
        return int(valor)
    except:
        return 0


def to_float(valor):

    try:
        return float(
            str(valor).replace(",", ".")
        )
    except:
        return 0


# ==================================================
# VALIDAR DUPLICIDADE
# ==================================================

def existe_local(nome, local_id=None):

    conn = get_connection()

    cursor = conn.cursor()

    if local_id:

        cursor.execute("""
            SELECT COUNT(*)
            FROM LocalEvento
            WHERE
                NomeCasa = ?
                AND LocalEventoID <> ?
        """, (

            nome,

            local_id
        ))

    else:

        cursor.execute("""
            SELECT COUNT(*)
            FROM LocalEvento
            WHERE NomeCasa = ?
        """, (nome,))

    total = cursor.fetchone()[0]

    conn.close()

    return total > 0


# ==================================================
# CRIAR LOCAL
# ==================================================

def criar_local(dados):

    nome = dados["nome"].strip()

    if existe_local(nome):

        raise Exception(
            "Já existe um local com esse nome."
        )

    conn = get_connection()

    cursor = conn.cursor()

    try:

        if coluna_eh_identity(
            cursor,
            "LocalEvento",
            "LocalEventoID",
        ):

            cursor.execute("""
                INSERT INTO LocalEvento
                (
                    NomeCasa,
                    LocTipoID,
                    Endereco,
                    Responsavel,
                    Contato,
                    PossuiEstacionamento,
                    Observacoes
                )

                OUTPUT INSERTED.LocalEventoID

                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (

                nome,

                dados["loc_tipo_id"],

                dados["endereco"],

                dados["responsavel"],

                dados["contato"],

                0,

                dados["observacoes"]
            ))

            local_id = cursor.fetchone()[0]

        else:

            local_id = obter_proximo_id(
                cursor,
                "LocalEvento",
                "LocalEventoID",
            )

            cursor.execute("""
                INSERT INTO LocalEvento
                (
                    LocalEventoID,
                    NomeCasa,
                    LocTipoID,
                    Endereco,
                    Responsavel,
                    Contato,
                    PossuiEstacionamento,
                    Observacoes
                )

                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (

                local_id,

                nome,

                dados["loc_tipo_id"],

                dados["endereco"],

                dados["responsavel"],

                dados["contato"],

                0,

                dados["observacoes"]
            ))

        conn.commit()

        return local_id

    except Exception as e:

        conn.rollback()

        print(
            "Erro ao criar local:",
            e
        )

        raise

    finally:

        conn.close()


# ==================================================
# ATUALIZAR LOCAL
# ==================================================

def atualizar_local(local_id, dados):

    nome = dados["nome"].strip()

    if existe_local(

        nome,

        local_id
    ):

        raise Exception(
            "Já existe um local com esse nome."
        )

    conn = get_connection()

    cursor = conn.cursor()

    try:

        cursor.execute("""
            UPDATE LocalEvento
            SET
                NomeCasa = ?,
                LocTipoID = ?,
                Endereco = ?,
                Responsavel = ?,
                Contato = ?,
                Observacoes = ?
            WHERE LocalEventoID = ?
        """, (

            nome,

            dados["loc_tipo_id"],

            dados["endereco"],

            dados["responsavel"],

            dados["contato"],

            dados["observacoes"],

            local_id
        ))

        conn.commit()

    except Exception as e:

        conn.rollback()

        print(
            "Erro ao atualizar local:",
            e
        )

        raise

    finally:

        conn.close()


# ==================================================
# LISTAR LOCAIS
# ==================================================

def listar_locais():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            l.LocalEventoID,
            l.NomeCasa,
            ISNULL(t.NomeTipo, ''),
            l.Contato

        FROM LocalEvento l

        LEFT JOIN LocTipo t
            ON t.LocTipoID = l.LocTipoID

        ORDER BY
            l.NomeCasa
    """)

    rows = cursor.fetchall()

    conn.close()

    return rows


# ==================================================
# OBTER LOCAL
# ==================================================

def obter_local(local_id):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            LocalEventoID,
            NomeCasa,
            LocTipoID,
            Endereco,
            Responsavel,
            Contato,
            Observacoes

        FROM LocalEvento

        WHERE LocalEventoID = ?
    """, (local_id,))

    row = cursor.fetchone()

    conn.close()

    return row


# ==================================================
# VALIDAR DEPENDÊNCIAS
# ==================================================

def local_possui_ambientes(local_id):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM LocAmbientes
        WHERE LocalEventoID = ?
    """, (local_id,))

    total = cursor.fetchone()[0]

    conn.close()

    return total > 0


# ==================================================
# REMOVER ESTRUTURAS
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


# ==================================================
# EXCLUIR LOCAL
# ==================================================

def excluir_local(local_id):

    # ==============================================
    # PROTEÇÃO
    # ==============================================

    if local_possui_ambientes(local_id):

        raise Exception(
            "O local possui ambientes cadastrados."
        )

    conn = get_connection()

    cursor = conn.cursor()

    try:

        # ==========================================
        # REMOVE ESTRUTURAS
        # ==========================================

        cursor.execute("""
            DELETE FROM LocalEventoEstrutura
            WHERE LocalEventoID = ?
        """, (local_id,))

        # ==========================================
        # REMOVE LOCAL
        # ==========================================

        cursor.execute("""
            DELETE FROM LocalEvento
            WHERE LocalEventoID = ?
        """, (local_id,))

        conn.commit()

    except Exception as e:

        conn.rollback()

        print(
            "Erro ao excluir local:",
            e
        )

        raise

    finally:

        conn.close()


# ==================================================
# LISTAR AMBIENTES
# ==================================================

def listar_ambientes(local_id):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            AmbienteID,
            NomeAmbiente,
            CapacidadeSentado,
            CapacidadePe,
            PrecoBase

        FROM LocAmbientes

        WHERE LocalEventoID = ?

        ORDER BY NomeAmbiente
    """, (local_id,))

    rows = cursor.fetchall()

    conn.close()

    return rows


# ==================================================
# OBTER AMBIENTE
# ==================================================

def obter_ambiente(ambiente_id):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            AmbienteID,
            LocalEventoID,
            NomeAmbiente,
            CapacidadeSentado,
            CapacidadePe,
            Metragem,
            PeDireito,
            ArCondicionado,
            PrecoBase

        FROM LocAmbientes

        WHERE AmbienteID = ?
    """, (ambiente_id,))

    row = cursor.fetchone()

    conn.close()

    return row


# ==================================================
# SALVAR AMBIENTE
# ==================================================

def salvar_ambiente_db(dados):

    conn = get_connection()

    cursor = conn.cursor()

    sentado = to_int(
        dados["sentado"]
    )

    pe = to_int(
        dados["pe"]
    )

    metragem = to_float(
        dados["metragem"]
    )

    pe_direito = to_float(
        dados["pe_direito"]
    )

    preco = to_float(
        dados["preco"]
    )

    ar = int(bool(
        dados["ar"]
    ))

    try:

        # ==========================================
        # UPDATE
        # ==========================================

        if dados.get("id"):

            cursor.execute("""
                UPDATE LocAmbientes
                SET
                    NomeAmbiente = ?,
                    CapacidadeSentado = ?,
                    CapacidadePe = ?,
                    Metragem = ?,
                    PeDireito = ?,
                    ArCondicionado = ?,
                    PrecoBase = ?
                WHERE AmbienteID = ?
            """, (

                dados["nome"],

                sentado,

                pe,

                metragem,

                pe_direito,

                ar,

                preco,

                dados["id"]
            ))

        # ==========================================
        # INSERT
        # ==========================================

        else:

            if coluna_eh_identity(
                cursor,
                "LocAmbientes",
                "AmbienteID",
            ):

                cursor.execute("""
                    INSERT INTO LocAmbientes
                    (
                        LocalEventoID,
                        NomeAmbiente,
                        CapacidadeSentado,
                        CapacidadePe,
                        Metragem,
                        PeDireito,
                        ArCondicionado,
                        PrecoBase
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (

                    dados["local_id"],

                    dados["nome"],

                    sentado,

                    pe,

                    metragem,

                    pe_direito,

                    ar,

                    preco
                ))

            else:

                cursor.execute("""
                    INSERT INTO LocAmbientes
                    (
                        AmbienteID,
                        LocalEventoID,
                        NomeAmbiente,
                        CapacidadeSentado,
                        CapacidadePe,
                        Metragem,
                        PeDireito,
                        ArCondicionado,
                        PrecoBase
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (

                    obter_proximo_id(
                        cursor,
                        "LocAmbientes",
                        "AmbienteID",
                    ),

                    dados["local_id"],

                    dados["nome"],

                    sentado,

                    pe,

                    metragem,

                    pe_direito,

                    ar,

                    preco
                ))

        conn.commit()

    except Exception as e:

        conn.rollback()

        print(
            "Erro ao salvar ambiente:",
            e
        )

        raise

    finally:

        conn.close()


# ==================================================
# REMOVER AMBIENTE
# ==================================================

def remover_ambiente(ambiente_id):

    conn = get_connection()

    cursor = conn.cursor()

    try:

        cursor.execute("""
            DELETE FROM LocAmbientes
            WHERE AmbienteID = ?
        """, (ambiente_id,))

        conn.commit()

    except Exception as e:

        conn.rollback()

        print(
            "Erro ao remover ambiente:",
            e
        )

        raise

    finally:

        conn.close()
