from database.connection import get_connection


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
# LISTAR LOCAIS COMBO
# ==================================================

def listar_locais_combo():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""

        SELECT
            LocalEventoID,
            NomeCasa

        FROM LocalEvento

        ORDER BY NomeCasa

    """)

    rows = cursor.fetchall()

    conn.close()

    return rows


# ==================================================
# LISTAR AMBIENTES
# ==================================================

def listar_ambientes(local_id=None):

    conn = get_connection()

    cursor = conn.cursor()

    # ==============================================
    # COM FILTRO
    # ==============================================

    if local_id:

        cursor.execute("""

            SELECT
                a.AmbienteID,
                l.NomeCasa,
                a.NomeAmbiente,
                a.CapacidadeSentado,
                a.CapacidadePe,
                a.Metragem,
                a.PrecoBase

            FROM LocAmbientes a

            INNER JOIN LocalEvento l
                ON l.LocalEventoID = a.LocalEventoID

            WHERE a.LocalEventoID = ?

            ORDER BY
                a.NomeAmbiente

        """, (local_id,))

    # ==============================================
    # SEM FILTRO
    # ==============================================

    else:

        cursor.execute("""

            SELECT
                a.AmbienteID,
                l.NomeCasa,
                a.NomeAmbiente,
                a.CapacidadeSentado,
                a.CapacidadePe,
                a.Metragem,
                a.PrecoBase

            FROM LocAmbientes a

            INNER JOIN LocalEvento l
                ON l.LocalEventoID = a.LocalEventoID

            ORDER BY
                l.NomeCasa,
                a.NomeAmbiente

        """)

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
            PrecoBase,
            SharePointID

        FROM LocAmbientes

        WHERE AmbienteID = ?

    """, (ambiente_id,))

    row = cursor.fetchone()

    conn.close()

    return row


# ==================================================
# VALIDAR DUPLICIDADE
# ==================================================

def existe_ambiente(
    local_id,
    nome,
    ambiente_id=None
):

    conn = get_connection()

    cursor = conn.cursor()

    # ==============================================
    # UPDATE
    # ==============================================

    if ambiente_id:

        cursor.execute("""

            SELECT COUNT(*)

            FROM LocAmbientes

            WHERE
                LocalEventoID = ?
                AND NomeAmbiente = ?
                AND AmbienteID <> ?

        """, (

            local_id,

            nome,

            ambiente_id
        ))

    # ==============================================
    # INSERT
    # ==============================================

    else:

        cursor.execute("""

            SELECT COUNT(*)

            FROM LocAmbientes

            WHERE
                LocalEventoID = ?
                AND NomeAmbiente = ?

        """, (

            local_id,

            nome
        ))

    total = cursor.fetchone()[0]

    conn.close()

    return total > 0


# ==================================================
# SALVAR AMBIENTE
# ==================================================

def salvar_ambiente(dados):

    conn = get_connection()

    cursor = conn.cursor()

    local_id = dados["local_id"]

    nome = dados["nome"].strip()

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

    # ==============================================
    # DUPLICIDADE
    # ==============================================

    if existe_ambiente(

        local_id,

        nome,

        dados.get("id")
    ):

        raise Exception(
            "Já existe um ambiente com esse nome para o local."
        )

    try:

        # ==========================================
        # UPDATE
        # ==========================================

        if dados.get("id"):

            cursor.execute("""

                UPDATE LocAmbientes
                SET
                    LocalEventoID = ?,
                    NomeAmbiente = ?,
                    CapacidadeSentado = ?,
                    CapacidadePe = ?,
                    Metragem = ?,
                    PeDireito = ?,
                    ArCondicionado = ?,
                    PrecoBase = ?

                WHERE AmbienteID = ?

            """, (

                local_id,

                nome,

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

                local_id,

                nome,

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
# EXCLUIR AMBIENTE
# ==================================================

def excluir_ambiente(ambiente_id):

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
            "Erro ao excluir ambiente:",
            e
        )

        raise

    finally:

        conn.close()
