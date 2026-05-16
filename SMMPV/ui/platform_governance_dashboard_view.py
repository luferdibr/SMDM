
import flet as ft


from core.logger import get_logger

from core.governance_center import (

    get_policies,

    get_violations,

    suspend_tenant
)

from core.billing_manager import (

    get_all_subscriptions,

    get_all_plans
)

from core.observability_center import (
    export_observability
)

from core.enterprise_command_center import (

    restart_enterprise_platform,

    get_executive_kpis
)

from core.deployment_manager import (
    get_deployments
)


# ==================================================
# LOGGER
# ==================================================

logger = get_logger(
    "platform_governance_dashboard"
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

def platform_governance_dashboard_view(page):

    logger.info(
        "Platform governance dashboard."
    )

    # ==============================================
    # LOAD DATA
    # ==============================================

    policies = get_policies()

    violations = (
        get_violations()
    )

    subscriptions = (
        get_all_subscriptions()
    )

    plans = get_all_plans()

    observability = (
        export_observability()
    )

    deployments = (
        get_deployments()
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
                "Runtime reiniciado."
            )
        )

        page.snack_bar.open = True

        page.update()

    def on_suspend(
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

                (
                    "Platform Governance "
                    "Dashboard"
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

                "Policies",

                len(policies),

                ft.Colors.BLUE
            ),

            create_card(

                "Violations",

                len(violations),

                ft.Colors.RED
            ),

            create_card(

                "Subscriptions",

                len(subscriptions),

                ft.Colors.GREEN
            ),

            create_card(

                "Deployments",

                len(deployments),

                ft.Colors.ORANGE
            )
        ]
    )

    # ==============================================
    # POLICIES
    # ==============================================

    policy_controls = []

    for policy_id, policy in (
        policies.items()
    ):

        policy_controls.append(

            ft.ListTile(

                leading=ft.Icon(
                    ft.Icons.GAVEL
                ),

                title=ft.Text(
                    policy_id
                ),

                subtitle=ft.Text(
                    str(policy)
                )
            )
        )

    policies_section = ft.Container(

        content=ft.Column(

            [

                section_title(
                    "Policies"
                ),

                ft.Column(
                    policy_controls
                )
            ]
        ),

        padding=15
    )

    # ==============================================
    # VIOLATIONS
    # ==============================================

    violation_controls = []

    for violation in violations[-25:]:

        violation_controls.append(

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
                            ),

                            ft.Text(

                                (
                                    f"Tenant: "
                                    f"{violation.get('tenant_id', '-')}"
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
                                            t=violation.get(
                                                "tenant_id"
                                            ):

                                            on_suspend(t)
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

    violations_section = ft.Container(

        content=ft.Column(

            [

                section_title(
                    "Violations"
                ),

                ft.Column(
                    violation_controls
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

            ft.ListTile(

                leading=ft.Icon(
                    ft.Icons.PAYMENTS
                ),

                title=ft.Text(
                    tenant_id
                ),

                subtitle=ft.Text(
                    str(subscription)
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
    # PLANS
    # ==============================================

    plan_controls = []

    for plan_id, plan in (
        plans.items()
    ):

        plan_controls.append(

            ft.ListTile(

                leading=ft.Icon(
                    ft.Icons.LIST_ALT
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
    # EXECUTIVE KPIS
    # ==============================================

    executive_section = ft.Container(

        content=ft.Column(

            [

                section_title(
                    "Executive KPIs"
                ),

                ft.Text(str(kpis))
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

            policies_section,

            violations_section,

            subscriptions_section,

            plans_section,

            observability_section,

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