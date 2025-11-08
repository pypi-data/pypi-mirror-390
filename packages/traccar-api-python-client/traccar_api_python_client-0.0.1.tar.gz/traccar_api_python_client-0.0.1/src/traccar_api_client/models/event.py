from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.event_attributes import EventAttributes


T = TypeVar("T", bound="Event")


@_attrs_define
class Event:
    """
    Attributes:
        id (int | Unset):
        type_ (str | Unset):
        event_time (datetime.datetime | Unset): in ISO 8601 format. eg. `1963-11-22T18:30:00Z`
        device_id (int | Unset):
        position_id (int | Unset):
        geofence_id (int | Unset):
        maintenance_id (int | Unset):
        attributes (EventAttributes | Unset):
    """

    id: int | Unset = UNSET
    type_: str | Unset = UNSET
    event_time: datetime.datetime | Unset = UNSET
    device_id: int | Unset = UNSET
    position_id: int | Unset = UNSET
    geofence_id: int | Unset = UNSET
    maintenance_id: int | Unset = UNSET
    attributes: EventAttributes | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        type_ = self.type_

        event_time: str | Unset = UNSET
        if not isinstance(self.event_time, Unset):
            event_time = self.event_time.isoformat()

        device_id = self.device_id

        position_id = self.position_id

        geofence_id = self.geofence_id

        maintenance_id = self.maintenance_id

        attributes: dict[str, Any] | Unset = UNSET
        if not isinstance(self.attributes, Unset):
            attributes = self.attributes.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if type_ is not UNSET:
            field_dict["type"] = type_
        if event_time is not UNSET:
            field_dict["eventTime"] = event_time
        if device_id is not UNSET:
            field_dict["deviceId"] = device_id
        if position_id is not UNSET:
            field_dict["positionId"] = position_id
        if geofence_id is not UNSET:
            field_dict["geofenceId"] = geofence_id
        if maintenance_id is not UNSET:
            field_dict["maintenanceId"] = maintenance_id
        if attributes is not UNSET:
            field_dict["attributes"] = attributes

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.event_attributes import EventAttributes

        d = dict(src_dict)
        id = d.pop("id", UNSET)

        type_ = d.pop("type", UNSET)

        _event_time = d.pop("eventTime", UNSET)
        event_time: datetime.datetime | Unset
        if isinstance(_event_time, Unset):
            event_time = UNSET
        else:
            event_time = isoparse(_event_time)

        device_id = d.pop("deviceId", UNSET)

        position_id = d.pop("positionId", UNSET)

        geofence_id = d.pop("geofenceId", UNSET)

        maintenance_id = d.pop("maintenanceId", UNSET)

        _attributes = d.pop("attributes", UNSET)
        attributes: EventAttributes | Unset
        if isinstance(_attributes, Unset):
            attributes = UNSET
        else:
            attributes = EventAttributes.from_dict(_attributes)

        event = cls(
            id=id,
            type_=type_,
            event_time=event_time,
            device_id=device_id,
            position_id=position_id,
            geofence_id=geofence_id,
            maintenance_id=maintenance_id,
            attributes=attributes,
        )

        event.additional_properties = d
        return event

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
