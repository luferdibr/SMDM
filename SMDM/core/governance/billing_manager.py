
import threading
from dataclasses import (
    dataclass,
    field
)
from datetime import (
    datetime,
    timedelta
)


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


# ==================================================
# LOGGER
# ==================================================

logger = get_logger(
    "billing_manager"
)


# ==================================================
# STORAGE
# ==================================================

_LOCK = threading.RLock()

_PLANS = {}

_SUBSCRIPTIONS = {}

_USAGE = {}


# ==================================================
# CONFIG
# ==================================================

DEFAULT_PLAN = "FREE"

STATUS_ACTIVE = "ACTIVE"

STATUS_SUSPENDED = "SUSPENDED"

STATUS_EXPIRED = "EXPIRED"

STATUS_GRACE = "GRACE"


# ==================================================
# PLAN
# ==================================================

@dataclass
class BillingPlan:

    plan_id: str

    nome: str

    preco: float = 0.0

    moeda: str = "BRL"

    usuarios: int = 1

    storage_mb: int = 512

    api_requests: int = 1000

    websocket_clients: int = 5

    workers: int = 1

    plugins: int = 5

    ativo: bool = True

    metadata: dict = field(
        default_factory=dict
    )

    # ==============================================
    # DICT
    # ==============================================

    def to_dict(self):

        return {

            "plan_id": self.plan_id,

            "nome": self.nome,

            "preco": self.preco,

            "moeda": self.moeda,

            "usuarios": self.usuarios,

            "storage_mb": (
                self.storage_mb
            ),

            "api_requests": (
                self.api_requests
            ),

            "websocket_clients": (
                self.websocket_clients
            ),

            "workers": self.workers,

            "plugins": self.plugins,

            "ativo": self.ativo,

            "metadata": (
                self.metadata
            )
        }


# ==================================================
# SUBSCRIPTION
# ==================================================

@dataclass
class TenantSubscription:

    tenant_id: str

    plan_id: str

    status: str = STATUS_ACTIVE

    created_at: str = field(

        default_factory=lambda:

        datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    )

    expires_at: str = field(

        default_factory=lambda:

        (

            datetime.now()

            + timedelta(days=30)

        ).strftime(
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

            "tenant_id": (
                self.tenant_id
            ),

            "plan_id": self.plan_id,

            "status": self.status,

            "created_at": (
                self.created_at
            ),

            "expires_at": (
                self.expires_at
            ),

            "metadata": (
                self.metadata
            )
        }


# ==================================================
# PLAN REGISTER
# ==================================================

def register_plan(

    plan_id,

    nome,

    preco=0.0,

    moeda="BRL",

    usuarios=1,

    storage_mb=512,

    api_requests=1000,

    websocket_clients=5,

    workers=1,

    plugins=5,

    metadata=None
):

    plan = BillingPlan(

        plan_id=plan_id,

        nome=nome,

        preco=preco,

        moeda=moeda,

        usuarios=usuarios,

        storage_mb=storage_mb,

        api_requests=api_requests,

        websocket_clients=(
            websocket_clients
        ),

        workers=workers,

        plugins=plugins,

        metadata=metadata or {}
    )

    with _LOCK:

        _PLANS[plan_id] = plan

    logger.info(
        f"PLAN REGISTER {plan_id}"
    )

    increment_counter(
        "billing_plans"
    )

    publish_event(

        "PLAN_REGISTERED",

        plan.to_dict(),

        source="billing_manager"
    )

    return ok(

        mensagem="Plano registrado.",

        dados=plan.to_dict()
    )


# ==================================================
# ASSIGN
# ==================================================

def assign_plan(

    tenant_id,

    plan_id,

    metadata=None
):

    plan = _PLANS.get(plan_id)

    if not plan:

        return erro(
            "Plano inválido."
        )

    subscription = TenantSubscription(

        tenant_id=tenant_id,

        plan_id=plan_id,

        metadata=metadata or {}
    )

    with _LOCK:

        _SUBSCRIPTIONS[
            tenant_id
        ] = subscription

    logger.info(

        (
            f"PLAN ASSIGN "
            f"{tenant_id} "
            f"{plan_id}"
        )
    )

    increment_counter(
        "billing_assignments"
    )

    publish_event(

        "PLAN_ASSIGNED",

        subscription.to_dict(),

        source="billing_manager"
    )

    return ok(

        mensagem="Plano atribuído.",

        dados=subscription.to_dict()
    )


# ==================================================
# GET
# ==================================================

def get_plan(plan_id):

    return _PLANS.get(plan_id)


def get_subscription(
    tenant_id
):

    return _SUBSCRIPTIONS.get(
        tenant_id
    )


# ==================================================
# USAGE
# ==================================================

def register_usage(

    tenant_id,

    resource,

    amount=1
):

    with _LOCK:

        if tenant_id not in _USAGE:

            _USAGE[tenant_id] = {}

        current = _USAGE[
            tenant_id
        ].get(resource, 0)

        _USAGE[
            tenant_id
        ][resource] = (

            current + amount
        )

    increment_counter(
        "billing_usage"
    )

    add_event(

        "billing",

        "usage",

        {

            "tenant": tenant_id,

            "resource": resource,

            "amount": amount
        }
    )

    return True


# ==================================================
# QUOTA
# ==================================================

def check_quota(

    tenant_id,

    resource,

    requested=1
):

    subscription = get_subscription(
        tenant_id
    )

    if not subscription:

        return False

    plan = get_plan(
        subscription.plan_id
    )

    if not plan:

        return False

    usage = _USAGE.get(
        tenant_id,
        {}
    )

    current = usage.get(
        resource,
        0
    )

    limit = getattr(
        plan,
        resource,
        None
    )

    if limit is None:

        return True

    return (

        current + requested

        <=

        limit
    )


# ==================================================
# STATUS
# ==================================================

def suspend_subscription(
    tenant_id
):

    subscription = get_subscription(
        tenant_id
    )

    if not subscription:

        return False

    subscription.status = (
        STATUS_SUSPENDED
    )

    publish_event(

        "SUBSCRIPTION_SUSPENDED",

        subscription.to_dict(),

        source="billing_manager"
    )

    return True


def activate_subscription(
    tenant_id
):

    subscription = get_subscription(
        tenant_id
    )

    if not subscription:

        return False

    subscription.status = (
        STATUS_ACTIVE
    )

    publish_event(

        "SUBSCRIPTION_ACTIVATED",

        subscription.to_dict(),

        source="billing_manager"
    )

    return True


# ==================================================
# LIST
# ==================================================

def get_all_plans():

    return {

        k: v.to_dict()

        for k, v in (
            _PLANS.items()
        )
    }


def get_all_subscriptions():

    return {

        k: v.to_dict()

        for k, v in (
            _SUBSCRIPTIONS.items()
        )
    }


def get_usage():

    return dict(_USAGE)


# ==================================================
# STATUS
# ==================================================

def get_billing_status():

    return {

        "plans": len(_PLANS),

        "subscriptions": len(
            _SUBSCRIPTIONS
        ),

        "usage_tracking": len(
            _USAGE
        )
    }


# ==================================================
# DEFAULT PLANS
# ==================================================

def register_default_plans():

    register_plan(

        plan_id="FREE",

        nome="Free",

        preco=0,

        usuarios=1,

        storage_mb=512,

        api_requests=1000,

        websocket_clients=5,

        workers=1,

        plugins=5
    )

    register_plan(

        plan_id="PRO",

        nome="Professional",

        preco=99.90,

        usuarios=10,

        storage_mb=10240,

        api_requests=50000,

        websocket_clients=50,

        workers=10,

        plugins=50
    )

    register_plan(

        plan_id="ENTERPRISE",

        nome="Enterprise",

        preco=999.90,

        usuarios=9999,

        storage_mb=999999,

        api_requests=999999,

        websocket_clients=9999,

        workers=999,

        plugins=999
    )


# ==================================================
# STARTUP
# ==================================================

register_default_plans()

logger.info(
    "Billing manager inicializado."
)
