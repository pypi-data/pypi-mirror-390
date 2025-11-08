from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="ReportTrips")


@_attrs_define
class ReportTrips:
    """
    Attributes:
        device_id (int | Unset):
        device_name (str | Unset):
        max_speed (float | Unset): in knots
        average_speed (float | Unset): in knots
        distance (float | Unset): in meters
        spent_fuel (float | Unset): in liters
        duration (int | Unset):
        start_time (datetime.datetime | Unset): in ISO 8601 format. eg. `1963-11-22T18:30:00Z`
        start_address (str | Unset):
        start_lat (float | Unset):
        start_lon (float | Unset):
        end_time (datetime.datetime | Unset): in ISO 8601 format. eg. `1963-11-22T18:30:00Z`
        end_address (str | Unset):
        end_lat (float | Unset):
        end_lon (float | Unset):
        driver_unique_id (str | Unset):
        driver_name (str | Unset):
    """

    device_id: int | Unset = UNSET
    device_name: str | Unset = UNSET
    max_speed: float | Unset = UNSET
    average_speed: float | Unset = UNSET
    distance: float | Unset = UNSET
    spent_fuel: float | Unset = UNSET
    duration: int | Unset = UNSET
    start_time: datetime.datetime | Unset = UNSET
    start_address: str | Unset = UNSET
    start_lat: float | Unset = UNSET
    start_lon: float | Unset = UNSET
    end_time: datetime.datetime | Unset = UNSET
    end_address: str | Unset = UNSET
    end_lat: float | Unset = UNSET
    end_lon: float | Unset = UNSET
    driver_unique_id: str | Unset = UNSET
    driver_name: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        device_id = self.device_id

        device_name = self.device_name

        max_speed = self.max_speed

        average_speed = self.average_speed

        distance = self.distance

        spent_fuel = self.spent_fuel

        duration = self.duration

        start_time: str | Unset = UNSET
        if not isinstance(self.start_time, Unset):
            start_time = self.start_time.isoformat()

        start_address = self.start_address

        start_lat = self.start_lat

        start_lon = self.start_lon

        end_time: str | Unset = UNSET
        if not isinstance(self.end_time, Unset):
            end_time = self.end_time.isoformat()

        end_address = self.end_address

        end_lat = self.end_lat

        end_lon = self.end_lon

        driver_unique_id = self.driver_unique_id

        driver_name = self.driver_name

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if device_id is not UNSET:
            field_dict["deviceId"] = device_id
        if device_name is not UNSET:
            field_dict["deviceName"] = device_name
        if max_speed is not UNSET:
            field_dict["maxSpeed"] = max_speed
        if average_speed is not UNSET:
            field_dict["averageSpeed"] = average_speed
        if distance is not UNSET:
            field_dict["distance"] = distance
        if spent_fuel is not UNSET:
            field_dict["spentFuel"] = spent_fuel
        if duration is not UNSET:
            field_dict["duration"] = duration
        if start_time is not UNSET:
            field_dict["startTime"] = start_time
        if start_address is not UNSET:
            field_dict["startAddress"] = start_address
        if start_lat is not UNSET:
            field_dict["startLat"] = start_lat
        if start_lon is not UNSET:
            field_dict["startLon"] = start_lon
        if end_time is not UNSET:
            field_dict["endTime"] = end_time
        if end_address is not UNSET:
            field_dict["endAddress"] = end_address
        if end_lat is not UNSET:
            field_dict["endLat"] = end_lat
        if end_lon is not UNSET:
            field_dict["endLon"] = end_lon
        if driver_unique_id is not UNSET:
            field_dict["driverUniqueId"] = driver_unique_id
        if driver_name is not UNSET:
            field_dict["driverName"] = driver_name

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        device_id = d.pop("deviceId", UNSET)

        device_name = d.pop("deviceName", UNSET)

        max_speed = d.pop("maxSpeed", UNSET)

        average_speed = d.pop("averageSpeed", UNSET)

        distance = d.pop("distance", UNSET)

        spent_fuel = d.pop("spentFuel", UNSET)

        duration = d.pop("duration", UNSET)

        _start_time = d.pop("startTime", UNSET)
        start_time: datetime.datetime | Unset
        if isinstance(_start_time, Unset):
            start_time = UNSET
        else:
            start_time = isoparse(_start_time)

        start_address = d.pop("startAddress", UNSET)

        start_lat = d.pop("startLat", UNSET)

        start_lon = d.pop("startLon", UNSET)

        _end_time = d.pop("endTime", UNSET)
        end_time: datetime.datetime | Unset
        if isinstance(_end_time, Unset):
            end_time = UNSET
        else:
            end_time = isoparse(_end_time)

        end_address = d.pop("endAddress", UNSET)

        end_lat = d.pop("endLat", UNSET)

        end_lon = d.pop("endLon", UNSET)

        driver_unique_id = d.pop("driverUniqueId", UNSET)

        driver_name = d.pop("driverName", UNSET)

        report_trips = cls(
            device_id=device_id,
            device_name=device_name,
            max_speed=max_speed,
            average_speed=average_speed,
            distance=distance,
            spent_fuel=spent_fuel,
            duration=duration,
            start_time=start_time,
            start_address=start_address,
            start_lat=start_lat,
            start_lon=start_lon,
            end_time=end_time,
            end_address=end_address,
            end_lat=end_lat,
            end_lon=end_lon,
            driver_unique_id=driver_unique_id,
            driver_name=driver_name,
        )

        report_trips.additional_properties = d
        return report_trips

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
