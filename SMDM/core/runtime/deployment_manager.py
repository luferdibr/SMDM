
import threading
import time
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

from core.orchestrator import (

    start_platform,

    stop_platform,

    restart_platform,

    get_platform_health
)


# ==================================================
# LOGGER
# ==================================================

logger = get_logger(
    "deployment_manager"
)


# ==================================================
# STORAGE
# ==================================================

_LOCK = threading.RLock()

_ENVIRONMENTS = {}

_DEPLOYMENTS = []


# ==================================================
# CONFIG
# ==================================================

STATUS_CREATED = "CREATED"

STATUS_DEPLOYING = "DEPLOYING"

STATUS_RUNNING = "RUNNING"

STATUS_FAILED = "FAILED"

STATUS_STOPPED = "STOPPED"

STATUS_ROLLBACK = "ROLLBACK"


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
# ENVIRONMENT
# ==================================================

@dataclass
class DeploymentEnvironment:

    environment_id: str

    nome: str

    host: str = "localhost"

    port: int = 8000

    status: str = STATUS_CREATED

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

            "environment_id": (
                self.environment_id
            ),

            "nome": self.nome,

            "host": self.host,

            "port": self.port,

            "status": self.status,

            "created_at": (
                self.created_at
            ),

            "metadata": (
                self.metadata
            )
        }


# ==================================================
# DEPLOYMENT
# ==================================================

@dataclass
class DeploymentRecord:

    deployment_id: str

    environment_id: str

    started_at: str = field(

        default_factory=lambda:

        now_str()
    )

    completed_at: str = None

    status: str = STATUS_DEPLOYING

    duration: float = 0

    metadata: dict = field(
        default_factory=dict
    )

    # ==============================================
    # DICT
    # ==============================================

    def to_dict(self):

        return {

            "deployment_id": (
                self.deployment_id
            ),

            "environment_id": (
                self.environment_id
            ),

            "started_at": (
                self.started_at
            ),

            "completed_at": (
                self.completed_at
            ),

            "status": self.status,

            "duration": self.duration,

            "metadata": (
                self.metadata
            )
        }


# ==================================================
# REGISTER
# ==================================================

def register_environment(

    environment_id,

    nome,

    host="localhost",

    port=8000,

    metadata=None
):

    env = DeploymentEnvironment(

        environment_id=environment_id,

        nome=nome,

        host=host,

        port=port,

        metadata=metadata or {}
    )

    with _LOCK:

        _ENVIRONMENTS[
            environment_id
        ] = env

    logger.info(

        (
            f"ENV REGISTER "
            f"{environment_id}"
        )
    )

    increment_counter(
        "deployment_envs"
    )

    publish_event(

        "ENVIRONMENT_REGISTERED",

        env.to_dict(),

        source=(
            "deployment_manager"
        )
    )

    return ok(

        mensagem="Ambiente registrado.",

        dados=env.to_dict()
    )


# ==================================================
# DEPLOY ID
# ==================================================

def generate_deployment_id():

    return (

        f"DEPLOY_"

        f"{int(now() * 1000)}"
    )


# ==================================================
# DEPLOY
# ==================================================

def deploy_environment(
    environment_id
):

    env = _ENVIRONMENTS.get(
        environment_id
    )

    if not env:

        return erro(
            "Ambiente inválido."
        )

    started = now()

    deploy = DeploymentRecord(

        deployment_id=(
            generate_deployment_id()
        ),

        environment_id=(
            environment_id
        )
    )

    try:

        logger.info(

            (
                f"DEPLOY START "
                f"{environment_id}"
            )
        )

        env.status = (
            STATUS_DEPLOYING
        )

        publish_event(

            "DEPLOY_STARTED",

            deploy.to_dict(),

            source=(
                "deployment_manager"
            )
        )

        # ==========================================
        # START PLATFORM
        # ==========================================

        start_platform()

        duration = now() - started

        deploy.completed_at = (
            now_str()
        )

        deploy.duration = duration

        deploy.status = (
            STATUS_RUNNING
        )

        env.status = STATUS_RUNNING

        _DEPLOYMENTS.append(
            deploy
        )

        logger.info(

            (
                f"DEPLOY END "
                f"{environment_id} "
                f"{duration:.4f}s"
            )
        )

        increment_counter(
            "deployments"
        )

        add_event(

            "deployment",

            "deploy_completed",

            deploy.to_dict()
        )

        publish_event(

            "DEPLOY_COMPLETED",

            deploy.to_dict(),

            source=(
                "deployment_manager"
            )
        )

        return ok(

            mensagem=(
                "Deploy realizado."
            ),

            dados=deploy.to_dict()
        )

    except Exception as ex:

        env.status = STATUS_FAILED

        deploy.status = STATUS_FAILED

        _DEPLOYMENTS.append(
            deploy
        )

        handle_exception(

            ex,

            contexto="DEPLOY"
        )

        publish_event(

            "DEPLOY_FAILED",

            {

                "deployment": (
                    deploy.to_dict()
                ),

                "error": str(ex)
            },

            source=(
                "deployment_manager"
            )
        )

        return erro(str(ex))


# ==================================================
# STOP
# ==================================================

def stop_environment(
    environment_id
):

    env = _ENVIRONMENTS.get(
        environment_id
    )

    if not env:

        return False

    stop_platform()

    env.status = STATUS_STOPPED

    logger.warning(

        (
            f"ENV STOP "
            f"{environment_id}"
        )
    )

    publish_event(

        "ENVIRONMENT_STOPPED",

        env.to_dict(),

        source=(
            "deployment_manager"
        )
    )

    return True


# ==================================================
# RESTART
# ==================================================

def restart_environment(
    environment_id
):

    env = _ENVIRONMENTS.get(
        environment_id
    )

    if not env:

        return False

    logger.warning(

        (
            f"ENV RESTART "
            f"{environment_id}"
        )
    )

    restart_platform()

    publish_event(

        "ENVIRONMENT_RESTARTED",

        env.to_dict(),

        source=(
            "deployment_manager"
        )
    )

    return True


# ==================================================
# ROLLBACK
# ==================================================

def rollback_environment(
    environment_id
):

    env = _ENVIRONMENTS.get(
        environment_id
    )

    if not env:

        return False

    logger.warning(

        (
            f"ROLLBACK "
            f"{environment_id}"
        )
    )

    env.status = STATUS_ROLLBACK

    publish_event(

        "DEPLOY_ROLLBACK",

        env.to_dict(),

        source=(
            "deployment_manager"
        )
    )

    return True


# ==================================================
# HEALTH
# ==================================================

def get_environment_health(
    environment_id
):

    env = _ENVIRONMENTS.get(
        environment_id
    )

    if not env:

        return None

    return {

        "environment": (
            env.to_dict()
        ),

        "platform": (
            get_platform_health()
        )
    }


# ==================================================
# STATUS
# ==================================================

def get_deployment_status():

    return {

        "environments": len(
            _ENVIRONMENTS
        ),

        "deployments": len(
            _DEPLOYMENTS
        ),

        "running": len([

            x

            for x in (
                _ENVIRONMENTS.values()
            )

            if (

                x.status

                ==

                STATUS_RUNNING
            )
        ])
    }


# ==================================================
# LIST
# ==================================================

def get_environments():

    return {

        k: v.to_dict()

        for k, v in (
            _ENVIRONMENTS.items()
        )
    }


def get_deployments():

    return [

        x.to_dict()

        for x in _DEPLOYMENTS
    ]


# ==================================================
# DEFAULT ENV
# ==================================================

def register_default_environment():

    register_environment(

        environment_id="LOCAL",

        nome="Local Environment",

        host="127.0.0.1",

        port=8000
    )


# ==================================================
# STARTUP
# ==================================================

register_default_environment()

logger.info(
    "Deployment manager inicializado."
)
