from datetime import datetime

from datetime import datetime

from database.connection import get_connection

from services.identity_service import (
    coluna_eh_identity,
    obter_proximo_id,
)

from services.documento_service import (
    normalizar_cpf,
    sql_documento_normalizado,
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
        "cpf": normalizar_cpf(
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

    cpf = normalizar_cpf(
        cpf
    )

    if not cpf:
        return False

    conn = get_connection()

    cursor = conn.cursor()

    if cliente_id:

        cursor.execute(f"""

            SELECT COUNT(*)

            FROM Cliente

            WHERE {sql_documento_normalizado("CPF")} = ?
            AND ClienteID <> ?

        """, (
            cpf,
            cliente_id,
        ))

    else:

        cursor.execute(f"""

            SELECT COUNT(*)

            FROM Cliente

            WHERE {sql_documento_normalizado("CPF")} = ?

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

            cliente_id = dados["id"]

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

                    OUTPUT INSERTED.ClienteID

                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

                """, valores)

                cliente_id = cursor.fetchone()[0]

            else:

                cliente_id = obter_proximo_id(
                    cursor,
                    "Cliente",
                    "ClienteID",
                )

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
                    cliente_id,
                    *valores,
                ))

        conn.commit()
        return cliente_id

    except Exception:

        conn.rollback()

        raise

    finally:

        conn.close()


def listar_aniversariantes(cliente_id):

    if not cliente_id:
        return []

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""

        SELECT
            ClienteAniversarianteID,
            Relacao,
            Nome,
            DataNascimento,
            Ativo

        FROM ClienteAniversariante

        WHERE ClienteID = ?

        ORDER BY
            Nome

    """, (
        cliente_id,
    ))

    rows = cursor.fetchall()

    conn.close()

    return rows


def salvar_aniversariante(dados):

    cliente_id = dados.get("cliente_id")

    if not cliente_id:
        raise Exception(
            "Salve o cliente antes de cadastrar aniversariantes."
        )

    nome = limpar_texto(
        dados.get("nome")
    )

    if not nome:
        raise Exception(
            "Informe o nome do aniversariante."
        )

    relacao = limpar_texto(
        dados.get("relacao")
    )

    data_nascimento = normalizar_data(
        dados.get("data_nascimento")
    )

    ativo = int(
        bool(
            dados.get(
                "ativo",
                True,
            )
        )
    )

    conn = get_connection()

    cursor = conn.cursor()

    try:

        if dados.get("id"):

            cursor.execute("""

                UPDATE ClienteAniversariante

                SET
                    Relacao = ?,
                    Nome = ?,
                    DataNascimento = ?,
                    Ativo = ?,
                    AtualizadoEm = GETDATE()

                WHERE ClienteAniversarianteID = ?
                AND ClienteID = ?

            """, (
                relacao,
                nome,
                data_nascimento,
                ativo,
                dados["id"],
                cliente_id,
            ))

        elif coluna_eh_identity(
            cursor,
            "ClienteAniversariante",
            "ClienteAniversarianteID",
        ):

            cursor.execute("""

                INSERT INTO ClienteAniversariante
                (
                    ClienteID,
                    Relacao,
                    Nome,
                    DataNascimento,
                    Ativo
                )

                VALUES (?, ?, ?, ?, ?)

            """, (
                cliente_id,
                relacao,
                nome,
                data_nascimento,
                ativo,
            ))

        else:

            cursor.execute("""

                INSERT INTO ClienteAniversariante
                (
                    ClienteAniversarianteID,
                    ClienteID,
                    Relacao,
                    Nome,
                    DataNascimento,
                    Ativo
                )

                VALUES (?, ?, ?, ?, ?, ?)

            """, (
                obter_proximo_id(
                    cursor,
                    "ClienteAniversariante",
                    "ClienteAniversarianteID",
                ),
                cliente_id,
                relacao,
                nome,
                data_nascimento,
                ativo,
            ))

        conn.commit()

    except Exception:

        conn.rollback()

        raise

    finally:

        conn.close()


def excluir_aniversariante(aniversariante_id):

    conn = get_connection()

    cursor = conn.cursor()

    try:

        cursor.execute("""

            DELETE FROM ClienteAniversariante

            WHERE ClienteAniversarianteID = ?

        """, (
            aniversariante_id,
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

            DELETE FROM ClienteAniversariante

            WHERE ClienteID = ?

        """, (
            cliente_id,
        ))

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
