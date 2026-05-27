
import json
import threading
from http.server import (
    BaseHTTPRequestHandler,
    HTTPServer
)
from urllib.parse import (
    urlparse,
    parse_qs
)


from core.logger import get_logger

from core.responses import (
    ok,
    erro
)

from core.middleware import (
    handle_exception
)

from core.telemetry import (
    increment_counter
)

from core.diagnostics import (

    get_status,

    get_system_health,

    export_diagnostics_json
)

from core.event_bus import (
    publish_event
)

from core.plugin_manager import (
    get_plugin_status
)


# ==================================================
# LOGGER
# ==================================================

logger = get_logger("api_server")


# ==================================================
# CONFIG
# ==================================================

API_HOST = "127.0.0.1"

API_PORT = 8080


# ==================================================
# STORAGE
# ==================================================

_SERVER = None

_SERVER_THREAD = None

_RUNNING = False

_ROUTES = {}


# ==================================================
# HELPERS
# ==================================================

def json_response(

    handler,

    data,

    status=200
):

    payload = json.dumps(

        data,

        ensure_ascii=False,

        default=str
    ).encode("utf-8")

    handler.send_response(status)

    handler.send_header(

        "Content-Type",

        "application/json; charset=utf-8"
    )

    handler.send_header(

        "Content-Length",

        str(len(payload))
    )

    handler.end_headers()

    handler.wfile.write(payload)


def register_api_route(

    method,

    path,

    callback
):

    key = (

        method.upper(),

        path
    )

    _ROUTES[key] = callback

    logger.info(

        (
            f"API ROUTE "
            f"{method.upper()} "
            f"{path}"
        )
    )


# ==================================================
# HANDLER
# ==================================================

class SMDMRequestHandler(
    BaseHTTPRequestHandler
):

    # ==============================================
    # GET
    # ==============================================

    def do_GET(self):

        self.handle_request("GET")

    # ==============================================
    # POST
    # ==============================================

    def do_POST(self):

        self.handle_request("POST")

    # ==============================================
    # REQUEST
    # ==============================================

    def handle_request(

        self,

        method
    ):

        try:

            increment_counter(
                "api_requests"
            )

            parsed = urlparse(
                self.path
            )

            path = parsed.path

            query = parse_qs(
                parsed.query
            )

            key = (
                method.upper(),
                path
            )

            callback = _ROUTES.get(key)

            if not callback:

                return json_response(

                    self,

                    erro(
                        "Endpoint não encontrado."
                    ),

                    status=404
                )

            body = {}

            if method == "POST":

                content_length = int(

                    self.headers.get(
                        "Content-Length",
                        0
                    )
                )

                if content_length > 0:

                    raw = self.rfile.read(
                        content_length
                    )

                    body = json.loads(
                        raw.decode("utf-8")
                    )

            response = callback({

                "path": path,

                "query": query,

                "body": body,

                "headers": dict(
                    self.headers
                )
            })

            publish_event(

                "API_REQUEST",

                {

                    "method": method,

                    "path": path
                },

                source="api_server"
            )

            return json_response(

                self,

                response
            )

        except Exception as ex:

            handle_exception(

                ex,

                contexto="API_SERVER"
            )

            return json_response(

                self,

                erro(str(ex)),

                status=500
            )

    # ==============================================
    # LOG
    # ==============================================

    def log_message(

        self,

        format,

        *args
    ):

        logger.info(
            format % args
        )


# ==================================================
# ENDPOINTS
# ==================================================

def health_endpoint(request):

    return ok(

        mensagem="API ONLINE",

        dados=get_status()
    )


def diagnostics_endpoint(request):

    return ok(

        mensagem="Diagnostics",

        dados=get_system_health()
    )


def plugins_endpoint(request):

    return ok(

        mensagem="Plugins",

        dados=get_plugin_status()
    )


def telemetry_endpoint(request):

    from core.telemetry import (
        dump_telemetry
    )

    return ok(

        mensagem="Telemetry",

        dados=dump_telemetry()
    )


def diagnostics_export_endpoint(
    request
):

    return {

        "success": True,

        "diagnostics": (
            export_diagnostics_json()
        )
    }


# ==================================================
# REGISTER DEFAULTS
# ==================================================

def register_default_routes():

    register_api_route(

        "GET",

        "/health",

        health_endpoint
    )

    register_api_route(

        "GET",

        "/ready",

        health_endpoint
    )

    register_api_route(

        "GET",

        "/diagnostics",

        diagnostics_endpoint
    )

    register_api_route(

        "GET",

        "/plugins",

        plugins_endpoint
    )

    register_api_route(

        "GET",

        "/telemetry",

        telemetry_endpoint
    )

    register_api_route(

        "GET",

        "/diagnostics/export",

        diagnostics_export_endpoint
    )


# ==================================================
# SERVER
# ==================================================

def start_api_server(

    host=API_HOST,

    port=API_PORT
):

    global _SERVER
    global _SERVER_THREAD
    global _RUNNING

    if _RUNNING:

        return False

    try:

        register_default_routes()

        _SERVER = HTTPServer(

            (host, port),

            SMDMRequestHandler
        )

        _SERVER_THREAD = threading.Thread(

            target=_SERVER.serve_forever,

            daemon=True
        )

        _SERVER_THREAD.start()

        _RUNNING = True

        logger.info(

            (
                f"API SERVER "
                f"http://{host}:{port}"
            )
        )

        increment_counter(
            "api_server_starts"
        )

        publish_event(

            "API_SERVER_STARTED",

            {

                "host": host,

                "port": port
            },

            source="api_server"
        )

        return True

    except Exception as ex:

        handle_exception(

            ex,

            contexto="API_START"
        )

        return False


# ==================================================
# STOP
# ==================================================

def stop_api_server():

    global _SERVER
    global _RUNNING

    try:

        if _SERVER:

            _SERVER.shutdown()

            _SERVER.server_close()

        _RUNNING = False

        logger.warning(
            "API SERVER STOPPED"
        )

        publish_event(

            "API_SERVER_STOPPED",

            source="api_server"
        )

        return True

    except Exception as ex:

        handle_exception(

            ex,

            contexto="API_STOP"
        )

        return False


# ==================================================
# STATUS
# ==================================================

def is_api_running():

    return _RUNNING


def get_api_routes():

    return [

        {

            "method": k[0],

            "path": k[1]
        }

        for k in _ROUTES.keys()
    ]


# ==================================================
# STARTUP
# ==================================================

logger.info(
    "API server manager inicializado."
)
