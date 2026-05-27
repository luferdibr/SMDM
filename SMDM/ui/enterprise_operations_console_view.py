
import flet as ft


from core.logger import get_logger

from core.enterprise_command_center import (

    get_enterprise_dashboard,

    get_executive_kpis,

    restart_enterprise_platform,

    get_operations_summary
)

from core.observability_center import (
    export_observability
)

from core.governance_center import (
    get_violations
)

from core.billing_manager import (
    get_all_subscriptions
)

from core.deployment_manager import (

    get_deployments,

    get_environments
)

from core.container_runtime import (
    get_runtime_status
)

from core.distributed_workers import (
    get_worker_status
)

from core.service_mesh import (
    get_mesh_status
)

from core.cloud_sync import (
    get_cloud_sync_status
)


# ==================================================
# LOGGER
# ==================================================

logger = get_logger(
    "enterprise_operations_console"
)


# ==================================================
# HELPERS
# ==================================================

def create_card(

    title,

    value,

    color=ft.Colors.BLUE
):

    return ft.Container(

        content=ft.Column(

            [

                ft.Text(

                    title,

                    size=14,

                    weight=(
                        ft.FontWeight.BOLD
                    )
                ),

                ft.Text(

                    str(value),

                    size=24,

                    weight=(
                        ft.FontWeight.BOLD
                    )
                )
            ]
        ),

        bgcolor=color,

        padding=15,

        border_radius=10,

        expand=True
    )


def section_title(title):

    return ft.Text(

        title,

        size=20,

        weight=ft.FontWeight.BOLD
    )


# ==================================================
# VIEW
# ==================================================

def enterprise_operations_console_view(page):

    logger.info(
        "Enterprise operations console."
    )

    # ==============================================
    # LOAD DATA
    # ==============================================

    dashboard = (
        get_enterprise_dashboard()
    )

    operations = (
        get_operations_summary()
    )

    observability = (
        export_observability()
    )

    violations = (
        get_violations()
    )

    subscriptions = (
        get_all_subscriptions()
    )

    deployments = (
        get_deployments()
    )

    environments = (
        get_environments()
    )

    runtime = (
        get_runtime_status()
    )

    workers = (
        get_worker_status()
    )

    mesh = (
        get_mesh_status()
    )

    cloud_sync = (
        get_cloud_sync_status()
    )

    kpis = (
        get_executive_kpis()
    )

    dashboard_data = dashboard.get(
        "dados",
        {}
    )

    # ==============================================
    # ACTIONS
    # ==============================================

    def on_restart(e):

        restart_enterprise_platform()

        page.snack_bar = ft.SnackBar(

            ft.Text(
                "Plataforma reiniciada."
            )
        )

        page.snack_bar.open = True

        page.update()

    # ==============================================
    # HEADER
    # ==============================================

    header = ft.Row(

        [

            ft.Text(

                (
                    "Enterprise "
                    "Operations Console"
                ),

                size=30,

                weight=(
                    ft.FontWeight.BOLD
                )
            ),

            ft.ElevatedButton(

                "Restart Platform",

                icon=(
                    ft.Icons.RESTART_ALT
                ),

                on_click=on_restart
            )
        ],

        alignment=(
            ft.MainAxisAlignment
            .SPACE_BETWEEN
        )
    )

    # ==============================================
    # KPI CARDS
    # ==============================================

    kpi_cards = ft.Row(

        [

            create_card(

                "Tenants",

                kpis.get(
                    "tenants",
                    0
                ),

                ft.Colors.BLUE
            ),

            create_card(

                "Deployments",

                kpis.get(
                    "deployments",
                    0
                ),

                ft.Colors.GREEN
            ),

            create_card(

                "Violations",

                len(violations),

                ft.Colors.RED
            ),

            create_card(

                "Alerts",

                len(

                    observability.get(
                        "alerts",
                        []
                    )
                ),

                ft.Colors.ORANGE
            )
        ]
    )

    # ==============================================
    # PLATFORM
    # ==============================================

    platform_section = ft.Container(

        content=ft.Column(

            [

                section_title(
                    "Platform"
                ),

                ft.Text(
                    str(operations)
                )
            ]
        ),

        padding=15
    )

    # ==============================================
    # RUNTIME
    # ==============================================

    runtime_section = ft.Container(

        content=ft.Column(

            [

                section_title(
                    "Runtime"
                ),

                ft.Text(
                    str(runtime)
                ),

                ft.Text(
                    str(workers)
                )
            ]
        ),

        padding=15
    )

    # ==============================================
    # GOVERNANCE
    # ==============================================

    governance_controls = []

    for violation in violations[-20:]:

        governance_controls.append(

            ft.ListTile(

                leading=ft.Icon(
                    ft.Icons.WARNING
                ),

                title=ft.Text(

                    violation.get(
                        "description",
                        "-"
                    )
                ),

                subtitle=ft.Text(

                    violation.get(
                        "severity",
                        "-"
                    )
                )
            )
        )

    governance_section = ft.Container(

        content=ft.Column(

            [

                section_title(
                    "Governance"
                ),

                ft.Text(

                    (
                        f"Subscriptions: "
                        f"{len(subscriptions)}"
                    )
                ),

                ft.Column(
                    governance_controls
                )
            ]
        ),

        padding=15
    )

    # ==============================================
    # DEPLOYMENTS
    # ==============================================

    deployment_controls = []

    for deploy in deployments[-20:]:

        deployment_controls.append(

            ft.ListTile(

                leading=ft.Icon(
                    ft.Icons.CLOUD
                ),

                title=ft.Text(

                    deploy.get(
                        "deployment_id",
                        "-"
                    )
                ),

                subtitle=ft.Text(
                    str(deploy)
                )
            )
        )

    deployments_section = ft.Container(

        content=ft.Column(

            [

                section_title(
                    "Deployments"
                ),

                ft.Column(
                    deployment_controls
                )
            ]
        ),

        padding=15
    )

    # ==============================================
    # ENVIRONMENTS
    # ==============================================

    env_controls = []

    for env_id, env in (
        environments.items()
    ):

        env_controls.append(

            ft.ListTile(

                leading=ft.Icon(
                    ft.Icons.COMPUTER
                ),

                title=ft.Text(
                    env_id
                ),

                subtitle=ft.Text(
                    str(env)
                )
            )
        )

    environments_section = ft.Container(

        content=ft.Column(

            [

                section_title(
                    "Environments"
                ),

                ft.Column(
                    env_controls
                )
            ]
        ),

        padding=15
    )

    # ==============================================
    # OBSERVABILITY
    # ==============================================

    observability_section = ft.Container(

        content=ft.Column(

            [

                section_title(
                    "Observability"
                ),

                ft.Text(

                    (
                        f"Metrics: "
                        f"{len(observability.get('metrics', {}))}"
                    )
                ),

                ft.Text(

                    (
                        f"Traces: "
                        f"{len(observability.get('traces', []))}"
                    )
                ),

                ft.Text(

                    (
                        f"Alerts: "
                        f"{len(observability.get('alerts', []))}"
                    )
                )
            ]
        ),

        padding=15
    )

    # ==============================================
    # SERVICE MESH
    # ==============================================

    mesh_section = ft.Container(

        content=ft.Column(

            [

                section_title(
                    "Service Mesh"
                ),

                ft.Text(
                    str(mesh)
                )
            ]
        ),

        padding=15
    )

    # ==============================================
    # CLOUD SYNC
    # ==============================================

    cloud_sync_section = ft.Container(

        content=ft.Column(

            [

                section_title(
                    "Cloud Sync"
                ),

                ft.Text(
                    str(cloud_sync)
                )
            ]
        ),

        padding=15
    )

    # ==============================================
    # MAIN
    # ==============================================

    content = ft.Column(

        [

            header,

            ft.Divider(),

            kpi_cards,

            ft.Divider(),

            platform_section,

            runtime_section,

            governance_section,

            deployments_section,

            environments_section,

            observability_section,

            mesh_section,

            cloud_sync_section
        ],

        scroll=ft.ScrollMode.AUTO,

        expand=True
    )

    return ft.Container(

        content=content,

        expand=True,

        padding=20
    )
