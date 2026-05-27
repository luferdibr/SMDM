
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


# ==================================================
# LOGGER
# ==================================================

logger = get_logger(
    "distributed_workers"
)


# ==================================================
# STORAGE
# ==================================================

_TASK_QUEUE = queue.Queue()

_WORKERS = {}

_RUNNING = False

_LOCK = threading.RLock()


# ==================================================
# CONFIG
# ==================================================

DEFAULT_WORKERS = 2

MAX_RETRIES = 3

POLL_INTERVAL = 1


# ==================================================
# TASK
# ==================================================

@dataclass
class WorkerTask:

    task_id: str

    name: str

    callback: callable

    args: tuple = ()

    kwargs: dict = field(
        default_factory=dict
    )

    tenant_id: str = None

    retries: int = 0

    max_retries: int = MAX_RETRIES

    created_at: str = field(

        default_factory=lambda:

        datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    )

    metadata: dict = field(
        default_factory=dict
    )

    # ==============================================
    # DICT
    # ==============================================

    def to_dict(self):

        return {

            "task_id": self.task_id,

            "name": self.name,

            "tenant_id": (
                self.tenant_id
            ),

            "retries": self.retries,

            "max_retries": (
                self.max_retries
            ),

            "created_at": (
                self.created_at
            ),

            "metadata": (
                self.metadata
            )
        }


# ==================================================
# WORKER
# ==================================================

@dataclass
class Worker:

    worker_id: str

    active: bool = True

    running: bool = False

    processed_tasks: int = 0

    failed_tasks: int = 0

    created_at: str = field(

        default_factory=lambda:

        datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    )

    thread = None

    # ==============================================
    # DICT
    # ==============================================

    def to_dict(self):

        return {

            "worker_id": self.worker_id,

            "active": self.active,

            "running": self.running,

            "processed_tasks": (
                self.processed_tasks
            ),

            "failed_tasks": (
                self.failed_tasks
            ),

            "created_at": (
                self.created_at
            )
        }


# ==================================================
# HELPERS
# ==================================================

def now():

    return time.time()


def generate_task_id():

    return (

        f"TASK_"

        f"{int(now() * 1000)}"
    )


# ==================================================
# REGISTER WORKER
# ==================================================

def register_worker(worker_id):

    worker = Worker(
        worker_id=worker_id
    )

    _WORKERS[worker_id] = worker

    logger.info(
        f"WORKER REGISTER {worker_id}"
    )

    increment_counter(
        "workers_registered"
    )

    return worker


# ==================================================
# TASK
# ==================================================

def dispatch_task(

    name,

    callback,

    *args,

    tenant_id=None,

    metadata=None,

    **kwargs
):

    task = WorkerTask(

        task_id=generate_task_id(),

        name=name,

        callback=callback,

        args=args,

        kwargs=kwargs,

        tenant_id=(
            tenant_id
            or
            get_current_tenant()
        ),

        metadata=metadata or {}
    )

    _TASK_QUEUE.put(task)

    logger.info(

        (
            f"TASK DISPATCH "
            f"{task.task_id}"
        )
    )

    increment_counter(
        "tasks_dispatched"
    )

    publish_event(

        "TASK_DISPATCHED",

        task.to_dict(),

        source="distributed_workers"
    )

    return task


# ==================================================
# EXECUTE
# ==================================================

def execute_task(

    worker,

    task
):

    started = now()

    try:

        worker.running = True

        logger.info(

            (
                f"TASK START "
                f"{task.task_id}"
            )
        )

        increment_counter(
            "tasks_started"
        )

        publish_event(

            "TASK_STARTED",

            task.to_dict(),

            source="distributed_workers"
        )

        result = task.callback(

            *task.args,

            **task.kwargs
        )

        duration = now() - started

        worker.processed_tasks += 1

        logger.info(

            (
                f"TASK END "
                f"{task.task_id} "
                f"{duration:.4f}s"
            )
        )

        increment_counter(
            "tasks_completed"
        )

        add_event(

            "worker",

            "task_completed",

            {

                "task": (
                    task.to_dict()
                ),

                "duration": duration
            }
        )

        publish_event(

            "TASK_COMPLETED",

            {

                "task": (
                    task.to_dict()
                ),

                "duration": duration
            },

            source="distributed_workers"
        )

        return result

    except Exception as ex:

        worker.failed_tasks += 1

        logger.exception(

            (
                f"TASK ERROR "
                f"{task.task_id}"
            )
        )

        increment_counter(
            "tasks_failed"
        )

        publish_event(

            "TASK_FAILED",

            {

                "task": (
                    task.to_dict()
                ),

                "error": str(ex),

                "traceback": (
                    traceback.format_exc()
                )
            },

            source="distributed_workers"
        )

        # ==========================================
        # RETRY
        # ==========================================

        if (

            task.retries

            <

            task.max_retries

        ):

            task.retries += 1

            _TASK_QUEUE.put(task)

            logger.warning(

                (
                    f"TASK RETRY "
                    f"{task.task_id} "
                    f"{task.retries}"
                )
            )

        else:

            handle_exception(

                ex,

                contexto=(
                    "DISTRIBUTED_TASK"
                )
            )

        return None

    finally:

        worker.running = False


# ==================================================
# LOOP
# ==================================================

def worker_loop(worker):

    logger.info(

        (
            f"WORKER START "
            f"{worker.worker_id}"
        )
    )

    while _RUNNING:

        try:

            try:

                task = _TASK_QUEUE.get(

                    timeout=POLL_INTERVAL
                )

            except queue.Empty:

                continue

            execute_task(
                worker,
                task
            )

        except Exception as ex:

            handle_exception(

                ex,

                contexto="WORKER_LOOP"
            )

    logger.warning(

        (
            f"WORKER STOP "
            f"{worker.worker_id}"
        )
    )


# ==================================================
# START
# ==================================================

def start_workers(

    total=DEFAULT_WORKERS
):

    global _RUNNING

    if _RUNNING:

        return False

    _RUNNING = True

    for i in range(total):

        worker_id = (
            f"worker_{i+1}"
        )

        worker = register_worker(
            worker_id
        )

        thread = threading.Thread(

            target=worker_loop,

            args=(worker,),

            daemon=True
        )

        worker.thread = thread

        thread.start()

    logger.info(
        "Distributed workers iniciado."
    )

    increment_counter(
        "worker_pool_starts"
    )

    publish_event(

        "WORKERS_STARTED",

        {

            "workers": total
        },

        source="distributed_workers"
    )

    return True


# ==================================================
# STOP
# ==================================================

def stop_workers():

    global _RUNNING

    _RUNNING = False

    logger.warning(
        "Distributed workers finalizado."
    )

    publish_event(

        "WORKERS_STOPPED",

        source="distributed_workers"
    )

    return True


# ==================================================
# STATUS
# ==================================================

def get_worker_status():

    return {

        "running": _RUNNING,

        "queue_size": (
            _TASK_QUEUE.qsize()
        ),

        "workers": [

            x.to_dict()

            for x in _WORKERS.values()
        ]
    }


# ==================================================
# DEBUG
# ==================================================

def dump_worker_state():

    return {

        "running": _RUNNING,

        "workers": {

            k: v.to_dict()

            for k, v in (
                _WORKERS.items()
            )
        },

        "queue_size": (
            _TASK_QUEUE.qsize()
        )
    }


# ==================================================
# STARTUP
# ==================================================

logger.info(
    "Distributed workers inicializado."
)
