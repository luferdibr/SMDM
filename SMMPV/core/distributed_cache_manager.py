
import threading
import time
from dataclasses import (
    dataclass,
    field
)
from datetime import datetime


from core.logger import get_logger

from core.responses import (
    ok,
    erro
)

from core.telemetry import (

    increment_counter,

    add_event
)

from core.event_bus import (
    publish_event
)

from core.middleware import (
    handle_exception
)

from core.governance_center import (
    enforce_quota
)

from core.observability_center import (

    record_metric,

    record_trace
)

from core.tenant_manager import (
    get_current_tenant
)


# ==================================================
# LOGGER
# ==================================================

logger = get_logger(
    "distributed_cache_manager"
)


# ==================================================
# STORAGE
# ==================================================

_LOCK = threading.RLock()

_CACHE = {}

_CACHE_STATS = {

    "hits": 0,

    "misses": 0,

    "invalidations": 0
}


# ==================================================
# HELPERS
# ==================================================

def now():

    return time.time()


def now_str():

    return datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )


# ==================================================
# CACHE ENTRY
# ==================================================

@dataclass
class CacheEntry:

    key: str

    value: any

    tenant_id: str

    created_at: str = field(

        default_factory=lambda:

        now_str()
    )

    ttl: int = 300

    metadata: dict = field(
        default_factory=dict
    )

    # ==============================================
    # EXPIRED
    # ==============================================

    def is_expired(self):

        return (

            now()

            >

            (

                datetime.strptime(

                    self.created_at,

                    "%Y-%m-%d %H:%M:%S"
                ).timestamp()

                +

                self.ttl
            )
        )

    # ==============================================
    # DICT
    # ==============================================

    def to_dict(self):

        return {

            "key": self.key,

            "tenant_id": (
                self.tenant_id
            ),

            "created_at": (
                self.created_at
            ),

            "ttl": self.ttl,

            "metadata": (
                self.metadata
            )
        }


# ==================================================
# SET CACHE
# ==================================================

def set_cache(

    key,

    value,

    ttl=300,

    tenant_id=None,

    metadata=None
):

    try:

        if not enforce_quota(
            "distributed_cache"
        ):

            return erro(
                "Quota excedida."
            )

        entry = CacheEntry(

            key=key,

            value=value,

            tenant_id=(

                tenant_id

                or

                get_current_tenant()
            ),

            ttl=ttl,

            metadata=metadata or {}
        )

        with _LOCK:

            _CACHE[key] = entry

        logger.info(

            (
                f"CACHE SET "
                f"{key}"
            )
        )

        increment_counter(
            "cache_set"
        )

        record_metric(
            "distributed_cache_set"
        )

        record_trace(

            operation="cache_set",

            source=(
                "distributed_cache"
            ),

            status="OK"
        )

        add_event(

            "cache",

            "set",

            {

                "key": key
            }
        )

        publish_event(

            "CACHE_SET",

            entry.to_dict(),

            source=(
                "distributed_cache"
            )
        )

        return ok(

            mensagem=(
                "Cache salvo."
            ),

            dados=entry.to_dict()
        )

    except Exception as ex:

        handle_exception(

            ex,

            contexto=(
                "CACHE_SET"
            )
        )

        return erro(str(ex))


# ==================================================
# GET CACHE
# ==================================================

def get_cache(key):

    try:

        entry = _CACHE.get(key)

        if not entry:

            _CACHE_STATS[
                "misses"
            ] += 1

            record_metric(
                "cache_miss"
            )

            return None

        if entry.is_expired():

            invalidate_cache(key)

            _CACHE_STATS[
                "misses"
            ] += 1

            return None

        _CACHE_STATS[
            "hits"
        ] += 1

        record_metric(
            "cache_hit"
        )

        return entry.value

    except Exception as ex:

        handle_exception(

            ex,

            contexto=(
                "CACHE_GET"
            )
        )

        return None


# ==================================================
# INVALIDATE
# ==================================================

def invalidate_cache(key):

    with _LOCK:

        if key in _CACHE:

            del _CACHE[key]

            _CACHE_STATS[
                "invalidations"
            ] += 1

            logger.warning(

                (
                    f"CACHE INVALIDATE "
                    f"{key}"
                )
            )

            increment_counter(
                "cache_invalidation"
            )

            record_metric(
                "cache_invalidation"
            )

            publish_event(

                "CACHE_INVALIDATED",

                {

                    "key": key
                },

                source=(
                    "distributed_cache"
                )
            )

            return True

    return False


# ==================================================
# CLEAR TENANT
# ==================================================

def clear_tenant_cache(
    tenant_id
):

    removed = []

    with _LOCK:

        keys = list(_CACHE.keys())

        for key in keys:

            entry = _CACHE[key]

            if (

                entry.tenant_id

                ==

                tenant_id
            ):

                removed.append(key)

                del _CACHE[key]

    logger.warning(

        (
            f"TENANT CACHE CLEAR "
            f"{tenant_id}"
        )
    )

    publish_event(

        "TENANT_CACHE_CLEARED",

        {

            "tenant_id": (
                tenant_id
            ),

            "removed": removed
        },

        source=(
            "distributed_cache"
        )
    )

    return removed


# ==================================================
# REPLICATION
# ==================================================

def replicate_cache():

    logger.info(
        "Cache replication."
    )

    publish_event(

        "CACHE_REPLICATION",

        {

            "entries": len(
                _CACHE
            )
        },

        source=(
            "distributed_cache"
        )
    )

    return True


# ==================================================
# CLEANUP
# ==================================================

def cleanup_expired():

    removed = 0

    with _LOCK:

        keys = list(_CACHE.keys())

        for key in keys:

            entry = _CACHE[key]

            if entry.is_expired():

                del _CACHE[key]

                removed += 1

    if removed > 0:

        logger.info(

            (
                f"CACHE CLEANUP "
                f"{removed}"
            )
        )

    return removed


# ==================================================
# STATUS
# ==================================================

def get_cache_status():

    return {

        "entries": len(
            _CACHE
        ),

        "hits": (
            _CACHE_STATS["hits"]
        ),

        "misses": (
            _CACHE_STATS["misses"]
        ),

        "invalidations": (

            _CACHE_STATS[
                "invalidations"
            ]
        )
    }


# ==================================================
# EXPORT
# ==================================================

def dump_cache():

    return {

        k: v.to_dict()

        for k, v in (
            _CACHE.items()
        )
    }


# ==================================================
# STARTUP
# ==================================================

logger.info(
    "Distributed cache manager inicializado."
)
