
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

    add_event,

    dump_telemetry
)

from core.event_bus import (
    publish_event
)

from core.middleware import (
    handle_exception
)

from core.governance_center import (
    get_violations
)

from core.service_mesh import (
    get_mesh_status
)


# ==================================================
# LOGGER
# ==================================================

logger = get_logger(
    "observability_center"
)


# ==================================================
# STORAGE
# ==================================================

_LOCK = threading.RLock()

_METRICS = {}

_TRACES = []

_ALERTS = []


# ==================================================
# CONFIG
# ==================================================

MAX_TRACES = 5000

MAX_ALERTS = 1000

SEVERITY_INFO = "INFO"

SEVERITY_WARNING = "WARNING"

SEVERITY_ERROR = "ERROR"

SEVERITY_CRITICAL = "CRITICAL"


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
# TRACE
# ==================================================

@dataclass
class TraceRecord:

    trace_id: str

    operation: str

    source: str

    duration: float = 0

    status: str = "OK"

    tenant_id: str = None

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

            "trace_id": self.trace_id,

            "operation": (
                self.operation
            ),

            "source": self.source,

            "duration": (
                self.duration
            ),

            "status": self.status,

            "tenant_id": (
                self.tenant_id
            ),

            "created_at": (
                self.created_at
            ),

            "metadata": (
                self.metadata
            )
        }


# ==================================================
# ALERT
# ==================================================

@dataclass
class AlertRecord:

    alert_id: str

    severity: str

    message: str

    source: str

    created_at: str = field(

        default_factory=lambda:

        now_str()
    )

    metadata: dict = field(
        default_factory=dict
    )

    acknowledged: bool = False

    # ==============================================
    # DICT
    # ==============================================

    def to_dict(self):

        return {

            "alert_id": self.alert_id,

            "severity": (
                self.severity
            ),

            "message": self.message,

            "source": self.source,

            "created_at": (
                self.created_at
            ),

            "metadata": (
                self.metadata
            ),

            "acknowledged": (
                self.acknowledged
            )
        }


# ==================================================
# HELPERS
# ==================================================

def generate_trace_id():

    return (

        f"TRACE_"

        f"{int(now() * 1000)}"
    )


def generate_alert_id():

    return (

        f"ALERT_"

        f"{int(now() * 1000)}"
    )


# ==================================================
# METRICS
# ==================================================

def record_metric(

    metric,

    value=1
):

    with _LOCK:

        current = _METRICS.get(
            metric,
            0
        )

        _METRICS[metric] = (
            current + value
        )

    increment_counter(
        "observability_metrics"
    )

    return True


# ==================================================
# TRACE
# ==================================================

def record_trace(

    operation,

    source,

    duration=0,

    status="OK",

    tenant_id=None,

    metadata=None
):

    trace = TraceRecord(

        trace_id=(
            generate_trace_id()
        ),

        operation=operation,

        source=source,

        duration=duration,

        status=status,

        tenant_id=tenant_id,

        metadata=metadata or {}
    )

    with _LOCK:

        _TRACES.append(trace)

        if (

            len(_TRACES)

            > MAX_TRACES

        ):

            _TRACES.pop(0)

    logger.info(

        (
            f"TRACE "
            f"{operation}"
        )
    )

    increment_counter(
        "observability_traces"
    )

    publish_event(

        "TRACE_RECORDED",

        trace.to_dict(),

        source=(
            "observability_center"
        )
    )

    return trace


# ==================================================
# ALERT
# ==================================================

def record_alert(

    severity,

    message,

    source,

    metadata=None
):

    alert = AlertRecord(

        alert_id=(
            generate_alert_id()
        ),

        severity=severity,

        message=message,

        source=source,

        metadata=metadata or {}
    )

    with _LOCK:

        _ALERTS.append(alert)

        if (

            len(_ALERTS)

            > MAX_ALERTS

        ):

            _ALERTS.pop(0)

    logger.warning(

        (
            f"ALERT "
            f"{severity} "
            f"{message}"
        )
    )

    increment_counter(
        "observability_alerts"
    )

    add_event(

        "observability",

        "alert",

        alert.to_dict()
    )

    publish_event(

        "ALERT_RECORDED",

        alert.to_dict(),

        source=(
            "observability_center"
        )
    )

    return alert


# ==================================================
# ACK
# ==================================================

def acknowledge_alert(
    alert_id
):

    with _LOCK:

        for alert in _ALERTS:

            if (

                alert.alert_id

                ==

                alert_id
            ):

                alert.acknowledged = (
                    True
                )

                return True

    return False


# ==================================================
# STATUS
# ==================================================

def get_observability_status():

    return {

        "metrics": len(
            _METRICS
        ),

        "traces": len(
            _TRACES
        ),

        "alerts": len(
            _ALERTS
        )
    }


# ==================================================
# EXPORT
# ==================================================

def export_observability():

    with _LOCK:

        return {

            "metrics": dict(
                _METRICS
            ),

            "traces": [

                x.to_dict()

                for x in _TRACES
            ],

            "alerts": [

                x.to_dict()

                for x in _ALERTS
            ]
        }


# ==================================================
# DASHBOARD
# ==================================================

def get_runtime_dashboard():

    return {

        "observability": (
            get_observability_status()
        ),

        "telemetry": (
            dump_telemetry()
        ),

        "governance": {

            "violations": len(
                get_violations()
            )
        },

        "mesh": (
            get_mesh_status()
        )
    }


# ==================================================
# HEALTH ALERTS
# ==================================================

def generate_health_alerts():

    violations = get_violations()

    if len(violations) > 10:

        record_alert(

            severity=(
                SEVERITY_WARNING
            ),

            message=(
                "Muitas violações."
            ),

            source="governance"
        )


# ==================================================
# STARTUP
# ==================================================

logger.info(
    "Observability center inicializado."
)
