
import gc
import json
import os
import platform
import socket
import sys
import time
from datetime import datetime


from core.logger import get_logger

from core.cache import (
    get_stats as get_cache_stats
)

from core.scheduler import (
    get_scheduler_status,
    is_scheduler_running
)

from core.telemetry import (
    get_health_snapshot
)

from core.config_manager import (
    dump_config
)


# ==================================================
# LOGGER
# ==================================================

logger = get_logger("diagnostics")


# ==================================================
# STARTUP
# ==================================================

START_TIME = time.time()


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
# UPTIME
# ==================================================

def get_uptime_seconds():

    return int(
        now() - START_TIME
    )


def get_uptime_human():

    segundos = get_uptime_seconds()

    dias = segundos // 86400

    segundos %= 86400

    horas = segundos // 3600

    segundos %= 3600

    minutos = segundos // 60

    segundos %= 60

    return (

        f"{dias}d "

        f"{horas}h "

        f"{minutos}m "

        f"{segundos}s"
    )


# ==================================================
# SYSTEM
# ==================================================

def get_system_info():

    return {

        "platform": platform.platform(),

        "python_version": (
            sys.version
        ),

        "hostname": socket.gethostname(),

        "process_id": os.getpid(),

        "cwd": os.getcwd(),

        "timestamp": now_str()
    }


# ==================================================
# MEMORY
# ==================================================

def get_memory_info():

    return {

        "gc_objects": len(
            gc.get_objects()
        ),

        "gc_threshold": gc.get_threshold(),

        "gc_counts": gc.get_count()
    }


# ==================================================
# CACHE
# ==================================================

def get_cache_health():

    stats = get_cache_stats()

    hits = stats.get("hits", 0)

    misses = stats.get("misses", 0)

    total = hits + misses

    hit_ratio = 0

    if total > 0:

        hit_ratio = round(
            (hits / total) * 100,
            2
        )

    return {

        "stats": stats,

        "hit_ratio": hit_ratio
    }


# ==================================================
# TELEMETRY
# ==================================================

def get_telemetry_health():

    return get_health_snapshot()


# ==================================================
# SCHEDULER
# ==================================================

def get_scheduler_health():

    return {

        "running": (
            is_scheduler_running()
        ),

        "status": (
            get_scheduler_status()
        )
    }


# ==================================================
# CONFIG
# ==================================================

def get_config_health():

    return dump_config()


# ==================================================
# APP HEALTH
# ==================================================

def get_app_health():

    return {

        "status": "UP",

        "uptime_seconds": (
            get_uptime_seconds()
        ),

        "uptime_human": (
            get_uptime_human()
        ),

        "startup": (
            datetime.fromtimestamp(
                START_TIME
            ).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        )
    }


# ==================================================
# HEALTH
# ==================================================

def get_system_health():

    return {

        "app": get_app_health(),

        "system": (
            get_system_info()
        ),

        "memory": (
            get_memory_info()
        ),

        "cache": (
            get_cache_health()
        ),

        "telemetry": (
            get_telemetry_health()
        ),

        "scheduler": (
            get_scheduler_health()
        ),

        "config": (
            get_config_health()
        )
    }


# ==================================================
# REPORT
# ==================================================

def build_diagnostics_report():

    health = get_system_health()

    report = {

        "generated_at": now_str(),

        "health": health
    }

    logger.info(
        "Diagnostics report gerado."
    )

    return report


# ==================================================
# JSON
# ==================================================

def export_diagnostics_json():

    return json.dumps(

        build_diagnostics_report(),

        indent=4,

        ensure_ascii=False,

        default=str
    )


# ==================================================
# TXT
# ==================================================

def export_diagnostics_text():

    health = build_diagnostics_report()

    linhas = []

    linhas.append(
        "=" * 60
    )

    linhas.append(
        "SMMPV DIAGNOSTICS"
    )

    linhas.append(
        "=" * 60
    )

    linhas.append(
        f"Gerado em: {now_str()}"
    )

    linhas.append("")

    # ==============================================
    # APP
    # ==============================================

    app = health["health"]["app"]

    linhas.append(
        "[APP]"
    )

    linhas.append(
        f"Status: {app['status']}"
    )

    linhas.append(
        f"Uptime: "
        f"{app['uptime_human']}"
    )

    linhas.append("")

    # ==============================================
    # SYSTEM
    # ==============================================

    system = health["health"]["system"]

    linhas.append(
        "[SYSTEM]"
    )

    linhas.append(
        f"Host: "
        f"{system['hostname']}"
    )

    linhas.append(
        f"Platform: "
        f"{system['platform']}"
    )

    linhas.append("")

    # ==============================================
    # CACHE
    # ==============================================

    cache = health["health"]["cache"]

    linhas.append(
        "[CACHE]"
    )

    linhas.append(
        f"Hit Ratio: "
        f"{cache['hit_ratio']}%"
    )

    linhas.append("")

    # ==============================================
    # SCHEDULER
    # ==============================================

    scheduler = (
        health["health"]["scheduler"]
    )

    linhas.append(
        "[SCHEDULER]"
    )

    linhas.append(
        f"Running: "
        f"{scheduler['running']}"
    )

    linhas.append("")

    return "\n".join(linhas)


# ==================================================
# READY
# ==================================================

def is_ready():

    try:

        scheduler = (
            get_scheduler_health()
        )

        if not scheduler["running"]:

            return False

        return True

    except Exception:

        logger.exception(
            "READINESS ERROR"
        )

        return False


# ==================================================
# LIVENESS
# ==================================================

def is_alive():

    return True


# ==================================================
# STATUS
# ==================================================

def get_status():

    return {

        "alive": is_alive(),

        "ready": is_ready(),

        "uptime": (
            get_uptime_human()
        ),

        "timestamp": now_str()
    }


# ==================================================
# STARTUP
# ==================================================

logger.info(
    "Diagnostics manager inicializado."
)
