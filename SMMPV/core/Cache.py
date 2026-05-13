
import time
from threading import RLock


from core.logger import get_logger


# ==================================================
# LOGGER
# ==================================================

logger = get_logger("cache")


# ==================================================
# CACHE STORE
# ==================================================

_CACHE = {}

_LOCK = RLock()


# ==================================================
# STATS
# ==================================================

_STATS = {

    "hits": 0,

    "misses": 0,

    "sets": 0,

    "deletes": 0,

    "clears": 0,

    "expired": 0
}


# ==================================================
# CONFIG
# ==================================================

DEFAULT_TTL = 300

MAX_NAMESPACE_LENGTH = 50

MAX_KEY_LENGTH = 200


# ==================================================
# HELPERS
# ==================================================

def now():

    return time.time()


def normalize_namespace(namespace):

    if not namespace:
        return "global"

    namespace = str(namespace).strip().lower()

    return namespace[:MAX_NAMESPACE_LENGTH]


def normalize_key(key):

    if key is None:
        return "null"

    key = str(key).strip().lower()

    return key[:MAX_KEY_LENGTH]


def build_cache_key(

    namespace,

    key
):

    namespace = normalize_namespace(
        namespace
    )

    key = normalize_key(key)

    return f"{namespace}:{key}"


# ==================================================
# CLEANUP
# ==================================================

def cleanup_expired():

    removidos = 0

    with _LOCK:

        chaves = list(
            _CACHE.keys()
        )

        timestamp = now()

        for k in chaves:

            item = _CACHE.get(k)

            if not item:
                continue

            expires_at = item.get(
                "expires_at"
            )

            if (
                expires_at
                and
                timestamp > expires_at
            ):

                del _CACHE[k]

                removidos += 1

                _STATS["expired"] += 1

    if removidos:

        logger.info(

            (
                f"CACHE CLEANUP "
                f"{removidos} removidos"
            )
        )

    return removidos


# ==================================================
# SET
# ==================================================

def set_cache(

    key,

    value,

    ttl=DEFAULT_TTL,

    namespace="global"
):

    cleanup_expired()

    cache_key = build_cache_key(

        namespace,

        key
    )

    expires_at = None

    if ttl:

        expires_at = (
            now() + int(ttl)
        )

    with _LOCK:

        _CACHE[cache_key] = {

            "value": value,

            "created_at": now(),

            "expires_at": expires_at
        }

        _STATS["sets"] += 1

    return value


# ==================================================
# GET
# ==================================================

def get_cache(

    key,

    default=None,

    namespace="global"
):

    cleanup_expired()

    cache_key = build_cache_key(

        namespace,

        key
    )

    with _LOCK:

        item = _CACHE.get(
            cache_key
        )

        if not item:

            _STATS["misses"] += 1

            return default

        expires_at = item.get(
            "expires_at"
        )

        if (
            expires_at
            and
            now() > expires_at
        ):

            del _CACHE[cache_key]

            _STATS["expired"] += 1

            _STATS["misses"] += 1

            return default

        _STATS["hits"] += 1

        return item.get("value")


# ==================================================
# HAS
# ==================================================

def has_cache(

    key,

    namespace="global"
):

    valor = get_cache(

        key,

        default=None,

        namespace=namespace
    )

    return valor is not None


# ==================================================
# DELETE
# ==================================================

def delete_cache(

    key,

    namespace="global"
):

    cache_key = build_cache_key(

        namespace,

        key
    )

    with _LOCK:

        if cache_key in _CACHE:

            del _CACHE[cache_key]

            _STATS["deletes"] += 1

            return True

    return False


# ==================================================
# CLEAR NAMESPACE
# ==================================================

def clear_namespace(namespace):

    namespace = normalize_namespace(
        namespace
    )

    removidos = 0

    with _LOCK:

        chaves = list(
            _CACHE.keys()
        )

        prefixo = f"{namespace}:"

        for k in chaves:

            if k.startswith(prefixo):

                del _CACHE[k]

                removidos += 1

        _STATS["clears"] += removidos

    logger.info(

        (
            f"CACHE CLEAR "
            f"namespace={namespace} "
            f"removidos={removidos}"
        )
    )

    return removidos


# ==================================================
# CLEAR ALL
# ==================================================

def clear_all():

    with _LOCK:

        total = len(_CACHE)

        _CACHE.clear()

        _STATS["clears"] += total

    logger.warning(

        (
            f"CACHE RESET "
            f"total={total}"
        )
    )

    return total


# ==================================================
# GET OR SET
# ==================================================

def get_or_set(

    key,

    factory,

    ttl=DEFAULT_TTL,

    namespace="global"
):

    valor = get_cache(

        key,

        default=None,

        namespace=namespace
    )

    if valor is not None:

        return valor

    valor = factory()

    set_cache(

        key,

        valor,

        ttl=ttl,

        namespace=namespace
    )

    return valor


# ==================================================
# INVALIDAÇÃO RBAC
# ==================================================

def invalidate_menu_cache():

    return clear_namespace(
        "menus"
    )


def invalidate_profile_cache():

    return clear_namespace(
        "profiles"
    )


def invalidate_session_cache():

    return clear_namespace(
        "session"
    )


def invalidate_config_cache():

    return clear_namespace(
        "config"
    )


# ==================================================
# STATS
# ==================================================

def get_stats():

    with _LOCK:

        return {

            "items": len(_CACHE),

            "hits": _STATS["hits"],

            "misses": _STATS["misses"],

            "sets": _STATS["sets"],

            "deletes": _STATS["deletes"],

            "clears": _STATS["clears"],

            "expired": _STATS["expired"]
        }


# ==================================================
# DEBUG
# ==================================================

def dump_cache():

    with _LOCK:

        return {

            k: v.copy()

            for k, v in _CACHE.items()
        }


# ==================================================
# SESSION HELPERS
# ==================================================

def set_user_menu_cache(

    usuario_id,

    menus,

    ttl=600
):

    return set_cache(

        key=f"user:{usuario_id}",

        value=menus,

        ttl=ttl,

        namespace="menus"
    )


def get_user_menu_cache(

    usuario_id
):

    return get_cache(

        key=f"user:{usuario_id}",

        namespace="menus"
    )


def clear_user_menu_cache(

    usuario_id
):

    return delete_cache(

        key=f"user:{usuario_id}",

        namespace="menus"
    )


# ==================================================
# STARTUP
# ==================================================

logger.info(
    "Cache central inicializado."
)
