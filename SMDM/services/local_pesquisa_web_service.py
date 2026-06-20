import json
import logging
import re
from datetime import datetime
from pathlib import Path

from database.connection import get_connection

from services.local_service import criar_local


LOGGER = logging.getLogger("MDM_LOCAL_PESQUISA_WEB")
NOMINATIM_SEARCH_URL = "https://nominatim.openstreetmap.org/search"
OVERPASS_URL = "https://overpass-api.de/api/interpreter"
TERMOS_CONFIG = (
    Path(__file__).resolve().parents[1]
    / "config"
    / "local_pesquisa_web_termos.json"
)

OVERPASS_TAGS_EVENTOS = (
    ("amenity", "events_venue|community_centre|theatre|conference_centre|restaurant|bar|pub|cafe"),
    ("tourism", "hotel|hostel|guest_house|attraction"),
    ("leisure", "sports_centre|stadium|park|garden"),
    ("building", "church|commercial|retail|public"),
)


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


TERMOS_PADRAO_PESQUISA_WEB = [
    "casa de festas",
    "casa de festas infantil",
    "espaco para eventos",
    "salao de festas",
    "salao de eventos",
    "buffet infantil",
    "buffet para festas",
    "centro de eventos",
    "sitio para eventos",
    "chacara para festas",
    "local para festa infantil",
    "local para aniversario",
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
    "NAO_SERVE",
]


def limpar(valor):
    return str(valor or "").strip()


def limpar_cep(valor):
    return re.sub(r"\D", "", limpar(valor))


def cep_rs_valido(valor):
    cep = limpar_cep(valor)

    if not cep:
        return True

    if len(cep) != 8:
        return False

    numero = int(cep)
    return 90000000 <= numero <= 99999999


def cep_informado_eh_rs(valor):
    cep = limpar_cep(valor)

    return bool(cep) and cep_rs_valido(cep)


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


def carregar_termos_pesquisa_web():
    try:
        if TERMOS_CONFIG.exists():
            with TERMOS_CONFIG.open("r", encoding="utf-8") as arquivo:
                dados = json.load(arquivo)

            termos = dados.get("termos") if isinstance(dados, dict) else dados

            if isinstance(termos, list):
                termos = [
                    limpar(termo)
                    for termo in termos
                    if limpar(termo)
                ]

                if termos:
                    return termos
    except Exception:
        LOGGER.exception("Erro carregando termos de pesquisa web.")

    return list(TERMOS_PADRAO_PESQUISA_WEB)


def _colunas_tabela(cursor, tabela):
    cursor.execute("""
        SELECT COLUMN_NAME
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_NAME = ?
    """, (
        tabela,
    ))

    return {
        str(row[0]).lower(): str(row[0])
        for row in cursor.fetchall()
    }


def _escolher_coluna(colunas, candidatos):
    for candidato in candidatos:
        coluna = colunas.get(candidato.lower())

        if coluna:
            return coluna

    return None


def listar_municipios_rs():
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT COUNT(*)
            FROM INFORMATION_SCHEMA.TABLES
            WHERE TABLE_NAME = 'Municipio'
        """)

        if not cursor.fetchone()[0]:
            return []

        colunas = _colunas_tabela(cursor, "Municipio")
        coluna_nome = _escolher_coluna(
            colunas,
            (
                "NomeMunicipio",
                "Municipio",
                "Nome",
                "Cidade",
                "Descricao",
            ),
        )
        coluna_uf = _escolher_coluna(
            colunas,
            (
                "UF",
                "Estado",
                "SiglaUF",
            ),
        )

        if not coluna_nome:
            return []

        if coluna_uf:
            cursor.execute(f"""
                SELECT DISTINCT {coluna_nome}
                FROM Municipio
                WHERE UPPER({coluna_uf}) = 'RS'
                AND {coluna_nome} IS NOT NULL
                ORDER BY {coluna_nome}
            """)
        else:
            cursor.execute(f"""
                SELECT DISTINCT {coluna_nome}
                FROM Municipio
                WHERE {coluna_nome} IS NOT NULL
                ORDER BY {coluna_nome}
            """)

        return [
            limpar(row[0])
            for row in cursor.fetchall()
            if limpar(row[0])
        ]
    finally:
        conn.close()


def _obter_colunas_municipio(cursor):
    colunas = _colunas_tabela(cursor, "Municipio")
    coluna_nome = _escolher_coluna(
        colunas,
        (
            "NomeMunicipio",
            "Municipio",
            "Nome",
            "Cidade",
            "Descricao",
        ),
    )
    coluna_uf = _escolher_coluna(
        colunas,
        (
            "UF",
            "Estado",
            "SiglaUF",
        ),
    )
    coluna_regiao = _escolher_coluna(
        colunas,
        (
            "REGIAO",
            "Regiao",
            "Região",
        ),
    )

    return coluna_nome, coluna_uf, coluna_regiao


def listar_municipios_prioritarios_sedes():
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT COUNT(*)
            FROM INFORMATION_SCHEMA.TABLES
            WHERE TABLE_NAME = 'Municipio'
        """)

        if not cursor.fetchone()[0]:
            return []

        coluna_nome, coluna_uf, coluna_regiao = _obter_colunas_municipio(cursor)

        if not coluna_nome or not coluna_regiao:
            return listar_municipios_rs()

        cursor.execute("""
            SELECT COUNT(*)
            FROM INFORMATION_SCHEMA.TABLES
            WHERE TABLE_NAME = 'SedesEmpresa'
        """)

        regioes_prioritarias = []

        if cursor.fetchone()[0]:
            filtro_uf = (
                "AND UPPER(ISNULL(s.UF, '')) = 'RS'"
                if coluna_uf
                else ""
            )
            cursor.execute(f"""
                SELECT DISTINCT m.{coluna_regiao}
                FROM SedesEmpresa s
                INNER JOIN Municipio m
                    ON UPPER(m.{coluna_nome}) = UPPER(s.Municipio)
                WHERE UPPER(s.NomeSede) IN ('PORTO ALEGRE', 'SANTA CRUZ DO SUL')
                AND ISNULL(s.Ativo, 1) = 1
                AND ISNULL(s.Operacional, 1) = 1
                AND ISNULL(s.Fantasma, 0) = 0
                {filtro_uf}
                AND m.{coluna_regiao} IS NOT NULL
            """)

            regioes_prioritarias = [
                limpar(row[0])
                for row in cursor.fetchall()
                if limpar(row[0])
            ]

        if not regioes_prioritarias:
            marcadores = "?, ?"
            filtro_uf = (
                f"AND UPPER(ISNULL({coluna_uf}, '')) = 'RS'"
                if coluna_uf
                else ""
            )
            cursor.execute(f"""
                SELECT DISTINCT {coluna_regiao}
                FROM Municipio
                WHERE UPPER({coluna_nome}) IN ({marcadores})
                {filtro_uf}
                AND {coluna_regiao} IS NOT NULL
            """, (
                "PORTO ALEGRE",
                "SANTA CRUZ DO SUL",
            ))

            regioes_prioritarias = [
                limpar(row[0])
                for row in cursor.fetchall()
                if limpar(row[0])
            ]

        if not regioes_prioritarias:
            return listar_municipios_rs()

        marcadores = ", ".join(
            "?"
            for _ in regioes_prioritarias
        )
        filtro_uf = (
            f"AND UPPER(ISNULL({coluna_uf}, '')) = 'RS'"
            if coluna_uf
            else ""
        )

        cursor.execute(f"""
            SELECT DISTINCT {coluna_nome}
            FROM Municipio
            WHERE {coluna_regiao} IN ({marcadores})
            {filtro_uf}
            AND {coluna_nome} IS NOT NULL
            ORDER BY {coluna_nome}
        """, tuple(regioes_prioritarias))

        prioritarios = [
            limpar(row[0])
            for row in cursor.fetchall()
            if limpar(row[0])
        ]
        demais = [
            municipio
            for municipio in listar_municipios_rs()
            if municipio.upper() not in {
                item.upper()
                for item in prioritarios
            }
        ]

        return prioritarios + demais

    finally:
        conn.close()


def municipio_rs_existe(municipio):
    municipio = limpar(municipio).upper()

    if not municipio:
        return False

    municipios = listar_municipios_rs()

    if not municipios:
        return True

    return municipio in {
        item.upper()
        for item in municipios
    }


def atende_regra_rs_ou_cep(dados):
    municipio = limpar(
        dados.get("municipio")
        or dados.get("Municipio")
    )
    cep = dados.get("cep") or dados.get("CEP")

    return (
        municipio_rs_existe(municipio)
        or cep_informado_eh_rs(cep)
    )


def localizar_local_oficial(cursor, nome, municipio, uf, cep=None):
    cep = limpar_cep(cep)

    if cep:
        cursor.execute("""
            SELECT TOP 1 LocalEventoID
            FROM LocalEvento
            WHERE REPLACE(REPLACE(ISNULL(CEP, ''), '-', ''), '.', '') = ?
            ORDER BY LocalEventoID
        """, (
            cep,
        ))

        row = cursor.fetchone()

        if row:
            return row[0]

    cursor.execute("""
        SELECT TOP 1 LocalEventoID
        FROM LocalEvento
        WHERE UPPER(NomeCasa) = ?
        AND UPPER(ISNULL(Municipio, '')) = ?
        AND UPPER(ISNULL(UF, '')) = ?
        ORDER BY LocalEventoID
    """, (
        limpar(nome).upper(),
        limpar(municipio).upper(),
        limpar(uf).upper(),
    ))

    row = cursor.fetchone()
    return row[0] if row else None


def aplicar_regra_rs_cadastro_automatico(resultado, cursor=None):
    atende_regra = atende_regra_rs_ou_cep(resultado)
    local_existente_id = None

    if cursor:
        local_existente_id = localizar_local_oficial(
            cursor,
            resultado.get("nome"),
            resultado.get("municipio"),
            resultado.get("uf"),
            resultado.get("cep"),
        )

    if not atende_regra:
        resultado["pontuacao"] = 0
        resultado["status"] = "NAO_SERVE"
        resultado["necessita_complemento"] = True
        resultado["necessita_revisao"] = True

        if local_existente_id:
            resultado["local_existente_id"] = local_existente_id
            resultado["possivel_duplicidade"] = True

        resultado["observacao_pesquisa"] = (
            limpar(resultado.get("observacao_pesquisa"))
            + " Resultado nao atende regra de cadastro automatico: "
            "municipio nao validado como RS e CEP fora da faixa 90000-000 a 99999-999."
        ).strip()

        return resultado

    if local_existente_id:
        resultado["local_existente_id"] = local_existente_id
        resultado["possivel_duplicidade"] = True
        resultado["status"] = "POSSIVEL_DUPLICIDADE"
        resultado["necessita_revisao"] = True

    return resultado


def _http_get_json(url, params=None):
    import httpx

    headers = {
        "User-Agent": "SMDM-MDM-ERP/1.0 pesquisa-local",
    }

    with httpx.Client(timeout=12.0, headers=headers) as client:
        response = client.get(
            url,
            params=params,
        )
        response.raise_for_status()
        return response.json()


def _http_post_text(url, data):
    import httpx

    headers = {
        "User-Agent": "SMDM-MDM-ERP/1.0 pesquisa-local",
    }

    with httpx.Client(timeout=30.0, headers=headers) as client:
        response = client.post(
            url,
            data=data,
        )
        response.raise_for_status()
        return response.json()


def _extrair_nome_osm(item):
    tags = item.get("extratags") or {}
    namedetails = item.get("namedetails") or {}

    for chave in (
        "name",
        "name:pt",
        "official_name",
        "brand",
    ):
        valor = limpar(tags.get(chave) or namedetails.get(chave))

        if valor:
            return valor

    display = limpar(item.get("display_name"))

    if display:
        return display.split(",")[0].strip()

    return ""


def _bbox_municipio_osm(municipio, uf):
    dados = _http_get_json(
        NOMINATIM_SEARCH_URL,
        params={
            "q": f"{municipio}, {uf}, Brasil",
            "format": "jsonv2",
            "addressdetails": 1,
            "limit": 1,
            "countrycodes": "br",
        },
    )

    if not dados:
        return None

    bbox = dados[0].get("boundingbox")

    if not bbox or len(bbox) != 4:
        return None

    sul, norte, oeste, leste = bbox
    return (
        float(sul),
        float(oeste),
        float(norte),
        float(leste),
    )


def _montar_query_overpass(bbox, limite):
    sul, oeste, norte, leste = bbox
    partes = []

    for chave, regex in OVERPASS_TAGS_EVENTOS:
        partes.append(
            f'nwr["name"]["{chave}"~"{regex}"]({sul},{oeste},{norte},{leste});'
        )

    return (
        "[out:json][timeout:25];"
        "("
        + "".join(partes)
        + ");"
        f"out center {limite};"
    )


def _tipo_sugerido_overpass(tags):
    if tags.get("amenity"):
        return tags.get("amenity")

    if tags.get("tourism"):
        return tags.get("tourism")

    if tags.get("leisure"):
        return tags.get("leisure")

    if tags.get("building"):
        return tags.get("building")

    return "local para eventos"


def _normalizar_resultado_overpass(item, municipio, uf):
    tags = item.get("tags") or {}
    nome = limpar(tags.get("name"))

    if not nome:
        return None

    lat = item.get("lat")
    lon = item.get("lon")

    if item.get("center"):
        lat = lat or item["center"].get("lat")
        lon = lon or item["center"].get("lon")

    cep = limpar_cep(tags.get("addr:postcode"))

    if uf.upper() == "RS" and not cep_rs_valido(cep):
        cep = ""

    logradouro = limpar(tags.get("addr:street"))
    numero = limpar(tags.get("addr:housenumber"))
    bairro = limpar(
        tags.get("addr:suburb")
        or tags.get("addr:neighbourhood")
    )
    municipio_item = limpar(
        tags.get("addr:city")
        or tags.get("addr:town")
        or tags.get("addr:municipality")
        or municipio
    )

    endereco_partes = [
        logradouro,
        numero,
        bairro,
        municipio_item,
        uf,
        "Brasil",
        cep,
    ]
    endereco_texto = ", ".join(
        parte
        for parte in endereco_partes
        if parte
    )
    tipo = _tipo_sugerido_overpass(tags)

    pontuacao = calcular_pontuacao_pesquisa({
        "nome": nome,
        "tipo_local_sugerido": tipo,
        "endereco": endereco_texto,
        "logradouro": logradouro,
        "bairro": bairro,
        "municipio": municipio_item,
        "uf": uf,
        "cep": cep,
        "latitude": lat,
        "longitude": lon,
        "telefone": tags.get("phone") or tags.get("contact:phone"),
        "site": tags.get("website") or tags.get("contact:website"),
        "fonte_principal": "OpenStreetMap/Overpass",
    })

    status = (
        "APTO_TRANSFERENCIA"
        if pontuacao >= 80
        else "PONTUACAO_BAIXA"
    )

    osm_type = item.get("type", "")
    osm_id = item.get("id", "")

    return {
        "tipo_local_sugerido": tipo,
        "nome": nome,
        "nome_fantasia": nome,
        "descricao_publica": endereco_texto,
        "cep": cep,
        "logradouro": logradouro,
        "numero": numero,
        "bairro": bairro,
        "municipio": municipio_item,
        "uf": uf,
        "pais": "Brasil",
        "endereco": endereco_texto,
        "latitude": lat,
        "longitude": lon,
        "fonte_geo": "overpass",
        "data_geo": datetime.now(),
        "telefone": tags.get("phone") or tags.get("contact:phone"),
        "email": tags.get("email") or tags.get("contact:email"),
        "site": tags.get("website") or tags.get("contact:website"),
        "instagram": tags.get("contact:instagram"),
        "facebook": tags.get("contact:facebook"),
        "fonte_principal": "OpenStreetMap/Overpass",
        "url_fonte": f"https://www.openstreetmap.org/{osm_type}/{osm_id}",
        "dados_brutos": json.dumps(item, ensure_ascii=False),
        "pontuacao": pontuacao,
        "status": status,
        "necessita_complemento": pontuacao < 80,
        "necessita_revisao": True,
        "observacao_pesquisa": (
            "Coleta automatica gratuita via OpenStreetMap/Overpass "
            f"em {municipio}/{uf}."
        ),
    }


def _normalizar_resultado_osm(item, termo, municipio, uf):
    endereco = item.get("address") or {}
    cep = limpar_cep(endereco.get("postcode"))

    if uf.upper() == "RS" and not cep_rs_valido(cep):
        cep = ""

    nome = _extrair_nome_osm(item)

    if not nome:
        return None

    municipio_item = (
        endereco.get("city")
        or endereco.get("town")
        or endereco.get("village")
        or endereco.get("municipality")
        or municipio
    )

    uf_item = (
        endereco.get("state_code")
        or uf
    )

    logradouro = (
        endereco.get("road")
        or endereco.get("pedestrian")
        or endereco.get("footway")
        or endereco.get("neighbourhood")
        or ""
    )

    bairro = (
        endereco.get("suburb")
        or endereco.get("neighbourhood")
        or endereco.get("quarter")
        or ""
    )

    pontuacao = calcular_pontuacao_pesquisa({
        "nome": nome,
        "tipo_local_sugerido": termo,
        "endereco": item.get("display_name"),
        "logradouro": logradouro,
        "bairro": bairro,
        "municipio": municipio_item,
        "uf": uf_item,
        "cep": cep,
        "latitude": item.get("lat"),
        "longitude": item.get("lon"),
        "site": item.get("osm_type"),
        "fonte_principal": "OpenStreetMap/Nominatim",
    })

    status = (
        "APTO_TRANSFERENCIA"
        if pontuacao >= 80
        else "PONTUACAO_BAIXA"
    )

    return {
        "tipo_local_sugerido": termo,
        "nome": nome,
        "nome_fantasia": nome,
        "descricao_publica": item.get("display_name"),
        "cep": cep,
        "logradouro": logradouro,
        "numero": endereco.get("house_number"),
        "bairro": bairro,
        "municipio": municipio_item,
        "uf": uf_item,
        "pais": "Brasil",
        "endereco": item.get("display_name"),
        "latitude": item.get("lat"),
        "longitude": item.get("lon"),
        "fonte_geo": "nominatim",
        "data_geo": datetime.now(),
        "fonte_principal": "OpenStreetMap/Nominatim",
        "url_fonte": (
            "https://www.openstreetmap.org/"
            f"{item.get('osm_type', '')}/{item.get('osm_id', '')}"
        ),
        "dados_brutos": json.dumps(item, ensure_ascii=False),
        "pontuacao": pontuacao,
        "status": status,
        "necessita_complemento": pontuacao < 80,
        "necessita_revisao": True,
        "observacao_pesquisa": (
            "Coleta automatica por termo "
            f"'{termo}' em {municipio}/{uf}."
        ),
    }


def pesquisar_nominatim_termo(termo, municipio, uf, limite):
    consulta = f"{termo} em {municipio} {uf} Brasil"
    dados = _http_get_json(
        NOMINATIM_SEARCH_URL,
        params={
            "q": consulta,
            "format": "jsonv2",
            "addressdetails": 1,
            "extratags": 1,
            "namedetails": 1,
            "limit": limite,
            "countrycodes": "br",
        },
    )

    resultados = []

    for item in dados or []:
        resultado = _normalizar_resultado_osm(
            item,
            termo,
            municipio,
            uf,
        )

        if resultado:
            resultados.append(resultado)

    return resultados


def pesquisar_overpass_municipio(municipio, uf, limite):
    bbox = _bbox_municipio_osm(
        municipio,
        uf,
    )

    if not bbox:
        return []

    dados = _http_post_text(
        OVERPASS_URL,
        {
            "data": _montar_query_overpass(
                bbox,
                limite,
            )
        },
    )

    resultados = []

    for item in dados.get("elements") or []:
        resultado = _normalizar_resultado_overpass(
            item,
            municipio,
            uf,
        )

        if resultado:
            resultados.append(resultado)

    return resultados


def calcular_pontuacao_pesquisa(dados):
    pontuacao = 0

    if limpar(dados.get("nome") or dados.get("NomeCasa")):
        pontuacao += 15

    if limpar(dados.get("municipio") or dados.get("Municipio")) and limpar(dados.get("uf") or dados.get("UF")):
        pontuacao += 10

    if limpar(dados.get("endereco") or dados.get("Endereco") or dados.get("logradouro") or dados.get("Logradouro")):
        pontuacao += 15

    if limpar(dados.get("bairro") or dados.get("Bairro")):
        pontuacao += 5

    if limpar_cep(dados.get("cep") or dados.get("CEP")):
        pontuacao += 5

    if dados.get("latitude") and dados.get("longitude"):
        pontuacao += 15

    if limpar(dados.get("telefone") or dados.get("whatsapp") or dados.get("Telefone") or dados.get("WhatsApp")):
        pontuacao += 10

    if limpar(dados.get("site") or dados.get("instagram") or dados.get("facebook") or dados.get("Site")):
        pontuacao += 10

    if limpar(dados.get("tipo_local_sugerido") or dados.get("TipoLocalSugerido")):
        pontuacao += 10

    if limpar(dados.get("fonte_principal") or dados.get("FontePrincipal")):
        pontuacao += 5

    return min(pontuacao, 100)


def pesquisa_ja_cadastrada(cursor, nome, municipio, uf, url_fonte=None):
    if url_fonte:
        cursor.execute("""
            SELECT COUNT(*)
            FROM LocalEventoPesquisaWeb
            WHERE UrlFonte = ?
        """, (
            url_fonte,
        ))

        if cursor.fetchone()[0]:
            return True

    cursor.execute("""
        SELECT COUNT(*)
        FROM LocalEventoPesquisaWeb
        WHERE UPPER(NomeCasa) = ?
        AND UPPER(ISNULL(Municipio, '')) = ?
        AND UPPER(ISNULL(UF, '')) = ?
    """, (
        limpar(nome).upper(),
        limpar(municipio).upper(),
        limpar(uf).upper(),
    ))

    return cursor.fetchone()[0] > 0


def coletar_locais_web(municipio, uf="RS", termos=None, limite_por_termo=5):
    municipio = limpar(municipio)
    uf = limpar(uf or "RS").upper()

    if not municipio:
        raise Exception("Informe o municipio para pesquisar.")

    if uf == "RS" and not municipio_rs_existe(municipio):
        raise Exception(
            "Municipio nao encontrado na tabela Municipio para o Rio Grande do Sul."
        )

    termos = [
        limpar(termo)
        for termo in (termos or carregar_termos_pesquisa_web())
        if limpar(termo)
    ]

    if not termos:
        raise Exception("Nenhum termo de pesquisa web configurado.")

    limite_por_termo = max(1, min(int(limite_por_termo or 5), 20))
    encontrados = []
    erros = []

    for termo in termos:
        try:
            encontrados.extend(
                pesquisar_nominatim_termo(
                    termo,
                    municipio,
                    uf,
                    limite_por_termo,
                )
            )
        except Exception as ex:
            erros.append(f"nominatim/{termo}: {ex}")

    try:
        encontrados.extend(
            pesquisar_overpass_municipio(
                municipio,
                uf,
                limite_por_termo * max(len(termos), 1),
            )
        )
    except Exception as ex:
        erros.append(f"overpass: {ex}")

    conn = get_connection()
    cursor = conn.cursor()
    inseridos = 0
    ignorados = 0

    try:
        for resultado in encontrados:
            resultado = aplicar_regra_rs_cadastro_automatico(
                resultado,
                cursor,
            )

            if pesquisa_ja_cadastrada(
                cursor,
                resultado["nome"],
                resultado["municipio"],
                resultado["uf"],
                resultado.get("url_fonte"),
            ):
                ignorados += 1
                continue

            salvar_pesquisa(
                None,
                resultado,
            )
            inseridos += 1

        return {
            "inseridos": inseridos,
            "ignorados": ignorados,
            "erros": erros,
            "consultados": len(encontrados),
        }
    finally:
        conn.close()


def coletar_locais_web_fluxo(
    municipio,
    uf="RS",
    termos=None,
    limite_por_termo=5,
    deve_parar=None,
    ao_pesquisar=None,
):
    municipio = limpar(municipio)
    uf = limpar(uf or "RS").upper()

    if not municipio:
        raise Exception("Informe o municipio para pesquisar.")

    if uf == "RS" and not municipio_rs_existe(municipio):
        raise Exception(
            "Municipio nao encontrado na tabela Municipio para o Rio Grande do Sul."
        )

    termos = [
        limpar(termo)
        for termo in (termos or carregar_termos_pesquisa_web())
        if limpar(termo)
    ]

    if not termos:
        raise Exception("Nenhum termo de pesquisa web configurado.")

    limite_por_termo = max(1, min(int(limite_por_termo or 5), 20))
    resumo = {
        "inseridos": 0,
        "ignorados": 0,
        "erros": [],
        "consultados": 0,
        "interrompido": False,
    }

    for termo in termos:
        if deve_parar and deve_parar():
            resumo["interrompido"] = True
            break

        try:
            dados = pesquisar_nominatim_termo(
                termo,
                municipio,
                uf,
                limite_por_termo,
            )
        except Exception as ex:
            erro = f"nominatim/{termo}: {ex}"
            resumo["erros"].append(erro)

            if ao_pesquisar:
                ao_pesquisar({
                    "nome": termo,
                    "municipio": municipio,
                    "uf": uf,
                    "status": "ERRO_COLETA",
                    "pontuacao": 0,
                    "mensagem": erro,
                })

            continue

        for resultado in dados or []:
            if deve_parar and deve_parar():
                resumo["interrompido"] = True
                break

            resumo["consultados"] += 1

            conn = get_connection()
            cursor = conn.cursor()

            try:
                resultado = aplicar_regra_rs_cadastro_automatico(
                    resultado,
                    cursor,
                )

                duplicado = pesquisa_ja_cadastrada(
                    cursor,
                    resultado["nome"],
                    resultado["municipio"],
                    resultado["uf"],
                    resultado.get("url_fonte"),
                )
            finally:
                conn.close()

            if duplicado:
                resumo["ignorados"] += 1
                status_fluxo = "IGNORADO"
            else:
                salvar_pesquisa(
                    None,
                    resultado,
                )
                resumo["inseridos"] += 1
                status_fluxo = "INCLUIDO"

            if ao_pesquisar:
                ao_pesquisar({
                    "nome": resultado["nome"],
                    "municipio": resultado["municipio"],
                    "uf": resultado["uf"],
                    "status": status_fluxo,
                    "pontuacao": resultado.get("pontuacao"),
                    "termo": termo,
                })

        if resumo["interrompido"]:
            break

    if not resumo["interrompido"]:
        try:
            dados_overpass = pesquisar_overpass_municipio(
                municipio,
                uf,
                limite_por_termo * max(len(termos), 1),
            )
        except Exception as ex:
            erro = f"overpass: {ex}"
            resumo["erros"].append(erro)

            if ao_pesquisar:
                ao_pesquisar({
                    "nome": "OpenStreetMap/Overpass",
                    "municipio": municipio,
                    "uf": uf,
                    "status": "ERRO_COLETA",
                    "pontuacao": 0,
                    "mensagem": erro,
                })
        else:
            for resultado in dados_overpass:
                if deve_parar and deve_parar():
                    resumo["interrompido"] = True
                    break

                resumo["consultados"] += 1

                conn = get_connection()
                cursor = conn.cursor()

                try:
                    resultado = aplicar_regra_rs_cadastro_automatico(
                        resultado,
                        cursor,
                    )

                    duplicado = pesquisa_ja_cadastrada(
                        cursor,
                        resultado["nome"],
                        resultado["municipio"],
                        resultado["uf"],
                        resultado.get("url_fonte"),
                    )
                finally:
                    conn.close()

                if duplicado:
                    resumo["ignorados"] += 1
                    status_fluxo = "IGNORADO"
                else:
                    salvar_pesquisa(
                        None,
                        resultado,
                    )
                    resumo["inseridos"] += 1
                    status_fluxo = "INCLUIDO"

                if ao_pesquisar:
                    ao_pesquisar({
                        "nome": resultado["nome"],
                        "municipio": resultado["municipio"],
                        "uf": resultado["uf"],
                        "status": status_fluxo,
                        "pontuacao": resultado.get("pontuacao"),
                        "termo": "OpenStreetMap/Overpass",
                    })

    return resumo


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


def listar_ultimas_pesquisas(limite=5):
    limite = max(1, min(int(limite or 5), 20))
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(f"""
            SELECT TOP ({limite})
                LocalPesquisaWebID,
                NomeCasa,
                ISNULL(Municipio, ''),
                ISNULL(UF, ''),
                PontuacaoConfiabilidade,
                StatusPesquisa,
                ISNULL(FontePrincipal, ''),
                DataPesquisa
            FROM LocalEventoPesquisaWeb
            ORDER BY
                DataPesquisa DESC,
                LocalPesquisaWebID DESC
        """)

        return cursor.fetchall()
    finally:
        conn.close()


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
