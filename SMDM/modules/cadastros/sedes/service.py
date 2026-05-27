from database.connection import get_connection

import logging

from datetime import datetime

from database.connection import get_connection

from services.identity_service import (
    coluna_eh_identity,
    obter_proximo_id,
)

from services.documento_service import (
    normalizar_cnpj,
    sql_documento_normalizado,
)

from services.endereco_service import (
    geocodificar_endereco,
    geocodificacao_automatica_ativa,
    possui_endereco_minimo,
)


logger = logging.getLogger(__name__)


COLUNAS = [
    "NomeSede",
    "CNPJ",
    "Responsavel",
    "Telefone",
    "Celular",
    "Email",
    "CEP",
    "Logradouro",
    "Numero",
    "Complemento",
    "Bairro",
    "Municipio",
    "UF",
    "Pais",
    "Endereco",
    "Latitude",
    "Longitude",
    "FonteGeo",
    "DataGeo",
    "Operacional",
    "Fantasma",
    "Observacoes",
    "Ativo",
]


def limpar_texto(valor):

    return str(
        valor or ""
    ).strip()


def normalizar_bool(valor):

    if isinstance(valor, bool):
        return int(valor)

    if valor is None:
        return 0

    return int(
        str(valor).strip().lower() in (
            "1",
            "true",
            "yes",
            "sim",
            "on",
        )
    )


def montar_endereco(dados):

    endereco = limpar_texto(
        dados.get("Endereco")
    )

    if endereco:
        return endereco

    partes = [
        dados.get("Logradouro"),
        dados.get("Numero"),
        dados.get("Complemento"),
        dados.get("Bairro"),
        dados.get("Municipio"),
        dados.get("UF"),
        dados.get("CEP"),
    ]

    return ", ".join(
        limpar_texto(parte)
        for parte in partes
        if limpar_texto(parte)
    )


def chave_endereco(dados):

    return tuple(
        limpar_texto(dados.get(campo)).upper()
        for campo in (
            "CEP",
            "Logradouro",
            "Numero",
            "Complemento",
            "Bairro",
            "Municipio",
            "UF",
            "Pais",
        )
    )


def endereco_atual(cursor, sede_id):

    if not sede_id:
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
        FROM SedesEmpresa
        WHERE SedeID = ?
    """, (
        sede_id,
    ))

    row = cursor.fetchone()

    if not row:
        return None

    return dict(
        zip(
            (
                "CEP",
                "Logradouro",
                "Numero",
                "Complemento",
                "Bairro",
                "Municipio",
                "UF",
                "Pais",
            ),
            row,
        )
    )


def atualizar_geolocalizacao_se_necessario(cursor, sede_id, dados):

    atual = endereco_atual(cursor, sede_id)
    mudou = not atual or chave_endereco(atual) != chave_endereco(dados)
    dados["_GeoErro"] = ""

    if not mudou:
        return

    if dados.get("Latitude") and dados.get("Longitude"):
        return

    if not geocodificacao_automatica_ativa():
        dados["Latitude"] = 0
        dados["Longitude"] = 0
        dados["FonteGeo"] = "desativada"
        dados["DataGeo"] = None
        dados["_GeoErro"] = (
            "Geocodificação automática desativada na configuração."
        )
        return

    dados["Latitude"] = None
    dados["Longitude"] = None
    dados["FonteGeo"] = None
    dados["DataGeo"] = None

    if not possui_endereco_minimo(dados):
        return

    try:
        geo = geocodificar_endereco(dados)
        dados["Latitude"] = geo.get("latitude")
        dados["Longitude"] = geo.get("longitude")
        dados["FonteGeo"] = geo.get("fonte")
        dados["DataGeo"] = geo.get("data_geo")
    except Exception as ex:
        dados["_GeoErro"] = str(ex)
        logger.warning(
            "Geolocalizacao nao gerada para sede %s: %s",
            sede_id,
            ex,
        )


def normalizar_dados(dados):

    nome = limpar_texto(
        dados.get("nome_sede")
    )

    if not nome:
        raise Exception(
            "Informe o nome da sede."
        )

    normalizado = {
        "NomeSede": nome,
        "CNPJ": normalizar_cnpj(dados.get("cnpj")),
        "Responsavel": limpar_texto(dados.get("responsavel")),
        "Telefone": limpar_texto(dados.get("telefone")),
        "Celular": limpar_texto(dados.get("celular")),
        "Email": limpar_texto(dados.get("email")),
        "CEP": limpar_texto(dados.get("cep")),
        "Logradouro": limpar_texto(dados.get("logradouro")),
        "Numero": limpar_texto(dados.get("numero")),
        "Complemento": limpar_texto(dados.get("complemento")),
        "Bairro": limpar_texto(dados.get("bairro")),
        "Municipio": limpar_texto(dados.get("municipio")),
        "UF": limpar_texto(dados.get("uf")).upper(),
        "Pais": limpar_texto(dados.get("pais")) or "Brasil",
        "Endereco": limpar_texto(dados.get("endereco")),
        "Latitude": dados.get("latitude"),
        "Longitude": dados.get("longitude"),
        "FonteGeo": limpar_texto(dados.get("fonte_geo") or dados.get("fonte")),
        "DataGeo": dados.get("data_geo"),
        "Operacional": normalizar_bool(dados.get("operacional", True)),
        "Fantasma": normalizar_bool(dados.get("fantasma", False)),
        "Observacoes": limpar_texto(dados.get("observacoes")),
        "Ativo": normalizar_bool(dados.get("ativo", True)),
    }

    normalizado["Endereco"] = montar_endereco(
        normalizado
    )

    if normalizado["Latitude"] and normalizado["Longitude"] and not normalizado["DataGeo"]:
        normalizado["DataGeo"] = datetime.now()

    return normalizado


def existe_nome_sede(nome, sede_id=None):

    conn = get_connection()

    cursor = conn.cursor()

    if sede_id:

        cursor.execute("""
            SELECT COUNT(*)
            FROM SedesEmpresa
            WHERE UPPER(NomeSede) = ?
            AND SedeID <> ?
        """, (
            limpar_texto(nome).upper(),
            sede_id,
        ))

    else:

        cursor.execute("""
            SELECT COUNT(*)
            FROM SedesEmpresa
            WHERE UPPER(NomeSede) = ?
        """, (
            limpar_texto(nome).upper(),
        ))

    total = cursor.fetchone()[0]

    conn.close()

    return total > 0


def existe_cnpj(cnpj, sede_id=None):

    cnpj = normalizar_cnpj(
        cnpj
    )

    if not cnpj:
        return False

    conn = get_connection()

    cursor = conn.cursor()

    if sede_id:

        cursor.execute(f"""
            SELECT COUNT(*)
            FROM SedesEmpresa
            WHERE {sql_documento_normalizado("CNPJ")} = ?
            AND SedeID <> ?
        """, (
            cnpj,
            sede_id,
        ))

    else:

        cursor.execute(f"""
            SELECT COUNT(*)
            FROM SedesEmpresa
            WHERE {sql_documento_normalizado("CNPJ")} = ?
        """, (
            cnpj,
        ))

    total = cursor.fetchone()[0]

    conn.close()

    return total > 0


def listar_sedes():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            SedeID,
            NomeSede,
            ISNULL(Municipio, ''),
            ISNULL(UF, ''),
            ISNULL(CEP, ''),
            ISNULL(Responsavel, ''),
            ISNULL(Celular, ''),
            Operacional,
            Fantasma,
            Ativo
        FROM SedesEmpresa
        ORDER BY Fantasma, NomeSede
    """)

    rows = cursor.fetchall()

    conn.close()

    return rows


def obter_sede(sede_id):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(f"""
        SELECT
            SedeID,
            {", ".join(COLUNAS)}
        FROM SedesEmpresa
        WHERE SedeID = ?
    """, (
        sede_id,
    ))

    row = cursor.fetchone()

    conn.close()

    return row


def salvar_sede(sede_id, dados):

    dados = normalizar_dados(
        dados
    )

    if existe_nome_sede(
        dados["NomeSede"],
        sede_id,
    ):

        raise Exception(
            "Já existe uma sede cadastrada com esse nome."
        )

    if existe_cnpj(
        dados["CNPJ"],
        sede_id,
    ):

        raise Exception(
            "Já existe uma sede cadastrada com esse CNPJ."
        )

    conn = get_connection()

    cursor = conn.cursor()

    atualizar_geolocalizacao_se_necessario(
        cursor,
        sede_id,
        dados,
    )

    valores = [
        dados.get(coluna)
        for coluna in COLUNAS
    ]

    try:

        if sede_id:

            set_sql = ", ".join(
                f"{coluna} = ?"
                for coluna in COLUNAS
            )

            cursor.execute(f"""
                UPDATE SedesEmpresa
                SET
                    {set_sql},
                    AtualizadoEm = GETDATE()
                WHERE SedeID = ?
            """, (
                *valores,
                sede_id,
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
                "SedesEmpresa",
                "SedeID",
            ):

                cursor.execute(f"""
                    INSERT INTO SedesEmpresa ({colunas_sql})
                    VALUES ({marcadores})
                """, valores)

            else:

                cursor.execute(f"""
                    INSERT INTO SedesEmpresa (SedeID, {colunas_sql})
                    VALUES (?, {marcadores})
                """, (
                    obter_proximo_id(
                        cursor,
                        "SedesEmpresa",
                        "SedeID",
                    ),
                    *valores,
                ))

        conn.commit()
        return {
            "id": sede_id,
            "geo_erro": dados.get("_GeoErro", ""),
        }

    except Exception:

        conn.rollback()

        raise

    finally:

        conn.close()


def excluir_sede(sede_id):

    conn = get_connection()

    cursor = conn.cursor()

    try:

        cursor.execute("""
            DELETE FROM SedesEmpresa
            WHERE SedeID = ?
        """, (
            sede_id,
        ))

        conn.commit()

    except Exception:

        conn.rollback()

        raise

    finally:

        conn.close()
