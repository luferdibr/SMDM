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
