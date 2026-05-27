from datetime import datetime

from database.connection import get_connection

from services.local_service import criar_local


COLUNAS_PESQUISA_WEB = [
    "TipoLocalSugerido",
    "NomeCasa",
    "NomeFantasia",
    "DescricaoPublica",
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
    "WhatsApp",
    "Email",
    "Site",
    "Instagram",
    "Facebook",
    "OutrasRedes",
    "HorarioFuncionamento",
    "FontePrincipal",
    "UrlFonte",
    "DadosBrutos",
    "PontuacaoConfiabilidade",
    "StatusPesquisa",
    "PossivelDuplicidade",
    "LocalExistenteId",
    "Transferido",
    "DataTransferencia",
    "UsuarioTransferenciaId",
    "Descartado",
    "DataDescarte",
    "UsuarioDescarteId",
    "MotivoDescarte",
    "NecessitaComplemento",
    "NecessitaRevisao",
    "DataPesquisa",
    "DataUltimaAtualizacao",
    "ObservacaoPesquisa",
]


STATUS_PESQUISA = [
    "PENDENTE_ANALISE",
    "PONTUACAO_BAIXA",
    "APTO_TRANSFERENCIA",
    "POSSIVEL_DUPLICIDADE",
    "TRANSFERIDO",
    "DESCARTADO",
    "DADOS_CONFLITANTES",
    "ERRO_COLETA",
]


def limpar(valor):
    return str(valor or "").strip()


def to_float(valor):
    if valor in ("", None):
        return 0
    try:
        return float(str(valor).replace(",", "."))
    except Exception:
        return 0


def to_bool(valor):
    if isinstance(valor, bool):
        return int(valor)
    return int(str(valor or "").strip().lower() in ("1", "true", "sim", "yes", "on"))


def normalizar_pesquisa(dados):
    nome = limpar(dados.get("nome") or dados.get("NomeCasa"))

    if not nome:
        raise Exception("Informe o nome do local pesquisado.")

    status = limpar(dados.get("status") or dados.get("StatusPesquisa")) or "PENDENTE_ANALISE"
    status = status.upper()

    if status not in STATUS_PESQUISA:
        raise Exception("Status de pesquisa inválido.")

    return {
        "TipoLocalSugerido": limpar(dados.get("tipo_local_sugerido")),
        "NomeCasa": nome,
        "NomeFantasia": limpar(dados.get("nome_fantasia")),
        "DescricaoPublica": limpar(dados.get("descricao_publica")),
        "CNPJ": limpar(dados.get("cnpj")),
        "CEP": limpar(dados.get("cep")),
        "Logradouro": limpar(dados.get("logradouro")),
        "Numero": limpar(dados.get("numero")),
        "Complemento": limpar(dados.get("complemento")),
        "Bairro": limpar(dados.get("bairro")),
        "Municipio": limpar(dados.get("municipio")),
        "UF": limpar(dados.get("uf")).upper(),
        "Pais": limpar(dados.get("pais")) or "Brasil",
        "Endereco": limpar(dados.get("endereco")),
        "Latitude": dados.get("latitude") or None,
        "Longitude": dados.get("longitude") or None,
        "FonteGeo": limpar(dados.get("fonte_geo")),
        "DataGeo": dados.get("data_geo") or None,
        "Responsavel": limpar(dados.get("responsavel")),
        "Contato": limpar(dados.get("contato")),
        "Telefone": limpar(dados.get("telefone")),
        "Celular": limpar(dados.get("celular")),
        "WhatsApp": limpar(dados.get("whatsapp")),
        "Email": limpar(dados.get("email")),
        "Site": limpar(dados.get("site")),
        "Instagram": limpar(dados.get("instagram")),
        "Facebook": limpar(dados.get("facebook")),
        "OutrasRedes": limpar(dados.get("outras_redes")),
        "HorarioFuncionamento": limpar(dados.get("horario_funcionamento")),
        "FontePrincipal": limpar(dados.get("fonte_principal")),
        "UrlFonte": limpar(dados.get("url_fonte")),
        "DadosBrutos": limpar(dados.get("dados_brutos")),
        "PontuacaoConfiabilidade": to_float(dados.get("pontuacao")),
        "StatusPesquisa": status,
        "PossivelDuplicidade": to_bool(dados.get("possivel_duplicidade")),
        "LocalExistenteId": dados.get("local_existente_id") or None,
        "Transferido": to_bool(dados.get("transferido")),
        "DataTransferencia": dados.get("data_transferencia") or None,
        "UsuarioTransferenciaId": dados.get("usuario_transferencia_id") or None,
        "Descartado": to_bool(dados.get("descartado")),
        "DataDescarte": dados.get("data_descarte") or None,
        "UsuarioDescarteId": dados.get("usuario_descarte_id") or None,
        "MotivoDescarte": limpar(dados.get("motivo_descarte")),
        "NecessitaComplemento": to_bool(dados.get("necessita_complemento", True)),
        "NecessitaRevisao": to_bool(dados.get("necessita_revisao", True)),
        "DataPesquisa": dados.get("data_pesquisa") or datetime.now(),
        "DataUltimaAtualizacao": dados.get("data_ultima_atualizacao") or None,
        "ObservacaoPesquisa": limpar(dados.get("observacao_pesquisa")),
    }


def listar_pesquisas(apenas_transferiveis=False):
    conn = get_connection()
    cursor = conn.cursor()

    filtro = ""

    if apenas_transferiveis:
        filtro = """
            WHERE StatusPesquisa = 'APTO_TRANSFERENCIA'
            AND Transferido = 0
            AND Descartado = 0
            AND PontuacaoConfiabilidade >= 80
        """

    cursor.execute(f"""
        SELECT
            LocalPesquisaWebID,
            NomeCasa,
            ISNULL(Municipio, ''),
            ISNULL(UF, ''),
            ISNULL(Telefone, ''),
            ISNULL(Site, ''),
            PontuacaoConfiabilidade,
            StatusPesquisa,
            Transferido,
            Descartado
        FROM LocalEventoPesquisaWeb
        {filtro}
        ORDER BY
            Transferido,
            Descartado,
            PontuacaoConfiabilidade DESC,
            NomeCasa
    """)

    rows = cursor.fetchall()
    conn.close()
    return rows


def obter_pesquisa(pesquisa_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(f"""
        SELECT
            LocalPesquisaWebID,
            {", ".join(COLUNAS_PESQUISA_WEB)}
        FROM LocalEventoPesquisaWeb
        WHERE LocalPesquisaWebID = ?
    """, (
        int(pesquisa_id),
    ))

    row = cursor.fetchone()
    conn.close()
    return row


def salvar_pesquisa(pesquisa_id, dados):
    normalizado = normalizar_pesquisa(dados)
    valores = [normalizado.get(coluna) for coluna in COLUNAS_PESQUISA_WEB]

    conn = get_connection()
    cursor = conn.cursor()

    try:
        if pesquisa_id:
            set_sql = ", ".join(f"{coluna} = ?" for coluna in COLUNAS_PESQUISA_WEB)
            cursor.execute(f"""
                UPDATE LocalEventoPesquisaWeb
                SET
                    {set_sql},
                    DataUltimaAtualizacao = GETDATE()
                WHERE LocalPesquisaWebID = ?
            """, (
                *valores,
                int(pesquisa_id),
            ))
        else:
            colunas = ", ".join(COLUNAS_PESQUISA_WEB)
            marcadores = ", ".join("?" for _ in COLUNAS_PESQUISA_WEB)
            cursor.execute(f"""
                INSERT INTO LocalEventoPesquisaWeb ({colunas})
                OUTPUT INSERTED.LocalPesquisaWebID
                VALUES ({marcadores})
            """, valores)
            pesquisa_id = cursor.fetchone()[0]

        conn.commit()
        return pesquisa_id
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def transferir_pesquisa_para_local(pesquisa_id):
    row = obter_pesquisa(pesquisa_id)

    if not row:
        raise Exception("Pesquisa web não encontrada.")

    dados = dict(zip(COLUNAS_PESQUISA_WEB, row[1:]))

    if bool(dados.get("Transferido")):
        raise Exception("Pesquisa web já transferida.")

    if bool(dados.get("Descartado")):
        raise Exception("Pesquisa web descartada.")

    if dados.get("StatusPesquisa") != "APTO_TRANSFERENCIA":
        raise Exception("Somente pesquisas aptas podem ser transferidas.")

    if float(dados.get("PontuacaoConfiabilidade") or 0) < 80:
        raise Exception("Pontuação mínima para transferência é 80.")

    resultado = criar_local({
        "nome": dados.get("NomeCasa"),
        "nome_fantasia": dados.get("NomeFantasia"),
        "cnpj": dados.get("CNPJ"),
        "cep": dados.get("CEP"),
        "logradouro": dados.get("Logradouro"),
        "numero": dados.get("Numero"),
        "complemento": dados.get("Complemento"),
        "bairro": dados.get("Bairro"),
        "municipio": dados.get("Municipio"),
        "uf": dados.get("UF"),
        "pais": dados.get("Pais"),
        "endereco": dados.get("Endereco"),
        "latitude": dados.get("Latitude"),
        "longitude": dados.get("Longitude"),
        "fonte_geo": dados.get("FonteGeo"),
        "data_geo": dados.get("DataGeo"),
        "responsavel": dados.get("Responsavel"),
        "contato": dados.get("Contato"),
        "telefone": dados.get("Telefone"),
        "celular": dados.get("Celular") or dados.get("WhatsApp"),
        "email": dados.get("Email"),
        "site": dados.get("Site"),
        "instagram": dados.get("Instagram"),
        "facebook": dados.get("Facebook"),
        "outras_redes": dados.get("OutrasRedes"),
        "horario_funcionamento": dados.get("HorarioFuncionamento"),
        "quem_indicou": "Pesquisa Web Automática",
        "ativo": True,
        "captado_web": True,
        "cadastro_validado": False,
        "pesquisa_incompleta": bool(dados.get("NecessitaComplemento")),
        "necessita_complemento": bool(dados.get("NecessitaComplemento")),
        "necessita_revisao": True,
        "pontuacao_origem_web": dados.get("PontuacaoConfiabilidade"),
        "fonte_origem_web": dados.get("FontePrincipal"),
        "data_origem_web": dados.get("DataPesquisa"),
        "local_pesquisa_web_id": row[0],
        "observacao_pesquisa": dados.get("ObservacaoPesquisa"),
    })

    local_id = resultado.get("id") if isinstance(resultado, dict) else resultado

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            UPDATE LocalEventoPesquisaWeb
            SET
                Transferido = 1,
                StatusPesquisa = 'TRANSFERIDO',
                LocalExistenteId = ?,
                DataTransferencia = GETDATE(),
                DataUltimaAtualizacao = GETDATE()
            WHERE LocalPesquisaWebID = ?
        """, (
            local_id,
            int(pesquisa_id),
        ))

        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

    return local_id
