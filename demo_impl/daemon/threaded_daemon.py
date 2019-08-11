import threading

from .support import init_serial
from .vrc_t70_daemon import VrcT70Daemon


class ThreadedVrcT70Daemon(threading.Thread):
    def __init__(
        self,
        events_queue,
        logger,
        uart_name,
        uart_speed,
        devices_addresses,
        *args
    ):
        super().__init__(*args)
        self._events_queue = events_queue
        self.logger = logger
        self.uart_name = uart_name
        self.uart_speed = uart_speed
        self.devices_addresses = devices_addresses

        uart = init_serial(self.uart_name, self.uart_speed)
        self._daemon = VrcT70Daemon(
            self._events_queue,
            uart,
            self.devices_addresses,
            self.logger
        )
        self._daemon.pre_queuing_func = self._port_info_adder_function

    def run(self):
        self._daemon.init()
        self._daemon.run()

    def stop(self):
        self.logger.warning("stopping daemon for uart '{}'".format(self.uart_name))
        self._daemon.stop()

    def _port_info_adder_function(self, event):
        event.device_port_name = str(self.uart_name).strip().lower()
        return event
