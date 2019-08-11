import datetime
from collections import namedtuple

from demo_impl.daemon.data_types import DeviceLastCommunicationTouch, SensorReadData
from demo_impl.shared.models.devices import VrcT70Device  # noqa
from demo_impl.shared.models.sensors import VrcT70Sensor  # noqa

DeviceIdentifier = namedtuple("DeviceIdentifier", ["device_port_name", "device_address"])


class EventProcessor(object):
    def __init__(self, logger, db_session):
        self._db_session = db_session
        self.logger = logger

        self._map_device_identifier_to_device_object = dict()
        self._map_sensor_unique_id_to_sensor_object = dict()

    def process_event(self, event):
        if isinstance(event, DeviceLastCommunicationTouch):
            self._update_last_read_timestamp_for_device(event, can_commit=True)
        elif isinstance(event, SensorReadData):
            self._register_read_event(event, can_commit=True)
        elif isinstance(event, list):
            for atomic_event in event:
                assert isinstance(atomic_event, SensorReadData)
                self._register_read_event(atomic_event, can_commit=False)

            if len(event):
                self._db_session.commit()
        else:
            self.logger.error("unknown event: {}".format(event))

    def _register_read_event(self, event, can_commit=True):
        device = self._get_device_by_port_name_and_device_address(event.device_port_name, event.device_address)
        device.last_update_timestamp = datetime.datetime.utcnow()

        sensor = self._get_sensor_by_unique_id(device.device_id, event.trunk_number, event.sensor_index, event.sensor_address)

        sensor.trunk_number = event.trunk_number
        sensor.sensor_index = event.sensor_index
        sensor.is_connected = event.is_connected
        sensor.temperature = event.temperature

        if can_commit:
            self._db_session.commit()

    def _get_sensor_by_unique_id(self, device_id, trunk_number, sensor_index, sensor_address):
        if sensor_address in self._map_sensor_unique_id_to_sensor_object:
            sensor = self._map_sensor_unique_id_to_sensor_object[sensor_address]
            return sensor

        sensor = self._db_session.query(
            VrcT70Sensor
        ).filter(
            VrcT70Sensor.sensor_address == sensor_address
        ).scalar()

        if not sensor:
            sensor = VrcT70Sensor()

            sensor.device_id = device_id
            sensor.sensor_address = sensor_address
            sensor.trunk_number = trunk_number
            sensor.sensor_index = sensor_index
            self._db_session.add(sensor)
            self._db_session.flush()

        self._map_sensor_unique_id_to_sensor_object[sensor_address] = sensor
        return sensor

    def _update_last_read_timestamp_for_device(self, event, can_commit=True):
        device = self._get_device_by_port_name_and_device_address(event.device_port_name, event.device_address)
        device.last_update_timestamp = datetime.datetime.utcnow()

        if can_commit:
            self._db_session.commit()

    def _get_device_by_port_name_and_device_address(self, device_port_name, device_address):
        identifier = DeviceIdentifier(device_port_name, device_address)
        if identifier in self._map_device_identifier_to_device_object:
            return self._map_device_identifier_to_device_object[identifier]

        device = self._db_session.query(
            VrcT70Device
        ).filter(
            VrcT70Device.device_port_name == device_port_name,
            VrcT70Device.device_address == device_address
        ).scalar()

        if not device:
            device = VrcT70Device()

            device.device_port_name = device_port_name
            device.device_address = device_address

            hex_device_address = "0x{0:02x}".format(device_address)
            device.device_name = "Device {}".format(hex_device_address)
            self._db_session.add(device)
            self._db_session.flush()

        self._map_device_identifier_to_device_object[identifier] = device
        return device
