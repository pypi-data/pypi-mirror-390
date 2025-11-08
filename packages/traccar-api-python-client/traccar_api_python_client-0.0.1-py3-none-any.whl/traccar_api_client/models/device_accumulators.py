from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="DeviceAccumulators")


@_attrs_define
class DeviceAccumulators:
    """
    Attributes:
        device_id (int | Unset):
        total_distance (float | Unset): in meters
        hours (float | Unset):
    """

    device_id: int | Unset = UNSET
    total_distance: float | Unset = UNSET
    hours: float | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        device_id = self.device_id

        total_distance = self.total_distance

        hours = self.hours

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if device_id is not UNSET:
            field_dict["deviceId"] = device_id
        if total_distance is not UNSET:
            field_dict["totalDistance"] = total_distance
        if hours is not UNSET:
            field_dict["hours"] = hours

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        device_id = d.pop("deviceId", UNSET)

        total_distance = d.pop("totalDistance", UNSET)

        hours = d.pop("hours", UNSET)

        device_accumulators = cls(
            device_id=device_id,
            total_distance=total_distance,
            hours=hours,
        )

        device_accumulators.additional_properties = d
        return device_accumulators

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
