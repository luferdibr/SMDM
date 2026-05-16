
import threading
import time
from collections import defaultdict
from dataclasses import (
    dataclass,
    field
)
from datetime import datetime


from core.logger import get_logger

from core.responses import (
    ok,
    erro
)

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

from core.governance_center import (
    enforce_quota
)

from core.observability_center import (

    record_metric,

    record_trace
)

from core.websocket_server import (
    broadcast_message
)

from core.tenant_manager import (
    get_current_tenant
)


# ==================================================
# LOGGER
# ==================================================

logger = get_logger(
    "distributed_event_stream"
)


# ==================================================
# STORAGE
# ==================================================

_LOCK = threading.RLock()

_STREAMS = defaultdict(list)

_CONSUMERS = defaultdict(list)

_STREAM_STATS = {

    "published": 0,

    "consumed": 0,

    "replayed": 0
}


# ==================================================
# CONFIG
# ==================================================

MAX_STREAM_EVENTS = 5000


# ==================================================
# HELPERS
# ==================================================

def now():

    return time.time()


def now_str():

    return datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )


def generate_event_id():

    return (

        f"STREAM_EVENT_"

        f"{int(now() * 1000)}"
    )


# ==================================================
# STREAM EVENT
# ==================================================

@dataclass
class StreamEvent:

    event_id: str

    channel: str

    event_type: str

    payload: dict

    tenant_id: str

    created_at: str = field(

        default_factory=lambda:

        now_str()
    )

    metadata: dict = field(
        default_factory=dict
    )

    # ==============================================
    # DICT
    # ==============================================

    def to_dict(self):

        return {

            "event_id": (
                self.event_id
            ),

            "channel": self.channel,

            "event_type": (
                self.event_type
            ),

            "payload": self.payload,

            "tenant_id": (
                self.tenant_id
            ),

            "created_at": (
                self.created_at
            ),

            "metadata": (
                self.metadata
            )
        }


# ==================================================
# PUBLISH
# ==================================================

def publish_stream_event(

    channel,

    event_type,

    payload,

    tenant_id=None,

    metadata=None
):

    try:

        if not enforce_quota(
            "event_stream"
        ):

            return erro(
                "Quota excedida."
            )

        event = StreamEvent(

            event_id=(
                generate_event_id()
            ),

            channel=channel,

            event_type=event_type,

            payload=payload,

            tenant_id=(

                tenant_id

                or

                get_current_tenant()
            ),

            metadata=metadata or {}
        )

        with _LOCK:

            _STREAMS[
                channel
            ].append(event)

            if (

                len(
                    _STREAMS[channel]
                )

                > MAX_STREAM_EVENTS
            ):

                _STREAMS[
                    channel
                ].pop(0)

            _STREAM_STATS[
                "published"
            ] += 1

        logger.info(

            (
                f"STREAM EVENT "
                f"{channel}"
            )
        )

        increment_counter(
            "stream_publish"
        )

        record_metric(
            "stream_publish"
        )

        record_trace(

            operation=(
                "publish_stream"
            ),

            source=(
                "distributed_event_stream"
            ),

            status="OK"
        )

        add_event(

            "stream",

            event_type,

            event.to_dict()
        )

        publish_event(

            "STREAM_EVENT_PUBLISHED",

            event.to_dict(),

            source=(
                "distributed_event_stream"
            )
        )

        try:

            broadcast_message(

                channel,

                event.to_dict()
            )

        except Exception:

            pass

        return ok(

            mensagem=(
                "Evento publicado."
            ),

            dados=event.to_dict()
        )

    except Exception as ex:

        handle_exception(

            ex,

            contexto=(
                "STREAM_PUBLISH"
            )
        )

        return erro(str(ex))


# ==================================================
# CONSUMER
# ==================================================

def register_consumer(

    channel,

    consumer_name
):

    with _LOCK:

        if (

            consumer_name

            not in

            _CONSUMERS[channel]
        ):

            _CONSUMERS[
                channel
            ].append(
                consumer_name
            )

    logger.info(

        (
            f"STREAM CONSUMER "
            f"{consumer_name}"
        )
    )

    publish_event(

        "STREAM_CONSUMER_REGISTERED",

        {

            "channel": channel,

            "consumer": (
                consumer_name
            )
        },

        source=(
            "distributed_event_stream"
        )
    )

    return True


# ==================================================
# CONSUME
# ==================================================

def consume_stream(

    channel,

    limit=100
):

    events = _STREAMS.get(
        channel,
        []
    )

    result = [

        x.to_dict()

        for x in (
            events[-limit:]
        )
    ]

    _STREAM_STATS[
        "consumed"
    ] += len(result)

    record_metric(
        "stream_consume"
    )

    return result


# ==================================================
# REPLAY
# ==================================================

def replay_stream(

    channel,

    limit=100
):

    events = consume_stream(

        channel,

        limit=limit
    )

    _STREAM_STATS[
        "replayed"
    ] += len(events)

    logger.warning(

        (
            f"STREAM REPLAY "
            f"{channel}"
        )
    )

    publish_event(

        "STREAM_REPLAY",

        {

            "channel": channel,

            "events": len(events)
        },

        source=(
            "distributed_event_stream"
        )
    )

    return events


# ==================================================
# CLEAR
# ==================================================

def clear_stream(channel):

    with _LOCK:

        removed = len(

            _STREAMS.get(
                channel,
                []
            )
        )

        _STREAMS[channel] = []

    logger.warning(

        (
            f"STREAM CLEAR "
            f"{channel}"
        )
    )

    publish_event(

        "STREAM_CLEARED",

        {

            "channel": channel,

            "removed": removed
        },

        source=(
            "distributed_event_stream"
        )
    )

    return removed


# ==================================================
# STATUS
# ==================================================

def get_stream_status():

    return {

        "channels": len(
            _STREAMS
        ),

        "consumers": sum(

            len(v)

            for v in (
                _CONSUMERS.values()
            )
        ),

        "published": (

            _STREAM_STATS[
                "published"
            ]
        ),

        "consumed": (

            _STREAM_STATS[
                "consumed"
            ]
        ),

        "replayed": (

            _STREAM_STATS[
                "replayed"
            ]
        )
    }


# ==================================================
# EXPORT
# ==================================================

def dump_streams():

    return {

        channel: [

            x.to_dict()

            for x in events
        ]

        for channel, events in (
            _STREAMS.items()
        )
    }


def dump_consumers():

    return dict(_CONSUMERS)


# ==================================================
# STARTUP
# ==================================================

logger.info(
    "Distributed event stream inicializado."
)
