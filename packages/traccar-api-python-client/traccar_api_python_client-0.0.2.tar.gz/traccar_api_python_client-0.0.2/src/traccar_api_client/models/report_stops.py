from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="ReportStops")


@_attrs_define
class ReportStops:
    """
    Attributes:
        device_id (int | Unset):
        device_name (str | Unset):
        duration (int | Unset):
        start_time (datetime.datetime | Unset): in ISO 8601 format. eg. `1963-11-22T18:30:00Z`
        address (str | Unset):
        lat (float | Unset):
        lon (float | Unset):
        end_time (datetime.datetime | Unset): in ISO 8601 format. eg. `1963-11-22T18:30:00Z`
        spent_fuel (float | Unset): in liters
        engine_hours (int | Unset):
    """

    device_id: int | Unset = UNSET
    device_name: str | Unset = UNSET
    duration: int | Unset = UNSET
    start_time: datetime.datetime | Unset = UNSET
    address: str | Unset = UNSET
    lat: float | Unset = UNSET
    lon: float | Unset = UNSET
    end_time: datetime.datetime | Unset = UNSET
    spent_fuel: float | Unset = UNSET
    engine_hours: int | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        device_id = self.device_id

        device_name = self.device_name

        duration = self.duration

        start_time: str | Unset = UNSET
        if not isinstance(self.start_time, Unset):
            start_time = self.start_time.isoformat()

        address = self.address

        lat = self.lat

        lon = self.lon

        end_time: str | Unset = UNSET
        if not isinstance(self.end_time, Unset):
            end_time = self.end_time.isoformat()

        spent_fuel = self.spent_fuel

        engine_hours = self.engine_hours

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if device_id is not UNSET:
            field_dict["deviceId"] = device_id
        if device_name is not UNSET:
            field_dict["deviceName"] = device_name
        if duration is not UNSET:
            field_dict["duration"] = duration
        if start_time is not UNSET:
            field_dict["startTime"] = start_time
        if address is not UNSET:
            field_dict["address"] = address
        if lat is not UNSET:
            field_dict["lat"] = lat
        if lon is not UNSET:
            field_dict["lon"] = lon
        if end_time is not UNSET:
            field_dict["endTime"] = end_time
        if spent_fuel is not UNSET:
            field_dict["spentFuel"] = spent_fuel
        if engine_hours is not UNSET:
            field_dict["engineHours"] = engine_hours

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        device_id = d.pop("deviceId", UNSET)

        device_name = d.pop("deviceName", UNSET)

        duration = d.pop("duration", UNSET)

        _start_time = d.pop("startTime", UNSET)
        start_time: datetime.datetime | Unset
        if isinstance(_start_time, Unset):
            start_time = UNSET
        else:
            start_time = isoparse(_start_time)

        address = d.pop("address", UNSET)

        lat = d.pop("lat", UNSET)

        lon = d.pop("lon", UNSET)

        _end_time = d.pop("endTime", UNSET)
        end_time: datetime.datetime | Unset
        if isinstance(_end_time, Unset):
            end_time = UNSET
        else:
            end_time = isoparse(_end_time)

        spent_fuel = d.pop("spentFuel", UNSET)

        engine_hours = d.pop("engineHours", UNSET)

        report_stops = cls(
            device_id=device_id,
            device_name=device_name,
            duration=duration,
            start_time=start_time,
            address=address,
            lat=lat,
            lon=lon,
            end_time=end_time,
            spent_fuel=spent_fuel,
            engine_hours=engine_hours,
        )

        report_stops.additional_properties = d
        return report_stops

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
