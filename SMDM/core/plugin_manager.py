
import importlib
import traceback
from dataclasses import dataclass, field


from core.logger import get_logger

from core.responses import (
    ok,
    erro
)

from core.telemetry import (

    increment_counter,

    add_event
)


# ==================================================
# LOGGER
# ==================================================

logger = get_logger("plugin_manager")


# ==================================================
# STORAGE
# ==================================================

_PLUGINS = {}


# ==================================================
# PLUGIN
# ==================================================

@dataclass
class Plugin:

    name: str

    version: str = "1.0.0"

    author: str = "SMDM"

    description: str = ""

    enabled: bool = True

    loaded: bool = False

    startup_called: bool = False

    shutdown_called: bool = False

    dependencies: list = field(
        default_factory=list
    )

    routes: list = field(
        default_factory=list
    )

    jobs: list = field(
        default_factory=list
    )

    metadata: dict = field(
        default_factory=dict
    )

    module = None

    # ==============================================
    # DICT
    # ==============================================

    def to_dict(self):

        return {

            "name": self.name,

            "version": self.version,

            "author": self.author,

            "description": (
                self.description
            ),

            "enabled": self.enabled,

            "loaded": self.loaded,

            "startup_called": (
                self.startup_called
            ),

            "shutdown_called": (
                self.shutdown_called
            ),

            "dependencies": (
                self.dependencies
            ),

            "routes": self.routes,

            "jobs": self.jobs,

            "metadata": (
                self.metadata
            )
        }


# ==================================================
# REGISTER
# ==================================================

def register_plugin(plugin):

    if not isinstance(
        plugin,
        Plugin
    ):

        return erro(
            "Plugin inválido."
        )

    _PLUGINS[
        plugin.name
    ] = plugin

    logger.info(
        f"PLUGIN REGISTER {plugin.name}"
    )

    increment_counter(
        "plugins_registered"
    )

    add_event(

        "plugin",

        "register",

        {

            "plugin": plugin.name
        }
    )

    return ok(
        f"Plugin {plugin.name} registrado."
    )


# ==================================================
# REMOVE
# ==================================================

def unregister_plugin(name):

    plugin = _PLUGINS.get(name)

    if not plugin:

        return False

    del _PLUGINS[name]

    logger.warning(
        f"PLUGIN REMOVE {name}"
    )

    return True


# ==================================================
# GET
# ==================================================

def get_plugin(name):

    return _PLUGINS.get(name)


def get_plugins():

    return {

        k: v.to_dict()

        for k, v in _PLUGINS.items()
    }


# ==================================================
# ENABLE
# ==================================================

def enable_plugin(name):

    plugin = get_plugin(name)

    if not plugin:

        return erro(
            "Plugin não encontrado."
        )

    plugin.enabled = True

    logger.info(
        f"PLUGIN ENABLE {name}"
    )

    return ok(
        f"Plugin {name} habilitado."
    )


# ==================================================
# DISABLE
# ==================================================

def disable_plugin(name):

    plugin = get_plugin(name)

    if not plugin:

        return erro(
            "Plugin não encontrado."
        )

    plugin.enabled = False

    logger.warning(
        f"PLUGIN DISABLE {name}"
    )

    return ok(
        f"Plugin {name} desabilitado."
    )


# ==================================================
# DEPENDENCIES
# ==================================================

def validate_dependencies(plugin):

    for dependency in plugin.dependencies:

        dep = get_plugin(
            dependency
        )

        if not dep:

            raise Exception(

                (
                    f"Dependência "
                    f"{dependency} "
                    f"não encontrada."
                )
            )

        if not dep.enabled:

            raise Exception(

                (
                    f"Dependência "
                    f"{dependency} "
                    f"desabilitada."
                )
            )

    return True


# ==================================================
# STARTUP
# ==================================================

def startup_plugin(name):

    plugin = get_plugin(name)

    if not plugin:

        return erro(
            "Plugin inválido."
        )

    if not plugin.enabled:

        return erro(
            "Plugin desabilitado."
        )

    try:

        validate_dependencies(
            plugin
        )

        if (

            plugin.module

            and

            hasattr(

                plugin.module,

                "startup"
            )

        ):

            plugin.module.startup()

        plugin.loaded = True

        plugin.startup_called = True

        logger.info(
            f"PLUGIN STARTUP {name}"
        )

        increment_counter(
            "plugin_startups"
        )

        add_event(

            "plugin",

            "startup",

            {

                "plugin": name
            }
        )

        return ok(
            f"Plugin {name} iniciado."
        )

    except Exception as ex:

        logger.exception(
            f"PLUGIN STARTUP ERROR {name}"
        )

        return erro(str(ex))


# ==================================================
# SHUTDOWN
# ==================================================

def shutdown_plugin(name):

    plugin = get_plugin(name)

    if not plugin:

        return erro(
            "Plugin inválido."
        )

    try:

        if (

            plugin.module

            and

            hasattr(

                plugin.module,

                "shutdown"
            )

        ):

            plugin.module.shutdown()

        plugin.loaded = False

        plugin.shutdown_called = True

        logger.warning(
            f"PLUGIN SHUTDOWN {name}"
        )

        increment_counter(
            "plugin_shutdowns"
        )

        add_event(

            "plugin",

            "shutdown",

            {

                "plugin": name
            }
        )

        return ok(
            f"Plugin {name} finalizado."
        )

    except Exception as ex:

        logger.exception(
            f"PLUGIN SHUTDOWN ERROR {name}"
        )

        return erro(str(ex))


# ==================================================
# LOAD MODULE
# ==================================================

def load_plugin_module(

    plugin_name,

    module_path
):

    plugin = get_plugin(
        plugin_name
    )

    if not plugin:

        return erro(
            "Plugin inválido."
        )

    try:

        module = importlib.import_module(
            module_path
        )

        plugin.module = module

        plugin.loaded = True

        logger.info(

            (
                f"PLUGIN MODULE "
                f"{plugin_name}"
            )
        )

        increment_counter(
            "plugin_modules_loaded"
        )

        return ok(
            f"Módulo carregado."
        )

    except Exception as ex:

        logger.exception(
            "PLUGIN LOAD ERROR"
        )

        add_event(

            "plugin_error",

            plugin_name,

            {

                "error": str(ex),

                "traceback": (
                    traceback.format_exc()
                )
            }
        )

        return erro(str(ex))


# ==================================================
# RELOAD
# ==================================================

def reload_plugin(name):

    plugin = get_plugin(name)

    if not plugin:

        return erro(
            "Plugin inválido."
        )

    try:

        if plugin.module:

            importlib.reload(
                plugin.module
            )

        logger.info(
            f"PLUGIN RELOAD {name}"
        )

        increment_counter(
            "plugin_reloads"
        )

        return ok(
            f"Plugin {name} recarregado."
        )

    except Exception as ex:

        logger.exception(
            "PLUGIN RELOAD ERROR"
        )

        return erro(str(ex))


# ==================================================
# ROUTES
# ==================================================

def register_plugin_route(

    plugin_name,

    route
):

    plugin = get_plugin(
        plugin_name
    )

    if not plugin:

        return False

    plugin.routes.append(route)

    return True


# ==================================================
# JOBS
# ==================================================

def register_plugin_job(

    plugin_name,

    job
):

    plugin = get_plugin(
        plugin_name
    )

    if not plugin:

        return False

    plugin.jobs.append(job)

    return True


# ==================================================
# STATUS
# ==================================================

def get_plugin_status():

    return {

        "total": len(_PLUGINS),

        "enabled": len([

            p for p in _PLUGINS.values()

            if p.enabled
        ]),

        "loaded": len([

            p for p in _PLUGINS.values()

            if p.loaded
        ]),

        "plugins": [

            p.to_dict()

            for p in _PLUGINS.values()
        ]
    }


# ==================================================
# STARTUP ALL
# ==================================================

def startup_all_plugins():

    logger.info(
        "STARTUP ALL PLUGINS"
    )

    for plugin_name in list(
        _PLUGINS.keys()
    ):

        startup_plugin(
            plugin_name
        )


# ==================================================
# SHUTDOWN ALL
# ==================================================

def shutdown_all_plugins():

    logger.warning(
        "SHUTDOWN ALL PLUGINS"
    )

    for plugin_name in list(
        _PLUGINS.keys()
    ):

        shutdown_plugin(
            plugin_name
        )


# ==================================================
# DISCOVERY
# ==================================================

def discover_plugins():

    """
    Placeholder para futura
    descoberta automática.
    """

    logger.info(
        "PLUGIN DISCOVERY"
    )

    return []


# ==================================================
# STARTUP
# ==================================================

logger.info(
    "Plugin manager inicializado."
)
