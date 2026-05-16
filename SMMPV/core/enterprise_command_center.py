
from datetime import datetime


from core.logger import get_logger

from core.responses import (
    ok,
    erro
)

from core.telemetry import (
    dump_telemetry
)

from core.event_bus import (
    publish_event
)

from core.middleware import (
    handle_exception
)

from core.orchestrator import (

    get_platform_status,

    restart_platform
)

from core.deployment_manager import (

    get_deployment_status,

    get_environments
)

from core.governance_center import (

    get_governance_status,

    get_violations,

    suspend_tenant
)

from core.observability_center import (

    get_runtime_dashboard,

    get_observability_status
)

from core.billing_manager import (

    get_all_subscriptions,

    get_billing_status
)

from core.service_mesh import (
    get_mesh_status
)

from core.container_runtime import (
    get_runtime_status
)

from core.distributed_workers import (
    get_worker_status
)

from core.cloud_sync import (
    get_cloud_sync_status
)

from core.websocket_server import (
    get_websocket_status
)

from core.api_server import (
    get_api_routes
)


# ==================================================
# LOGGER
# ==================================================

logger = get_logger(
    "enterprise_command_center"
)


# ==================================================
# HELPERS
# ==================================================

def now_str():

    return datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )


# ==================================================
# DASHBOARD
# ==================================================

def get_enterprise_dashboard():

    try:

        dashboard = {

            "timestamp": now_str(),

            # ======================================
            # PLATFORM
            # ======================================

            "platform": (
                get_platform_status()
            ),

            # ======================================
            # DEPLOYMENT
            # ======================================

            "deployment": {

                "status": (
                    get_deployment_status()
                ),

                "environments": (
                    get_environments()
                )
            },

            # ======================================
            # GOVERNANCE
            # ======================================

            "governance": {

                "status": (
                    get_governance_status()
                ),

                "violations": len(
                    get_violations()
                )
            },

            # ======================================
            # OBSERVABILITY
            # ======================================

            "observability": {

                "status": (
                    get_observability_status()
                ),

                "dashboard": (
                    get_runtime_dashboard()
                )
            },

            # ======================================
            # BILLING
            # ======================================

            "billing": {

                "status": (
                    get_billing_status()
                ),

                "subscriptions": len(
                    get_all_subscriptions()
                )
            },

            # ======================================
            # SERVICE MESH
            # ======================================

            "mesh": (
                get_mesh_status()
            ),

            # ======================================
            # RUNTIME
            # ======================================

            "runtime": (
                get_runtime_status()
            ),

            # ======================================
            # WORKERS
            # ======================================

            "workers": (
                get_worker_status()
            ),

            # ======================================
            # CLOUD SYNC
            # ======================================

            "cloud_sync": (
                get_cloud_sync_status()
            ),

            # ======================================
            # WEBSOCKET
            # ======================================

            "websocket": (
                get_websocket_status()
            ),

            # ======================================
            # API
            # ======================================

            "api": {

                "routes": len(
                    get_api_routes()
                )
            },

            # ======================================
            # TELEMETRY
            # ======================================

            "telemetry": (
                dump_telemetry()
            )
        }

        publish_event(

            "COMMAND_CENTER_DASHBOARD",

            {

                "generated": True
            },

            source=(
                "enterprise_command_center"
            )
        )

        return ok(

            mensagem=(
                "Dashboard enterprise."
            ),

            dados=dashboard
        )

    except Exception as ex:

        handle_exception(

            ex,

            contexto=(
                "ENTERPRISE_DASHBOARD"
            )
        )

        return erro(str(ex))


# ==================================================
# ACTIONS
# ==================================================

def restart_enterprise_platform():

    logger.warning(
        "ENTERPRISE RESTART"
    )

    publish_event(

        "ENTERPRISE_RESTART",

        source=(
            "enterprise_command_center"
        )
    )

    return restart_platform()


# ==================================================
# TENANT CONTROL
# ==================================================

def suspend_enterprise_tenant(

    tenant_id,

    reason="Administrative action"
):

    logger.warning(

        (
            f"ENTERPRISE SUSPEND "
            f"{tenant_id}"
        )
    )

    publish_event(

        "ENTERPRISE_TENANT_SUSPEND",

        {

            "tenant_id": (
                tenant_id
            ),

            "reason": reason
        },

        source=(
            "enterprise_command_center"
        )
    )

    return suspend_tenant(

        tenant_id,

        reason=reason
    )


# ==================================================
# EXECUTIVE KPIS
# ==================================================

def get_executive_kpis():

    telemetry = dump_telemetry()

    governance = (
        get_governance_status()
    )

    billing = get_billing_status()

    deployment = (
        get_deployment_status()
    )

    return {

        "generated_at": (
            now_str()
        ),

        "tenants": (
            billing.get(
                "subscriptions",
                0
            )
        ),

        "deployments": (
            deployment.get(
                "deployments",
                0
            )
        ),

        "governance_violations": (
            governance.get(
                "violations",
                0
            )
        ),

        "telemetry_events": len(
            telemetry.get(
                "events",
                []
            )
        )
    }


# ==================================================
# OPERATIONS
# ==================================================

def get_operations_summary():

    return {

        "platform": (
            get_platform_status()
        ),

        "workers": (
            get_worker_status()
        ),

        "runtime": (
            get_runtime_status()
        ),

        "mesh": (
            get_mesh_status()
        ),

        "cloud_sync": (
            get_cloud_sync_status()
        )
    }


# ==================================================
# STATUS
# ==================================================

def get_command_center_status():

    return {

        "status": "ONLINE",

        "timestamp": now_str(),

        "services": [

            "orchestrator",

            "deployment",

            "governance",

            "observability",

            "billing",

            "mesh",

            "runtime"
        ]
    }


# ==================================================
# STARTUP
# ==================================================

logger.info(
    "Enterprise command center inicializado."
)
