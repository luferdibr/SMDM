from datetime import datetime

from database.connection import get_connection

from services.identity_service import (
    coluna_eh_identity,
    obter_proximo_id,
)


DISPONIBILIDADES = (
    "DISPONIVEL",
    "HIGIENIZANDO",
    "MANUTENCAO",
)

COLUNAS = [
    "NomeLongo",
    "NomeCurto",
    "DataAquisicao",
    "SedeID",
    "Disponibilidade",
    "DataUltimoUso",
    "UltimoAtorID",
    "Observacoes",
    "Ativo",
]


def limpar_texto(valor):
    return str(valor or "").strip()


def normalizar_bool(valor):
    if isinstance(valor, bool):
        return int(valor)

    return int(
        str(valor or "").strip().lower()
        in ("1", "true", "yes", "sim", "on")
    )


def normalizar_id(valor):
    valor = limpar_texto(valor)

    if not valor:
        return None

    return int(valor)


def normalizar_data(valor):
    valor = limpar_texto(valor)

    if not valor:
        return None

    for formato in (
        "%d/%m/%Y",
        "%Y-%m-%d",
    ):
        try:
            return datetime.strptime(
                valor,
                formato,
            ).date()
        except ValueError:
            pass

    raise Exception(
        "Data inválida. Use DD/MM/AAAA."
    )


def formatar_data(valor):
    if not valor:
        return ""

    if hasattr(valor, "strftime"):
        return valor.strftime("%d/%m/%Y")

    return str(valor)


def normalizar_disponibilidade(valor):
    valor = limpar_texto(valor).upper()

    if valor in (
        "DISPONÍVEL",
        "DISPONIVEL",
    ):
        return "DISPONIVEL"

    if valor in (
        "HIGIENIZANDO",
        "HIGIENIZACAO",
        "HIGIENIZAÇÃO",
    ):
        return "HIGIENIZANDO"

    if valor in (
        "MANUTENCAO",
        "MANUTENÇÃO",
        "MANUTENCAO",
    ):
        return "MANUTENCAO"

    if not valor:
        return "DISPONIVEL"

    raise Exception(
        "Disponibilidade inválida."
    )


def normalizar_dados(dados):
    nome_longo = limpar_texto(
        dados.get("nome_longo")
    )

    if not nome_longo:
        raise Exception(
            "Informe o nome longo do figurino."
        )

    return {
        "NomeLongo": nome_longo,
        "NomeCurto": limpar_texto(dados.get("nome_curto")),
        "DataAquisicao": normalizar_data(dados.get("data_aquisicao")),
        "SedeID": normalizar_id(dados.get("sede_id")),
        "Disponibilidade": normalizar_disponibilidade(
            dados.get("disponibilidade")
        ),
        "DataUltimoUso": normalizar_data(dados.get("data_ultimo_uso")),
        "UltimoAtorID": normalizar_id(dados.get("ultimo_ator_id")),
        "Observacoes": limpar_texto(dados.get("observacoes")),
        "Ativo": normalizar_bool(dados.get("ativo", True)),
    }


def listar_sedes():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT SedeID, NomeSede
        FROM SedesEmpresa
        WHERE Ativo = 1
        ORDER BY Fantasma, NomeSede
    """)

    rows = cursor.fetchall()
    conn.close()

    return rows


def listar_atores():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT AtorID, Nome
        FROM Ator
        WHERE Ativo = 1
        ORDER BY Nome
    """)

    rows = cursor.fetchall()
    conn.close()

    return rows


def listar_figurinos(filtro=""):
    conn = get_connection()
    cursor = conn.cursor()

    filtro = limpar_texto(filtro)

    query = """
        SELECT
            f.FigurinoID,
            f.NomeLongo,
            ISNULL(f.NomeCurto, ''),
            ISNULL(s.NomeSede, ''),
            f.Disponibilidade,
            f.DataUltimoUso,
            ISNULL(a.Nome, ''),
            f.Ativo
        FROM Figurino f
        LEFT JOIN SedesEmpresa s
            ON s.SedeID = f.SedeID
        LEFT JOIN Ator a
            ON a.AtorID = f.UltimoAtorID
    """

    params = []

    if filtro:
        query += """
            WHERE
                f.NomeLongo LIKE ?
                OR f.NomeCurto LIKE ?
        """
        params.extend([
            f"%{filtro}%",
            f"%{filtro}%",
        ])

    query += """
        ORDER BY
            f.Ativo DESC,
            f.NomeLongo
    """

    cursor.execute(
        query,
        tuple(params),
    )

    rows = cursor.fetchall()
    conn.close()

    return rows


def obter_figurino(figurino_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(f"""
        SELECT
            FigurinoID,
            {", ".join(COLUNAS)}
        FROM Figurino
        WHERE FigurinoID = ?
    """, (
        figurino_id,
    ))

    row = cursor.fetchone()
    conn.close()

    return row


def existe_nome(nome_longo, figurino_id=None):
    conn = get_connection()
    cursor = conn.cursor()

    if figurino_id:
        cursor.execute("""
            SELECT COUNT(*)
            FROM Figurino
            WHERE UPPER(NomeLongo) = ?
            AND FigurinoID <> ?
        """, (
            limpar_texto(nome_longo).upper(),
            figurino_id,
        ))
    else:
        cursor.execute("""
            SELECT COUNT(*)
            FROM Figurino
            WHERE UPPER(NomeLongo) = ?
        """, (
            limpar_texto(nome_longo).upper(),
        ))

    total = int(
        cursor.fetchone()[0] or 0
    )

    conn.close()

    return total > 0


def salvar_figurino(figurino_id, dados):
    dados = normalizar_dados(
        dados
    )

    if existe_nome(
        dados["NomeLongo"],
        figurino_id,
    ):
        raise Exception(
            "Já existe figurino com esse nome longo."
        )

    conn = get_connection()
    cursor = conn.cursor()

    valores = [
        dados[coluna]
        for coluna in COLUNAS
    ]

    try:
        if figurino_id:
            set_sql = ", ".join(
                f"{coluna} = ?"
                for coluna in COLUNAS
            )

            cursor.execute(f"""
                UPDATE Figurino
                SET
                    {set_sql},
                    AtualizadoEm = GETDATE()
                WHERE FigurinoID = ?
            """, (
                *valores,
                figurino_id,
            ))
        else:
            colunas_sql = ", ".join(
                COLUNAS
            )

            marcadores = ", ".join(
                "?"
                for _ in COLUNAS
            )

            if coluna_eh_identity(
                cursor,
                "Figurino",
                "FigurinoID",
            ):
                cursor.execute(f"""
                    INSERT INTO Figurino ({colunas_sql})
                    VALUES ({marcadores})
                """, valores)
            else:
                cursor.execute(f"""
                    INSERT INTO Figurino (FigurinoID, {colunas_sql})
                    VALUES (?, {marcadores})
                """, (
                    obter_proximo_id(
                        cursor,
                        "Figurino",
                        "FigurinoID",
                    ),
                    *valores,
                ))

        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


def excluir_figurino(figurino_id):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            DELETE FROM Figurino
            WHERE FigurinoID = ?
        """, (
            figurino_id,
        ))

        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()
