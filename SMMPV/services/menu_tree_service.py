# services/menu_tree_service.py

import logging


LOGGER = logging.getLogger(
    "MDM_MENU_TREE"
)


# ==================================================
# HELPERS
# ==================================================

def sort_items(items):

    return sorted(

        items,

        key=lambda x: (

            int(
                x.get(
                    "ordem",
                    0
                )
            ),

            str(
                x.get(
                    "nome",
                    ""
                )
            ).upper()
        )
    )


# ==================================================
# BUILD TREE
# ==================================================

def build_menu_tree(menus):

    LOGGER.info(
        (
            f"Montando árvore "
            f"{len(menus)} itens"
        )
    )

    mapa = {}

    raiz = []

    # ==============================================
    # INDEXAÇÃO
    # ==============================================

    for menu in menus:

        menu["filhos"] = []

        mapa[
            menu["id"]
        ] = menu

    # ==============================================
    # VINCULAÇÃO
    # ==============================================

    for menu in menus:

        pai = (

            menu.get("menu_pai")

            or

            menu.get("pai")
        )

        # ==========================================
        # RAIZ
        # ==========================================

        if pai is None:

            raiz.append(menu)

            continue

        # ==========================================
        # PAI NÃO EXISTE
        # ==========================================

        if pai not in mapa:

            LOGGER.warning(
                (
                    f"Pai inexistente "
                    f"menu={menu['id']} "
                    f"pai={pai}"
                )
            )

            raiz.append(menu)

            continue

        mapa[pai][
            "filhos"
        ].append(menu)

    # ==============================================
    # ORDENAÇÃO RECURSIVA
    # ==============================================

    def ordenar(items):

        items = sort_items(items)

        for item in items:

            filhos = item.get(
                "filhos",
                []
            )

            if filhos:

                item["filhos"] = ordenar(
                    filhos
                )

        return items

    retorno = ordenar(raiz)

    LOGGER.info(
        (
            f"Árvore final "
            f"{len(retorno)} raízes"
        )
    )

    return retorno


# ==================================================
# FLATTEN
# ==================================================

def flatten_tree(tree):

    retorno = []

    def processar(items, nivel=0):

        items = sort_items(items)

        for item in items:

            item["_nivel"] = nivel

            retorno.append(item)

            filhos = item.get(
                "filhos",
                []
            )

            if filhos:

                processar(
                    filhos,
                    nivel + 1
                )

    processar(tree)

    return retorno


# ==================================================
# DEPTH
# ==================================================

def get_depth(menu):

    return int(
        menu.get(
            "_nivel",
            0
        )
    )


# ==================================================
# HAS CHILDREN
# ==================================================

def has_children(menu):

    return bool(
        menu.get(
            "filhos"
        )
    )


# ==================================================
# FILTER TREE
# ==================================================

def filter_tree(
    tree,
    texto
):

    texto = str(
        texto or ""
    ).strip().upper()

    if not texto:
        return tree

    retorno = []

    for item in tree:

        filhos = item.get(
            "filhos",
            []
        )

        filhos_filtrados = filter_tree(
            filhos,
            texto
        )

        nome = str(
            item.get(
                "nome",
                ""
            )
        ).upper()

        rota = str(
            item.get(
                "rota",
                ""
            )
        ).upper()

        encontrou = (

            texto in nome

            or

            texto in rota
        )

        if encontrou or filhos_filtrados:

            novo = dict(item)

            novo["filhos"] = filhos_filtrados

            retorno.append(novo)

    return retorno
