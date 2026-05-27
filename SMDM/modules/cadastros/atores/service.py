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

from services.endereco_service import (
    geocodificar_endereco,
    possui_endereco_minimo,
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


def chave_endereco(dados):

    return tuple(
        limpar_texto(dados.get(campo)).upper()
        for campo in (
            "cep",
            "logradouro",
            "numero",
            "complemento",
            "bairro",
            "municipio",
            "uf",
            "pais",
        )
    )


def endereco_atual(cursor, ator_id):

    if not ator_id:
        return None

    cursor.execute("""
        SELECT
            CEP,
            Logradouro,
            Numero,
            Complemento,
            Bairro,
            Municipio,
            UF,
            Pais
        FROM Ator
        WHERE AtorID = ?
    """, (
        ator_id,
    ))

    row = cursor.fetchone()

    if not row:
        return None

    return dict(
        zip(
            (
                "cep",
                "logradouro",
                "numero",
                "complemento",
                "bairro",
                "municipio",
                "uf",
                "pais",
            ),
            row,
        )
    )


def atualizar_geolocalizacao_se_necessario(cursor, ator_id, dados):

    atual = endereco_atual(cursor, ator_id)
    mudou = not atual or chave_endereco(atual) != chave_endereco(dados)

    if not mudou:
        return

    dados["latitude"] = None
    dados["longitude"] = None
    dados["fonte_geo"] = None
    dados["data_geo"] = None

    if not possui_endereco_minimo(dados):
        return

    try:
        geo = geocodificar_endereco(dados)
        dados["latitude"] = geo.get("latitude")
        dados["longitude"] = geo.get("longitude")
        dados["fonte_geo"] = geo.get("fonte")
        dados["data_geo"] = geo.get("data_geo")
    except Exception:
        pass


def normalizar_dados(dados):

    nome = limpar_texto(
        dados.get("nome")
    )

    if not nome:
        raise Exception(
            "Informe o nome."
        )

    logradouro = limpar_texto(
        dados.get("logradouro")
    )

    numero = limpar_texto(
        dados.get("numero")
    )

    complemento = limpar_texto(
        dados.get("complemento")
    )

    bairro = limpar_texto(
        dados.get("bairro")
    )

    municipio = limpar_texto(
        dados.get("municipio")
        or dados.get("cidade")
    )

    uf = limpar_texto(
        dados.get("uf")
        or dados.get("estado")
    ).upper()

    endereco = limpar_texto(
        dados.get("endereco")
    )

    if not endereco:

        partes = [
            logradouro,
            numero,
            complemento,
            bairro,
            municipio,
            uf,
        ]

        endereco = ", ".join(
            parte
            for parte in partes
            if parte
        )

    retorno = {
        "id": dados.get("id"),
        "nome": nome,
        "nome_profissional": limpar_texto(
            dados.get("nome_profissional")
        ),
        "cep": limpar_texto(
            dados.get("cep")
        ),
        "logradouro": logradouro,
        "numero": numero,
        "complemento": complemento,
        "bairro": bairro,
        "municipio": municipio,
        "uf": uf,
        "pais": limpar_texto(
            dados.get("pais")
        ) or "Brasil",
        "endereco": endereco,
        "latitude": dados.get("latitude"),
        "longitude": dados.get("longitude"),
        "fonte_geo": limpar_texto(dados.get("fonte_geo") or dados.get("fonte")),
        "data_geo": dados.get("data_geo"),
        "nacionalidade": limpar_texto(
            dados.get("nacionalidade")
        ),
        "telefone": limpar_texto(
            dados.get("telefone")
        ),
        "celular": limpar_texto(
            dados.get("celular")
        ),
        "data_nascimento": normalizar_data(
            dados.get("data_nascimento")
        ),
        "cpf": normalizar_cpf(
            dados.get("cpf")
        ),
        "rg": limpar_texto(
            dados.get("rg")
        ),
        "email": limpar_texto(
            dados.get("email")
        ),
        "ensino": limpar_texto(
            dados.get("ensino")
        ),
        "sexo": limpar_texto(
            dados.get("sexo")
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

    if retorno["latitude"] and retorno["longitude"] and not retorno["data_geo"]:
        retorno["data_geo"] = datetime.now()

    return retorno


def listar_atores():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""

        SELECT
            AtorID,
            Nome,
            ISNULL(NomeProfissional, ''),
            ISNULL(CPF, ''),
            ISNULL(Celular, ''),
            ISNULL(Email, ''),
            Ativo

        FROM Ator

        ORDER BY
            Nome

    """)

    rows = cursor.fetchall()

    conn.close()

    return rows


def obter_ator(ator_id):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""

        SELECT
            AtorID,
            Nome,
            NomeProfissional,
            CEP,
            Logradouro,
            Numero,
            Complemento,
            Bairro,
            Municipio,
            UF,
            Pais,
            Endereco,
            Latitude,
            Longitude,
            FonteGeo,
            DataGeo,
            Nacionalidade,
            Telefone,
            Celular,
            DataNascimento,
            CPF,
            RG,
            Email,
            Ensino,
            Sexo,
            Ativo

        FROM Ator

        WHERE AtorID = ?

    """, (
        ator_id,
    ))

    row = cursor.fetchone()

    conn.close()

    return row


def existe_cpf(cpf, ator_id=None):

    cpf = normalizar_cpf(
        cpf
    )

    if not cpf:
        return False

    conn = get_connection()

    cursor = conn.cursor()

    if ator_id:

        cursor.execute(f"""

            SELECT COUNT(*)

            FROM Ator

            WHERE {sql_documento_normalizado("CPF")} = ?
            AND AtorID <> ?

        """, (
            cpf,
            ator_id,
        ))

    else:

        cursor.execute(f"""

            SELECT COUNT(*)

            FROM Ator

            WHERE {sql_documento_normalizado("CPF")} = ?

        """, (
            cpf,
        ))

    total = cursor.fetchone()[0]

    conn.close()

    return total > 0


def salvar_ator(dados):

    dados = normalizar_dados(
        dados
    )

    if existe_cpf(
        dados["cpf"],
        dados.get("id"),
    ):

        raise Exception(
            "Já existe um ator cadastrado com esse CPF."
        )

    conn = get_connection()

    cursor = conn.cursor()

    atualizar_geolocalizacao_se_necessario(
        cursor,
        dados.get("id"),
        dados,
    )

    valores = (
        dados["nome"],
        dados["nome_profissional"],
        dados["cep"],
        dados["logradouro"],
        dados["numero"],
        dados["complemento"],
        dados["bairro"],
        dados["municipio"],
        dados["uf"],
            dados["pais"],
            dados["endereco"],
            dados["latitude"],
            dados["longitude"],
            dados["fonte_geo"],
            dados["data_geo"],
            dados["nacionalidade"],
        dados["telefone"],
        dados["celular"],
        dados["data_nascimento"],
        dados["cpf"],
        dados["rg"],
        dados["email"],
        dados["ensino"],
        dados["sexo"],
        dados["ativo"],
    )

    try:

        if dados.get("id"):

            cursor.execute("""

                UPDATE Ator

                SET
                    Nome = ?,
                    NomeProfissional = ?,
                    CEP = ?,
                    Logradouro = ?,
                    Numero = ?,
                    Complemento = ?,
                    Bairro = ?,
                    Municipio = ?,
                    UF = ?,
                    Pais = ?,
                    Endereco = ?,
                    Latitude = ?,
                    Longitude = ?,
                    FonteGeo = ?,
                    DataGeo = ?,
                    Nacionalidade = ?,
                    Telefone = ?,
                    Celular = ?,
                    DataNascimento = ?,
                    CPF = ?,
                    RG = ?,
                    Email = ?,
                    Ensino = ?,
                    Sexo = ?,
                    Ativo = ?,
                    AtualizadoEm = GETDATE()

                WHERE AtorID = ?

            """, (
                *valores,
                dados["id"],
            ))

        else:

            if coluna_eh_identity(
                cursor,
                "Ator",
                "AtorID",
            ):

                cursor.execute("""

                    INSERT INTO Ator
                    (
                        Nome,
                        NomeProfissional,
                        CEP,
                        Logradouro,
                        Numero,
                        Complemento,
                        Bairro,
                        Municipio,
                        UF,
                        Pais,
                        Endereco,
                        Latitude,
                        Longitude,
                        FonteGeo,
                        DataGeo,
                        Nacionalidade,
                        Telefone,
                        Celular,
                        DataNascimento,
                        CPF,
                        RG,
                        Email,
                        Ensino,
                        Sexo,
                        Ativo
                    )

                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

                """, valores)

            else:

                cursor.execute("""

                    INSERT INTO Ator
                    (
                        AtorID,
                        Nome,
                        NomeProfissional,
                        CEP,
                        Logradouro,
                        Numero,
                        Complemento,
                        Bairro,
                        Municipio,
                        UF,
                        Pais,
                        Endereco,
                        Latitude,
                        Longitude,
                        FonteGeo,
                        DataGeo,
                        Nacionalidade,
                        Telefone,
                        Celular,
                        DataNascimento,
                        CPF,
                        RG,
                        Email,
                        Ensino,
                        Sexo,
                        Ativo
                    )

                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

                """, (
                    obter_proximo_id(
                        cursor,
                        "Ator",
                        "AtorID",
                    ),
                    *valores,
                ))

        conn.commit()

    except Exception:

        conn.rollback()

        raise

    finally:

        conn.close()


def excluir_ator(ator_id):

    conn = get_connection()

    cursor = conn.cursor()

    try:

        cursor.execute("""

            DELETE FROM Ator

            WHERE AtorID = ?

        """, (
            ator_id,
        ))

        conn.commit()

    except Exception:

        conn.rollback()

        raise

    finally:

        conn.close()
