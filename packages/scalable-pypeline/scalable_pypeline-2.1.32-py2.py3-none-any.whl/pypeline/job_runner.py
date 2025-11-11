import os
import logging
import argparse
import threading
import multiprocessing as mp

# Prefer 'spawn' for user code using multiprocessing
if mp.get_start_method(allow_none=True) != "spawn":
    mp.set_start_method("spawn", force=True)

# Avoid staging more than one message; must be set before Dramatiq import path runs
os.environ.setdefault("dramatiq_queue_prefetch", "1")

from dramatiq import Worker, get_broker, set_broker
from dramatiq.middleware import Middleware


try:
    # If your project exposes a helper to configure the default broker, use it.
    from pypeline.dramatiq import configure_default_broker  # adjust import if needed

    broker = configure_default_broker() or get_broker()
    set_broker(broker)
except Exception:
    # Fall back to whatever Dramatiq has as the active broker.
    import pypeline.dramatiq  # noqa: F401 (ensure module side-effects run)

    broker = get_broker()


class OneAndDone(Middleware):
    """
    Signals when the first message starts ('got_work') and completes ('done').
    If stop_on_failure=True, we'll also mark done after the first failure.
    """

    def __init__(
        self,
        got_work: threading.Event,
        done: threading.Event,
        *,
        stop_on_failure: bool = False
    ):
        self.got_work = got_work
        self.done = done
        self.stop_on_failure = stop_on_failure

    def before_process_message(self, broker, message):
        # First time we see a message begin processing in this process
        if not self.got_work.is_set():
            self.got_work.set()

    def after_process_message(self, broker, message, *, result=None, exception=None):
        # On success (or also on failure if configured), finish this worker
        if exception is None or self.stop_on_failure:
            if not self.done.is_set():
                self.done.set()


def _graceful_stop(worker: Worker, log: logging.Logger):
    try:
        log.info("Stopping dramatiq worker...")
        worker.stop()  # stop consumers; no new messages will start
        worker.join()
        log.info("Worker stopped.")
    except Exception as e:
        log.exception("Error stopping worker: %s", e)


def _close_broker(log: logging.Logger):
    try:
        b = get_broker()
        if b is not None and hasattr(b, "close"):
            b.close()
            log.info("Broker closed.")
    except Exception as e:
        log.exception("Error closing broker: %s", e)


def job_runner(queues, idle_timeout_ms: int = 0, *, stop_on_failure: bool = False):
    """
    Start a single-thread Dramatiq worker. Behavior:
      - Wait up to `idle_timeout_ms` for *a job to start* (time-to-first-job).
      - Once a job begins, wait indefinitely for it to complete.
      - After the first successful job completes (or first job, if stop_on_failure=True), stop and exit.

    Args:
        queues (list[str]): queues to listen to
        idle_timeout_ms (int): <=0 => wait forever for first job; >0 => exit if no job starts in time
        stop_on_failure (bool): if True, exit after first job even if it fails
    """
    logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
    log = logging.getLogger("oneshot")

    # Normalize timeout (treat non-positive as "infinite")
    timeout_ms = (
        int(idle_timeout_ms) if idle_timeout_ms and int(idle_timeout_ms) > 0 else 0
    )
    log.info(
        "Launching worker with queues=%s, idle_timeout_ms=%s", queues, timeout_ms or "∞"
    )

    got_work = threading.Event()
    done = threading.Event()
    broker.add_middleware(OneAndDone(got_work, done, stop_on_failure=stop_on_failure))

    worker = Worker(
        broker,
        worker_threads=1,  # strictly one at a time
        queues=queues,
        worker_timeout=1000,  # ms; how often the worker checks for stop
    )

    worker.start()

    def controller():
        log.debug("Controller thread started.")
        try:
            # Phase 1: Wait for *first job to start*
            if timeout_ms > 0:
                started = got_work.wait(timeout_ms / 1000.0)
                if not started:
                    log.info(
                        "Idle timeout reached (%d ms); no jobs started. Stopping worker.",
                        timeout_ms,
                    )
                    return
            else:
                got_work.wait()

            log.info("First job started; waiting for it to finish...")
            # Phase 2: Wait for the first job to complete (no timeout)
            done.wait()
            log.info("First job finished; shutting down.")
        finally:
            _graceful_stop(worker, log)
            _close_broker(log)
            # Hard-exit to ensure K8s Job is marked Succeeded promptly, no lingering threads.
            os._exit(0)

    t = threading.Thread(target=controller, name="oneshot-controller", daemon=False)
    t.start()
    t.join()  # Block until controller completes (which shuts everything down)


def _parse_args(argv=None):
    ap = argparse.ArgumentParser(description="Run a one-shot Dramatiq worker.")
    ap.add_argument(
        "-q",
        "--queue",
        action="append",
        default=None,
        help="Queue to listen to (repeatable). You can also pass a comma-separated list.",
    )
    ap.add_argument(
        "--idle-timeout-ms",
        type=int,
        default=int(os.getenv("IDLE_TIMEOUT_MS", "0")),
        help="Exit if no job starts within this time (<=0 = wait forever).",
    )
    ap.add_argument(
        "--stop-on-failure",
        action="store_true",
        help="Exit after the first job even if it fails.",
    )
    return ap.parse_args(argv)


def main(argv=None):
    args = _parse_args(argv)

    # Build queue list from flags or env, support comma-separated entries.
    raw_entries = (
        args.queue if args.queue else [os.getenv("JOB_QUEUE", "pipeline-queue")]
    )
    queues = []
    for entry in raw_entries:
        queues.extend([q.strip() for q in str(entry).split(",") if q and q.strip()])

    if not queues:
        raise SystemExit("No queues provided. Use -q ... or set JOB_QUEUE.")

    logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
    log = logging.getLogger("oneshot")

    pid = os.getpid()
    ppid = os.getppid()
    log.info(
        "Starting one-shot worker PID=%s, Parent PID=%s, queues=%s, idle_timeout_ms=%s, stop_on_failure=%s",
        pid,
        ppid,
        queues,
        args.idle_timeout_ms if args.idle_timeout_ms > 0 else "∞",
        args.stop_on_failure,
    )

    job_runner(
        queues,
        idle_timeout_ms=args.idle_timeout_ms,
        stop_on_failure=args.stop_on_failure,
    )


if __name__ == "__main__":
    main()
