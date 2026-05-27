import logging

import flet as ft

from modules.administracao.perfis.services.perfil_service import (
    listar_perfis,
)

from security.session_service import (
    obter_usuario,
)

from services.menu_admin_service import (
    get_permissoes_usuario,
    listar_menus_com_permissao,
    salvar_permissoes,
)

from ui.components.base_view import (
    base_view,
)

from ui.components.buttons import (
    save_button,
)

from ui.components.cards import (
    section_card,
)

from ui.components.fields import (
    app_dropdown,
)

from ui.components.snackbars import (
    show_error,
    show_success,
)


LOGGER = logging.getLogger(
    "SMDM_PERFIL_MENU_UI"
)


def perfil_menu_view(page: ft.Page):

    usuario = (
        getattr(page, "usuario_logado", None)
        or obter_usuario()
        or {}
    )

    permissoes_usuario = get_permissoes_usuario(
        usuario,
        "perfil_menu",
    )

    if not permissoes_usuario.get("ver"):

        return ft.Container(
            expand=True,
            alignment=ft.Alignment(0, 0),
            content=ft.Text(
                "Acesso negado.",
                size=18,
                color=ft.Colors.RED,
            ),
        )

    pode_editar = bool(
        permissoes_usuario.get("editar")
    )

    perfil_atual = {
        "id": None,
    }

    checks = {}

    tabela_container = ft.Container(
        expand=True,
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
    )

    lbl_status = ft.Text(
        "Selecione um perfil.",
        size=12,
        color=ft.Colors.GREY_700,
    )

    perfis = listar_perfis()

    ddl_perfil = app_dropdown(
        label="Perfil",
        options=[
            (
                item["id"],
                (
                    f"{item['nome']} "
                    f"(nível {item['admin_level']})"
                ),
            )
            for item in perfis
        ],
        width=320,
    )

    def montar_linha(menu):

        menu_id = int(menu["id"])

        ck_ver = ft.Checkbox(
            label="Ver",
            value=bool(menu.get("ver")),
            disabled=not pode_editar,
        )

        ck_editar = ft.Checkbox(
            label="Editar",
            value=bool(menu.get("editar")),
            disabled=not pode_editar,
        )

        ck_excluir = ft.Checkbox(
            label="Excluir",
            value=bool(menu.get("excluir")),
            disabled=not pode_editar,
        )

        checks[menu_id] = {
            "ver": ck_ver,
            "editar": ck_editar,
            "excluir": ck_excluir,
        }

        nome = str(
            menu.get("nome")
            or ""
        )

        rota = str(
            menu.get("rota")
            or ""
        )

        tipo = str(
            menu.get("tipo_menu")
            or ""
        )

        level = 0

        if menu.get("pai"):
            level = 1

        if tipo == "S":
            level = 2

        return ft.Container(
            height=30,
            padding=ft.Padding(
                8 + (level * 14),
                0,
                8,
                0,
            ),
            bgcolor=ft.Colors.WHITE,
            border_radius=4,
            content=ft.Row(
                spacing=6,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Text(
                        tipo,
                        width=24,
                        size=11,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Text(
                        nome,
                        expand=True,
                        size=12,
                        max_lines=1,
                        overflow=ft.TextOverflow.ELLIPSIS,
                    ),
                    ft.Text(
                        rota,
                        width=150,
                        size=11,
                        color=ft.Colors.GREY_700,
                        max_lines=1,
                        overflow=ft.TextOverflow.ELLIPSIS,
                    ),
                    ft.Container(width=80, content=ck_ver),
                    ft.Container(width=90, content=ck_editar),
                    ft.Container(width=90, content=ck_excluir),
                ],
            ),
        )

    def carregar(e=None):

        try:

            checks.clear()

            perfil_id = ddl_perfil.value

            if not perfil_id:

                perfil_atual["id"] = None

                tabela_container.content = ft.Container(
                    padding=20,
                    content=ft.Text(
                        "Selecione um perfil para editar as permissões.",
                    ),
                )

                page.update()

                return

            perfil_atual["id"] = int(perfil_id)

            menus = listar_menus_com_permissao(
                perfil_atual["id"]
            )

            lbl_status.value = (
                f"Menus carregados: {len(menus)}"
            )

            tabela_container.content = ft.Column(
                expand=True,
                scroll=ft.ScrollMode.AUTO,
                spacing=1,
                controls=[
                    ft.Container(
                        height=30,
                        padding=ft.Padding(8, 0, 8, 0),
                        bgcolor=ft.Colors.BLUE_GREY_50,
                        border_radius=4,
                        content=ft.Row(
                            spacing=6,
                            controls=[
                                ft.Text("T", width=24, size=11, weight=ft.FontWeight.BOLD),
                                ft.Text("Menu", expand=True, size=11, weight=ft.FontWeight.BOLD),
                                ft.Text("Rota", width=150, size=11, weight=ft.FontWeight.BOLD),
                                ft.Text("Ver", width=80, size=11, weight=ft.FontWeight.BOLD),
                                ft.Text("Editar", width=90, size=11, weight=ft.FontWeight.BOLD),
                                ft.Text("Excluir", width=90, size=11, weight=ft.FontWeight.BOLD),
                            ],
                        ),
                    ),
                    *[
                        montar_linha(menu)
                        for menu in menus
                    ],
                ],
            )

            page.update()

        except Exception as ex:

            LOGGER.exception(
                "LOAD PERFIL MENU ERROR"
            )

            show_error(
                page,
                str(ex),
            )

    def salvar(e=None):

        try:

            if not pode_editar:

                show_error(
                    page,
                    "Sem permissão.",
                )

                return

            if not perfil_atual["id"]:

                show_error(
                    page,
                    "Selecione um perfil.",
                )

                return

            payload = []

            for menu_id, controles in checks.items():

                payload.append({
                    "menu_id": menu_id,
                    "ver": controles["ver"].value,
                    "editar": controles["editar"].value,
                    "excluir": controles["excluir"].value,
                })

            resultado = salvar_permissoes(
                perfil_atual["id"],
                payload,
                usuario,
            )

            if not resultado.get("sucesso"):

                show_error(
                    page,
                    resultado.get("mensagem")
                    or "Erro ao salvar permissões.",
                )

                return

            show_success(
                page,
                "Permissões salvas.",
            )

            carregar()

        except Exception as ex:

            LOGGER.exception(
                "SAVE PERFIL MENU ERROR"
            )

            show_error(
                page,
                str(ex),
            )

    ddl_perfil.on_change = carregar

    painel_perfil = section_card(
        title="Perfil",
        subtitle="Selecione o perfil para revisar o menu",
        icon=ft.Icons.SECURITY,
        content=ft.Column(
            spacing=8,
            controls=[
                ddl_perfil,
                lbl_status,
                ft.Row(
                    controls=[
                        save_button(
                            on_click=salvar,
                        ),
                    ],
                ),
            ],
        ),
    )

    painel_menus = section_card(
        title="Perfil x Menu",
        subtitle="Permissões de visualização e manutenção",
        icon=ft.Icons.ACCOUNT_TREE,
        content=tabela_container,
        expand=True,
    )

    carregar(
        None
    )

    return base_view(
        title="Perfil x Menu",
        subtitle="Administração de permissões de menu por perfil",
        content_controls=[
            ft.Row(
                expand=True,
                spacing=8,
                vertical_alignment=ft.CrossAxisAlignment.START,
                controls=[
                    ft.Container(
                        width=340,
                        content=painel_perfil,
                    ),
                    ft.Container(
                        expand=True,
                        content=painel_menus,
                    ),
                ],
            )
        ],
        scroll=None,
    )
