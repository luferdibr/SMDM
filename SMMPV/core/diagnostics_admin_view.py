
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

from core.deployment_manager import (
    get_deployments
)

from core.billing_manager import (
    get_all_subscriptions
)


# ==================================================
# LOGGER
# ==================================================

logger = get_logger(
    "diagnostics_admin_view"
)


# ==================================================
# HELPERS
# ==================================================

def create_stat_card(

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
            ],

            spacing=5
        ),

        padding=15,

        border_radius=10,

        bgcolor=color,

        expand=True
    )


def create_section_title(title):

    return ft.Text(

        title,

        size=20,

        weight=ft.FontWeight.BOLD
    )


# ==================================================
# VIEW
# ==================================================

def diagnostics_admin_view(page):

    logger.info(
        "Diagnostics admin view."
    )

    # ==============================================
    # LOAD DATA
    # ==============================================

    dashboard = (
        get_enterprise_dashboard()
    )

    kpis = (
        get_executive_kpis()
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

    deployments = (
        get_deployments()
    )

    subscriptions = (
        get_all_subscriptions()
    )

    dashboard_data = dashboard.get(
        "dados",
        {}
    )

    # ==============================================
    # ACTIONS
    # ==============================================

    def on_restart_click(e):

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

                "Enterprise Command Center",

                size=28,

                weight=(
                    ft.FontWeight.BOLD
                )
            ),

            ft.ElevatedButton(

                "Reiniciar Plataforma",

                icon=ft.Icons.RESTART_ALT,

                on_click=(
                    on_restart_click
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

            create_stat_card(

                "Tenants",

                kpis.get(
                    "tenants",
                    0
                ),

                ft.Colors.BLUE
            ),

            create_stat_card(

                "Deployments",

                kpis.get(
                    "deployments",
                    0
                ),

                ft.Colors.GREEN
            ),

            create_stat_card(

                "Violations",

                kpis.get(
                    (
                        "governance_"
                        "violations"
                    ),
                    0
                ),

                ft.Colors.RED
            ),

            create_stat_card(

                "Telemetry Events",

                kpis.get(
                    (
                        "telemetry_"
                        "events"
                    ),
                    0
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

                create_section_title(
                    "Platform"
                ),

                ft.Text(

                    str(

                        dashboard_data.get(
                            "platform",
                            {}
                        )
                    )
                )
            ]
        ),

        padding=15
    )

    # ==============================================
    # OPERATIONS
    # ==============================================

    operations_section = ft.Container(

        content=ft.Column(

            [

                create_section_title(
                    "Operations"
                ),

                ft.Text(
                    str(operations)
                )
            ]
        ),

        padding=15
    )

    # ==============================================
    # GOVERNANCE
    # ==============================================

    governance_section = ft.Container(

        content=ft.Column(

            [

                create_section_title(
                    "Governance"
                ),

                ft.Text(

                    (
                        f"Violations: "
                        f"{len(violations)}"
                    )
                ),

                ft.Text(

                    (
                        f"Subscriptions: "
                        f"{len(subscriptions)}"
                    )
                )
            ]
        ),

        padding=15
    )

    # ==============================================
    # DEPLOYMENTS
    # ==============================================

    deployment_items = []

    for deploy in deployments:

        deployment_items.append(

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

                create_section_title(
                    "Deployments"
                ),

                ft.Column(
                    deployment_items
                )
            ]
        ),

        padding=15
    )

    # ==============================================
    # ALERTS
    # ==============================================

    alert_items = []

    for alert in observability.get(
        "alerts",
        []
    )[-10:]:

        alert_items.append(

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

                create_section_title(
                    "Alerts"
                ),

                ft.Column(
                    alert_items
                )
            ]
        ),

        padding=15
    )

    # ==============================================
    # TELEMETRY
    # ==============================================

    telemetry_section = ft.Container(

        content=ft.Column(

            [

                create_section_title(
                    "Telemetry"
                ),

                ft.Text(

                    str(

                        dashboard_data.get(
                            "telemetry",
                            {}
                        )
                    )
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

            operations_section,

            governance_section,

            deployments_section,

            alerts_section,

            telemetry_section
        ],

        scroll=ft.ScrollMode.AUTO,

        expand=True
    )

    return ft.Container(

        content=content,

        expand=True,

        padding=20
    )
