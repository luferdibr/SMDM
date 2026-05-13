from database.connection import get_connection


# ==================================================
# LISTAR
# ==================================================

def listar_loc_tipos():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            LocTipoID,
            NomeTipo,
            Ativo
        FROM LocTipo
        ORDER BY
            NomeTipo
    """)

    rows = cursor.fetchall()

    conn.close()

    return rows


# ==================================================
# OBTER
# ==================================================

def obter_loc_tipo(tipo_id):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            LocTipoID,
            NomeTipo,
            Ativo
        FROM LocTipo
        WHERE LocTipoID = ?
    """, (tipo_id,))

    row = cursor.fetchone()

    conn.close()

    return row


# ==================================================
# VALIDAR DUPLICIDADE
# ==================================================

def existe_nome(nome, tipo_id=None):

    conn = get_connection()

    cursor = conn.cursor()

    if tipo_id:

        cursor.execute("""
            SELECT COUNT(*)
            FROM LocTipo
            WHERE
                NomeTipo = ?
                AND LocTipoID <> ?
        """, (

            nome,

            tipo_id
        ))

    else:

        cursor.execute("""
            SELECT COUNT(*)
            FROM LocTipo
            WHERE NomeTipo = ?
        """, (nome,))

    total = cursor.fetchone()[0]

    conn.close()

    return total > 0


# ==================================================
# SALVAR
# ==================================================

def salvar_loc_tipo(dados):

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

            "Já existe um tipo com esse nome."
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
                UPDATE LocTipo
                SET
                    NomeTipo = ?,
                    Ativo = ?
                WHERE LocTipoID = ?
            """, (

                nome,

                ativo,

                dados["id"]
            ))

        # ==========================================
        # INSERT
        # ==========================================

        else:

            cursor.execute("""
                INSERT INTO LocTipo
                (
                    NomeTipo,
                    Ativo
                )
                VALUES (?, ?)
            """, (

                nome,

                ativo
            ))

        conn.commit()

    except Exception as e:

        conn.rollback()

        print(

            "Erro ao salvar tipo:",

            e
        )

        raise

    finally:

        conn.close()


# ==================================================
# VALIDAR USO
# ==================================================

def tipo_em_uso(tipo_id):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM LocalEvento
        WHERE LocTipoID = ?
    """, (tipo_id,))

    total = cursor.fetchone()[0]

    conn.close()

    return total > 0


# ==================================================
# EXCLUIR
# ==================================================

def excluir_loc_tipo(tipo_id):

    if tipo_em_uso(tipo_id):

        raise Exception(

            "Tipo vinculado a locais cadastrados."
        )

    conn = get_connection()

    cursor = conn.cursor()

    try:

        cursor.execute("""
            DELETE FROM LocTipo
            WHERE LocTipoID = ?
        """, (tipo_id,))

        conn.commit()

    except Exception as e:

        conn.rollback()

        print(

            "Erro ao excluir tipo:",

            e
        )

        raise

    finally:

        conn.close()
