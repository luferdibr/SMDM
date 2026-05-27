
import threading
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


# ==================================================
# LOGGER
# ==================================================

logger = get_logger(
    "tenant_manager"
)


# ==================================================
# STORAGE
# ==================================================

_LOCK = threading.RLock()

_TENANTS = {}

_THREAD_LOCAL = threading.local()


# ==================================================
# CONFIG
# ==================================================

DEFAULT_TENANT = "default"


# ==================================================
# TENANT
# ==================================================

@dataclass
class Tenant:

    tenant_id: str

    nome: str

    ativo: bool = True

    created_at: str = field(

        default_factory=lambda:

        datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    )

    metadata: dict = field(
        default_factory=dict
    )

    settings: dict = field
