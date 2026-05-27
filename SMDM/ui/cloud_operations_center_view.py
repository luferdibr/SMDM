
import flet as ft


from core.logger import get_logger

from core.enterprise_command_center import (

    get_enterprise_dashboard,

    restart_enterprise_platform,

    get_operations_summary
)

from core.observability_center import (
    export_observability
)

from core.deployment_manager import (

    get_environments,

    get_deployments
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

from core.governance_center import (
    get_violations
)


# ==================================================
# LOGGER
# ==================================================

logger = get_logger(
    "cloud_operations_center_view"
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

def cloud_operations_center_view(page):

    logger.info(
        "Cloud operations center."
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

    environments = (
        get_environments()
    )

    deployments = (
        get_deployments()
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

    violations = (
        get_violations()
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
                    "Cloud Operations "
                    "Center"
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

    kpis = ft.Row(

        [

            create_card(

                "Containers",

                runtime.get(
                    "containers",
                    0
                ),

                ft.Colors.BLUE
            ),

            create_card(

                "Workers",

                len(

                    workers.get(
                        "workers",
                        []
                    )
                ),

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
                )
            ]
        ),

        padding=15
    )

    # ==============================================
    # WORKERS
    # ==============================================

    worker_controls = []

    for worker in workers.get(
        "workers",
        []
    ):

        worker_controls.append(

            ft.ListTile(

                leading=ft.Icon(
                    ft.Icons.SETTINGS
                ),

                title=ft.Text(

                    worker.get(
                        "worker_id",
                        "-"
                    )
                ),

                subtitle=ft.Text(
                    str(worker)
                )
            )
        )

    workers_section = ft.Container(

        content=ft.Column(

            [

                section_title(
                    "Workers"
                ),

                ft.Column(
                    worker_controls
                )
            ]
        ),

        padding=15
    )

    # ==============================================
    # MESH
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

    sync_section = ft.Container(

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
    # ALERTS
    # ==============================================

    alert_controls = []

    for alert in observability.get(
        "alerts",
        []
    )[-20:]:

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

                    alert.get(
                        "severity",
                        "-"
                    )
                )
            )
        )

    alerts_section = ft.Container(

        content=ft.Column(

            [

                section_title(
                    "Alerts"
                ),

                ft.Column(
                    alert_controls
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

            kpis,

            ft.Divider(),

            platform_section,

            runtime_section,

            workers_section,

            mesh_section,

            sync_section,

            deployments_section,

            environments_section,

            alerts_section
        ],

        scroll=ft.ScrollMode.AUTO,

        expand=True
    )

    return ft.Container(

        content=content,

        expand=True,

        padding=20
    )
