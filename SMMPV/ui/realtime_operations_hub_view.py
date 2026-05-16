
import flet as ft


from core.logger import get_logger

from core.enterprise_command_center import (

    get_enterprise_dashboard,

    restart_enterprise_platform,

    get_executive_kpis
)

from core.observability_center import (
    export_observability
)

from core.governance_center import (
    get_violations
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

from core.service_mesh import (
    get_mesh_status
)

from core.deployment_manager import (
    get_deployments
)


# ==================================================
# LOGGER
# ==================================================

logger = get_logger(
    "realtime_operations_hub"
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

def realtime_operations_hub_view(page):

    logger.info(
        "Realtime operations hub."
    )

    # ==============================================
    # LOAD DATA
    # ==============================================

    dashboard = (
        get_enterprise_dashboard()
    )

    observability = (
        export_observability()
    )

    violations = (
        get_violations()
    )

    runtime = (
        get_runtime_status()
    )

    workers = (
        get_worker_status()
    )

    cloud_sync = (
        get_cloud_sync_status()
    )

    mesh = (
        get_mesh_status()
    )

    deployments = (
        get_deployments()
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
                "Runtime reiniciado."
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
                    "Realtime "
                    "Operations Hub"
                ),

                size=30,

                weight=(
                    ft.FontWeight.BOLD
                )
            ),

            ft.ElevatedButton(

                "Restart Runtime",

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

                "Workers",

                len(

                    workers.get(
                        "workers",
                        []
                    )
                ),

                ft.Colors.BLUE
            ),

            create_card(

                "Deployments",

                len(deployments),

                ft.Colors.GREEN
            ),

            create_card(

                "Alerts",

                len(

                    observability.get(
                        "alerts",
                        []
                    )
                ),

                ft.Colors.RED
            ),

            create_card(

                "Violations",

                len(violations),

                ft.Colors.ORANGE
            )
        ]
    )

    # ==============================================
    # LIVE PLATFORM
    # ==============================================

    platform_section = ft.Container(

        content=ft.Column(

            [

                section_title(
                    "Live Platform"
                ),

                ft.Text(
                    str(runtime)
                ),

                ft.Text(
                    str(workers)
                ),

                ft.Text(
                    str(cloud_sync)
                )
            ]
        ),

        padding=15
    )

    # ==============================================
    # LIVE OBSERVABILITY
    # ==============================================

    alert_controls = []

    for alert in observability.get(
        "alerts",
        []
    )[-25:]:

        alert_controls.append(

            ft.ListTile(

                leading=ft.Icon(
                    ft.Icons.WARNING
                ),

                title=ft.Text(

                    alert.get(
                        "message",
                        "-"
                    )
                ),

                subtitle=ft.Text(

                    (
                        f"{alert.get('severity', '-')}"
                    )
                )
            )
        )

    observability_section = ft.Container(

        content=ft.Column(

            [

                section_title(
                    "Live Observability"
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

                ft.Column(
                    alert_controls
                )
            ]
        ),

        padding=15
    )

    # ==============================================
    # LIVE GOVERNANCE
    # ==============================================

    governance_controls = []

    for violation in violations[-25:]:

        governance_controls.append(

            ft.ListTile(

                leading=ft.Icon(
                    ft.Icons.GAVEL
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
                    "Live Governance"
                ),

                ft.Column(
                    governance_controls
                )
            ]
        ),

        padding=15
    )

    # ==============================================
    # LIVE MESH
    # ==============================================

    mesh_section = ft.Container(

        content=ft.Column(

            [

                section_title(
                    "Live Service Mesh"
                ),

                ft.Text(
                    str(mesh)
                )
            ]
        ),

        padding=15
    )

    # ==============================================
    # LIVE DEPLOYMENTS
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
                    "Live Deployments"
                ),

                ft.Column(
                    deployment_controls
                )
            ]
        ),

        padding=15
    )

    # ==============================================
    # EXECUTIVE LIVE KPIS
    # ==============================================

    executive_section = ft.Container(

        content=ft.Column(

            [

                section_title(
                    "Executive Live KPIs"
                ),

                ft.Text(
                    str(kpis)
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

            observability_section,

            governance_section,

            mesh_section,

            deployments_section,

            executive_section
        ],

        scroll=ft.ScrollMode.AUTO,

        expand=True
    )

    return ft.Container(

        content=content,

        expand=True,

        padding=20
    )
