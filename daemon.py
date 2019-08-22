import queue
import signal
import sys
import threading
from functools import partial

from demo_impl.daemon.events_processor import EventProcessor
from demo_impl.daemon.threaded_daemon import ThreadedVrcT70Daemon
from demo_impl.shared.models.devices import VrcT70Device  # noqa
from demo_impl.shared.models.sensors import VrcT70Sensor  # noqa
from demo_impl.shared.models.shared import Base
from demo_impl.shared.support.config_helper import DaemonConfigHelper
from demo_impl.shared.support.config_support import get_config

from loguru import logger as initial_logger


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def initialize_database(connection_uri, echo=False):
    engine = create_engine(connection_uri, echo=echo)
    return engine


def init_logger(config):
    initial_logger.remove()

    log_format = "{time:YYYY-MM-DD at HH:mm:ss} {level} {file}:{line} {function}() : {message}"

    initial_logger.add(
        sys.stderr,
        format=log_format,
        level=DaemonConfigHelper.get_daemon_log_level(config),
        backtrace=DaemonConfigHelper.get_daemon_log_backtrace(config),
        diagnose=DaemonConfigHelper.get_daemon_log_diagnose(config)
    )

    log_file_name = DaemonConfigHelper.get_daemon_log_file_name(config)
    if log_file_name:
        initial_logger.add(
            log_file_name,
            format=log_format,
            level=DaemonConfigHelper.get_daemon_log_level(config),
            rotation=DaemonConfigHelper.get_daemon_log_file_rotation(config),
            compression=DaemonConfigHelper.get_daemon_log_file_compression(config),
            backtrace=DaemonConfigHelper.get_daemon_log_backtrace(config),
            diagnose=DaemonConfigHelper.get_daemon_log_diagnose(config)
        )

    return initial_logger


def signal_handler(sig, frame, daemon, need_stop, logger):
    logger.warning("!!!!!! want to stop daemon !!!!!!")
    need_stop.set()

    if not daemon:
        sys.exit(0)

    logger.warning("going to shutdown with Ctrl-C")
    daemon.stop()


def main():
    need_stop = threading.Event()

    config = get_config()
    if not config:
        initial_logger.error("can't initialize, can't read config file")
        return -1

    logger = init_logger(config)

    logger.info("daemon started")

    db_uri = DaemonConfigHelper.get_database_connection_uri(config)
    logger.debug("db_uri: '{}'".format(db_uri))

    logger.info("initializing database connection")
    engine = initialize_database(db_uri)

    logger.info("recreating all tables (if required)")
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    uart_name = DaemonConfigHelper.get_uart_name(config)
    uart_speed = DaemonConfigHelper.get_uart_speed(config)
    devices_addresses = DaemonConfigHelper.get_devices_address(config)

    logger.info("going connect to port {} with speed {}".format(uart_name, uart_speed))
    logger.info("will poll for devices with addresses: {}".format(devices_addresses))

    if not devices_addresses:
        logger.error("no device addresses for polling, going out")
        return -1

    events_queue = queue.Queue()
    threaded_daemon = ThreadedVrcT70Daemon(events_queue, logger, uart_name, uart_speed, devices_addresses)
    events_processor = EventProcessor(logger, session)

    partial_handler = partial(signal_handler, daemon=threaded_daemon, need_stop=need_stop, logger=logger)
    signal.signal(signal.SIGINT, partial_handler)

    threaded_daemon.start()
    while not need_stop.is_set():
        try:
            event = events_queue.get(block=True, timeout=0.5)
        except queue.Empty:
            event = None

        if not event:
            continue

        logger.debug("event registered: {}".format(event))
        events_processor.process_event(event)

    threaded_daemon.join()
    while not events_queue.empty():
        event = events_queue.get()
        logger.debug("event skipped at end: {}".format(event))

    session.commit()
    logger.info("daemon finished")
    return 0


if __name__ == "__main__":
    res = main()
    exit(res)
