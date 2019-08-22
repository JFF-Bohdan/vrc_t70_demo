import datetime
import random
import time

from .data_types import DeviceLastCommunicationTouch, SensorReadData
from .utils import hexlify_to_string
from .vrc_t70_stateful_communicator import VrcT70StatefulCommunicator


class VrcT70Daemon(object):
    DEFAULT_POLLING_SLEEP_INTERVAL = 1
    DEFAULT_TEMP_ROUND_PRESISSION = 3

    def __init__(self, events_queue, serial, devices_addresses, logger):  # , db_session
        self._serial = serial
        self._devices_addresses = devices_addresses
        self._communicators = []
        self.logger = logger
        self._stop = False
        self._polling_sleep_interval = VrcT70Daemon.DEFAULT_POLLING_SLEEP_INTERVAL
        # self.db_session = db_session
        self._events_queue = events_queue

        # self._map_device_addresses_to_ids = dict()
        self._round_precission = VrcT70Daemon.DEFAULT_TEMP_ROUND_PRESISSION
        self.pre_queuing_func = None

    def init(self):
        for device_address in self._devices_addresses:
            hex_device_address = "0x{0:02x}".format(device_address)
            self.logger.info("creating new communicator for device {}".format(hex_device_address))

            communicator = VrcT70StatefulCommunicator(self._serial, controller_address=device_address, logger=self.logger)
            communicator.ping()

            new_session_id = random_byte_array(4)
            self.logger.debug("initializing session id with {}".format(hexlify_to_string(new_session_id)))
            r = communicator.set_session_id(new_session_id)
            assert r.session_id() == new_session_id

            self.logger.debug("scanning for sensors on trunks...")
            communicator.rescan_sensors_on_trunks()

            self.logger.info(
                "sensors count per trunk for {}: {}".format(
                    hex_device_address,
                    communicator.get_sensors_per_trunk_count()
                )
            )
            self._communicators.append(communicator)
            self._on_communicator_registration(communicator)

    def run(self):
        while not self._stop:
            for communicator in self._communicators:
                if self._stop:
                    break

                self.logger.debug("updating data for controller {}".format(communicator.hex_device_address_for_communicator()))
                events = communicator.update_temperatures()
                self.logger.debug("events: {}".format(events))

                self._on_events_from_device_received(communicator, events)

            if self._stop:
                break

            self.logger.debug("going to sleep for {} second(s)".format(self._polling_sleep_interval))
            time.sleep(self._polling_sleep_interval)

    def stop(self):
        self._stop = True

    def _on_communicator_registration(self, communicator):
        event = DeviceLastCommunicationTouch(device_address=communicator.controller_address)

        if self.pre_queuing_func:
            event = self.pre_queuing_func(event)

        self._events_queue.put(event)

    def _on_events_from_device_received(self, communicator, events):
        external_event = SensorReadData()
        external_event.device_address = communicator.controller_address

        events_list = list()
        for event in events:
            external_event.sensor_address = event.sensor_address
            external_event.trunk_number = event.trunk_number
            external_event.sensor_index = event.sensor_index
            external_event.is_connected = event.is_connected
            external_event.temperature = round(event.temperature, self._round_precission) \
                if event.temperature is not None else None

            if self.pre_queuing_func:
                external_event = self.pre_queuing_func(external_event)

            events_list.append(external_event)

        self._events_queue.put(external_event)


def random_byte_array(length):
    return bytearray((random.getrandbits(8) for _ in range(length)))


def utc_now():
    return datetime.datetime.utcnow()
