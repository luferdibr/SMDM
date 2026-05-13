
import logging

import flet as ft

from ui.dashboard import navegar

from services.user_service import (
    listar_perfis
)

from services.menu_admin_service import (

    listar_menus_com_permissao,

    salvar_permissoes,

    copiar_permissoes,

    get_permissoes_usuario
)


# ==================================================
# CONFIG
# ==================================================

ROOT_LEVEL = 100


# ==================================================
# HELPERS
# ==================================================

def get_usuario(page):

    usuario = getattr(
        page,
        "usuario_logado",
        None
    )

    if (
        not usuario
        or
        not isinstance(usuario, dict)
    ):
        return None

    return usuario


def exibir_snackbar(
    page,
    mensagem,
    erro=False
):

    page.snack_bar = ft.SnackBar(

        content=ft.Text(
            mensagem
        ),

        bgcolor=(

            ft.Colors.RED_400

            if erro

            else

            ft.Colors.GREEN_600
        ),

        open=True
    )

    page.update()


# ==================================================
# VIEW
# ==================================================

def menu_admin_view(page):

    usuario = get_usuario(page)

    # ==============================================
    # SESSÃO
    # ==============================================

    if not usuario:

        return ft.Container(

            content=ft.Column([

                ft.Icon(
                    ft.Icons.ERROR,
                    size=72,
                    color=ft.Colors.RED
                ),

                ft.Text(
                    "Sessão inválida.",
                    size=24,
                    weight="bold",
                    color=ft.Colors.RED
                )

            ],

                spacing=20,

                horizontal_alignment=(
                    ft.CrossAxisAlignment.CENTER
                )
            ),

            alignment=ft.Alignment(0, 0),

            expand=True
        )

    usuario_level = int(
        usuario.get(
            "admin_level",
            0
        )
    )

    is_root = (
        usuario_level >= ROOT_LEVEL
    )

    # ==============================================
    # RBAC
    # ==============================================

    permissoes_usuario = get_permissoes_usuario(

        usuario,

        "menu_config"
    )

    if not permissoes_usuario.get("ver"):

        return ft.Container(

            content=ft.Column([

                ft.Icon(
                    ft.Icons.LOCK,
                    size=72,
                    color=ft.Colors.RED
                ),

                ft.Text(
                    "Acesso negado.",
                    size=24,
                    weight="bold",
                    color=ft.Colors.RED
                )

            ],

                spacing=20,

                horizontal_alignment=(
                    ft.CrossAxisAlignment.CENTER
                )
            ),

            alignment=ft.Alignment(0, 0),

            expand=True
        )

    pode_editar = bool(
        permissoes_usuario.get("editar")
    )

    carregando = False

    controles = []

    menus_cache = []

    # ==============================================
    # COMPONENTES
    # ==============================================

    txt_filtro = ft.TextField(

        label="Pesquisar Menu",

        width=320,

        prefix_icon=ft.Icons.SEARCH
    )

    ddl_perfil = ft.Dropdown(

        label="Perfil",

        width=320
    )

    ddl_copiar = ft.Dropdown(

        label="Copiar permissões de",

        width=320
    )

    txt_status = ft.Text(
        "",
        color=ft.Colors.RED
    )

    progress = ft.ProgressRing(
        visible=False
    )

    lista = ft.Column(
        spacing=6
    )

    # ==============================================
    # BOTÕES
    # ==============================================

    btn_carregar = ft.ElevatedButton(

        "Carregar",

        icon=ft.Icons.SEARCH
    )

    btn_salvar = ft.ElevatedButton(

        "Salvar",

        icon=ft.Icons.SAVE,

        disabled=not pode_editar
    )

    btn_copiar = ft.ElevatedButton(

        "Copiar",

        icon=ft.Icons.COPY,

        disabled=not pode_editar
    )

    btn_voltar = ft.ElevatedButton(

        "Voltar",

        icon=ft.Icons.ARROW_BACK
    )

    # ==============================================
    # LOCK UI
    # ==============================================

    def bloquear_ui(status):

        progress.visible = status

        btn_carregar.disabled = status

        btn_salvar.disabled = (
            status or not pode_editar
        )

        btn_copiar.disabled = (
            status or not pode_editar
        )

        btn_voltar.disabled = status

        ddl_perfil.disabled = status

        ddl_copiar.disabled = status

        txt_filtro.disabled = status

        page.update()

    # ==============================================
    # STATUS
    # ==============================================

    def status(
        texto,
        erro=True
    ):

        txt_status.value = texto

        txt_status.color = (

            ft.Colors.RED

            if erro

            else ft.Colors.GREEN
        )

        page.update()

    # ==============================================
    # PERFIS
    # ==============================================

    def carregar_perfis():

        resultado = listar_perfis(
            usuario
        )

        if not resultado["sucesso"]:

            raise Exception(
                resultado["mensagem"]
            )

        ddl_perfil.options.clear()

        ddl_copiar.options.clear()

        for p in resultado["dados"]:

            perfil_level = int(
                p.get(
                    "admin_level",
                    0
                )
            )

            perfil_sistema = bool(
                p.get(
                    "sistema",
                    0
                )
            )

            # ======================================
            # ROOT
            # ======================================

            if is_root:

                pass

            # ======================================
            # ADMIN
            # ======================================

            else:

                if perfil_sistema:
                    continue

                if perfil_level >= usuario_level:
                    continue

            texto = (
                f"{p['nome']} "
                f"(L{perfil_level})"
            )

            ddl_perfil.options.append(

                ft.dropdown.Option(

                    str(p["id"]),

                    texto
                )
            )

            ddl_copiar.options.append(

                ft.dropdown.Option(

                    str(p["id"]),

                    texto
                )
            )

    # ==============================================
    # PREFIXO
    # ==============================================

    def obter_prefixo(menu):

        if menu["sistema"]:
            return "🔒"

        if menu["tipo"] == "T":
            return "📁"

        if menu["tipo"] == "S":
            return "📂"

        return "📄"

    # ==============================================
    # NÍVEL
    # ==============================================

    def obter_nivel(menu_id):

        lookup = {
            m["id"]: m
            for m in menus_cache
        }

        nivel = 0

        atual = lookup.get(menu_id)

        contador = 0

        while (

            atual
            and
            atual.get("pai")
            and
            contador < 30
        ):

            atual = lookup.get(
                atual["pai"]
            )

            if not atual:
                break

            nivel += 1

            contador += 1

        return nivel

    # ==============================================
    # MENU PROTEGIDO
    # ==============================================

    def menu_protegido(menu):

        if is_root:
            return False

        if menu["sistema"]:
            return True

        if int(
            menu.get(
                "admin_level",
                0
            )
        ) >= ROOT_LEVEL:

            return True

        return False

    # ==============================================
    # VOLTAR
    # ==============================================

    def voltar_dashboard(e=None):

        navegar(page, "dashboard")

    btn_voltar.on_click = voltar_dashboard

    # ==============================================
    # CARREGAR
    # ==============================================

    def carregar(e=None):

        nonlocal carregando

        if carregando:
            return

        carregando = True

        bloquear_ui(True)

        try:

            lista.controls.clear()

            controles.clear()

            if not ddl_perfil.value:

                raise Exception(
                    "Selecione um perfil."
                )

            perfil_id = int(
                ddl_perfil.value
            )

            resultado = listar_menus_com_permissao(

                usuario,

                perfil_id
            )

            if not resultado["sucesso"]:

                raise Exception(
                    resultado["mensagem"]
                )

            menus_cache.clear()

            menus_cache.extend(
                resultado["dados"]
            )

            menus = sorted(

                menus_cache,

                key=lambda x: (

                    x["ordem"],

                    x["nome"]
                )
            )

            filtro = str(

                txt_filtro.value or ""

            ).strip().upper()

            for m in menus:

                texto = (
                    f"{m['nome']} "
                    f"{m.get('rota') or ''}"
                ).upper()

                if filtro:

                    if filtro not in texto:
                        continue

                tipo = m["tipo"]

                sistema = bool(
                    m["sistema"]
                )

                protegido = (
                    menu_protegido(m)
                )

                nivel = obter_nivel(
                    m["id"]
                )

                chk_ver = ft.Checkbox(
                    value=bool(m["ver"])
                )

                chk_editar = ft.Checkbox(
                    value=bool(m["editar"])
                )

                chk_excluir = ft.Checkbox(
                    value=bool(m["excluir"])
                )

                # ==================================
                # TÍTULO
                # ==================================

                if tipo == "T":

                    chk_editar.disabled = True

                    chk_excluir.disabled = True

                # ==================================
                # SUBMENU
                # ==================================

                elif tipo == "S":

                    chk_editar.disabled = True

                    chk_excluir.disabled = True

                # ==================================
                # PROTEGIDO
                # ==================================

                if protegido:

                    chk_ver.disabled = True

                    chk_editar.disabled = True

                    chk_excluir.disabled = True

                controles.append({

                    "menu_id": m["id"],

                    "ver": chk_ver,

                    "editar": chk_editar,

                    "excluir": chk_excluir
                })

                lista.controls.append(

                    ft.Container(

                        content=ft.Row([

                            ft.Container(

                                content=ft.Text(

                                    (
                                        f"{obter_prefixo(m)} "
                                        f"{m['nome']}"
                                    ),

                                    weight=(

                                        "bold"

                                        if tipo in [
                                            "T",
                                            "S"
                                        ]

                                        else None
                                    ),

                                    size=(

                                        16

                                        if tipo == "T"

                                        else 14
                                    )
                                ),

                                width=380,

                                padding=ft.padding.only(
                                    left=nivel * 24
                                )
                            ),

                            ft.Text(

                                str(
                                    m.get(
                                        "admin_level",
                                        0
                                    )
                                ),

                                width=70
                            ),

                            chk_ver,

                            chk_editar,

                            chk_excluir

                        ],

                            wrap=True
                        ),

                        padding=10,

                        border=ft.border.all(

                            1,

                            ft.Colors.GREY_300
                        ),

                        border_radius=8,

                        bgcolor=(

                            ft.Colors.RED_50

                            if sistema

                            else (

                                ft.Colors.BLUE_50

                                if tipo == "T"

                                else (

                                    ft.Colors.GREY_100

                                    if tipo == "S"

                                    else None
                                )
                            )
                        )
                    )
                )

            page.update()

        except Exception as ex:

            logging.exception(
                "LOAD PERMISSIONS ERROR"
            )

            status(str(ex))

        finally:

            carregando = False

            bloquear_ui(False)

    btn_carregar.on_click = carregar

    txt_filtro.on_change = (
        lambda e: carregar()
    )

    # ==============================================
    # SALVAR
    # ==============================================

    def salvar(e=None):

        nonlocal carregando

        if carregando:
            return

        carregando = True

        bloquear_ui(True)

        try:

            if not ddl_perfil.value:

                raise Exception(
                    "Selecione um perfil."
                )

            perfil_id = int(
                ddl_perfil.value
            )

            permissoes = []

            for c in controles:

                permissoes.append({

                    "menu_id": c["menu_id"],

                    "ver": int(
                        bool(
                            c["ver"].value
                        )
                    ),

                    "editar": int(
                        bool(
                            c["editar"].value
                        )
                    ),

                    "excluir": int(
                        bool(
                            c["excluir"].value
                        )
                    )
                })

            resultado = salvar_permissoes(

                usuario,

                perfil_id,

                permissoes
            )

            if not resultado["sucesso"]:

                raise Exception(
                    resultado["mensagem"]
                )

            exibir_snackbar(

                page,

                resultado["mensagem"]
            )

        except Exception as ex:

            logging.exception(
                "SAVE PERMISSIONS ERROR"
            )

            exibir_snackbar(

                page,

                str(ex),

                erro=True
            )

        finally:

            carregando = False

            bloquear_ui(False)

    btn_salvar.on_click = salvar

    # ==============================================
    # COPIAR
    # ==============================================

    def copiar(e=None):

        nonlocal carregando

        if carregando:
            return

        carregando = True

        bloquear_ui(True)

        try:

            if (

                not ddl_perfil.value

                or

                not ddl_copiar.value
            ):

                raise Exception(
                    "Selecione origem e destino."
                )

            destino = int(
                ddl_perfil.value
            )

            origem = int(
                ddl_copiar.value
            )

            resultado = copiar_permissoes(

                usuario,

                origem,

                destino
            )

            if not resultado["sucesso"]:

                raise Exception(
                    resultado["mensagem"]
                )

            carregar()

            exibir_snackbar(

                page,

                resultado["mensagem"]
            )

        except Exception as ex:

            logging.exception(
                "COPY PERMISSIONS ERROR"
            )

            exibir_snackbar(

                page,

                str(ex),

                erro=True
            )

        finally:

            carregando = False

            bloquear_ui(False)

    btn_copiar.on_click = copiar

    # ==============================================
    # INIT
    # ==============================================

    try:

        carregar_perfis()

    except Exception as ex:

        logging.exception(
            "LOAD PROFILES ERROR"
        )

        status(str(ex))

    # ==============================================
    # LAYOUT
    # ==============================================

    return ft.Column([

        ft.Row([

            ft.Text(

                "Administração de Permissões",

                size=28,

                weight="bold"
            ),

            progress

        ],

            alignment=(
                ft.MainAxisAlignment.SPACE_BETWEEN
            )
        ),

        ft.Divider(),

        ft.Row([

            ddl_perfil,

            ddl_copiar,

            txt_filtro

        ],

            wrap=True
        ),

        txt_status,

        ft.Row([

            btn_carregar,

            btn_salvar,

            btn_copiar,

            btn_voltar

        ],

            wrap=True
        ),

        ft.Divider(),

        ft.Container(

            content=ft.Row([

                ft.Text(

                    "Menu",

                    width=380,

                    weight="bold"
                ),

                ft.Text(

                    "Level",

                    width=70,

                    weight="bold"
                ),

                ft.Text(

                    "Ver",

                    width=60,

                    weight="bold"
                ),

                ft.Text(

                    "Editar",

                    width=70,

                    weight="bold"
                ),

                ft.Text(

                    "Excluir",

                    width=70,

                    weight="bold"
                )

            ],

                wrap=True
            ),

            padding=10
        ),

        lista

    ],

        expand=True,

        scroll=ft.ScrollMode.AUTO
    )