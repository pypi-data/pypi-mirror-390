from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.position_attributes import PositionAttributes
    from ..models.position_network import PositionNetwork


T = TypeVar("T", bound="Position")


@_attrs_define
class Position:
    """
    Attributes:
        id (int | Unset):
        device_id (int | Unset):
        protocol (str | Unset):
        device_time (datetime.datetime | Unset): in ISO 8601 format. eg. `1963-11-22T18:30:00Z`
        fix_time (datetime.datetime | Unset): in ISO 8601 format. eg. `1963-11-22T18:30:00Z`
        server_time (datetime.datetime | Unset): in ISO 8601 format. eg. `1963-11-22T18:30:00Z`
        valid (bool | Unset):
        latitude (float | Unset):
        longitude (float | Unset):
        altitude (float | Unset):
        speed (float | Unset): in knots
        course (float | Unset):
        address (str | Unset):
        accuracy (float | Unset):
        network (PositionNetwork | Unset):
        geofence_ids (list[int] | Unset):
        attributes (PositionAttributes | Unset):
    """

    id: int | Unset = UNSET
    device_id: int | Unset = UNSET
    protocol: str | Unset = UNSET
    device_time: datetime.datetime | Unset = UNSET
    fix_time: datetime.datetime | Unset = UNSET
    server_time: datetime.datetime | Unset = UNSET
    valid: bool | Unset = UNSET
    latitude: float | Unset = UNSET
    longitude: float | Unset = UNSET
    altitude: float | Unset = UNSET
    speed: float | Unset = UNSET
    course: float | Unset = UNSET
    address: str | Unset = UNSET
    accuracy: float | Unset = UNSET
    network: PositionNetwork | Unset = UNSET
    geofence_ids: list[int] | Unset = UNSET
    attributes: PositionAttributes | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        device_id = self.device_id

        protocol = self.protocol

        device_time: str | Unset = UNSET
        if not isinstance(self.device_time, Unset):
            device_time = self.device_time.isoformat()

        fix_time: str | Unset = UNSET
        if not isinstance(self.fix_time, Unset):
            fix_time = self.fix_time.isoformat()

        server_time: str | Unset = UNSET
        if not isinstance(self.server_time, Unset):
            server_time = self.server_time.isoformat()

        valid = self.valid

        latitude = self.latitude

        longitude = self.longitude

        altitude = self.altitude

        speed = self.speed

        course = self.course

        address = self.address

        accuracy = self.accuracy

        network: dict[str, Any] | Unset = UNSET
        if not isinstance(self.network, Unset):
            network = self.network.to_dict()

        geofence_ids: list[int] | Unset = UNSET
        if not isinstance(self.geofence_ids, Unset):
            geofence_ids = self.geofence_ids

        attributes: dict[str, Any] | Unset = UNSET
        if not isinstance(self.attributes, Unset):
            attributes = self.attributes.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if device_id is not UNSET:
            field_dict["deviceId"] = device_id
        if protocol is not UNSET:
            field_dict["protocol"] = protocol
        if device_time is not UNSET:
            field_dict["deviceTime"] = device_time
        if fix_time is not UNSET:
            field_dict["fixTime"] = fix_time
        if server_time is not UNSET:
            field_dict["serverTime"] = server_time
        if valid is not UNSET:
            field_dict["valid"] = valid
        if latitude is not UNSET:
            field_dict["latitude"] = latitude
        if longitude is not UNSET:
            field_dict["longitude"] = longitude
        if altitude is not UNSET:
            field_dict["altitude"] = altitude
        if speed is not UNSET:
            field_dict["speed"] = speed
        if course is not UNSET:
            field_dict["course"] = course
        if address is not UNSET:
            field_dict["address"] = address
        if accuracy is not UNSET:
            field_dict["accuracy"] = accuracy
        if network is not UNSET:
            field_dict["network"] = network
        if geofence_ids is not UNSET:
            field_dict["geofenceIds"] = geofence_ids
        if attributes is not UNSET:
            field_dict["attributes"] = attributes

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.position_attributes import PositionAttributes
        from ..models.position_network import PositionNetwork

        d = dict(src_dict)
        id = d.pop("id", UNSET)

        device_id = d.pop("deviceId", UNSET)

        protocol = d.pop("protocol", UNSET)

        _device_time = d.pop("deviceTime", UNSET)
        device_time: datetime.datetime | Unset
        if isinstance(_device_time, Unset):
            device_time = UNSET
        else:
            device_time = isoparse(_device_time)

        _fix_time = d.pop("fixTime", UNSET)
        fix_time: datetime.datetime | Unset
        if isinstance(_fix_time, Unset):
            fix_time = UNSET
        else:
            fix_time = isoparse(_fix_time)

        _server_time = d.pop("serverTime", UNSET)
        server_time: datetime.datetime | Unset
        if isinstance(_server_time, Unset):
            server_time = UNSET
        else:
            server_time = isoparse(_server_time)

        valid = d.pop("valid", UNSET)

        latitude = d.pop("latitude", UNSET)

        longitude = d.pop("longitude", UNSET)

        altitude = d.pop("altitude", UNSET)

        speed = d.pop("speed", UNSET)

        course = d.pop("course", UNSET)

        address = d.pop("address", UNSET)

        accuracy = d.pop("accuracy", UNSET)

        _network = d.pop("network", UNSET)
        network: PositionNetwork | Unset
        if isinstance(_network, Unset):
            network = UNSET
        else:
            network = PositionNetwork.from_dict(_network)

        geofence_ids = cast(list[int], d.pop("geofenceIds", UNSET))

        _attributes = d.pop("attributes", UNSET)
        attributes: PositionAttributes | Unset
        if isinstance(_attributes, Unset):
            attributes = UNSET
        else:
            attributes = PositionAttributes.from_dict(_attributes)

        position = cls(
            id=id,
            device_id=device_id,
            protocol=protocol,
            device_time=device_time,
            fix_time=fix_time,
            server_time=server_time,
            valid=valid,
            latitude=latitude,
            longitude=longitude,
            altitude=altitude,
            speed=speed,
            course=course,
            address=address,
            accuracy=accuracy,
            network=network,
            geofence_ids=geofence_ids,
            attributes=attributes,
        )

        position.additional_properties = d
        return position

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
