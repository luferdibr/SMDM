
import threading
import time
from datetime import datetime


from core.logger import get_logger

from core.telemetry import (

    increment_counter,

    add_event
)

from core.event_bus import (
    publish_event
)

from core.middleware import (
    handle_exception
)

from core.scheduler import (
    start_scheduler,
    stop_scheduler,
    is_scheduler_running
)

from core.background_jobs import (
    register_system_jobs
)

from core.plugin_manager import (
    startup_all_plugins,
    shutdown_all_plugins
)

from core.api_server import (

    start_api_server,

    stop_api_server,

    is_api_running
)

from core.websocket_server import (

    start_websocket_server,

    stop_websocket_server,

    is_websocket_running
)

from core.distributed_workers import (

    start_workers,

    stop_workers
)

from core.cloud_sync import (

    start_cloud_sync,

    stop_cloud_sync
)

from core.diagnostics import (
    get_status
)


# ==================================================
# LOGGER
# ==================================================

logger = get_logger(
    "orchestrator"
)


# ==================================================
# STORAGE
# ==================================================

_RUNNING = False

_START_TIME = None

_LOCK = threading.RLock()


# ==================================================
# HELPERS
# ==================================================

def now():

    return time.time()


def now_str():

    return datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )


# ==================================================
# COMPONENTS
# ==================================================

def initialize_scheduler():

    logger.info(
        "Inicializando scheduler."
    )

    register_system_jobs()

    return start_scheduler()


def initialize_plugins():

    logger.info(
        "Inicializando plugins."
    )

    startup_all_plugins()

    return True


def initialize_api():

    logger.info(
        "Inicializando API."
    )

    return start_api_server()


def initialize_websocket():

    logger.info(
        "Inicializando websocket."
    )

    return start_websocket_server()


def initialize_workers():

    logger.info(
        "Inicializando workers."
    )

    return start_workers()


def initialize_cloud_sync():

    logger.info(
        "Inicializando cloud sync."
    )

    return start_cloud_sync()


# ==================================================
# START
# ==================================================

def start_platform():

    global _RUNNING
    global _START_TIME

    with _LOCK:

        if _RUNNING:

            logger.warning(
                "Plataforma já iniciada."
            )

            return False

        started = now()

        try:

            logger.info(
                "START PLATFORM"
            )

            publish_event(

                "PLATFORM_STARTING",

                source="orchestrator"
            )

            # ======================================
            # SCHEDULER
            # ======================================

            initialize_scheduler()

            # ======================================
            # PLUGINS
            # ======================================

            initialize_plugins()

            # ======================================
            # API
            # ======================================

            initialize_api()

            # ======================================
            # WEBSOCKET
            # ======================================

            initialize_websocket()

            # ======================================
            # WORKERS
            # ======================================

            initialize_workers()

            # ======================================
            # CLOUD SYNC
            # ======================================

            initialize_cloud_sync()

            # ======================================
            # STATUS
            # ======================================

            _RUNNING = True

            _START_TIME = now()

            duration = now() - started

            logger.info(

                (
                    f"PLATFORM STARTED "
                    f"{duration:.4f}s"
                )
            )

            increment_counter(
                "platform_starts"
            )

            add_event(

                "orchestrator",

                "platform_started",

                {

                    "duration": duration
                }
            )

            publish_event(

                "PLATFORM_STARTED",

                {

                    "duration": duration
                },

                source="orchestrator"
            )

            return True

        except Exception as ex:

            handle_exception(

                ex,

                contexto=(
                    "PLATFORM_START"
                )
            )

            _RUNNING = False

            return False


# ==================================================
# STOP
# ==================================================

def stop_platform():

    global _RUNNING

    with _LOCK:

        if not _RUNNING:

            return False

        try:

            logger.warning(
                "STOP PLATFORM"
            )

            publish_event(

                "PLATFORM_STOPPING",

                source="orchestrator"
            )

            # ======================================
            # CLOUD
            # ======================================

            stop_cloud_sync()

            # ======================================
            # WORKERS
            # ======================================

            stop_workers()

            # ======================================
            # WEBSOCKET
            # ======================================

            stop_websocket_server()

            # ======================================
            # API
            # ======================================

            stop_api_server()

            # ======================================
            # PLUGINS
            # ======================================

            shutdown_all_plugins()

            # ======================================
            # SCHEDULER
            # ======================================

            stop_scheduler()

            _RUNNING = False

            logger.warning(
                "PLATFORM STOPPED"
            )

            increment_counter(
                "platform_stops"
            )

            publish_event(

                "PLATFORM_STOPPED",

                source="orchestrator"
            )

            return True

        except Exception as ex:

            handle_exception(

                ex,

                contexto=(
                    "PLATFORM_STOP"
                )
            )

            return False


# ==================================================
# STATUS
# ==================================================

def is_platform_running():

    return _RUNNING


def get_platform_status():

    uptime = 0

    if _START_TIME:

        uptime = int(
            now() - _START_TIME
        )

    return {

        "running": _RUNNING,

        "started_at": _START_TIME,

        "uptime_seconds": uptime,

        "scheduler": (
            is_scheduler_running()
        ),

        "api": (
            is_api_running()
        ),

        "websocket": (
            is_websocket_running()
        ),

        "timestamp": now_str()
    }


# ==================================================
# HEALTH
# ==================================================

def get_platform_health():

    return {

        "status": (

            "UP"

            if _RUNNING

            else

            "DOWN"
        ),

        "platform": (
            get_platform_status()
        ),

        "diagnostics": (
            get_status()
        )
    }


# ==================================================
# WAIT
# ==================================================

def wait_forever():

    logger.info(
        "WAIT FOREVER"
    )

    try:

        while _RUNNING:

            time.sleep(1)

    except KeyboardInterrupt:

        logger.warning(
            "Keyboard interrupt."
        )

        stop_platform()


# ==================================================
# RESTART
# ==================================================

def restart_platform():

    logger.warning(
        "RESTART PLATFORM"
    )

    stop_platform()

    time.sleep(2)

    return start_platform()


# ==================================================
# BOOTSTRAP
# ==================================================

def bootstrap_platform():

    logger.info(
        "BOOTSTRAP PLATFORM"
    )

    ok = start_platform()

    if not ok:

        return False

    wait_forever()

    return True


# ==================================================
# STARTUP
# ==================================================

logger.info(
    "Orchestrator inicializado."
)
