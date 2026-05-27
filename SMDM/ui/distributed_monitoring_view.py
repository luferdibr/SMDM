
import flet as ft


from core.logger import get_logger

from core.container_runtime import (
    get_containers,
    get_runtime_status
)

from core.distributed_workers import (
    get_worker_status
)

from core.service_mesh import (
    get_mesh_status
)

from core.observability_center import (
    export_observability
)

from core.cloud_sync import (
    get_cloud_sync_status
)

from core.deployment_manager import (

    get_environments,

    get_deployments
)


# ==================================================
# LOGGER
# ==================================================

logger = get_logger(
    "distributed_monitoring_view"
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

def distributed_monitoring_view(page):

    logger.info(
        "Distributed monitoring."
    )

    # ==============================================
    # LOAD
    # ==============================================

    runtime = get_runtime_status()

    containers = get_containers()

    workers = get_worker_status()

    mesh = get_mesh_status()

    observability = (
        export_observability()
    )

    cloud_sync = (
        get_cloud_sync_status()
    )

    environments = (
        get_environments()
    )

    deployments = (
        get_deployments()
    )

    # ==============================================
    # HEADER
    # ==============================================

    header = ft.Row(

        [

            ft.Text(

                (
                    "Distributed "
                    "Monitoring Center"
                ),

                size=28,

                weight=(
                    ft.FontWeight.BOLD
                )
            )
        ]
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

                "Deployments",

                len(deployments),

                ft.Colors.ORANGE
            )
        ]
    )

    # ==============================================
    # CONTAINERS
    # ==============================================

    container_controls = []

    for (

        container_id,

        container

    ) in containers.items():

        container_controls.append(

            ft.ListTile(

                leading=ft.Icon(
                    ft.Icons.DATA_OBJECT
                ),

                title=ft.Text(
                    container_id
                ),

                subtitle=ft.Text(
                    str(container)
                )
            )
        )

    containers_section = ft.Container(

        content=ft.Column(

            [

                section_title(
                    "Containers"
                ),

                ft.Column(
                    container_controls
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

                ft.Text(str(mesh))
            ]
        ),

        padding=15
    )

    # ==============================================
    # OBSERVABILITY
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

                ft.Column(
                    alert_controls
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
    # MAIN
    # ==============================================

    content = ft.Column(

        [

            header,

            ft.Divider(),

            kpis,

            ft.Divider(),

            containers_section,

            workers_section,

            mesh_section,

            observability_section,

            cloud_sync_section,

            deployments_section,

            environments_section
        ],

        scroll=ft.ScrollMode.AUTO,

        expand=True
    )

    return ft.Container(

        content=content,

        expand=True,

        padding=20
    )
