
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

from core.tenant_manager import (
    get_current_tenant
)


# ==================================================
# LOGGER
# ==================================================

logger = get_logger(
    "container_runtime"
)


# ==================================================
# STORAGE
# ==================================================

_LOCK = threading.RLock()

_CONTAINERS = {}

_RUNTIME_RUNNING = False


# ==================================================
# CONFIG
# ==================================================

STATUS_CREATED = "CREATED"

STATUS_RUNNING = "RUNNING"

STATUS_STOPPED = "STOPPED"

STATUS_FAILED = "FAILED"

STATUS_DESTROYED = "DESTROYED"


# ==================================================
# HELPERS
# ==================================================

def now():

    return time.time()


def now_str():

    return datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )


def generate_container_id():

    return (

        f"CTR_"

        f"{int(now() * 1000)}"
    )


# ==================================================
# CONTAINER
# ==================================================

@dataclass
class RuntimeContainer:

    container_id: str

    nome: str

    image: str

    tenant_id: str = None

    status: str = STATUS_CREATED

    created_at: str = field(

        default_factory=lambda:

        now_str()
    )

    started_at: str = None

    stopped_at: str = None

    restart_count: int = 0

    metadata: dict = field(
        default_factory=dict
    )

    health: str = "UP"

    # ==============================================
    # DICT
    # ==============================================

    def to_dict(self):

        return {

            "container_id": (
                self.container_id
            ),

            "nome": self.nome,

            "image": self.image,

            "tenant_id": (
                self.tenant_id
            ),

            "status": self.status,

            "created_at": (
                self.created_at
            ),

            "started_at": (
                self.started_at
            ),

            "stopped_at": (
                self.stopped_at
            ),

            "restart_count": (
                self.restart_count
            ),

            "metadata": (
                self.metadata
            ),

            "health": self.health
        }


# ==================================================
# CREATE
# ==================================================

def create_container(

    nome,

    image,

    tenant_id=None,

    metadata=None
):

    container = RuntimeContainer(

        container_id=(
            generate_container_id()
        ),

        nome=nome,

        image=image,

        tenant_id=(

            tenant_id

            or

            get_current_tenant()
        ),

        metadata=metadata or {}
    )

    with _LOCK:

        _CONTAINERS[
            container.container_id
        ] = container

    logger.info(

        (
            f"CONTAINER CREATE "
            f"{container.container_id}"
        )
    )

    increment_counter(
        "containers_created"
    )

    publish_event(

        "CONTAINER_CREATED",

        container.to_dict(),

        source="container_runtime"
    )

    return ok(

        mensagem="Container criado.",

        dados=container.to_dict()
    )


# ==================================================
# GET
# ==================================================

def get_container(container_id):

    return _CONTAINERS.get(
        container_id
    )


# ==================================================
# START
# ==================================================

def start_container(container_id):

    container = get_container(
        container_id
    )

    if not container:

        return erro(
            "Container inválido."
        )

    try:

        container.status = (
            STATUS_RUNNING
        )

        container.started_at = (
            now_str()
        )

        logger.info(

            (
                f"CONTAINER START "
                f"{container_id}"
            )
        )

        increment_counter(
            "containers_started"
        )

        publish_event(

            "CONTAINER_STARTED",

            container.to_dict(),

            source=(
                "container_runtime"
            )
        )

        return ok(

            mensagem=(
                "Container iniciado."
            ),

            dados=container.to_dict()
        )

    except Exception as ex:

        container.status = (
            STATUS_FAILED
        )

        handle_exception(

            ex,

            contexto=(
                "CONTAINER_START"
            )
        )

        return erro(str(ex))


# ==================================================
# STOP
# ==================================================

def stop_container(container_id):

    container = get_container(
        container_id
    )

    if not container:

        return False

    container.status = (
        STATUS_STOPPED
    )

    container.stopped_at = (
        now_str()
    )

    logger.warning(

        (
            f"CONTAINER STOP "
            f"{container_id}"
        )
    )

    increment_counter(
        "containers_stopped"
    )

    publish_event(

        "CONTAINER_STOPPED",

        container.to_dict(),

        source="container_runtime"
    )

    return True


# ==================================================
# RESTART
# ==================================================

def restart_container(
    container_id
):

    container = get_container(
        container_id
    )

    if not container:

        return False

    stop_container(container_id)

    time.sleep(1)

    container.restart_count += 1

    result = start_container(
        container_id
    )

    publish_event(

        "CONTAINER_RESTARTED",

        container.to_dict(),

        source="container_runtime"
    )

    return result


# ==================================================
# DESTROY
# ==================================================

def destroy_container(
    container_id
):

    container = get_container(
        container_id
    )

    if not container:

        return False

    container.status = (
        STATUS_DESTROYED
    )

    logger.warning(

        (
            f"CONTAINER DESTROY "
            f"{container_id}"
        )
    )

    increment_counter(
        "containers_destroyed"
    )

    publish_event(

        "CONTAINER_DESTROYED",

        container.to_dict(),

        source="container_runtime"
    )

    return True


# ==================================================
# HEALTH
# ==================================================

def update_container_health(

    container_id,

    health
):

    container = get_container(
        container_id
    )

    if not container:

        return False

    container.health = str(
        health
    )

    return True


# ==================================================
# STATUS
# ==================================================

def get_runtime_status():

    return {

        "runtime_running": (
            _RUNTIME_RUNNING
        ),

        "containers": len(
            _CONTAINERS
        ),

        "running": len([

            x

            for x in (
                _CONTAINERS.values()
            )

            if (

                x.status

                ==

                STATUS_RUNNING
            )
        ])
    }


# ==================================================
# LIST
# ==================================================

def get_containers():

    return {

        k: v.to_dict()

        for k, v in (
            _CONTAINERS.items()
        )
    }


# ==================================================
# START RUNTIME
# ==================================================

def start_runtime():

    global _RUNTIME_RUNNING

    if _RUNTIME_RUNNING:

        return False

    _RUNTIME_RUNNING = True

    logger.info(
        "Container runtime iniciado."
    )

    increment_counter(
        "runtime_starts"
    )

    publish_event(

        "RUNTIME_STARTED",

        source="container_runtime"
    )

    return True


# ==================================================
# STOP RUNTIME
# ==================================================

def stop_runtime():

    global _RUNTIME_RUNNING

    _RUNTIME_RUNNING = False

    logger.warning(
        "Container runtime parado."
    )

    publish_event(

        "RUNTIME_STOPPED",

        source="container_runtime"
    )

    return True


# ==================================================
# DEBUG
# ==================================================

def dump_runtime():

    return {

        "runtime_running": (
            _RUNTIME_RUNNING
        ),

        "containers": {

            k: v.to_dict()

            for k, v in (
                _CONTAINERS.items()
            )
        }
    }


# ==================================================
# STARTUP
# ==================================================

logger.info(
    "Container runtime inicializado."
)
