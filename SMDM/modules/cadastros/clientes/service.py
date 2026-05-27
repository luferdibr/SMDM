from datetime import datetime

from database.connection import get_connection

from services.identity_service import (
    coluna_eh_identity,
    obter_proximo_id,
)


def limpar_texto(valor):

    return str(
        valor or ""
    ).strip()


def normalizar_data(valor):

    valor = limpar_texto(
        valor
    )

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
        "Data de nascimento inválida. Use DD/MM/AAAA."
    )


def normalizar_dados(dados):

    nome = limpar_texto(
        dados.get("nome")
    )

    if not nome:
        raise Exception(
            "Informe o nome."
        )

    return {
        "id": dados.get("id"),
        "nome": nome,
        "municipio": limpar_texto(
            dados.get("municipio")
            or dados.get("cidade")
        ),
        "uf": limpar_texto(
            dados.get("uf")
            or dados.get("estado")
        ).upper(),
        "pais": limpar_texto(
            dados.get("pais")
        ) or "Brasil",
        "celular": limpar_texto(
            dados.get("celular")
        ),
        "data_nascimento": normalizar_data(
            dados.get("data_nascimento")
        ),
        "cpf": limpar_texto(
            dados.get("cpf")
        ),
        "email": limpar_texto(
            dados.get("email")
        ),
        "sexo": limpar_texto(
            dados.get("sexo")
        ),
        "receber_resumo": limpar_texto(
            dados.get("receber_resumo")
        ) or "Não",
        "profissao": limpar_texto(
            dados.get("profissao")
        ),
        "observacoes": limpar_texto(
            dados.get("observacoes")
        ),
        "primeiro_canal": limpar_texto(
            dados.get("primeiro_canal")
        ),
        "ativo": int(
            bool(
                dados.get(
                    "ativo",
                    True,
                )
            )
        ),
    }


def listar_clientes():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""

        SELECT
            ClienteID,
            Nome,
            ISNULL(CPF, ''),
            ISNULL(Celular, ''),
            ISNULL(Email, ''),
            ISNULL(Municipio, ''),
            ISNULL(UF, ''),
            Ativo

        FROM Cliente

        ORDER BY
            Nome

    """)

    rows = cursor.fetchall()

    conn.close()

    return rows


def obter_cliente(cliente_id):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""

        SELECT
            ClienteID,
            Nome,
            Municipio,
            UF,
            Pais,
            Celular,
            DataNascimento,
            CPF,
            Email,
            Sexo,
            ReceberResumoProgramacao,
            Profissao,
            Observacoes,
            PrimeiroCanalContato,
            Ativo

        FROM Cliente

        WHERE ClienteID = ?

    """, (
        cliente_id,
    ))

    row = cursor.fetchone()

    conn.close()

    return row


def existe_cpf(cpf, cliente_id=None):

    cpf = limpar_texto(
        cpf
    )

    if not cpf:
        return False

    conn = get_connection()

    cursor = conn.cursor()

    if cliente_id:

        cursor.execute("""

            SELECT COUNT(*)

            FROM Cliente

            WHERE CPF = ?
            AND ClienteID <> ?

        """, (
            cpf,
            cliente_id,
        ))

    else:

        cursor.execute("""

            SELECT COUNT(*)

            FROM Cliente

            WHERE CPF = ?

        """, (
            cpf,
        ))

    total = cursor.fetchone()[0]

    conn.close()

    return total > 0


def salvar_cliente(dados):

    dados = normalizar_dados(
        dados
    )

    if existe_cpf(
        dados["cpf"],
        dados.get("id"),
    ):

        raise Exception(
            "Já existe um cliente cadastrado com esse CPF."
        )

    conn = get_connection()

    cursor = conn.cursor()

    valores = (
        dados["nome"],
        dados["municipio"],
        dados["uf"],
        dados["pais"],
        dados["celular"],
        dados["data_nascimento"],
        dados["cpf"],
        dados["email"],
        dados["sexo"],
        dados["receber_resumo"],
        dados["profissao"],
        dados["observacoes"],
        dados["primeiro_canal"],
        dados["ativo"],
    )

    try:

        if dados.get("id"):

            cursor.execute("""

                UPDATE Cliente

                SET
                    Nome = ?,
                    Municipio = ?,
                    UF = ?,
                    Pais = ?,
                    Celular = ?,
                    DataNascimento = ?,
                    CPF = ?,
                    Email = ?,
                    Sexo = ?,
                    ReceberResumoProgramacao = ?,
                    Profissao = ?,
                    Observacoes = ?,
                    PrimeiroCanalContato = ?,
                    Ativo = ?,
                    AtualizadoEm = GETDATE()

                WHERE ClienteID = ?

            """, (
                *valores,
                dados["id"],
            ))

        else:

            if coluna_eh_identity(
                cursor,
                "Cliente",
                "ClienteID",
            ):

                cursor.execute("""

                    INSERT INTO Cliente
                    (
                        Nome,
                        Municipio,
                        UF,
                        Pais,
                        Celular,
                        DataNascimento,
                        CPF,
                        Email,
                        Sexo,
                        ReceberResumoProgramacao,
                        Profissao,
                        Observacoes,
                        PrimeiroCanalContato,
                        Ativo
                    )

                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

                """, valores)

            else:

                cursor.execute("""

                    INSERT INTO Cliente
                    (
                        ClienteID,
                        Nome,
                        Municipio,
                        UF,
                        Pais,
                        Celular,
                        DataNascimento,
                        CPF,
                        Email,
                        Sexo,
                        ReceberResumoProgramacao,
                        Profissao,
                        Observacoes,
                        PrimeiroCanalContato,
                        Ativo
                    )

                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

                """, (
                    obter_proximo_id(
                        cursor,
                        "Cliente",
                        "ClienteID",
                    ),
                    *valores,
                ))

        conn.commit()

    except Exception:

        conn.rollback()

        raise

    finally:

        conn.close()


def excluir_cliente(cliente_id):

    conn = get_connection()

    cursor = conn.cursor()

    try:

        cursor.execute("""

            DELETE FROM Cliente

            WHERE ClienteID = ?

        """, (
            cliente_id,
        ))

        conn.commit()

    except Exception:

        conn.rollback()

        raise

    finally:

        conn.close()
