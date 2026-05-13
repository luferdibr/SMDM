
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
    "service_registry"
)


# ==================================================
# STORAGE
# ==================================================

_LOCK = threading.RLock()

_SERVICES = {}


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
# SERVICE
# ==================================================

@dataclass
class RegisteredService:

    service_name: str

    instance: object = None

    singleton: bool = True

    tenant_aware: bool = False

    enabled: bool = True

    created_at: str = field(

        default_factory=lambda:

        now_str()
    )

    last_access: str = None

    access_count: int = 0

    metadata: dict = field(
        default_factory=dict
    )

    health: str = "UP"

    lazy_factory: callable = None

    # ==============================================
    # DICT
    # ==============================================

    def to_dict(self):

        return {

            "service_name": (
                self.service_name
            ),

            "singleton": (
                self.singleton
            ),

            "tenant_aware": (
                self.tenant_aware
            ),

            "enabled": self.enabled,

            "created_at": (
                self.created_at
            ),

            "last_access": (
                self.last_access
            ),

            "access_count": (
                self.access_count
            ),

            "metadata": (
                self.metadata
            ),

            "health": self.health,

            "lazy_loaded": (
                self.lazy_factory
                is not None
            )
        }


# ==================================================
# REGISTER
# ==================================================

def register_service(

    service_name,

    instance=None,

    singleton=True,

    tenant_aware=False,

    metadata=None,

    lazy_factory=None
):

    with _LOCK:

        service = RegisteredService(

            service_name=service_name,

            instance=instance,

            singleton=singleton,

            tenant_aware=tenant_aware,

            metadata=metadata or {},

            lazy_factory=lazy_factory
        )

        _SERVICES[
            service_name
        ] = service

    logger.info(

        (
            f"SERVICE REGISTER "
            f"{service_name}"
        )
    )

    increment_counter(
        "services_registered"
    )

    publish_event(

        "SERVICE_REGISTERED",

        {

            "service": (
                service_name
            )
        },

        source="service_registry"
    )

    return ok(

        mensagem="Serviço registrado.",

        dados=service.to_dict()
    )


# ==================================================
# GET
# ==================================================

def get_service(

    service_name,

    default=None
):

    with _LOCK:

        service = _SERVICES.get(
            service_name
        )

    if not service:

        return default

    if not service.enabled:

        return default

    try:

        # ==========================================
        # LAZY
        # ==========================================

        if (

            service.instance is None

            and

            service.lazy_factory
        ):

            logger.info(

                (
                    f"LAZY LOAD "
                    f"{service_name}"
                )
            )

            service.instance = (
                service.lazy_factory()
            )

        service.last_access = (
            now_str()
        )

        service.access_count += 1

        increment_counter(
            "service_access"
        )

        return service.instance

    except Exception as ex:

        handle_exception(

            ex,

            contexto=(
                "SERVICE_LOOKUP"
            )
        )

        return default


# ==================================================
# EXISTS
# ==================================================

def service_exists(service_name):

    return service_name in _SERVICES


# ==================================================
# REMOVE
# ==================================================

def unregister_service(
    service_name
):

    with _LOCK:

        if service_name in _SERVICES:

            del _SERVICES[
                service_name
            ]

            logger.warning(

                (
                    f"SERVICE REMOVE "
                    f"{service_name}"
                )
            )

            increment_counter(
                "services_removed"
            )

            publish_event(

                "SERVICE_REMOVED",

                {

                    "service": (
                        service_name
                    )
                },

                source=(
                    "service_registry"
                )
            )

            return True

    return False


# ==================================================
# ENABLE
# ==================================================

def enable_service(service_name):

    service = _SERVICES.get(
        service_name
    )

    if not service:

        return False

    service.enabled = True

    logger.info(

        (
            f"SERVICE ENABLE "
            f"{service_name}"
        )
    )

    return True


def disable_service(service_name):

    service = _SERVICES.get(
        service_name
    )

    if not service:

        return False

    service.enabled = False

    logger.warning(

        (
            f"SERVICE DISABLE "
            f"{service_name}"
        )
    )

    return True


# ==================================================
# HEALTH
# ==================================================

def update_service_health(

    service_name,

    health
):

    service = _SERVICES.get(
        service_name
    )

    if not service:

        return False

    service.health = str(
        health
    )

    return True


# ==================================================
# TENANT
# ==================================================

def get_tenant_service_name(
    service_name
):

    tenant = get_current_tenant()

    return (

        f"{tenant}::"

        f"{service_name}"
    )


# ==================================================
# TENANT REGISTER
# ==================================================

def register_tenant_service(

    service_name,

    instance=None,

    metadata=None
):

    return register_service(

        service_name=(
            get_tenant_service_name(
                service_name
            )
        ),

        instance=instance,

        tenant_aware=True,

        metadata=metadata
    )


# ==================================================
# TENANT GET
# ==================================================

def get_tenant_service(
    service_name
):

    return get_service(

        get_tenant_service_name(
            service_name
        )
    )


# ==================================================
# STATUS
# ==================================================

def get_service_registry_status():

    with _LOCK:

        return {

            "services": len(
                _SERVICES
            ),

            "registered": [

                x.to_dict()

                for x in (
                    _SERVICES.values()
                )
            ]
        }


# ==================================================
# DEBUG
# ==================================================

def dump_service_registry():

    with _LOCK:

        return {

            k: v.to_dict()

            for k, v in (
                _SERVICES.items()
            )
        }


# ==================================================
# HEARTBEAT
# ==================================================

def service_heartbeat(
    service_name
):

    service = _SERVICES.get(
        service_name
    )

    if not service:

        return False

    service.last_access = (
        now_str()
    )

    add_event(

        "service_registry",

        "heartbeat",

        {

            "service": (
                service_name
            )
        }
    )

    return True


# ==================================================
# CLEAR
# ==================================================

def clear_services():

    with _LOCK:

        total = len(
            _SERVICES
        )

        _SERVICES.clear()

    logger.warning(
        "ALL SERVICES CLEARED"
    )

    return total


# ==================================================
# STARTUP
# ==================================================

logger.info(
    "Service registry inicializado."
)
