
import queue
import threading
import time
import traceback
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

from core.tenant_manager import (
    get_current_tenant
)

from core.distributed_workers import (
    dispatch_task
)


# ==================================================
# LOGGER
# ==================================================

logger = get_logger(
    "cloud_sync"
)


# ==================================================
# STORAGE
# ==================================================

_SYNC_QUEUE = queue.Queue()

_SYNC_HISTORY = []

_LOCK = threading.RLock()

_RUNNING = False


# ==================================================
# CONFIG
# ==================================================

MAX_RETRIES = 5

POLL_INTERVAL = 1

MAX_HISTORY = 1000


# ==================================================
# SYNC ITEM
# ==================================================

@dataclass
class SyncItem:

    sync_id: str

    entity: str

    operation: str

    payload: dict

    tenant_id: str

    retries: int = 0

    max_retries: int = MAX_RETRIES

    synced: bool = False

    failed: bool = False

    created_at: str = field(

        default_factory=lambda:

        datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    )

    synced_at: str = None

    metadata: dict = field(
        default_factory=dict
    )

    # ==============================================
    # DICT
    # ==============================================

    def to_dict(self):

        return {

            "sync_id": self.sync_id,

            "entity": self.entity,

            "operation": (
                self.operation
            ),

            "tenant_id": (
                self.tenant_id
            ),

            "retries": self.retries,

            "max_retries": (
                self.max_retries
            ),

            "synced": self.synced,

            "failed": self.failed,

            "created_at": (
                self.created_at
            ),

            "synced_at": (
                self.synced_at
            ),

            "metadata": (
                self.metadata
            )
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


def generate_sync_id():

    return (

        f"SYNC_"

        f"{int(now() * 1000)}"
    )


# ==================================================
# HISTORY
# ==================================================

def add_sync_history(item):

    with _LOCK:

        _SYNC_HISTORY.append(
            item.to_dict()
        )

        if (

            len(_SYNC_HISTORY)

            > MAX_HISTORY

        ):

            _SYNC_HISTORY.pop(0)


# ==================================================
# CREATE
# ==================================================

def create_sync_item(

    entity,

    operation,

    payload,

    tenant_id=None,

    metadata=None
):

    item = SyncItem(

        sync_id=generate_sync_id(),

        entity=entity,

        operation=operation,

        payload=payload,

        tenant_id=(

            tenant_id

            or

            get_current_tenant()
        ),

        metadata=metadata or {}
    )

    return item


# ==================================================
# ENQUEUE
# ==================================================

def enqueue_sync(item):

    _SYNC_QUEUE.put(item)

    logger.info(

        (
            f"SYNC ENQUEUE "
            f"{item.sync_id}"
        )
    )

    increment_counter(
        "sync_enqueued"
    )

    publish_event(

        "SYNC_ENQUEUED",

        item.to_dict(),

        source="cloud_sync"
    )

    return item


# ==================================================
# API
# ==================================================

def sync_entity(

    entity,

    operation,

    payload,

    tenant_id=None,

    metadata=None
):

    item = create_sync_item(

        entity=entity,

        operation=operation,

        payload=payload,

        tenant_id=tenant_id,

        metadata=metadata
    )

    enqueue_sync(item)

    return ok(

        mensagem="Sync enfileirado.",

        dados=item.to_dict()
    )


# ==================================================
# EXECUTE
# ==================================================

def execute_sync(item):

    started = now()

    try:

        logger.info(

            (
                f"SYNC START "
                f"{item.sync_id}"
            )
        )

        increment_counter(
            "sync_started"
        )

        publish_event(

            "SYNC_STARTED",

            item.to_dict(),

            source="cloud_sync"
        )

        # ==========================================
        # PLACEHOLDER CLOUD
        # ==========================================

        time.sleep(0.1)

        item.synced = True

        item.synced_at = now_str()

        duration = now() - started

        logger.info(

            (
                f"SYNC END "
                f"{item.sync_id} "
                f"{duration:.4f}s"
            )
        )

        increment_counter(
            "sync_completed"
        )

        add_event(

            "cloud_sync",

            "sync_completed",

            {

                "sync": (
                    item.to_dict()
                ),

                "duration": duration
            }
        )

        publish_event(

            "SYNC_COMPLETED",

            {

                "sync": (
                    item.to_dict()
                ),

                "duration": duration
            },

            source="cloud_sync"
        )

        add_sync_history(item)

        return True

    except Exception as ex:

        item.retries += 1

        logger.exception(

            (
                f"SYNC ERROR "
                f"{item.sync_id}"
            )
        )

        increment_counter(
            "sync_failed"
        )

        publish_event(

            "SYNC_FAILED",

            {

                "sync": (
                    item.to_dict()
                ),

                "error": str(ex),

                "traceback": (
                    traceback.format_exc()
                )
            },

            source="cloud_sync"
        )

        # ==========================================
        # RETRY
        # ==========================================

        if (

            item.retries

            <

            item.max_retries

        ):

            enqueue_sync(item)

            logger.warning(

                (
                    f"SYNC RETRY "
                    f"{item.sync_id} "
                    f"{item.retries}"
                )
            )

        else:

            item.failed = True

            handle_exception(

                ex,

                contexto="CLOUD_SYNC"
            )

            add_sync_history(item)

        return False


# ==================================================
# LOOP
# ==================================================

def sync_loop():

    logger.info(
        "Cloud sync iniciado."
    )

    while _RUNNING:

        try:

            try:

                item = _SYNC_QUEUE.get(

                    timeout=POLL_INTERVAL
                )

            except queue.Empty:

                continue

            dispatch_task(

                "cloud_sync",

                execute_sync,

                item,

                tenant_id=(
                    item.tenant_id
                )
            )

        except Exception as ex:

            handle_exception(

                ex,

                contexto="SYNC_LOOP"
            )

    logger.warning(
        "Cloud sync finalizado."
    )


# ==================================================
# START
# ==================================================

def start_cloud_sync():

    global _RUNNING

    if _RUNNING:

        return False

    _RUNNING = True

    threading.Thread(

        target=sync_loop,

        daemon=True
    ).start()

    logger.info(
        "Cloud sync manager iniciado."
    )

    increment_counter(
        "cloud_sync_starts"
    )

    publish_event(

        "CLOUD_SYNC_STARTED",

        source="cloud_sync"
    )

    return True


# ==================================================
# STOP
# ==================================================

def stop_cloud_sync():

    global _RUNNING

    _RUNNING = False

    logger.warning(
        "Cloud sync parado."
    )

    publish_event(

        "CLOUD_SYNC_STOPPED",

        source="cloud_sync"
    )

    return True


# ==================================================
# STATUS
# ==================================================

def get_cloud_sync_status():

    return {

        "running": _RUNNING,

        "queue_size": (
            _SYNC_QUEUE.qsize()
        ),

        "history": len(
            _SYNC_HISTORY
        )
    }


# ==================================================
# HISTORY
# ==================================================

def get_sync_history():

    with _LOCK:

        return list(
            _SYNC_HISTORY
        )


# ==================================================
# DEBUG
# ==================================================

def dump_cloud_sync():

    return {

        "running": _RUNNING,

        "queue_size": (
            _SYNC_QUEUE.qsize()
        ),

        "history": len(
            _SYNC_HISTORY
        )
    }


# ==================================================
# BUILTIN EVENTS
# ==================================================

def sync_created_entity(

    entity,

    payload
):

    return sync_entity(

        entity=entity,

        operation="CREATE",

        payload=payload
    )


def sync_updated_entity(

    entity,

    payload
):

    return sync_entity(

        entity=entity,

        operation="UPDATE",

        payload=payload
    )


def sync_deleted_entity(

    entity,

    payload
):

    return sync_entity(

        entity=entity,

        operation="DELETE",

        payload=payload
    )


# ==================================================
# STARTUP
# ==================================================

logger.info(
    "Cloud sync inicializado."
)
