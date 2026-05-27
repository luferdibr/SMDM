
import threading
import time
import traceback
from datetime import datetime


from core.logger import get_logger

from core.telemetry import (

    increment_counter,

    add_event,

    track_execution_time
)


# ==================================================
# LOGGER
# ==================================================

logger = get_logger("scheduler")


# ==================================================
# STORAGE
# ==================================================

_LOCK = threading.RLock()

_JOBS = {}

_RUNNING = False

_THREAD = None


# ==================================================
# CONFIG
# ==================================================

DEFAULT_INTERVAL = 60

LOOP_SLEEP = 1


# ==================================================
# HELPERS
# ==================================================

def now():

    return time.time()


def now_datetime():

    return datetime.now()


# ==================================================
# JOB CLASS
# ==================================================

class SchedulerJob:

    def __init__(

        self,

        name,

        func,

        interval=DEFAULT_INTERVAL,

        enabled=True,

        run_on_startup=False,

        args=None,

        kwargs=None
    ):

        self.name = str(name)

        self.func = func

        self.interval = max(
            1,
            int(interval)
        )

        self.enabled = bool(enabled)

        self.run_on_startup = bool(
            run_on_startup
        )

        self.args = args or []

        self.kwargs = kwargs or {}

        self.created_at = now()

        self.last_run = None

        self.next_run = now() + self.interval

        self.running = False

        self.total_runs = 0

        self.total_errors = 0

        self.last_error = None

        self.last_duration = 0

    # ==============================================
    # EXECUTE
    # ==============================================

    def execute(self):

        if not self.enabled:
            return

        self.running = True

        started = now()

        try:

            logger.info(
                f"JOB START {self.name}"
            )

            increment_counter(
                "scheduler_job_runs"
            )

            add_event(

                "scheduler",

                f"JOB START {self.name}"
            )

            with track_execution_time(
                f"job_{self.name}"
            ):

                self.func(

                    *self.args,

                    **self.kwargs
                )

            duration = now() - started

            self.last_duration = duration

            self.last_run = now()

            self.next_run = (
                now() + self.interval
            )

            self.total_runs += 1

            logger.info(

                (
                    f"JOB END "
                    f"{self.name} "
                    f"{duration:.4f}s"
                )
            )

        except Exception as ex:

            self.total_errors += 1

            self.last_error = str(ex)

            logger.exception(

                (
                    f"JOB ERROR "
                    f"{self.name}"
                )
            )

            add_event(

                "scheduler_error",

                self.name,

                {

                    "error": str(ex),

                    "traceback": (
                        traceback.format_exc()
                    )
                }
            )

        finally:

            self.running = False

    # ==============================================
    # STATUS
    # ==============================================

    def to_dict(self):

        return {

            "name": self.name,

            "enabled": self.enabled,

            "running": self.running,

            "interval": self.interval,

            "created_at": self.created_at,

            "last_run": self.last_run,

            "next_run": self.next_run,

            "total_runs": self.total_runs,

            "total_errors": (
                self.total_errors
            ),

            "last_error": self.last_error,

            "last_duration": (
                self.last_duration
            )
        }


# ==================================================
# REGISTER
# ==================================================

def register_job(

    name,

    func,

    interval=DEFAULT_INTERVAL,

    enabled=True,

    run_on_startup=False,

    args=None,

    kwargs=None
):

    global _JOBS

    with _LOCK:

        job = SchedulerJob(

            name=name,

            func=func,

            interval=interval,

            enabled=enabled,

            run_on_startup=run_on_startup,

            args=args,

            kwargs=kwargs
        )

        _JOBS[name] = job

    logger.info(
        f"JOB REGISTER {name}"
    )

    # ==============================================
    # STARTUP
    # ==============================================

    if run_on_startup:

        try:

            threading.Thread(

                target=job.execute,

                daemon=True

            ).start()

        except Exception:

            logger.exception(
                "STARTUP JOB ERROR"
            )

    return job


# ==================================================
# REMOVE
# ==================================================

def unregister_job(name):

    with _LOCK:

        if name in _JOBS:

            del _JOBS[name]

            logger.info(
                f"JOB REMOVE {name}"
            )

            return True

    return False


# ==================================================
# GET JOB
# ==================================================

def get_job(name):

    with _LOCK:

        return _JOBS.get(name)


# ==================================================
# EXECUTION LOOP
# ==================================================

def scheduler_loop():

    global _RUNNING

    logger.info(
        "Scheduler iniciado."
    )

    while _RUNNING:

        try:

            timestamp = now()

            with _LOCK:

                jobs = list(
                    _JOBS.values()
                )

            for job in jobs:

                if not job.enabled:
                    continue

                if job.running:
                    continue

                if timestamp >= job.next_run:

                    threading.Thread(

                        target=job.execute,

                        daemon=True

                    ).start()

            time.sleep(LOOP_SLEEP)

        except Exception:

            logger.exception(
                "SCHEDULER LOOP ERROR"
            )

            time.sleep(LOOP_SLEEP)

    logger.warning(
        "Scheduler parado."
    )


# ==================================================
# START
# ==================================================

def start_scheduler():

    global _RUNNING
    global _THREAD

    if _RUNNING:

        return False

    _RUNNING = True

    _THREAD = threading.Thread(

        target=scheduler_loop,

        daemon=True
    )

    _THREAD.start()

    increment_counter(
        "scheduler_starts"
    )

    return True


# ==================================================
# STOP
# ==================================================

def stop_scheduler():

    global _RUNNING

    _RUNNING = False

    logger.warning(
        "Parando scheduler."
    )

    return True


# ==================================================
# STATUS
# ==================================================

def is_scheduler_running():

    return _RUNNING


def get_scheduler_status():

    with _LOCK:

        return {

            "running": _RUNNING,

            "jobs": len(_JOBS),

            "job_list": [

                x.to_dict()

                for x in _JOBS.values()
            ]
        }


# ==================================================
# ENABLE
# ==================================================

def enable_job(name):

    job = get_job(name)

    if not job:
        return False

    job.enabled = True

    return True


def disable_job(name):

    job = get_job(name)

    if not job:
        return False

    job.enabled = False

    return True


# ==================================================
# RUN NOW
# ==================================================

def run_job_now(name):

    job = get_job(name)

    if not job:

        return False

    threading.Thread(

        target=job.execute,

        daemon=True

    ).start()

    return True


# ==================================================
# CLEAR
# ==================================================

def clear_jobs():

    global _JOBS

    with _LOCK:

        total = len(_JOBS)

        _JOBS.clear()

    logger.warning(
        f"ALL JOBS CLEARED {total}"
    )

    return total


# ==================================================
# BUILTIN JOBS
# ==================================================

def register_builtin_jobs():

    try:

        from core.cache import (
            cleanup_expired
        )

        register_job(

            name="cache_cleanup",

            func=cleanup_expired,

            interval=300,

            enabled=True
        )

    except Exception:

        logger.exception(
            "BUILTIN JOB ERROR"
        )


# ==================================================
# STARTUP
# ==================================================

register_builtin_jobs()

logger.info(
    "Scheduler manager inicializado."
)
