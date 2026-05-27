import json
import json
import logging
import os
import re
from datetime import datetime
from urllib.parse import quote

from database.connection import get_connection


LOGGER = logging.getLogger("MDM_ENDERECO")

VIACEP_URL = "https://viacep.com.br/ws"
GOOGLE_GEOCODING_URL = "https://maps.googleapis.com/maps/api/geocode/json"


def limpar_texto(valor):

    return str(valor or "").strip()


def limpar_cep(valor):

    return re.sub(r"\D", "", limpar_texto(valor))


def obter_google_maps_api_key():

    return limpar_texto(
        os.getenv("GOOGLE_MAPS_API_KEY")
    )


def obter_env_int(chave, default=0):

    try:
        return int(
            limpar_texto(
                os.getenv(chave)
            )
            or default
        )
    except Exception:
        return default


def obter_env_bool(chave, default=False):

    valor = limpar_texto(
        os.getenv(chave)
    ).lower()

    if not valor:
        return bool(default)

    return valor in (
        "1",
        "true",
        "yes",
        "sim",
        "on",
    )


def geocodificacao_automatica_ativa():

    return obter_env_bool(
        "AUTO_GEOCODING_ENABLED",
        False,
    )


def registrar_google_maps_usage(
    servico,
    consulta,
    status,
    sucesso,
    detalhes=None,
):

    conn = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO GoogleMapsUsage
            (
                Servico,
                Provedor,
                Consulta,
                Status,
                Sucesso,
                Detalhes,
                ConsultadoEm
            )
            VALUES (?, 'google', ?, ?, ?, ?, GETDATE())
        """, (
            limpar_texto(servico),
            limpar_texto(consulta)[:1000],
            limpar_texto(status)[:80],
            int(bool(sucesso)),
            limpar_texto(detalhes)[:2000],
        ))

        cursor.execute("""
            SELECT COUNT(*)
            FROM GoogleMapsUsage
            WHERE Provedor = 'google'
            AND YEAR(ConsultadoEm) = YEAR(GETDATE())
            AND MONTH(ConsultadoEm) = MONTH(GETDATE())
        """)

        total_mes = int(
            cursor.fetchone()[0]
            or 0
        )

        conn.commit()

        limite = obter_env_int(
            "GOOGLE_MAPS_MONTHLY_LIMIT",
            0,
        )
        alerta = obter_env_int(
            "GOOGLE_MAPS_MONTHLY_ALERT_LIMIT",
            0,
        )

        if alerta and total_mes >= alerta:
            LOGGER.warning(
                "Uso Google Maps no mes atingiu alerta: %s/%s",
                total_mes,
                alerta,
            )

        if limite and total_mes >= limite:
            LOGGER.warning(
                "Uso Google Maps no mes atingiu limite configurado: %s/%s",
                total_mes,
                limite,
            )

        return total_mes

    except Exception as ex:
        if conn:
            try:
                conn.rollback()
            except Exception:
                pass

        LOGGER.warning(
            "Nao foi possivel registrar uso Google Maps: %s",
            ex,
        )
        return None

    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass


def normalizar_endereco(dados, fonte="manual"):

    dados = dados or {}

    return {
        "cep": limpar_cep(dados.get("cep") or dados.get("CEP")),
        "logradouro": limpar_texto(dados.get("logradouro") or dados.get("Logradouro")),
        "numero": limpar_texto(dados.get("numero") or dados.get("Numero")),
        "complemento": limpar_texto(dados.get("complemento") or dados.get("Complemento")),
        "bairro": limpar_texto(dados.get("bairro") or dados.get("Bairro")),
        "municipio": limpar_texto(
            dados.get("municipio")
            or dados.get("Municipio")
            or dados.get("localidade")
        ),
        "uf": limpar_texto(dados.get("uf") or dados.get("UF")).upper(),
        "pais": limpar_texto(dados.get("pais") or dados.get("Pais")) or "Brasil",
        "latitude": dados.get("latitude") or dados.get("Latitude"),
        "longitude": dados.get("longitude") or dados.get("Longitude"),
        "fonte": limpar_texto(dados.get("fonte") or dados.get("Fonte")) or fonte,
    }


def montar_texto_endereco(dados):

    dados = normalizar_endereco(dados)

    partes = [
        dados.get("logradouro"),
        dados.get("numero"),
        dados.get("complemento"),
        dados.get("bairro"),
        dados.get("municipio"),
        dados.get("uf"),
        dados.get("pais"),
        dados.get("cep"),
    ]

    return ", ".join(
        limpar_texto(parte)
        for parte in partes
        if limpar_texto(parte)
    )


def montar_textos_geocodificacao(dados):

    dados = normalizar_endereco(dados)

    tentativas = [
        [
            dados.get("logradouro"),
            dados.get("numero"),
            dados.get("bairro"),
            dados.get("municipio"),
            dados.get("uf"),
            dados.get("pais"),
            dados.get("cep"),
        ],
        [
            dados.get("logradouro"),
            dados.get("numero"),
            dados.get("municipio"),
            dados.get("uf"),
            dados.get("pais"),
        ],
        [
            dados.get("logradouro"),
            dados.get("bairro"),
            dados.get("municipio"),
            dados.get("uf"),
            dados.get("pais"),
        ],
        [
            dados.get("logradouro"),
            dados.get("municipio"),
            dados.get("uf"),
            dados.get("pais"),
        ],
    ]

    textos = []

    for partes in tentativas:
        texto = ", ".join(
            limpar_texto(parte)
            for parte in partes
            if limpar_texto(parte)
        )

        if texto and texto not in textos:
            textos.append(texto)

    return textos


def possui_endereco_minimo(dados):

    dados = normalizar_endereco(dados)

    return bool(
        dados.get("logradouro")
        and dados.get("municipio")
        and dados.get("uf")
    )


def _http_get_json(url, params=None):

    import httpx

    with httpx.Client(timeout=8.0) as client:
        response = client.get(
            url,
            params=params,
        )
        response.raise_for_status()
        return response.json()


def _obter_cache_cep(cep):

    conn = get_connection()

    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                CEP,
                Logradouro,
                Bairro,
                Municipio,
                UF,
                Pais,
                Fonte,
                DadosJson
            FROM CepCache
            WHERE CEP = ?
        """, (
            cep,
        ))

        row = cursor.fetchone()

        if not row:
            return None

        return normalizar_endereco({
            "cep": row[0],
            "logradouro": row[1],
            "bairro": row[2],
            "municipio": row[3],
            "uf": row[4],
            "pais": row[5],
            "fonte": row[6],
        }, row[6] or "cache")

    finally:
        conn.close()


def _salvar_cache_cep(endereco, dados_json=None):

    cep = limpar_cep(endereco.get("cep"))

    if not cep:
        return

    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT COUNT(*)
            FROM CepCache
            WHERE CEP = ?
        """, (
            cep,
        ))

        existe = cursor.fetchone()[0] > 0

        dados_serializados = json.dumps(
            dados_json or endereco,
            ensure_ascii=False,
        )

        if existe:
            cursor.execute("""
                UPDATE CepCache
                SET
                    Logradouro = ?,
                    Bairro = ?,
                    Municipio = ?,
                    UF = ?,
                    Pais = ?,
                    Fonte = ?,
                    DadosJson = ?,
                    ConsultadoEm = GETDATE()
                WHERE CEP = ?
            """, (
                endereco.get("logradouro"),
                endereco.get("bairro"),
                endereco.get("municipio"),
                endereco.get("uf"),
                endereco.get("pais") or "Brasil",
                endereco.get("fonte") or "viacep",
                dados_serializados,
                cep,
            ))
        else:
            cursor.execute("""
                INSERT INTO CepCache
                (
                    CEP,
                    Logradouro,
                    Bairro,
                    Municipio,
                    UF,
                    Pais,
                    Fonte,
                    DadosJson,
                    ConsultadoEm
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, GETDATE())
            """, (
                cep,
                endereco.get("logradouro"),
                endereco.get("bairro"),
                endereco.get("municipio"),
                endereco.get("uf"),
                endereco.get("pais") or "Brasil",
                endereco.get("fonte") or "viacep",
                dados_serializados,
            ))

        conn.commit()

    except Exception:
        conn.rollback()
        LOGGER.exception("Erro salvando cache de CEP.")
        raise

    finally:
        conn.close()


def limpar_cache_antigo(dias=180):

    conn = get_connection()

    try:
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM CepCache
            WHERE ConsultadoEm < DATEADD(day, ?, GETDATE())
        """, (
            -abs(int(dias)),
        ))
        conn.commit()
    except Exception:
        conn.rollback()
        LOGGER.exception("Erro limpando cache antigo de CEP.")
    finally:
        conn.close()


def buscar_cep(cep, usar_cache=True):

    cep = limpar_cep(cep)

    if len(cep) != 8:
        raise Exception("Informe um CEP com 8 dígitos.")

    if usar_cache:
        endereco_cache = _obter_cache_cep(cep)

        if endereco_cache:
            endereco_cache["fonte"] = endereco_cache.get("fonte") or "cache"
            return endereco_cache

    try:
        dados = _http_get_json(f"{VIACEP_URL}/{cep}/json/")
    except Exception as ex:
        raise Exception(f"Não foi possível consultar o CEP: {ex}") from ex

    if dados.get("erro"):
        raise Exception("CEP não encontrado.")

    endereco = normalizar_endereco({
        "cep": dados.get("cep") or cep,
        "logradouro": dados.get("logradouro"),
        "complemento": dados.get("complemento"),
        "bairro": dados.get("bairro"),
        "municipio": dados.get("localidade"),
        "uf": dados.get("uf"),
        "pais": "Brasil",
        "fonte": "viacep",
    }, "viacep")

    _salvar_cache_cep(endereco, dados)

    return endereco


def pesquisar_endereco(logradouro=None, municipio=None, uf=None, texto=None):

    if texto:
        partes = [
            parte.strip()
            for parte in limpar_texto(texto).split(",")
            if parte.strip()
        ]

        if len(partes) >= 3:
            logradouro = logradouro or partes[0]
            municipio = municipio or partes[1]
            uf = uf or partes[2]

    logradouro = limpar_texto(logradouro)
    municipio = limpar_texto(municipio)
    uf = limpar_texto(uf).upper()

    if len(uf) != 2:
        raise Exception("Informe a UF para pesquisar o endereço.")

    if len(municipio) < 3:
        raise Exception("Informe a cidade com pelo menos 3 caracteres.")

    if len(logradouro) < 3:
        raise Exception("Informe o endereço com pelo menos 3 caracteres.")

    url = (
        f"{VIACEP_URL}/"
        f"{quote(uf)}/"
        f"{quote(municipio)}/"
        f"{quote(logradouro)}/json/"
    )

    try:
        dados = _http_get_json(url)
    except Exception as ex:
        raise Exception(f"Não foi possível pesquisar o endereço: {ex}") from ex

    if isinstance(dados, dict) and dados.get("erro"):
        return []

    resultados = []

    for item in dados or []:
        endereco = normalizar_endereco({
            "cep": item.get("cep"),
            "logradouro": item.get("logradouro"),
            "complemento": item.get("complemento"),
            "bairro": item.get("bairro"),
            "municipio": item.get("localidade"),
            "uf": item.get("uf"),
            "pais": "Brasil",
            "fonte": "viacep",
        }, "viacep")
        resultados.append(endereco)

        if endereco.get("cep"):
            _salvar_cache_cep(endereco, item)

    return resultados


def geocodificar_google_endereco(dados, api_key):

    tentativas = montar_textos_geocodificacao(dados)

    if not tentativas:
        raise Exception("Informe o endereço antes de gerar a localização.")

    ultimo_status = ""
    ultimo_erro = ""

    for endereco in tentativas:
        LOGGER.info(
            "Geocodificando endereco via Google: %s",
            endereco,
        )

        try:
            resposta = _http_get_json(
                GOOGLE_GEOCODING_URL,
                params={
                    "address": endereco,
                    "key": api_key,
                    "region": "br",
                    "language": "pt-BR",
                },
            )
        except Exception as ex:
            registrar_google_maps_usage(
                "geocoding",
                endereco,
                "ERRO_HTTP",
                False,
                str(ex),
            )
            raise

        status = resposta.get("status")
        ultimo_status = status or ""
        ultimo_erro = resposta.get("error_message") or ""

        registrar_google_maps_usage(
            "geocoding",
            endereco,
            ultimo_status,
            status == "OK" and bool(resposta.get("results")),
            ultimo_erro,
        )

        if status == "OK" and resposta.get("results"):
            resultado = resposta["results"][0]
            location = resultado.get("geometry", {}).get("location", {})

            retorno = normalizar_endereco(dados)
            retorno.update({
                "latitude": float(location.get("lat")),
                "longitude": float(location.get("lng")),
                "fonte": "google",
                "data_geo": datetime.now(),
                "geo_json": resultado,
                "endereco_pesquisado": endereco,
                "endereco_geocodificado": resultado.get("formatted_address"),
            })

            return retorno

        if status not in ("ZERO_RESULTS", None, ""):
            break

    if ultimo_erro:
        raise Exception(
            f"Google Geocoding retornou {ultimo_status}: {ultimo_erro}"
        )

    raise Exception(
        "Google Geocoding nao encontrou localizacao para o endereco informado: "
        f"{tentativas[0]}"
    )


def geocodificar_nominatim_endereco(dados, user_agent="smdm_mdm_erp"):

    tentativas = montar_textos_geocodificacao(dados)

    if not tentativas:
        raise Exception("Informe o endereço antes de gerar a localização.")

    try:
        from geopy.geocoders import Nominatim
    except Exception as ex:
        raise Exception(
            "Biblioteca geopy não instalada. Instale o pacote geopy para gerar localização."
        ) from ex

    try:
        geolocator = Nominatim(
            user_agent=user_agent,
            timeout=10,
        )

        localizacao = None
        endereco_usado = ""

        for endereco in tentativas:
            LOGGER.info(
                "Geocodificando endereco: %s",
                endereco,
            )
            localizacao = geolocator.geocode(
                endereco,
                exactly_one=True,
                addressdetails=True,
                country_codes="br",
            )

            if localizacao:
                endereco_usado = endereco
                break

    except Exception as ex:
        raise Exception(f"Não foi possível gerar a localização: {ex}") from ex

    if not localizacao:
        raise Exception(
            "Localização não encontrada para o endereço informado: "
            f"{tentativas[0]}"
        )

    retorno = normalizar_endereco(dados)
    retorno.update({
        "latitude": float(localizacao.latitude),
        "longitude": float(localizacao.longitude),
        "fonte": "nominatim",
        "data_geo": datetime.now(),
        "geo_json": localizacao.raw,
        "endereco_pesquisado": endereco_usado,
        "endereco_geocodificado": localizacao.address,
    })

    return retorno


def geocodificar_endereco(dados, user_agent="smdm_mdm_erp"):

    api_key = obter_google_maps_api_key()

    if api_key:
        return geocodificar_google_endereco(
            dados,
            api_key,
        )

    return geocodificar_nominatim_endereco(
        dados,
        user_agent,
    )
