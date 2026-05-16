
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

from core.distributed_cache_manager import (

    set_cache,

    get_cache
)

from core.tenant_manager import (
    get_current_tenant
)


# ==================================================
# LOGGER
# ==================================================

logger = get_logger(
    "runtime_state_manager"
)


# ==================================================
# STORAGE
# ==================================================

_LOCK = threading.RLock()

_RUNTIME_STATE = {}

_RUNTIME_SNAPSHOTS = []


# ==================================================
# CONFIG
# ==================================================

MAX_SNAPSHOTS = 100


# ==================================================
# HELPERS
# ==================================================

def now():

    return time.time()


def now_str():

    return datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )


def generate_snapshot_id():

    return (

        f"SNAPSHOT_"

        f"{int(now() * 1000)}"
    )


# ==================================================
# STATE ENTRY
# ==================================================

@dataclass
class RuntimeState:

    key: str

    value: any

    tenant_id: str

    updated_at: str = field(

        default_factory=lambda:

        now_str()
    )

    metadata: dict = field(
        default_factory=dict
    )

    # ==============================================
    # DICT
    # ==============================================

    def to_dict(self):

        return {

            "key": self.key,

            "value": self.value,

            "tenant_id": (
                self.tenant_id
            ),

            "updated_at": (
                self.updated_at
            ),

            "metadata": (
                self.metadata
            )
        }


# ==================================================
# SNAPSHOT
# ==================================================

@dataclass
class RuntimeSnapshot:

    snapshot_id: str

    created_at: str = field(

        default_factory=lambda:

        now_str()
    )

    state: dict = field(
        default_factory=dict
    )

    metadata: dict = field(
        default_factory=dict
    )

    # ==============================================
    # DICT
    # ==============================================

    def to_dict(self):

        return {

            "snapshot_id": (
                self.snapshot_id
            ),

            "created_at": (
                self.created_at
            ),

            "state": self.state,

            "metadata": (
                self.metadata
            )
        }


# ==================================================
# SET STATE
# ==================================================

def set_runtime_state(

    key,

    value,

    tenant_id=None,

    metadata=None
):

    try:

        if not enforce_quota(
            "runtime_state"
        ):

            return erro(
                "Quota excedida."
            )

        state = RuntimeState(

            key=key,

            value=value,

            tenant_id=(

                tenant_id

                or

                get_current_tenant()
            ),

            metadata=metadata or {}
        )

        with _LOCK:

            _RUNTIME_STATE[
                key
            ] = state

        set_cache(

            key=(
                f"runtime_state:{key}"
            ),

            value=state.to_dict(),

            ttl=600
        )

        logger.info(

            (
                f"STATE UPDATE "
                f"{key}"
            )
        )

        increment_counter(
            "runtime_state_update"
        )

        record_metric(
            "runtime_state_update"
        )

        record_trace(

            operation=(
                "set_runtime_state"
            ),

            source=(
                "runtime_state"
            ),

            status="OK"
        )

        add_event(

            "runtime_state",

            "update",

            {

                "key": key
            }
        )

        publish_event(

            "RUNTIME_STATE_UPDATED",

            state.to_dict(),

            source=(
                "runtime_state"
            )
        )

        return ok(

            mensagem=(
                "Estado atualizado."
            ),

            dados=state.to_dict()
        )

    except Exception as ex:

        handle_exception(

            ex,

            contexto=(
                "RUNTIME_STATE_SET"
            )
        )

        return erro(str(ex))


# ==================================================
# GET STATE
# ==================================================

def get_runtime_state(
    key
):

    cache_key = (
        f"runtime_state:{key}"
    )

    cached = get_cache(
        cache_key
    )

    if cached:

        return cached

    state = _RUNTIME_STATE.get(
        key
    )

    if not state:

        return None

    return state.to_dict()


# ==================================================
# DELETE STATE
# ==================================================

def delete_runtime_state(
    key
):

    with _LOCK:

        if key in _RUNTIME_STATE:

            del _RUNTIME_STATE[key]

            logger.warning(

                (
                    f"STATE DELETE "
                    f"{key}"
                )
            )

            increment_counter(
                "runtime_state_delete"
            )

            publish_event(

                "RUNTIME_STATE_DELETED",

                {

                    "key": key
                },

                source=(
                    "runtime_state"
                )
            )

            return True

    return False


# ==================================================
# SNAPSHOT
# ==================================================

def create_snapshot(
    metadata=None
):

    snapshot = RuntimeSnapshot(

        snapshot_id=(
            generate_snapshot_id()
        ),

        state={

            k: v.to_dict()

            for k, v in (
                _RUNTIME_STATE.items()
            )
        },

        metadata=metadata or {}
    )

    with _LOCK:

        _RUNTIME_SNAPSHOTS.append(
            snapshot
        )

        if (

            len(
                _RUNTIME_SNAPSHOTS
            )

            > MAX_SNAPSHOTS
        ):

            _RUNTIME_SNAPSHOTS.pop(0)

    logger.info(
        "Runtime snapshot."
    )

    increment_counter(
        "runtime_snapshot"
    )

    record_metric(
        "runtime_snapshot"
    )

    publish_event(

        "RUNTIME_SNAPSHOT_CREATED",

        snapshot.to_dict(),

        source=(
            "runtime_state"
        )
    )

    return ok(

        mensagem=(
            "Snapshot criado."
        ),

        dados=snapshot.to_dict()
    )


# ==================================================
# RESTORE
# ==================================================

def restore_snapshot(
    snapshot_id
):

    snapshot = None

    for item in (
        _RUNTIME_SNAPSHOTS
    ):

        if (

            item.snapshot_id

            ==

            snapshot_id
        ):

            snapshot = item

            break

    if not snapshot:

        return erro(
            "Snapshot inválido."
        )

    with _LOCK:

        _RUNTIME_STATE.clear()

        for key, value in (
            snapshot.state.items()
        ):

            state = RuntimeState(

                key=value["key"],

                value=value["value"],

                tenant_id=(
                    value["tenant_id"]
                ),

                metadata=(
                    value.get(
                        "metadata",
                        {}
                    )
                )
            )

            _RUNTIME_STATE[
                key
            ] = state

    logger.warning(

        (
            f"SNAPSHOT RESTORE "
            f"{snapshot_id}"
        )
    )

    publish_event(

        "RUNTIME_SNAPSHOT_RESTORED",

        {

            "snapshot_id": (
                snapshot_id
            )
        },

        source=(
            "runtime_state"
        )
    )

    return ok(

        mensagem=(
            "Snapshot restaurado."
        ),

        dados=snapshot.to_dict()
    )


# ==================================================
# STATUS
# ==================================================

def get_runtime_state_status():

    return {

        "states": len(
            _RUNTIME_STATE
        ),

        "snapshots": len(
            _RUNTIME_SNAPSHOTS
        )
    }


# ==================================================
# EXPORT
# ==================================================

def dump_runtime_state():

    return {

        k: v.to_dict()

        for k, v in (
            _RUNTIME_STATE.items()
        )
    }


def dump_snapshots():

    return [

        x.to_dict()

        for x in (
            _RUNTIME_SNAPSHOTS
        )
    ]


# ==================================================
# STARTUP
# ==================================================

logger.info(
    "Runtime state manager inicializado."
)
