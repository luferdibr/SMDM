
import random
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

from core.container_runtime import (
    create_container
)

from core.governance_center import (
    enforce_quota
)

from core.observability_center import (

    record_metric,

    record_trace
)


# ==================================================
# LOGGER
# ==================================================

logger = get_logger(
    "cluster_orchestrator"
)


# ==================================================
# STORAGE
# ==================================================

_LOCK = threading.RLock()

_NODES = {}

_WORKLOADS = {}


# ==================================================
# CONFIG
# ==================================================

STATUS_ONLINE = "ONLINE"

STATUS_OFFLINE = "OFFLINE"

STATUS_BUSY = "BUSY"

STATUS_FAILED = "FAILED"


# ==================================================
# HELPERS
# ==================================================

def now():

    return time.time()


def now_str():

    return datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )


def generate_node_id():

    return (

        f"NODE_"

        f"{int(now() * 1000)}"
    )


def generate_workload_id():

    return (

        f"WORKLOAD_"

        f"{int(now() * 1000)}"
    )


# ==================================================
# NODE
# ==================================================

@dataclass
class ClusterNode:

    node_id: str

    nome: str

    host: str

    cpu_limit: int = 100

    memory_limit: int = 1024

    current_load: int = 0

    status: str = STATUS_ONLINE

    created_at: str = field(

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

            "node_id": self.node_id,

            "nome": self.nome,

            "host": self.host,

            "cpu_limit": (
                self.cpu_limit
            ),

            "memory_limit": (
                self.memory_limit
            ),

            "current_load": (
                self.current_load
            ),

            "status": self.status,

            "created_at": (
                self.created_at
            ),

            "metadata": (
                self.metadata
            )
        }


# ==================================================
# WORKLOAD
# ==================================================

@dataclass
class ClusterWorkload:

    workload_id: str

    nome: str

    node_id: str

    container_id: str

    created_at: str = field(

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

            "workload_id": (
                self.workload_id
            ),

            "nome": self.nome,

            "node_id": self.node_id,

            "container_id": (
                self.container_id
            ),

            "created_at": (
                self.created_at
            ),

            "metadata": (
                self.metadata
            )
        }


# ==================================================
# NODE REGISTER
# ==================================================

def register_node(

    nome,

    host,

    cpu_limit=100,

    memory_limit=1024,

    metadata=None
):

    node = ClusterNode(

        node_id=(
            generate_node_id()
        ),

        nome=nome,

        host=host,

        cpu_limit=cpu_limit,

        memory_limit=memory_limit,

        metadata=metadata or {}
    )

    with _LOCK:

        _NODES[
            node.node_id
        ] = node

    logger.info(

        (
            f"NODE REGISTER "
            f"{node.node_id}"
        )
    )

    increment_counter(
        "cluster_nodes"
    )

    publish_event(

        "CLUSTER_NODE_REGISTERED",

        node.to_dict(),

        source=(
            "cluster_orchestrator"
        )
    )

    return ok(

        mensagem=(
            "Node registrado."
        ),

        dados=node.to_dict()
    )


# ==================================================
# SELECT NODE
# ==================================================

def select_node():

    available = [

        x

        for x in (
            _NODES.values()
        )

        if (

            x.status

            ==

            STATUS_ONLINE
        )
    ]

    if not available:

        return None

    available.sort(

        key=lambda x:
        x.current_load
    )

    return available[0]


# ==================================================
# SCHEDULE
# ==================================================

def schedule_container(

    nome,

    image,

    tenant_id=None,

    metadata=None
):

    try:

        if not enforce_quota(
            "cluster_workloads"
        ):

            return erro(
                "Quota excedida."
            )

        node = select_node()

        if not node:

            return erro(
                "Nenhum node disponível."
            )

        container_result = (
            create_container(

                nome=nome,

                image=image,

                tenant_id=tenant_id,

                metadata=metadata
            )
        )

        container_data = (
            container_result.get(
                "dados",
                {}
            )
        )

        workload = ClusterWorkload(

            workload_id=(
                generate_workload_id()
            ),

            nome=nome,

            node_id=node.node_id,

            container_id=(
                container_data.get(
                    "container_id"
                )
            ),

            metadata=metadata or {}
        )

        with _LOCK:

            _WORKLOADS[
                workload.workload_id
            ] = workload

            node.current_load += 1

        logger.info(

            (
                f"SCHEDULE "
                f"{workload.workload_id}"
            )
        )

        increment_counter(
            "cluster_workloads"
        )

        record_metric(
            "cluster_schedule"
        )

        record_trace(

            operation=(
                "schedule_container"
            ),

            source=(
                "cluster_orchestrator"
            ),

            status="OK"
        )

        add_event(

            "cluster",

            "schedule",

            workload.to_dict()
        )

        publish_event(

            "WORKLOAD_SCHEDULED",

            workload.to_dict(),

            source=(
                "cluster_orchestrator"
            )
        )

        return ok(

            mensagem=(
                "Workload agendado."
            ),

            dados=workload.to_dict()
        )

    except Exception as ex:

        handle_exception(

            ex,

            contexto=(
                "CLUSTER_SCHEDULE"
            )
        )

        return erro(str(ex))


# ==================================================
# LOAD BALANCER
# ==================================================

def rebalance_cluster():

    logger.info(
        "Cluster rebalance."
    )

    publish_event(

        "CLUSTER_REBALANCE",

        source=(
            "cluster_orchestrator"
        )
    )

    return True


# ==================================================
# HEALTH
# ==================================================

def get_cluster_health():

    return {

        "nodes": len(
            _NODES
        ),

        "workloads": len(
            _WORKLOADS
        ),

        "online_nodes": len([

            x

            for x in (
                _NODES.values()
            )

            if (

                x.status

                ==

                STATUS_ONLINE
            )
        ])
    }


# ==================================================
# LIST
# ==================================================

def get_nodes():

    return {

        k: v.to_dict()

        for k, v in (
            _NODES.items()
        )
    }


def get_workloads():

    return {

        k: v.to_dict()

        for k, v in (
            _WORKLOADS.items()
        )
    }


# ==================================================
# NODE STATUS
# ==================================================

def update_node_status(

    node_id,

    status
):

    node = _NODES.get(
        node_id
    )

    if not node:

        return False

    node.status = status

    publish_event(

        "NODE_STATUS_CHANGED",

        node.to_dict(),

        source=(
            "cluster_orchestrator"
        )
    )

    return True


# ==================================================
# STARTUP
# ==================================================

logger.info(
    "Cluster orchestrator inicializado."
)
