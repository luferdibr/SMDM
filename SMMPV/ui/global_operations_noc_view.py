
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
    get_deployments,

    get_environments
)


# ==================================================
# LOGGER
# ==================================================

logger = get_logger(
    "global_operations_noc"
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

                    size=26,

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

        size=22,

        weight=ft.FontWeight.BOLD
    )


# ==================================================
# VIEW
# ==================================================

def global_operations_noc_view(page):

    logger.info(
        "Global operations NOC."
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

    environments = (
        get_environments()
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
                    "Global Operations "
                    "NOC"
                ),

                size=34,

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
    # GLOBAL KPIS
    # ==============================================

    kpi_cards = ft.Row(

        [

            create_card(

                "Global Workers",

                len(

                    workers.get(
                        "workers",
                        []
                    )
                ),

                ft.Colors.BLUE
            ),

            create_card(

                "Global Deployments",

                len(deployments),

                ft.Colors.GREEN
            ),

            create_card(

                "Critical Alerts",

                len(
                    critical_alerts
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
    # GLOBAL HEALTH
    # ==============================================

    health_section = ft.Container(

        content=ft.Column(

            [

                section_title(
                    "Global Health Center"
                ),

                ft.Text(
                    str(runtime)
                ),

                ft.Text(
                    str(workers)
                ),

                ft.Text(
                    str(cloud_sync)
                ),

                ft.Text(
                    str(mesh)
                )
            ]
        ),

        padding=15
    )

    # ==============================================
    # GLOBAL ALERTS
    # ==============================================

    alert_controls = []

    for alert in critical_alerts[-40:]:

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
    # DEPLOYMENTS
    # ==============================================

    deployment_controls = []

    for deploy in deployments[-30:]:

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
                    "Global Deployments"
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
                    "Global Environments"
                ),

                ft.Column(
                    env_controls
                )
            ]
        ),

        padding=15
    )

    # ==============================================
    # GOVERNANCE
    # ==============================================

    governance_controls = []

    for violation in violations[-30:]:

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
                    "Governance Operations"
                ),

                ft.Column(
                    governance_controls
                )
            ]
        ),

        padding=15
    )

    # ==============================================
    # EXECUTIVE KPIS
    # ==============================================

    executive_section = ft.Container(

        content=ft.Column(

            [

                section_title(
                    "Executive NOC KPIs"
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

            health_section,

            alerts_section,

            deployments_section,

            environments_section,

            governance_section,

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
