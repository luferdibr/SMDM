
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

from core.cluster_orchestrator import (

    schedule_container,

    get_cluster_health
)

from core.governance_center import (
    enforce_quota
)

from core.observability_center import (

    record_metric,

    record_trace,

    record_alert
)


# ==================================================
# LOGGER
# ==================================================

logger = get_logger(
    "autoscaling_engine"
)


# ==================================================
# STORAGE
# ==================================================

_LOCK = threading.RLock()

_POLICIES = {}

_SCALING_EVENTS = []


# ==================================================
# CONFIG
# ==================================================

MAX_EVENTS = 1000

ACTION_SCALE_UP = "SCALE_UP"

ACTION_SCALE_DOWN = "SCALE_DOWN"

ACTION_REBALANCE = "REBALANCE"


# ==================================================
# HELPERS
# ==================================================

def now():

    return time.time()


def now_str():

    return datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )


def generate_policy_id():

    return (

        f"POLICY_"

        f"{int(now() * 1000)}"
    )


# ==================================================
# POLICY
# ==================================================

@dataclass
class ScalingPolicy:

    policy_id: str

    nome: str

    min_instances: int = 1

    max_instances: int = 10

    cpu_threshold: int = 70

    memory_threshold: int = 70

    enabled: bool = True

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

            "policy_id": (
                self.policy_id
            ),

            "nome": self.nome,

            "min_instances": (
                self.min_instances
            ),

            "max_instances": (
                self.max_instances
            ),

            "cpu_threshold": (
                self.cpu_threshold
            ),

            "memory_threshold": (
                self.memory_threshold
            ),

            "enabled": self.enabled,

            "created_at": (
                self.created_at
            ),

            "metadata": (
                self.metadata
            )
        }


# ==================================================
# EVENT
# ==================================================

@dataclass
class ScalingEvent:

    action: str

    policy_id: str

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

            "action": self.action,

            "policy_id": (
                self.policy_id
            ),

            "created_at": (
                self.created_at
            ),

            "metadata": (
                self.metadata
            )
        }


# ==================================================
# POLICY REGISTER
# ==================================================

def register_scaling_policy(

    nome,

    min_instances=1,

    max_instances=10,

    cpu_threshold=70,

    memory_threshold=70,

    metadata=None
):

    policy = ScalingPolicy(

        policy_id=(
            generate_policy_id()
        ),

        nome=nome,

        min_instances=min_instances,

        max_instances=max_instances,

        cpu_threshold=cpu_threshold,

        memory_threshold=(
            memory_threshold
        ),

        metadata=metadata or {}
    )

    with _LOCK:

        _POLICIES[
            policy.policy_id
        ] = policy

    logger.info(

        (
            f"SCALING POLICY "
            f"{policy.policy_id}"
        )
    )

    increment_counter(
        "scaling_policies"
    )

    publish_event(

        "SCALING_POLICY_REGISTERED",

        policy.to_dict(),

        source=(
            "autoscaling_engine"
        )
    )

    return ok(

        mensagem=(
            "Policy registrada."
        ),

        dados=policy.to_dict()
    )


# ==================================================
# SCALE UP
# ==================================================

def scale_up(

    policy_id,

    workload_name,

    image
):

    try:

        policy = _POLICIES.get(
            policy_id
        )

        if not policy:

            return erro(
                "Policy inválida."
            )

        if not enforce_quota(
            "autoscaling"
        ):

            return erro(
                "Quota excedida."
            )

        result = schedule_container(

            nome=workload_name,

            image=image
        )

        event = ScalingEvent(

            action=ACTION_SCALE_UP,

            policy_id=policy_id,

            metadata={

                "workload": (
                    workload_name
                )
            }
        )

        with _LOCK:

            _SCALING_EVENTS.append(
                event
            )

            if (

                len(_SCALING_EVENTS)

                > MAX_EVENTS

            ):

                _SCALING_EVENTS.pop(0)

        logger.warning(

            (
                f"SCALE UP "
                f"{workload_name}"
            )
        )

        increment_counter(
            "scale_up"
        )

        record_metric(
            "autoscaling_scale_up"
        )

        record_trace(

            operation="scale_up",

            source=(
                "autoscaling_engine"
            ),

            status="OK"
        )

        add_event(

            "autoscaling",

            "scale_up",

            event.to_dict()
        )

        publish_event(

            "AUTOSCALING_SCALE_UP",

            event.to_dict(),

            source=(
                "autoscaling_engine"
            )
        )

        return result

    except Exception as ex:

        handle_exception(

            ex,

            contexto=(
                "AUTOSCALING_UP"
            )
        )

        return erro(str(ex))


# ==================================================
# SCALE DOWN
# ==================================================

def scale_down(
    policy_id
):

    policy = _POLICIES.get(
        policy_id
    )

    if not policy:

        return erro(
            "Policy inválida."
        )

    event = ScalingEvent(

        action=(
            ACTION_SCALE_DOWN
        ),

        policy_id=policy_id
    )

    with _LOCK:

        _SCALING_EVENTS.append(
            event
        )

    logger.warning(

        (
            f"SCALE DOWN "
            f"{policy_id}"
        )
    )

    increment_counter(
        "scale_down"
    )

    record_metric(
        "autoscaling_scale_down"
    )

    publish_event(

        "AUTOSCALING_SCALE_DOWN",

        event.to_dict(),

        source=(
            "autoscaling_engine"
        )
    )

    return ok(

        mensagem=(
            "Scale down executado."
        ),

        dados=event.to_dict()
    )


# ==================================================
# REBALANCE
# ==================================================

def rebalance_workloads():

    event = ScalingEvent(

        action=ACTION_REBALANCE,

        policy_id="GLOBAL"
    )

    with _LOCK:

        _SCALING_EVENTS.append(
            event
        )

    logger.info(
        "Cluster rebalance."
    )

    increment_counter(
        "rebalance"
    )

    record_metric(
        "autoscaling_rebalance"
    )

    publish_event(

        "AUTOSCALING_REBALANCE",

        event.to_dict(),

        source=(
            "autoscaling_engine"
        )
    )

    return True


# ==================================================
# ANALYZE
# ==================================================

def analyze_cluster():

    health = (
        get_cluster_health()
    )

    workloads = health.get(
        "workloads",
        0
    )

    nodes = health.get(
        "nodes",
        1
    )

    load_ratio = (

        workloads

        /

        max(nodes, 1)
    )

    if load_ratio > 5:

        record_alert(

            severity="WARNING",

            message=(
                "Cluster sobrecarregado."
            ),

            source=(
                "autoscaling_engine"
            )
        )

    return {

        "health": health,

        "load_ratio": (
            load_ratio
        )
    }


# ==================================================
# STATUS
# ==================================================

def get_autoscaling_status():

    return {

        "policies": len(
            _POLICIES
        ),

        "events": len(
            _SCALING_EVENTS
        )
    }


# ==================================================
# LIST
# ==================================================

def get_scaling_policies():

    return {

        k: v.to_dict()

        for k, v in (
            _POLICIES.items()
        )
    }


def get_scaling_events():

    return [

        x.to_dict()

        for x in (
            _SCALING_EVENTS
        )
    ]


# ==================================================
# DEFAULT POLICY
# ==================================================

def register_default_policy():

    register_scaling_policy(

        nome="Default Policy",

        min_instances=1,

        max_instances=5
    )


# ==================================================
# STARTUP
# ==================================================

register_default_policy()

logger.info(
    "Autoscaling engine inicializado."
)
