
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

from core.billing_manager import (
    check_quota,
    suspend_subscription
)

from core.tenant_manager import (
    get_current_tenant
)


# ==================================================
# LOGGER
# ==================================================

logger = get_logger(
    "governance_center"
)


# ==================================================
# STORAGE
# ==================================================

_LOCK = threading.RLock()

_POLICIES = {}

_VIOLATIONS = []


# ==================================================
# CONFIG
# ==================================================

MAX_VIOLATIONS = 1000

SEVERITY_LOW = "LOW"

SEVERITY_MEDIUM = "MEDIUM"

SEVERITY_HIGH = "HIGH"

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
# POLICY
# ==================================================

@dataclass
class GovernancePolicy:

    policy_id: str

    nome: str

    descricao: str = ""

    enabled: bool = True

    severity: str = SEVERITY_MEDIUM

    metadata: dict = field(
        default_factory=dict
    )

    created_at: str = field(

        default_factory=lambda:

        now_str()
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

            "descricao": (
                self.descricao
            ),

            "enabled": self.enabled,

            "severity": (
                self.severity
            ),

            "metadata": (
                self.metadata
            ),

            "created_at": (
                self.created_at
            )
        }


# ==================================================
# VIOLATION
# ==================================================

@dataclass
class GovernanceViolation:

    violation_id: str

    tenant_id: str

    policy_id: str

    severity: str

    description: str

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

            "violation_id": (
                self.violation_id
            ),

            "tenant_id": (
                self.tenant_id
            ),

            "policy_id": (
                self.policy_id
            ),

            "severity": (
                self.severity
            ),

            "description": (
                self.description
            ),

            "created_at": (
                self.created_at
            ),

            "metadata": (
                self.metadata
            )
        }


# ==================================================
# HELPERS
# ==================================================

def generate_violation_id():

    return (

        f"GOV_"

        f"{int(now() * 1000)}"
    )


# ==================================================
# POLICY REGISTER
# ==================================================

def register_policy(

    policy_id,

    nome,

    descricao="",

    severity=SEVERITY_MEDIUM,

    metadata=None
):

    policy = GovernancePolicy(

        policy_id=policy_id,

        nome=nome,

        descricao=descricao,

        severity=severity,

        metadata=metadata or {}
    )

    with _LOCK:

        _POLICIES[
            policy_id
        ] = policy

    logger.info(

        (
            f"POLICY REGISTER "
            f"{policy_id}"
        )
    )

    increment_counter(
        "governance_policies"
    )

    publish_event(

        "POLICY_REGISTERED",

        policy.to_dict(),

        source=(
            "governance_center"
        )
    )

    return ok(

        mensagem="Policy registrada.",

        dados=policy.to_dict()
    )


# ==================================================
# GET POLICY
# ==================================================

def get_policy(policy_id):

    return _POLICIES.get(
        policy_id
    )


# ==================================================
# VIOLATION
# ==================================================

def register_violation(

    policy_id,

    description,

    severity=None,

    tenant_id=None,

    metadata=None
):

    policy = get_policy(
        policy_id
    )

    if not policy:

        return erro(
            "Policy inválida."
        )

    violation = GovernanceViolation(

        violation_id=(
            generate_violation_id()
        ),

        tenant_id=(

            tenant_id

            or

            get_current_tenant()
        ),

        policy_id=policy_id,

        severity=(

            severity

            or

            policy.severity
        ),

        description=description,

        metadata=metadata or {}
    )

    with _LOCK:

        _VIOLATIONS.append(
            violation
        )

        if (

            len(_VIOLATIONS)

            > MAX_VIOLATIONS

        ):

            _VIOLATIONS.pop(0)

    logger.warning(

        (
            f"POLICY VIOLATION "
            f"{policy_id}"
        )
    )

    increment_counter(
        "governance_violations"
    )

    add_event(

        "governance",

        "violation",

        violation.to_dict()
    )

    publish_event(

        "POLICY_VIOLATION",

        violation.to_dict(),

        source=(
            "governance_center"
        )
    )

    return violation


# ==================================================
# QUOTA ENFORCEMENT
# ==================================================

def enforce_quota(

    resource,

    requested=1,

    tenant_id=None
):

    tenant_id = (

        tenant_id

        or

        get_current_tenant()
    )

    allowed = check_quota(

        tenant_id=tenant_id,

        resource=resource,

        requested=requested
    )

    if allowed:

        return True

    register_violation(

        policy_id="QUOTA_LIMIT",

        description=(

            f"Quota excedida: "
            f"{resource}"
        ),

        severity=SEVERITY_HIGH,

        tenant_id=tenant_id
    )

    return False


# ==================================================
# SUSPEND
# ==================================================

def suspend_tenant(

    tenant_id,

    reason="Governance violation"
):

    logger.warning(

        (
            f"TENANT SUSPEND "
            f"{tenant_id}"
        )
    )

    suspend_subscription(
        tenant_id
    )

    publish_event(

        "TENANT_SUSPENDED",

        {

            "tenant_id": (
                tenant_id
            ),

            "reason": reason
        },

        source=(
            "governance_center"
        )
    )

    return True


# ==================================================
# VALIDATIONS
# ==================================================

def validate_deployment():

    return True


def validate_runtime():

    return True


def validate_security():

    return True


# ==================================================
# STATUS
# ==================================================

def get_governance_status():

    return {

        "policies": len(
            _POLICIES
        ),

        "violations": len(
            _VIOLATIONS
        )
    }


# ==================================================
# LIST
# ==================================================

def get_policies():

    return {

        k: v.to_dict()

        for k, v in (
            _POLICIES.items()
        )
    }


def get_violations():

    return [

        x.to_dict()

        for x in _VIOLATIONS
    ]


# ==================================================
# DEFAULT POLICIES
# ==================================================

def register_default_policies():

    register_policy(

        policy_id="QUOTA_LIMIT",

        nome="Quota Limit",

        descricao=(
            "Controle de quotas."
        ),

        severity=SEVERITY_HIGH
    )

    register_policy(

        policy_id="SECURITY_CHECK",

        nome="Security Check",

        descricao=(
            "Validação segurança."
        ),

        severity=SEVERITY_CRITICAL
    )

    register_policy(

        policy_id="DEPLOYMENT_RULE",

        nome="Deployment Rule",

        descricao=(
            "Governança deploy."
        ),

        severity=SEVERITY_MEDIUM
    )


# ==================================================
# STARTUP
# ==================================================

register_default_policies()

logger.info(
    "Governance center inicializado."
)