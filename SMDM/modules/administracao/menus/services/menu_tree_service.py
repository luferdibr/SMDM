# =========================================================
# services/menu_tree_service.py
# =========================================================

import logging

from copy import deepcopy

# =========================================================
# LOGGER
# =========================================================

LOGGER = logging.getLogger(
    "SMDM_MENU_TREE"
)

# =========================================================
# SORT ITEMS
# =========================================================

def sort_items(
    items,
):

    return sorted(

        items,

        key=lambda x: (

            int(
                x.get(
                    "ordem",
                    0,
                )
            ),

            str(
                x.get(
                    "nome",
                    "",
                )
            ).upper(),
        ),
    )

# =========================================================
# SAFE COPY
# =========================================================

def safe_copy(
    item,
):

    copia = deepcopy(item)

    copia["filhos"] = []

    return copia

# =========================================================
# IS ROOT
# =========================================================

def is_root(
    pai,
):

    return (

        pai is None

        or

        pai == ""

        or

        pai == 0

        or

        pai == "0"
    )

# =========================================================
# BUILD TREE
# =========================================================

def build_menu_tree(
    menus,
):

    menus = menus or []

    LOGGER.info(

        (
            f"Montando árvore "
            f"{len(menus)} itens"
        )
    )

    mapa = {}

    raiz = []

    # =====================================================
    # INDEX
    # =====================================================

    for item in menus:

        try:

            copia = safe_copy(
                item
            )

            menu_id = copia.get(
                "id"
            )

            if menu_id is None:

                LOGGER.warning(
                    "Menu sem ID ignorado."
                )

                continue

            mapa[
                menu_id
            ] = copia

        except Exception:

            LOGGER.exception(
                "Erro indexando menu."
            )

    LOGGER.info(

        (
            f"Mapa indexado "
            f"{len(mapa)} itens"
        )
    )

    # =====================================================
    # LINK TREE
    # =====================================================

    for menu_id, menu in mapa.items():

        try:

            pai = (

                menu.get(
                    "menu_pai"
                )

                or

                menu.get(
                    "pai"
                )

                or

                menu.get(
                    "parent_id"
                )

                or

                menu.get(
                    "menu_parent"
                )
            )

            LOGGER.info(

                (
                    f"Processando "
                    f"menu={menu_id} "
                    f"pai={pai}"
                )
            )

            # =============================================
            # ROOT
            # =============================================

            if is_root(pai):

                raiz.append(menu)

                LOGGER.info(
                    f"Raiz: {menu_id}"
                )

                continue

            # =============================================
            # SELF LOOP
            # =============================================

            if str(pai) == str(menu_id):

                LOGGER.warning(

                    (
                        f"Loop próprio "
                        f"menu={menu_id}"
                    )
                )

                raiz.append(menu)

                continue

            # =============================================
            # PARENT NOT FOUND
            # =============================================

            pai_menu = mapa.get(
                pai
            )

            if not pai_menu:

                LOGGER.warning(

                    (
                        f"Pai inexistente "
                        f"menu={menu_id} "
                        f"pai={pai}"
                    )
                )

                raiz.append(menu)

                continue

            # =============================================
            # LINK CHILD
            # =============================================

            pai_menu[
                "filhos"
            ].append(menu)

            LOGGER.info(

                (
                    f"Vinculado "
                    f"filho={menu_id} "
                    f"pai={pai}"
                )
            )

        except Exception:

            LOGGER.exception(
                f"Erro vinculando menu {menu_id}"
            )

    # =====================================================
    # SORT RECURSIVO
    # =====================================================

    def ordenar(
        items,
    ):

        items = sort_items(
            items
        )

        for item in items:

            filhos = item.get(
                "filhos",
                []
            )

            if filhos:

                item["filhos"] = (
                    ordenar(
                        filhos
                    )
                )

        return items

    retorno = ordenar(raiz)

    LOGGER.info(

        (
            f"Árvore montada "
            f"{len(retorno)} raízes"
        )
    )

    LOGGER.info(
        f"Árvore final: {retorno}"
    )

    return retorno

# =========================================================
# FLATTEN TREE
# =========================================================

def flatten_tree(
    tree,
):

    retorno = []

    def processar(
        items,
        nivel=0,
    ):

        items = sort_items(
            items
        )

        for item in items:

            copia = dict(item)

            copia["_nivel"] = nivel

            retorno.append(copia)

            filhos = item.get(
                "filhos",
                []
            )

            if filhos:

                processar(
                    filhos,
                    nivel + 1,
                )

    processar(tree)

    return retorno

# =========================================================
# DEPTH
# =========================================================

def get_depth(
    menu,
):

    return int(

        menu.get(
            "_nivel",
            0,
        )
    )

# =========================================================
# HAS CHILDREN
# =========================================================

def has_children(
    menu,
):

    return bool(

        menu.get(
            "filhos",
            []
        )
    )

# =========================================================
# FILTER TREE
# =========================================================

def filter_tree(
    tree,
    texto,
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

        filhos_filtrados = (
            filter_tree(
                filhos,
                texto,
            )
        )

        nome = str(

            item.get(
                "nome",
                "",
            )

        ).upper()

        rota = str(

            item.get(
                "rota",
                "",
            )

        ).upper()

        encontrou = (

            texto in nome

            or

            texto in rota
        )

        if encontrou or filhos_filtrados:

            novo = dict(item)

            novo[
                "filhos"
            ] = filhos_filtrados

            retorno.append(novo)

    return retorno

# =========================================================
# FIND BY ID
# =========================================================

def find_menu_by_id(
    tree,
    menu_id,
):

    for item in tree:

        if item.get("id") == menu_id:

            return item

        filhos = item.get(
            "filhos",
            []
        )

        if filhos:

            encontrado = (
                find_menu_by_id(
                    filhos,
                    menu_id,
                )
            )

            if encontrado:

                return encontrado

    return None

# =========================================================
# FIND BY ROUTE
# =========================================================

def find_menu_by_route(
    tree,
    rota,
):

    rota = str(
        rota or ""
    ).strip().lower()

    for item in tree:

        item_rota = str(

            item.get(
                "rota",
                ""
            )

        ).strip().lower()

        if item_rota == rota:

            return item

        filhos = item.get(
            "filhos",
            []
        )

        if filhos:

            encontrado = (
                find_menu_by_route(
                    filhos,
                    rota,
                )
            )

            if encontrado:

                return encontrado

    return None