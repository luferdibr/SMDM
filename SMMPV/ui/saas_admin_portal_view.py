
import flet as ft


from core.logger import get_logger

from core.billing_manager import (

    get_all_plans,

    get_all_subscriptions
)

from core.governance_center import (

    get_violations,

    suspend_tenant
)

from core.enterprise_command_center import (

    get_executive_kpis,

    restart_enterprise_platform
)

from core.deployment_manager import (
    get_environments
)

from core.observability_center import (
    export_observability
)


# ==================================================
# LOGGER
# ==================================================

logger = get_logger(
    "saas_admin_portal_view"
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

def saas_admin_portal_view(page):

    logger.info(
        "SaaS admin portal."
    )

    # ==============================================
    # LOAD DATA
    # ==============================================

    plans = get_all_plans()

    subscriptions = (
        get_all_subscriptions()
    )

    violations = (
        get_violations()
    )

    environments = (
        get_environments()
    )

    observability = (
        export_observability()
    )

    kpis = (
        get_executive_kpis()
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

    def on_suspend_tenant(
        tenant_id
    ):

        suspend_tenant(
            tenant_id
        )

        page.snack_bar = ft.SnackBar(

            ft.Text(

                (
                    f"Tenant "
                    f"{tenant_id} "
                    f"suspenso."
                )
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

                "SaaS Administration Portal",

                size=28,

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

                kpis.get(
                    (
                        "governance_"
                        "violations"
                    ),
                    0
                ),

                ft.Colors.RED
            ),

            create_card(

                "Telemetry",

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
    # PLANS
    # ==============================================

    plan_controls = []

    for plan_id, plan in plans.items():

        plan_controls.append(

            ft.ListTile(

                leading=ft.Icon(
                    ft.Icons.PAYMENTS
                ),

                title=ft.Text(
                    plan_id
                ),

                subtitle=ft.Text(
                    str(plan)
                )
            )
        )

    plans_section = ft.Container(

        content=ft.Column(

            [

                section_title(
                    "Plans"
                ),

                ft.Column(
                    plan_controls
                )
            ]
        ),

        padding=15
    )

    # ==============================================
    # SUBSCRIPTIONS
    # ==============================================

    subscription_controls = []

    for (

        tenant_id,

        subscription

    ) in subscriptions.items():

        subscription_controls.append(

            ft.Card(

                content=ft.Container(

                    content=ft.Column(

                        [

                            ft.Text(

                                (
                                    f"Tenant: "
                                    f"{tenant_id}"
                                ),

                                weight=(
                                    ft.FontWeight
                                    .BOLD
                                )
                            ),

                            ft.Text(
                                str(
                                    subscription
                                )
                            ),

                            ft.Row(

                                [

                                    ft.ElevatedButton(

                                        "Suspender",

                                        icon=(
                                            ft.Icons
                                            .BLOCK
                                        ),

                                        on_click=(
                                            lambda e,
                                            t=tenant_id:

                                            on_suspend_tenant(
                                                t
                                            )
                                        )
                                    )
                                ]
                            )
                        ]
                    ),

                    padding=10
                )
            )
        )

    subscriptions_section = ft.Container(

        content=ft.Column(

            [

                section_title(
                    "Subscriptions"
                ),

                ft.Column(
                    subscription_controls
                )
            ]
        ),

        padding=15
    )

    # ==============================================
    # GOVERNANCE
    # ==============================================

    violation_controls = []

    for violation in violations[-20:]:

        violation_controls.append(

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

                ft.Column(
                    violation_controls
                )
            ]
        ),

        padding=15
    )

    # ==============================================
    # DEPLOYMENTS
    # ==============================================

    env_controls = []

    for env_id, env in (
        environments.items()
    ):

        env_controls.append(

            ft.ListTile(

                leading=ft.Icon(
                    ft.Icons.CLOUD
                ),

                title=ft.Text(
                    env_id
                ),

                subtitle=ft.Text(
                    str(env)
                )
            )
        )

    deployment_section = ft.Container(

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
                        f"Alerts: "
                        f"{len(observability.get('alerts', []))}"
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
                        f"Metrics: "
                        f"{len(observability.get('metrics', {}))}"
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

            plans_section,

            subscriptions_section,

            governance_section,

            deployment_section,

            observability_section
        ],

        scroll=ft.ScrollMode.AUTO,

        expand=True
    )

    return ft.Container(

        content=content,

        expand=True,

        padding=20
    )
