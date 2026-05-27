
import time
from threading import RLock
from contextlib import contextmanager


from core.logger import get_logger


# ==================================================
# LOGGER
# ==================================================

logger = get_logger("telemetry")


# ==================================================
# STORAGE
# ==================================================

_LOCK = RLock()

_COUNTERS = {}

_TIMERS = {}

_EVENTS = []


# ==================================================
# CONFIG
# ==================================================

MAX_EVENTS = 1000

SLOW_OPERATION_SECONDS = 1.5


# ==================================================
# TIME
# ==================================================

def now():

    return time.time()


# ==================================================
# COUNTERS
# ==================================================

def increment_counter(

    name,

    value=1
):

    name = str(name).lower()

    with _LOCK:

        _COUNTERS[name] = (

            _COUNTERS.get(name, 0)

            + value
        )

    return _COUNTERS[name]


def decrement_counter(

    name,

    value=1
):

    return increment_counter(
        name,
        -value
    )


def get_counter(

    name,

    default=0
):

    name = str(name).lower()

    with _LOCK:

        return _COUNTERS.get(
            name,
            default
        )


def reset_counter(name):

    name = str(name).lower()

    with _LOCK:

        _COUNTERS[name] = 0

    return 0


# ==================================================
# EVENTS
# ==================================================

def add_event(

    category,

    message,

    data=None
):

    evento = {

        "timestamp": now(),

        "category": str(category),

        "message": str(message),

        "data": data
    }

    with _LOCK:

        _EVENTS.append(evento)

        if len(_EVENTS) > MAX_EVENTS:

            _EVENTS.pop(0)

    return evento


def get_events():

    with _LOCK:

        return list(_EVENTS)


def clear_events():

    with _LOCK:

        total = len(_EVENTS)

        _EVENTS.clear()

    return total


# ==================================================
# TIMERS
# ==================================================

def start_timer(name):

    name = str(name).lower()

    with _LOCK:

        _TIMERS[name] = now()

    return _TIMERS[name]


def stop_timer(name):

    name = str(name).lower()

    with _LOCK:

        inicio = _TIMERS.get(name)

        if not inicio:

            return None

        duracao = now() - inicio

        del _TIMERS[name]

    # ==============================================
    # METRICS
    # ==============================================

    increment_counter(
        f"{name}_executions"
    )

    add_event(

        "timer",

        f"{name} finalizado",

        {

            "duration": duracao
        }
    )

    # ==============================================
    # SLOW
    # ==============================================

    if duracao >= SLOW_OPERATION_SECONDS:

        logger.warning(

            (
                f"SLOW OPERATION "
                f"{name} "
                f"{duracao:.4f}s"
            )
        )

    return duracao


# ==================================================
# TRACK EXECUTION
# ==================================================

@contextmanager
def track_execution_time(name):

    start_timer(name)

    try:

        yield

    finally:

        stop_timer(name)


# ==================================================
# DECORATOR
# ==================================================

def telemetry_timer(name=None):

    def decorator(func):

        timer_name = (

            name

            or

            func.__name__
        )

        def wrapper(*args, **kwargs):

            with track_execution_time(
                timer_name
            ):

                return func(
                    *args,
                    **kwargs
                )

        return wrapper

    return decorator


# ==================================================
# METRICS
# ==================================================

def register_login():

    increment_counter(
        "login_success"
    )


def register_login_failure():

    increment_counter(
        "login_failure"
    )


def register_navigation(route):

    increment_counter(
        f"route_{route}"
    )


def register_exception():

    increment_counter(
        "exceptions"
    )


def register_database_query():

    increment_counter(
        "database_queries"
    )


def register_cache_hit():

    increment_counter(
        "cache_hit"
    )


def register_cache_miss():

    increment_counter(
        "cache_miss"
    )


# ==================================================
# SNAPSHOT
# ==================================================

def get_health_snapshot():

    with _LOCK:

        return {

            "timestamp": now(),

            "counters": dict(
                _COUNTERS
            ),

            "active_timers": list(
                _TIMERS.keys()
            ),

            "events": len(_EVENTS)
        }


# ==================================================
# DEBUG
# ==================================================

def dump_telemetry():

    with _LOCK:

        return {

            "counters": dict(
                _COUNTERS
            ),

            "timers": dict(
                _TIMERS
            ),

            "events": list(
                _EVENTS
            )
        }


# ==================================================
# RESET
# ==================================================

def reset_telemetry():

    with _LOCK:

        _COUNTERS.clear()

        _TIMERS.clear()

        _EVENTS.clear()

    logger.warning(
        "Telemetry reset."
    )


# ==================================================
# PERFORMANCE
# ==================================================

def track_database_query(

    query_name,

    duration
):

    increment_counter(
        "database_queries"
    )

    add_event(

        "database",

        query_name,

        {

            "duration": duration
        }
    )

    if duration >= SLOW_OPERATION_SECONDS:

        logger.warning(

            (
                f"SLOW QUERY "
                f"{query_name} "
                f"{duration:.4f}s"
            )
        )


def track_ui_render(

    screen,

    duration
):

    add_event(

        "ui",

        screen,

        {

            "duration": duration
        }
    )

    if duration >= SLOW_OPERATION_SECONDS:

        logger.warning(

            (
                f"SLOW UI "
                f"{screen} "
                f"{duration:.4f}s"
            )
        )


# ==================================================
# STARTUP
# ==================================================

logger.info(
    "Telemetry manager inicializado."
)

increment_counter(
    "telemetry_startups"
)
