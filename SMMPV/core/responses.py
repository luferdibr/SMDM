
from math import ceil

from core.logger import get_logger

from core.exceptions import (
    SMMPVError,
    exception_to_response
)


# ==================================================
# LOGGER
# ==================================================

logger = get_logger("responses")


# ==================================================
# OK
# ==================================================

def ok(
    mensagem="OK",
    dados=None,
    meta=None
):

    return {

        "sucesso": True,

        "mensagem": str(mensagem),

        "dados": dados,

        "meta": meta or {}
    }


# ==================================================
# WARNING
# ==================================================

def warning(
    mensagem="Aviso.",
    dados=None,
    meta=None
):

    return {

        "sucesso": False,

        "warning": True,

        "mensagem": str(mensagem),

        "dados": dados,

        "meta": meta or {}
    }


# ==================================================
# ERROR
# ==================================================

def erro(
    mensagem="Erro.",
    dados=None,
    codigo="ERROR",
    detalhes=None,
    meta=None
):

    return {

        "sucesso": False,

        "codigo": codigo,

        "mensagem": str(mensagem),

        "detalhes": detalhes,

        "dados": dados,

        "meta": meta or {}
    }


# ==================================================
# CREATED
# ==================================================

def created(
    mensagem="Registro criado.",
    dados=None,
    meta=None
):

    return {

        "sucesso": True,

        "created": True,

        "mensagem": str(mensagem),

        "dados": dados,

        "meta": meta or {}
    }


# ==================================================
# UPDATED
# ==================================================

def updated(
    mensagem="Registro atualizado.",
    dados=None,
    meta=None
):

    return {

        "sucesso": True,

        "updated": True,

        "mensagem": str(mensagem),

        "dados": dados,

        "meta": meta or {}
    }


# ==================================================
# DELETED
# ==================================================

def deleted(
    mensagem="Registro removido.",
    dados=None,
    meta=None
):

    return {

        "sucesso": True,

        "deleted": True,

        "mensagem": str(mensagem),

        "dados": dados,

        "meta": meta or {}
    }


# ==================================================
# VALIDATION ERROR
# ==================================================

def validation_error(
    mensagem="Dados inválidos.",
    detalhes=None,
    dados=None
):

    return erro(

        mensagem=mensagem,

        codigo="VALIDATION_ERROR",

        detalhes=detalhes,

        dados=dados
    )


# ==================================================
# NOT FOUND
# ==================================================

def not_found(
    mensagem="Registro não encontrado.",
    dados=None
):

    return erro(

        mensagem=mensagem,

        codigo="NOT_FOUND",

        dados=dados
    )


# ==================================================
# ACCESS DENIED
# ==================================================

def access_denied(
    mensagem="Acesso negado.",
    dados=None
):

    return erro(

        mensagem=mensagem,

        codigo="ACCESS_DENIED",

        dados=dados
    )


# ==================================================
# DATABASE ERROR
# ==================================================

def database_error(
    mensagem="Erro banco dados.",
    detalhes=None,
    dados=None
):

    return erro(

        mensagem=mensagem,

        codigo="DATABASE_ERROR",

        detalhes=detalhes,

        dados=dados
    )


# ==================================================
# SYSTEM ERROR
# ==================================================

def system_error(
    mensagem="Erro interno sistema.",
    detalhes=None,
    dados=None
):

    return erro(

        mensagem=mensagem,

        codigo="SYSTEM_ERROR",

        detalhes=detalhes,

        dados=dados
    )


# ==================================================
# PAGINATED
# ==================================================

def paginated(

    registros,

    pagina=1,

    tamanho=50,

    total=None,

    mensagem="OK"
):

    try:

        pagina = int(pagina)

    except Exception:

        pagina = 1

    try:

        tamanho = int(tamanho)

    except Exception:

        tamanho = 50

    if pagina <= 0:
        pagina = 1

    if tamanho <= 0:
        tamanho = 50

    if total is None:

        total = len(registros)

    total_paginas = ceil(
        total / tamanho
    ) if tamanho else 1

    return {

        "sucesso": True,

        "mensagem": mensagem,

        "dados": registros,

        "meta": {

            "pagina": pagina,

            "tamanho": tamanho,

            "total": total,

            "total_paginas": total_paginas
        }
    }


# ==================================================
# EXCEPTION RESPONSE
# ==================================================

def from_exception(ex):

    try:

        # ==========================================
        # EXCEPTION CUSTOM
        # ==========================================

        if isinstance(
            ex,
            SMMPVError
        ):

            return exception_to_response(ex)

        # ==========================================
        # GENERIC
        # ==========================================

        logger.exception(
            "UNHANDLED EXCEPTION"
        )

        return erro(

            mensagem=str(ex),

            codigo="UNHANDLED_EXCEPTION"
        )

    except Exception as fatal:

        logger.exception(
            "FATAL RESPONSE ERROR"
        )

        return {

            "sucesso": False,

            "codigo": "FATAL_RESPONSE_ERROR",

            "mensagem": str(fatal),

            "detalhes": None,

            "dados": None,

            "meta": {}
        }


# ==================================================
# BOOLEAN
# ==================================================

def is_ok(response):

    try:

        return bool(
            response.get(
                "sucesso"
            )
        )

    except Exception:

        return False


# ==================================================
# MESSAGE
# ==================================================

def get_message(
    response,
    default=""
):

    try:

        return str(

            response.get(
                "mensagem",
                default
            )
        )

    except Exception:

        return default


# ==================================================
# DATA
# ==================================================

def get_data(
    response,
    default=None
):

    try:

        return response.get(
            "dados",
            default
        )

    except Exception:

        return default


# ==================================================
# META
# ==================================================

def get_meta(
    response,
    default=None
):

    try:

        return response.get(
            "meta",
            default or {}
        )

    except Exception:

        return default or {}
