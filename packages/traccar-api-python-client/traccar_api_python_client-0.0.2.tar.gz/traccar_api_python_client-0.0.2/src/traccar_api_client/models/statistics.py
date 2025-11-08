from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="Statistics")


@_attrs_define
class Statistics:
    """
    Attributes:
        capture_time (datetime.datetime | Unset): in ISO 8601 format. eg. `1963-11-22T18:30:00Z`
        active_users (int | Unset):
        active_devices (int | Unset):
        requests (int | Unset):
        messages_received (int | Unset):
        messages_stored (int | Unset):
    """

    capture_time: datetime.datetime | Unset = UNSET
    active_users: int | Unset = UNSET
    active_devices: int | Unset = UNSET
    requests: int | Unset = UNSET
    messages_received: int | Unset = UNSET
    messages_stored: int | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        capture_time: str | Unset = UNSET
        if not isinstance(self.capture_time, Unset):
            capture_time = self.capture_time.isoformat()

        active_users = self.active_users

        active_devices = self.active_devices

        requests = self.requests

        messages_received = self.messages_received

        messages_stored = self.messages_stored

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if capture_time is not UNSET:
            field_dict["captureTime"] = capture_time
        if active_users is not UNSET:
            field_dict["activeUsers"] = active_users
        if active_devices is not UNSET:
            field_dict["activeDevices"] = active_devices
        if requests is not UNSET:
            field_dict["requests"] = requests
        if messages_received is not UNSET:
            field_dict["messagesReceived"] = messages_received
        if messages_stored is not UNSET:
            field_dict["messagesStored"] = messages_stored

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        _capture_time = d.pop("captureTime", UNSET)
        capture_time: datetime.datetime | Unset
        if isinstance(_capture_time, Unset):
            capture_time = UNSET
        else:
            capture_time = isoparse(_capture_time)

        active_users = d.pop("activeUsers", UNSET)

        active_devices = d.pop("activeDevices", UNSET)

        requests = d.pop("requests", UNSET)

        messages_received = d.pop("messagesReceived", UNSET)

        messages_stored = d.pop("messagesStored", UNSET)

        statistics = cls(
            capture_time=capture_time,
            active_users=active_users,
            active_devices=active_devices,
            requests=requests,
            messages_received=messages_received,
            messages_stored=messages_stored,
        )

        statistics.additional_properties = d
        return statistics

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
