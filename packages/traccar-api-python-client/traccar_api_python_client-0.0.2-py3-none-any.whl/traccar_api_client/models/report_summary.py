from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ReportSummary")


@_attrs_define
class ReportSummary:
    """
    Attributes:
        device_id (int | Unset):
        device_name (str | Unset):
        max_speed (float | Unset): in knots
        average_speed (float | Unset): in knots
        distance (float | Unset): in meters
        spent_fuel (float | Unset): in liters
        engine_hours (int | Unset):
    """

    device_id: int | Unset = UNSET
    device_name: str | Unset = UNSET
    max_speed: float | Unset = UNSET
    average_speed: float | Unset = UNSET
    distance: float | Unset = UNSET
    spent_fuel: float | Unset = UNSET
    engine_hours: int | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        device_id = self.device_id

        device_name = self.device_name

        max_speed = self.max_speed

        average_speed = self.average_speed

        distance = self.distance

        spent_fuel = self.spent_fuel

        engine_hours = self.engine_hours

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
        if engine_hours is not UNSET:
            field_dict["engineHours"] = engine_hours

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

        engine_hours = d.pop("engineHours", UNSET)

        report_summary = cls(
            device_id=device_id,
            device_name=device_name,
            max_speed=max_speed,
            average_speed=average_speed,
            distance=distance,
            spent_fuel=spent_fuel,
            engine_hours=engine_hours,
        )

        report_summary.additional_properties = d
        return report_summary

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
