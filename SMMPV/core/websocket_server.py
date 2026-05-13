
import asyncio
import json
import threading
from datetime import datetime


from core.logger import get_logger

from core.telemetry import (

    increment_counter,

    add_event
)

from core.event_bus import (

    subscribe_event,

    publish_event
)

from core.middleware import (
    handle_exception
)


# ==================================================
# LOGGER
# ==================================================

logger = get_logger(
    "websocket_server"
)


# ==================================================
# OPTIONAL IMPORT
# ==================================================

try:

    import websockets

    WEBSOCKET_AVAILABLE = True

except Exception:

    WEBSOCKET_AVAILABLE = False


# ==================================================
# CONFIG
# ==================================================

WS_HOST = "127.0.0.1"

WS_PORT = 8765

HEARTBEAT_INTERVAL = 30


# ==================================================
# STORAGE
# ==================================================

_CLIENTS = set()

_SERVER = None

_LOOP = None

_RUNNING = False


# ==================================================
# HELPERS
# ==================================================

def now_str():

    return datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )


# ==================================================
# CLIENTS
# ==================================================

async def register_client(ws):

    _CLIENTS.add(ws)

    logger.info(
        f"WS CLIENT CONNECTED"
    )

    increment_counter(
        "ws_clients_connected"
    )

    add_event(

        "websocket",

        "client_connected",

        {

            "clients": len(_CLIENTS)
        }
    )


async def unregister_client(ws):

    if ws in _CLIENTS:

        _CLIENTS.remove(ws)

    logger.warning(
        f"WS CLIENT DISCONNECTED"
    )

    increment_counter(
        "ws_clients_disconnected"
    )

    add_event(

        "websocket",

        "client_disconnected",

        {

            "clients": len(_CLIENTS)
        }
    )


# ==================================================
# SEND
# ==================================================

async def send_message(

    ws,

    event,

    payload
):

    try:

        message = {

            "event": event,

            "payload": payload,

            "timestamp": now_str()
        }

        await ws.send(

            json.dumps(

                message,

                ensure_ascii=False,

                default=str
            )
        )

        increment_counter(
            "ws_messages_sent"
        )

        return True

    except Exception as ex:

        handle_exception(

            ex,

            contexto="WS_SEND"
        )

        return False


# ==================================================
# BROADCAST
# ==================================================

async def broadcast_message(

    event,

    payload
):

    if not _CLIENTS:

        return 0

    disconnected = []

    total = 0

    for ws in list(_CLIENTS):

        try:

            ok = await send_message(

                ws,

                event,

                payload
            )

            if ok:

                total += 1

        except Exception:

            disconnected.append(ws)

    for ws in disconnected:

        try:

            await unregister_client(
                ws
            )

        except Exception:
            pass

    logger.info(

        (
            f"WS BROADCAST "
            f"{event} "
            f"clients={total}"
        )
    )

    increment_counter(
        "ws_broadcasts"
    )

    return total


# ==================================================
# EVENT BUS
# ==================================================

def websocket_event_handler(event):

    try:

        if not _RUNNING:
            return

        if not _LOOP:
            return

        asyncio.run_coroutine_threadsafe(

            broadcast_message(

                event.name,

                event.to_dict()
            ),

            _LOOP
        )

    except Exception as ex:

        handle_exception(

            ex,

            contexto="WS_EVENT_HANDLER"
        )


# ==================================================
# HEARTBEAT
# ==================================================

async def heartbeat_loop():

    while _RUNNING:

        try:

            await broadcast_message(

                "HEARTBEAT",

                {

                    "status": "alive",

                    "clients": len(
                        _CLIENTS
                    )
                }
            )

            await asyncio.sleep(
                HEARTBEAT_INTERVAL
            )

        except Exception as ex:

            handle_exception(

                ex,

                contexto="WS_HEARTBEAT"
            )


# ==================================================
# CLIENT HANDLER
# ==================================================

async def client_handler(ws):

    await register_client(ws)

    try:

        async for message in ws:

            increment_counter(
                "ws_messages_received"
            )

            add_event(

                "websocket",

                "message_received",

                {

                    "message": message
                }
            )

            try:

                data = json.loads(
                    message
                )

            except Exception:

                data = {

                    "raw": message
                }

            publish_event(

                "WS_MESSAGE",

                data,

                source="websocket"
            )

            await send_message(

                ws,

                "ACK",

                {

                    "received": True
                }
            )

    except Exception as ex:

        handle_exception(

            ex,

            contexto="WS_CLIENT"
        )

    finally:

        await unregister_client(ws)


# ==================================================
# SERVER
# ==================================================

async def websocket_server_loop():

    global _SERVER

    _SERVER = await websockets.serve(

        client_handler,

        WS_HOST,

        WS_PORT
    )

    logger.info(

        (
            f"WEBSOCKET SERVER "
            f"ws://{WS_HOST}:{WS_PORT}"
        )
    )

    increment_counter(
        "ws_server_starts"
    )

    publish_event(

        "WS_SERVER_STARTED",

        {

            "host": WS_HOST,

            "port": WS_PORT
        },

        source="websocket"
    )

    asyncio.create_task(
        heartbeat_loop()
    )

    await _SERVER.wait_closed()


# ==================================================
# THREAD
# ==================================================

def websocket_thread():

    global _LOOP

    try:

        _LOOP = asyncio.new_event_loop()

        asyncio.set_event_loop(
            _LOOP
        )

        _LOOP.run_until_complete(

            websocket_server_loop()
        )

    except Exception as ex:

        handle_exception(

            ex,

            contexto="WS_THREAD"
        )


# ==================================================
# START
# ==================================================

def start_websocket_server():

    global _RUNNING

    if not WEBSOCKET_AVAILABLE:

        logger.warning(
            "websockets não instalado."
        )

        return False

    if _RUNNING:

        return False

    _RUNNING = True

    subscribe_event(

        "USER_LOGIN",

        websocket_event_handler
    )

    subscribe_event(

        "USER_LOGOUT",

        websocket_event_handler
    )

    subscribe_event(

        "ERROR",

        websocket_event_handler
    )

    subscribe_event(

        "DIAGNOSTICS",

        websocket_event_handler
    )

    subscribe_event(

        "JOB_EXECUTED",

        websocket_event_handler
    )

    threading.Thread(

        target=websocket_thread,

        daemon=True
    ).start()

    logger.info(
        "WebSocket iniciado."
    )

    return True


# ==================================================
# STOP
# ==================================================

def stop_websocket_server():

    global _RUNNING

    _RUNNING = False

    logger.warning(
        "WebSocket finalizado."
    )

    publish_event(

        "WS_SERVER_STOPPED",

        source="websocket"
    )

    return True


# ==================================================
# STATUS
# ==================================================

def is_websocket_running():

    return _RUNNING


def get_websocket_status():

    return {

        "running": _RUNNING,

        "clients": len(_CLIENTS),

        "host": WS_HOST,

        "port": WS_PORT,

        "available": (
            WEBSOCKET_AVAILABLE
        )
    }


# ==================================================
# DEBUG
# ==================================================

def dump_websocket_state():

    return {

        "running": _RUNNING,

        "clients": len(_CLIENTS),

        "available": (
            WEBSOCKET_AVAILABLE
        ),

        "host": WS_HOST,

        "port": WS_PORT
    }


# ==================================================
# STARTUP
# ==================================================

logger.info(
    "WebSocket manager inicializado."
)
