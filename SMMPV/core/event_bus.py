
import threading
import traceback
from dataclasses import (
    dataclass,
    field
)
from datetime import datetime


from core.logger import get_logger

from core.telemetry import (

    increment_counter,

    add_event
)

from core.middleware import (
    handle_exception
)


# ==================================================
# LOGGER
# ==================================================

logger = get_logger("event_bus")


# ==================================================
# STORAGE
# ==================================================

_LOCK = threading.RLock()

_SUBSCRIBERS = {}

_EVENT_HISTORY = []


# ==================================================
# CONFIG
# ==================================================

MAX_EVENT_HISTORY = 1000


# ==================================================
# EVENT
# ==================================================

@dataclass
class Event:

    name: str

    payload: dict = field(
        default_factory=dict
    )

    source: str = "system"

    timestamp: str = field(

        default_factory=lambda:

        datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    )

    metadata: dict = field(
        default_factory=dict
    )

    # ==============================================
    # DICT
    # ==============================================

    def to_dict(self):

        return {

            "name": self.name,

            "payload": self.payload,

            "source": self.source,

            "timestamp": (
                self.timestamp
            ),

            "metadata": (
                self.metadata
            )
        }


# ==================================================
# HELPERS
# ==================================================

def normalize_event_name(name):

    if not name:

        return "UNKNOWN_EVENT"

    return (

        str(name)

        .strip()

        .upper()
    )


# ==================================================
# HISTORY
# ==================================================

def add_event_history(event):

    with _LOCK:

        _EVENT_HISTORY.append(
            event.to_dict()
        )

        if (

            len(_EVENT_HISTORY)

            > MAX_EVENT_HISTORY

        ):

            _EVENT_HISTORY.pop(0)


def get_event_history():

    with _LOCK:

        return list(
            _EVENT_HISTORY
        )


def clear_event_history():

    with _LOCK:

        total = len(
            _EVENT_HISTORY
        )

        _EVENT_HISTORY.clear()

    return total


# ==================================================
# SUBSCRIBE
# ==================================================

def subscribe_event(

    event_name,

    handler
):

    event_name = normalize_event_name(
        event_name
    )

    with _LOCK:

        if event_name not in _SUBSCRIBERS:

            _SUBSCRIBERS[event_name] = []

        _SUBSCRIBERS[event_name].append(
            handler
        )

    logger.info(

        (
            f"EVENT SUBSCRIBE "
            f"{event_name}"
        )
    )

    increment_counter(
        "event_subscriptions"
    )

    return True


# ==================================================
# UNSUBSCRIBE
# ==================================================

def unsubscribe_event(

    event_name,

    handler
):

    event_name = normalize_event_name(
        event_name
    )

    with _LOCK:

        handlers = _SUBSCRIBERS.get(
            event_name,
            []
        )

        if handler in handlers:

            handlers.remove(handler)

            return True

    return False


# ==================================================
# PUBLISH
# ==================================================

def publish_event(

    event_name,

    payload=None,

    source="system",

    metadata=None
):

    event_name = normalize_event_name(
        event_name
    )

    payload = payload or {}

    metadata = metadata or {}

    event = Event(

        name=event_name,

        payload=payload,

        source=source,

        metadata=metadata
    )

    logger.info(

        (
            f"EVENT PUBLISH "
            f"{event_name}"
        )
    )

    increment_counter(
        "events_published"
    )

    add_event(

        "event_bus",

        event_name,

        event.to_dict()
    )

    add_event_history(event)

    # ==============================================
    # HANDLERS
    # ==============================================

    with _LOCK:

        handlers = list(

            _SUBSCRIBERS.get(
                event_name,
                []
            )
        )

    for handler in handlers:

        try:

            handler(event)

        except Exception as ex:

            logger.exception(

                (
                    f"EVENT HANDLER ERROR "
                    f"{event_name}"
                )
            )

            handle_exception(

                ex,

                contexto=(
                    f"EVENT_{event_name}"
                )
            )

    return event


# ==================================================
# ASYNC PUBLISH
# ==================================================

def publish_event_async(

    event_name,

    payload=None,

    source="system",

    metadata=None
):

    thread = threading.Thread(

        target=publish_event,

        kwargs={

            "event_name": (
                event_name
            ),

            "payload": payload,

            "source": source,

            "metadata": metadata
        },

        daemon=True
    )

    thread.start()

    return True


# ==================================================
# EXISTS
# ==================================================

def has_subscribers(event_name):

    event_name = normalize_event_name(
        event_name
    )

    with _LOCK:

        return bool(

            _SUBSCRIBERS.get(
                event_name
            )
        )


# ==================================================
# EVENTS
# ==================================================

def get_registered_events():

    with _LOCK:

        return {

            k: len(v)

            for k, v in (
                _SUBSCRIBERS.items()
            )
        }


# ==================================================
# CLEAR
# ==================================================

def clear_subscribers():

    with _LOCK:

        total = len(
            _SUBSCRIBERS
        )

        _SUBSCRIBERS.clear()

    logger.warning(
        "EVENT SUBSCRIBERS CLEARED"
    )

    return total


# ==================================================
# BUILTIN EVENTS
# ==================================================

EVENT_USER_LOGIN = (
    "USER_LOGIN"
)

EVENT_USER_LOGOUT = (
    "USER_LOGOUT"
)

EVENT_NAVIGATION = (
    "NAVIGATION"
)

EVENT_ERROR = (
    "ERROR"
)

EVENT_CACHE_CLEANUP = (
    "CACHE_CLEANUP"
)

EVENT_DIAGNOSTICS = (
    "DIAGNOSTICS"
)

EVENT_PLUGIN_LOADED = (
    "PLUGIN_LOADED"
)

EVENT_JOB_EXECUTED = (
    "JOB_EXECUTED"
)


# ==================================================
# DEBUG
# ==================================================

def dump_event_bus():

    with _LOCK:

        return {

            "events": {

                k: [

                    str(x)

                    for x in v

                ]

                for k, v in (
                    _SUBSCRIBERS.items()
                )
            },

            "history": list(
                _EVENT_HISTORY
            )
        }


# ==================================================
# DEFAULT HANDLER
# ==================================================

def default_log_handler(event):

    logger.info(

        (
            f"EVENT RECEIVED "
            f"{event.name}"
        )
    )


# ==================================================
# STARTUP
# ==================================================

subscribe_event(

    EVENT_ERROR,

    default_log_handler
)

logger.info(
    "Event bus inicializado."
)
