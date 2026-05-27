import logging

from database.connection import get_connection

from datetime import datetime

from services.identity_service import (
    coluna_eh_identity,
    obter_proximo_id,
)

from services.documento_service import (
    normalizar_documento,
    sql_documento_normalizado,
)

from services.endereco_service import (
    geocodificar_endereco,
    geocodificacao_automatica_ativa,
    possui_endereco_minimo,
)


logger = logging.getLogger(__name__)


COLUNAS_LOCAL = [
    "NomeCasa",
    "NomeFantasia",
    "LocTipoID",
    "CNPJ",
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
    "Responsavel",
    "Contato",
    "Telefone",
    "Celular",
    "Email",
    "Site",
    "Instagram",
    "Facebook",
    "OutrasRedes",
    "HorarioFuncionamento",
    "Contato1Nome",
    "Contato1Telefone",
    "Contato1Cargo",
    "Contato2Nome",
    "Contato2Telefone",
    "Contato2Cargo",
    "Contato3Nome",
    "Contato3Telefone",
    "Contato3Cargo",
    "QuemIndicou",
    "PossuiEstacionamento",
    "Observacoes",
    "Ativo",
    "CaptadoWeb",
    "ComplementadoWeb",
    "CadastroValidado",
    "PesquisaIncompleta",
    "NecessitaComplemento",
    "NecessitaRevisao",
    "PontuacaoOrigemWeb",
    "FonteOrigemWeb",
    "DataOrigemWeb",
    "LocalPesquisaWebId",
    "DataValidacaoCadastro",
    "ObservacaoPesquisa",
]


def limpar_texto(valor):

    return str(
        valor or ""
    ).strip()


def to_int(valor):

    try:
        return int(valor)
    except Exception:
        return 0


def to_float(valor):

    try:
        return float(
            str(valor or "").replace(",", ".")
        )
    except Exception:
        return 0


def to_float_or_none(valor):

    if valor in ("", None):
        return None

    try:
        return float(
            str(valor).replace(",", ".")
        )
    except Exception:
        return None


def to_int_or_none(valor):

    if valor in ("", None):
        return None

    try:
        return int(valor)
    except Exception:
        return None


def normalizar_data_hora(valor):

    if valor in ("", None):
        return None

    if not isinstance(valor, str):
        return valor

    texto = valor.strip()

    for formato in (
        "%d/%m/%Y %H:%M",
        "%d/%m/%Y %H:%M:%S",
        "%d/%m/%Y",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d",
    ):
        try:
            return datetime.strptime(
                texto,
                formato,
            )
        except ValueError:
            pass

    return None


def normalizar_id(valor, nome_campo="ID"):

    try:
        return int(valor)
    except Exception:
        raise Exception(
            f"{nome_campo} invalido."
        )


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


def endereco_atual(cursor, local_id):

    if not local_id:
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
        FROM LocalEvento
        WHERE LocalEventoID = ?
    """, (
        local_id,
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


def atualizar_geolocalizacao_se_necessario(cursor, local_id, dados):

    atual = endereco_atual(cursor, local_id)
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
            "Geolocalizacao nao gerada para local %s: %s",
            local_id,
            ex,
        )


def normalizar_local(dados):

    nome = limpar_texto(
        dados.get("nome")
    )

    if not nome:
        raise Exception(
            "Informe o nome do local."
        )

    loc_tipo_id = dados.get("loc_tipo_id")

    if loc_tipo_id in ("", None):
        loc_tipo_id = None
    else:
        loc_tipo_id = int(loc_tipo_id)

    normalizado = {
        "NomeCasa": nome,
        "NomeFantasia": limpar_texto(dados.get("nome_fantasia")),
        "LocTipoID": loc_tipo_id,
        "CNPJ": normalizar_documento(
            dados.get("cnpj"),
            campo="CPF/CNPJ",
        ),
        "CEP": limpar_texto(dados.get("cep")),
        "Logradouro": limpar_texto(dados.get("logradouro")),
        "Numero": limpar_texto(dados.get("numero")),
        "Complemento": limpar_texto(dados.get("complemento")),
        "Bairro": limpar_texto(dados.get("bairro")),
        "Municipio": limpar_texto(dados.get("municipio") or dados.get("cidade")),
        "UF": limpar_texto(dados.get("uf") or dados.get("estado")).upper(),
        "Pais": limpar_texto(dados.get("pais")) or "Brasil",
        "Endereco": limpar_texto(dados.get("endereco")),
        "Latitude": dados.get("latitude"),
        "Longitude": dados.get("longitude"),
        "FonteGeo": limpar_texto(dados.get("fonte_geo") or dados.get("fonte")),
        "DataGeo": dados.get("data_geo"),
        "Responsavel": limpar_texto(dados.get("responsavel")),
        "Contato": limpar_texto(dados.get("contato")),
        "Telefone": limpar_texto(dados.get("telefone")),
        "Celular": limpar_texto(dados.get("celular")),
        "Email": limpar_texto(dados.get("email")),
        "Site": limpar_texto(dados.get("site")),
        "Instagram": limpar_texto(dados.get("instagram")),
        "Facebook": limpar_texto(dados.get("facebook")),
        "OutrasRedes": limpar_texto(dados.get("outras_redes")),
        "HorarioFuncionamento": limpar_texto(dados.get("horario_funcionamento")),
        "Contato1Nome": limpar_texto(dados.get("contato1_nome")),
        "Contato1Telefone": limpar_texto(dados.get("contato1_telefone")),
        "Contato1Cargo": limpar_texto(dados.get("contato1_cargo")),
        "Contato2Nome": limpar_texto(dados.get("contato2_nome")),
        "Contato2Telefone": limpar_texto(dados.get("contato2_telefone")),
        "Contato2Cargo": limpar_texto(dados.get("contato2_cargo")),
        "Contato3Nome": limpar_texto(dados.get("contato3_nome")),
        "Contato3Telefone": limpar_texto(dados.get("contato3_telefone")),
        "Contato3Cargo": limpar_texto(dados.get("contato3_cargo")),
        "QuemIndicou": limpar_texto(dados.get("quem_indicou")),
        "PossuiEstacionamento": normalizar_bool(dados.get("estacionamento")),
        "Observacoes": limpar_texto(dados.get("observacoes")),
        "Ativo": normalizar_bool(dados.get("ativo", True)),
        "CaptadoWeb": normalizar_bool(dados.get("captado_web")),
        "ComplementadoWeb": normalizar_bool(dados.get("complementado_web")),
        "CadastroValidado": normalizar_bool(dados.get("cadastro_validado")),
        "PesquisaIncompleta": normalizar_bool(dados.get("pesquisa_incompleta")),
        "NecessitaComplemento": normalizar_bool(dados.get("necessita_complemento")),
        "NecessitaRevisao": normalizar_bool(dados.get("necessita_revisao")),
        "PontuacaoOrigemWeb": to_float_or_none(dados.get("pontuacao_origem_web")),
        "FonteOrigemWeb": limpar_texto(dados.get("fonte_origem_web")),
        "DataOrigemWeb": normalizar_data_hora(dados.get("data_origem_web")),
        "LocalPesquisaWebId": to_int_or_none(dados.get("local_pesquisa_web_id")),
        "DataValidacaoCadastro": normalizar_data_hora(
            dados.get("data_validacao_cadastro")
        ),
        "ObservacaoPesquisa": limpar_texto(dados.get("observacao_pesquisa")),
    }

    normalizado["Endereco"] = montar_endereco(
        normalizado
    )

    if normalizado["Latitude"] and normalizado["Longitude"] and not normalizado["DataGeo"]:
        normalizado["DataGeo"] = datetime.now()

    return normalizado


def existe_local(nome, local_id=None):

    conn = get_connection()
    cursor = conn.cursor()

    if local_id:
        cursor.execute("""
            SELECT COUNT(*)
            FROM LocalEvento
            WHERE UPPER(NomeCasa) = ?
            AND LocalEventoID <> ?
        """, (
            limpar_texto(nome).upper(),
            local_id,
        ))
    else:
        cursor.execute("""
            SELECT COUNT(*)
            FROM LocalEvento
            WHERE UPPER(NomeCasa) = ?
        """, (
            limpar_texto(nome).upper(),
        ))

    total = cursor.fetchone()[0]
    conn.close()
    return total > 0


def existe_documento(documento, local_id=None):

    documento = normalizar_documento(
        documento,
        campo="CPF/CNPJ",
    )

    if not documento:
        return False

    conn = get_connection()
    cursor = conn.cursor()

    if local_id:
        cursor.execute(f"""
            SELECT COUNT(*)
            FROM LocalEvento
            WHERE {sql_documento_normalizado("CNPJ")} = ?
            AND LocalEventoID <> ?
        """, (
            documento,
            local_id,
        ))
    else:
        cursor.execute(f"""
            SELECT COUNT(*)
            FROM LocalEvento
            WHERE {sql_documento_normalizado("CNPJ")} = ?
        """, (
            documento,
        ))

    total = cursor.fetchone()[0]
    conn.close()
    return total > 0


def salvar_local_db(local_id, dados):

    if local_id:
        local_id = normalizar_id(
            local_id,
            "LocalEventoID",
        )

    dados = normalizar_local(
        dados
    )

    if existe_local(
        dados["NomeCasa"],
        local_id,
    ):
        raise Exception(
            "Já existe um local com esse nome."
        )

    if existe_documento(
        dados["CNPJ"],
        local_id,
    ):
        raise Exception(
            "Já existe um local cadastrado com esse CPF/CNPJ."
        )

    conn = get_connection()
    cursor = conn.cursor()

    atualizar_geolocalizacao_se_necessario(
        cursor,
        local_id,
        dados,
    )

    valores = [
        dados.get(coluna)
        for coluna in COLUNAS_LOCAL
    ]

    try:
        if local_id:
            set_sql = ", ".join(
                f"{coluna} = ?"
                for coluna in COLUNAS_LOCAL
            )

            cursor.execute(f"""
                UPDATE LocalEvento
                SET
                    {set_sql},
                    AtualizadoEm = GETDATE()
                WHERE LocalEventoID = ?
            """, (
                *valores,
                local_id,
            ))

            if cursor.rowcount == 0:
                raise Exception(
                    f"Local {local_id} nao encontrado para atualizacao."
                )

            logger.info(
                "Local atualizado: %s",
                local_id,
            )
        else:
            colunas_sql = ", ".join(
                COLUNAS_LOCAL
            )

            marcadores = ", ".join(
                "?"
                for _ in COLUNAS_LOCAL
            )

            if coluna_eh_identity(
                cursor,
                "LocalEvento",
                "LocalEventoID",
            ):
                cursor.execute(f"""
                    INSERT INTO LocalEvento ({colunas_sql})
                    OUTPUT INSERTED.LocalEventoID
                    VALUES ({marcadores})
                """, valores)
                local_id = cursor.fetchone()[0]
            else:
                local_id = obter_proximo_id(
                    cursor,
                    "LocalEvento",
                    "LocalEventoID",
                )
                cursor.execute(f"""
                    INSERT INTO LocalEvento (LocalEventoID, {colunas_sql})
                    VALUES (?, {marcadores})
                """, (
                    local_id,
                    *valores,
                ))

        conn.commit()
        return {
            "id": local_id,
            "geo_erro": dados.get("_GeoErro", ""),
        }
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def criar_local(dados):
    return salvar_local_db(
        None,
        dados,
    )


def atualizar_local(local_id, dados):
    return salvar_local_db(
        local_id,
        dados,
    )


def listar_locais():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            l.LocalEventoID,
            l.NomeCasa,
            ISNULL(l.NomeFantasia, ''),
            ISNULL(t.NomeTipo, ''),
            ISNULL(l.Municipio, ''),
            ISNULL(l.UF, ''),
            ISNULL(l.Celular, ''),
            ISNULL(l.Email, ''),
            l.Ativo
        FROM LocalEvento l
        LEFT JOIN LocTipo t
            ON t.LocTipoID = l.LocTipoID
        ORDER BY
            l.NomeCasa
    """)

    rows = cursor.fetchall()
    conn.close()
    return rows


def obter_local(local_id):

    local_id = normalizar_id(
        local_id,
        "LocalEventoID",
    )

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(f"""
        SELECT
            LocalEventoID,
            {", ".join(COLUNAS_LOCAL)}
        FROM LocalEvento
        WHERE LocalEventoID = ?
    """, (
        local_id,
    ))

    row = cursor.fetchone()
    conn.close()
    return row


def local_possui_ambientes(local_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM LocAmbientes
        WHERE LocalEventoID = ?
    """, (
        local_id,
    ))

    total = cursor.fetchone()[0]
    conn.close()
    return total > 0


def remover_estruturas_local(local_id):

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            DELETE FROM LocalEventoEstrutura
            WHERE LocalEventoID = ?
        """, (
            local_id,
        ))
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def excluir_local(local_id):

    if local_possui_ambientes(local_id):
        raise Exception(
            "O local possui espaços cadastrados."
        )

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            DELETE FROM LocalEventoEstrutura
            WHERE LocalEventoID = ?
        """, (
            local_id,
        ))
        cursor.execute("""
            DELETE FROM LocalEvento
            WHERE LocalEventoID = ?
        """, (
            local_id,
        ))
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def listar_ambientes(local_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            AmbienteID,
            NomeAmbiente,
            ISNULL(TipoEspaco, ''),
            CapacidadeSentado,
            DimensaoComprimento,
            DimensaoLargura,
            ISNULL(ServicosOferecidos, '')
        FROM LocAmbientes
        WHERE LocalEventoID = ?
        ORDER BY NomeAmbiente
    """, (
        local_id,
    ))

    rows = cursor.fetchall()
    conn.close()
    return rows


def obter_ambiente(ambiente_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            AmbienteID,
            LocalEventoID,
            NomeAmbiente,
            ISNULL(TipoEspaco, ''),
            CapacidadeSentado,
            CapacidadePe,
            Metragem,
            PeDireito,
            ArCondicionado,
            PrecoBase,
            DimensaoComprimento,
            DimensaoLargura,
            ISNULL(ServicosOferecidos, '')
        FROM LocAmbientes
        WHERE AmbienteID = ?
    """, (
        ambiente_id,
    ))

    row = cursor.fetchone()
    conn.close()
    return row


def salvar_ambiente_db(dados):

    conn = get_connection()
    cursor = conn.cursor()

    nome = limpar_texto(
        dados.get("nome")
    )

    if not nome:
        raise Exception(
            "Informe o nome do espaço."
        )

    comprimento = to_float(
        dados.get("comprimento")
    )

    largura = to_float(
        dados.get("largura")
    )

    metragem = to_float(
        dados.get("metragem")
    )

    if not metragem and comprimento and largura:
        metragem = comprimento * largura

    valores = {
        "LocalEventoID": dados["local_id"],
        "NomeAmbiente": nome,
        "TipoEspaco": limpar_texto(dados.get("tipo_espaco")),
        "CapacidadeSentado": to_int(dados.get("sentado")),
        "CapacidadePe": to_int(dados.get("pe")),
        "Metragem": metragem,
        "DimensaoComprimento": comprimento,
        "DimensaoLargura": largura,
        "PeDireito": to_float(dados.get("pe_direito")),
        "ServicosOferecidos": limpar_texto(dados.get("servicos")),
        "ArCondicionado": int(bool(dados.get("ar"))),
        "PrecoBase": to_float(dados.get("preco")),
    }

    try:
        if dados.get("id"):
            cursor.execute("""
                UPDATE LocAmbientes
                SET
                    LocalEventoID = ?,
                    NomeAmbiente = ?,
                    TipoEspaco = ?,
                    CapacidadeSentado = ?,
                    CapacidadePe = ?,
                    Metragem = ?,
                    DimensaoComprimento = ?,
                    DimensaoLargura = ?,
                    PeDireito = ?,
                    ServicosOferecidos = ?,
                    ArCondicionado = ?,
                    PrecoBase = ?
                WHERE AmbienteID = ?
            """, (
                valores["LocalEventoID"],
                valores["NomeAmbiente"],
                valores["TipoEspaco"],
                valores["CapacidadeSentado"],
                valores["CapacidadePe"],
                valores["Metragem"],
                valores["DimensaoComprimento"],
                valores["DimensaoLargura"],
                valores["PeDireito"],
                valores["ServicosOferecidos"],
                valores["ArCondicionado"],
                valores["PrecoBase"],
                dados["id"],
            ))
        elif coluna_eh_identity(
            cursor,
            "LocAmbientes",
            "AmbienteID",
        ):
            cursor.execute("""
                INSERT INTO LocAmbientes
                (
                    LocalEventoID,
                    NomeAmbiente,
                    TipoEspaco,
                    CapacidadeSentado,
                    CapacidadePe,
                    Metragem,
                    DimensaoComprimento,
                    DimensaoLargura,
                    PeDireito,
                    ServicosOferecidos,
                    ArCondicionado,
                    PrecoBase
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                valores["LocalEventoID"],
                valores["NomeAmbiente"],
                valores["TipoEspaco"],
                valores["CapacidadeSentado"],
                valores["CapacidadePe"],
                valores["Metragem"],
                valores["DimensaoComprimento"],
                valores["DimensaoLargura"],
                valores["PeDireito"],
                valores["ServicosOferecidos"],
                valores["ArCondicionado"],
                valores["PrecoBase"],
            ))
        else:
            cursor.execute("""
                INSERT INTO LocAmbientes
                (
                    AmbienteID,
                    LocalEventoID,
                    NomeAmbiente,
                    TipoEspaco,
                    CapacidadeSentado,
                    CapacidadePe,
                    Metragem,
                    DimensaoComprimento,
                    DimensaoLargura,
                    PeDireito,
                    ServicosOferecidos,
                    ArCondicionado,
                    PrecoBase
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                obter_proximo_id(
                    cursor,
                    "LocAmbientes",
                    "AmbienteID",
                ),
                valores["LocalEventoID"],
                valores["NomeAmbiente"],
                valores["TipoEspaco"],
                valores["CapacidadeSentado"],
                valores["CapacidadePe"],
                valores["Metragem"],
                valores["DimensaoComprimento"],
                valores["DimensaoLargura"],
                valores["PeDireito"],
                valores["ServicosOferecidos"],
                valores["ArCondicionado"],
                valores["PrecoBase"],
            ))

        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def remover_ambiente(ambiente_id):

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            DELETE FROM LocAmbientes
            WHERE AmbienteID = ?
        """, (
            ambiente_id,
        ))
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
