
import flet as ft


from core.logger import get_logger

from core.enterprise_command_center import (

    restart_enterprise_platform,

    get_executive_kpis,

    get_operations_summary
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
    "enterprise_war_room"
)


# ==================================================
# HELPERS
# ==================================================

def create_card(

    title,

    value,

    color=ft.Colors.RED
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

def enterprise_war_room_view(page):

    logger.info(
        "Enterprise war room."
    )

    # ==============================================
    # LOAD DATA
    # ==============================================

    operations = (
        get_operations_summary()
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

    critical_alerts = [

        x

        for x in (
            observability.get(
                "alerts",
                []
            )
        )

        if (

            x.get("severity")

            in

            [

                "ERROR",

                "CRITICAL"
            ]
        )
    ]

    critical_violations = [

        x

        for x in violations

        if (

            x.get("severity")

            in

            [

                "HIGH",

                "CRITICAL"
            ]
        )
    ]

    # ==============================================
    # ACTIONS
    # ==============================================

    def emergency_restart(e):

        restart_enterprise_platform()

        page.snack_bar = ft.SnackBar(

            ft.Text(
                "Emergency restart executado."
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
                    "War Room"
                ),

                size=32,

                color=ft.Colors.RED,

                weight=(
                    ft.FontWeight.BOLD
                )
            ),

            ft.ElevatedButton(

                "Emergency Restart",

                icon=(
                    ft.Icons.WARNING
                ),

                bgcolor=ft.Colors.RED,

                color=ft.Colors.WHITE,

                on_click=(
                    emergency_restart
                )
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

                "Critical Alerts",

                len(critical_alerts)
            ),

            create_card(

                "Critical Violations",

                len(
                    critical_violations
                )
            ),

            create_card(

                "Deployments",

                len(deployments)
            ),

            create_card(

                "Workers",

                len(

                    workers.get(
                        "workers",
                        []
                    )
                )
            )
        ]
    )

    # ==============================================
    # CRITICAL RUNTIME
    # ==============================================

    runtime_section = ft.Container(

        content=ft.Column(

            [

                section_title(
                    "Critical Runtime"
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
    # CRITICAL ALERTS
    # ==============================================

    alert_controls = []

    for alert in critical_alerts[-30:]:

        alert_controls.append(

            ft.Card(

                content=ft.Container(

                    content=ft.Column(

                        [

                            ft.Text(

                                alert.get(
                                    "message",
                                    "-"
                                ),

                                color=(
                                    ft.Colors.RED
                                ),

                                weight=(
                                    ft.FontWeight
                                    .BOLD
                                )
                            ),

                            ft.Text(

                                (
                                    f"Severity: "
                                    f"{alert.get('severity', '-')}"
                                )
                            )
                        ]
                    ),

                    padding=10
                )
            )
        )

    alerts_section = ft.Container(

        content=ft.Column(

            [

                section_title(
                    "Critical Alerts"
                ),

                ft.Column(
                    alert_controls
                )
            ]
        ),

        padding=15
    )

    # ==============================================
    # GOVERNANCE CRITICAL
    # ==============================================

    governance_controls = []

    for violation in (
        critical_violations[-30:]
    ):

        governance_controls.append(

            ft.Card(

                content=ft.Container(

                    content=ft.Column(

                        [

                            ft.Text(

                                violation.get(
                                    (
                                        "description"
                                    ),
                                    "-"
                                ),

                                color=(
                                    ft.Colors.RED
                                ),

                                weight=(
                                    ft.FontWeight
                                    .BOLD
                                )
                            ),

                            ft.Text(

                                (
                                    f"Severity: "
                                    f"{violation.get('severity', '-')}"
                                )
                            )
                        ]
                    ),

                    padding=10
                )
            )
        )

    governance_section = ft.Container(

        content=ft.Column(

            [

                section_title(
                    "Critical Governance"
                ),

                ft.Column(
                    governance_controls
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
                    "Critical Mesh"
                ),

                ft.Text(
                    str(mesh)
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
                    "Critical Deployments"
                ),

                ft.Column(
                    deployment_controls
                )
            ]
        ),

        padding=15
    )

    # ==============================================
    # EXECUTIVE CRITICAL KPIS
    # ==============================================

    executive_section = ft.Container(

        content=ft.Column(

            [

                section_title(
                    "Executive Critical KPIs"
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

            runtime_section,

            alerts_section,

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

        padding=20,

        bgcolor=(
            ft.Colors.BLACK12
        )
    )
