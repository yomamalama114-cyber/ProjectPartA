from __future__ import annotations

from datetime import datetime
from typing import Optional


class Measurement:
    def __init__(self, timestamp: datetime, value: float, unit: str):
        self.timestamp = timestamp
        self.value = float(value)
        self.unit = unit


class Device:
    def __init__(self, id: str, device_name: str, supplier: str, device_type: str):
        self.id = str(id)
        self.device_name = str(device_name)
        self.supplier = str(supplier)
        self.device_type = str(device_type)
        self.room = None

    def is_sensor(self) -> bool:
        return False

    def is_actuator(self) -> bool:
        return False

    def get_device_type(self) -> str:
        return self.device_type


class Sensor(Device):
    def __init__(
        self,
        id: str,
        device_name: str,
        supplier: str,
        device_type: str,
        unit: Optional[str] = None
    ):
        super().__init__(id, device_name, supplier, device_type)
        self.unit = unit
        self.measurements: list[Measurement] = []

    def is_sensor(self) -> bool:
        return True

    def last_measurement(self) -> Optional[Measurement]:
        if not self.measurements:
            return None
        return self.measurements[-1]

    def get_measurements(self) -> list[Measurement]:
        return list(self.measurements)

    def remove_current_measurement(self) -> Optional[Measurement]:
        if not self.measurements:
            return None
        return self.measurements.pop()

    def clear_measurements(self) -> None:
        self.measurements.clear()

    def add_measurement(
        self,
        value: float,
        unit: Optional[str] = None,
        timestamp: Optional[datetime] = None
    ) -> Measurement:
        if unit is None:
            if self.unit is None:
                raise ValueError("Unit må oppgis første gangen")
            unit = self.unit
        else:
            self.unit = unit

        if timestamp is None:
            timestamp = datetime.now()

        measurement = Measurement(timestamp, value, unit)
        self.measurements.append(measurement)
        return measurement


class Actuator(Device):
    def __init__(self, id: str, device_name: str, supplier: str, device_type: str):
        super().__init__(id, device_name, supplier, device_type)
        self.active = False
        self.target_value: Optional[float] = None

    def is_actuator(self) -> bool:
        return True

    def turn_on(self, target_value: Optional[float] = None) -> None:
        self.active = True
        if target_value is not None:
            self.target_value = float(target_value)

    def turn_off(self) -> None:
        self.active = False
        self.target_value = None

    def is_active(self) -> bool:
        return self.active

    def set_state(self, active: bool, target_value: Optional[float] = None) -> None:
        if active:
            self.turn_on(target_value)
        else:
            self.turn_off()


class ActuatorWithSensor(Actuator):
    def __init__(
        self,
        id: str,
        device_name: str,
        supplier: str,
        device_type: str,
        unit: Optional[str] = None
    ):
        super().__init__(id, device_name, supplier, device_type)
        self.unit = unit
        self.measurements: list[Measurement] = []

    def is_sensor(self) -> bool:
        return True

    def add_measurement(
        self,
        value: float,
        unit: Optional[str] = None,
        timestamp: Optional[datetime] = None
    ) -> Measurement:
        if unit is None:
            if self.unit is None:
                raise ValueError("Unit må oppgis første gangen")
            unit = self.unit
        else:
            self.unit = unit

        if timestamp is None:
            timestamp = datetime.now()

        measurement = Measurement(timestamp, value, unit)
        self.measurements.append(measurement)
        return measurement

    def last_measurement(self) -> Optional[Measurement]:
        if not self.measurements:
            return None
        return self.measurements[-1]

    def get_measurements(self) -> list[Measurement]:
        return list(self.measurements)

    def remove_current_measurement(self) -> Optional[Measurement]:
        if not self.measurements:
            return None
        return self.measurements.pop()

    def clear_measurements(self) -> None:
        self.measurements.clear()


class Room:
    def __init__(self, floor: Floor, room_size: float, room_name: Optional[str] = None):
        self.floor = floor
        self.room_size = float(room_size)
        self.room_name = room_name
        self.devices: list[Device] = []

    def add_device(self, device: Device) -> None:
        device.room = self
        self.devices.append(device)

    def get_devices(self) -> list[Device]:
        return list(self.devices)

    def get_area(self) -> float:
        return self.room_size


class Floor:
    def __init__(self, level: int):
        self.level = int(level)
        self.rooms: list[Room] = []

    def add_room(self, room: Room) -> None:
        self.rooms.append(room)

    def get_rooms(self) -> list[Room]:
        return list(self.rooms)


class SmartHouse:
    def __init__(self):
        self.floors: list[Floor] = []

    def register_floor(self, level):
        floor = Floor(level)
        self.floors.append(floor)
        self.floors.sort(key=lambda f: f.level)
        return floor

    def register_room(self, floor, room_size, room_name=None):
        room = Room(floor, room_size, room_name)
        floor.add_room(room)
        return room

    def get_floors(self):
        return list(self.floors)

    def get_rooms(self):
        rooms = []
        for floor in self.floors:
            rooms.extend(floor.get_rooms())
        return rooms

    def get_area(self):
        total = 0
        for room in self.get_rooms():
            total += room.get_area()
        return total

    def register_device(self, room, device):
        room.add_device(device)
        return device

    def get_devices(self, device_id):
        for room in self.get_rooms():
            for device in room.get_devices():
                if device.id == str(device_id):
                    return device
        return None