from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.geofence_attributes import GeofenceAttributes


T = TypeVar("T", bound="Geofence")


@_attrs_define
class Geofence:
    """
    Attributes:
        id (int | Unset):
        name (str | Unset):
        description (str | Unset):
        area (str | Unset):
        calendar_id (int | Unset):
        attributes (GeofenceAttributes | Unset):
    """

    id: int | Unset = UNSET
    name: str | Unset = UNSET
    description: str | Unset = UNSET
    area: str | Unset = UNSET
    calendar_id: int | Unset = UNSET
    attributes: GeofenceAttributes | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        description = self.description

        area = self.area

        calendar_id = self.calendar_id

        attributes: dict[str, Any] | Unset = UNSET
        if not isinstance(self.attributes, Unset):
            attributes = self.attributes.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if name is not UNSET:
            field_dict["name"] = name
        if description is not UNSET:
            field_dict["description"] = description
        if area is not UNSET:
            field_dict["area"] = area
        if calendar_id is not UNSET:
            field_dict["calendarId"] = calendar_id
        if attributes is not UNSET:
            field_dict["attributes"] = attributes

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.geofence_attributes import GeofenceAttributes

        d = dict(src_dict)
        id = d.pop("id", UNSET)

        name = d.pop("name", UNSET)

        description = d.pop("description", UNSET)

        area = d.pop("area", UNSET)

        calendar_id = d.pop("calendarId", UNSET)

        _attributes = d.pop("attributes", UNSET)
        attributes: GeofenceAttributes | Unset
        if isinstance(_attributes, Unset):
            attributes = UNSET
        else:
            attributes = GeofenceAttributes.from_dict(_attributes)

        geofence = cls(
            id=id,
            name=name,
            description=description,
            area=area,
            calendar_id=calendar_id,
            attributes=attributes,
        )

        geofence.additional_properties = d
        return geofence

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
