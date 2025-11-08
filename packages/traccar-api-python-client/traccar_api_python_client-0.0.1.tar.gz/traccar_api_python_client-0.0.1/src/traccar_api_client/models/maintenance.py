from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.maintenance_attributes import MaintenanceAttributes


T = TypeVar("T", bound="Maintenance")


@_attrs_define
class Maintenance:
    """
    Attributes:
        id (int | Unset):
        name (str | Unset):
        type_ (str | Unset):
        start (float | Unset):
        period (float | Unset):
        attributes (MaintenanceAttributes | Unset):
    """

    id: int | Unset = UNSET
    name: str | Unset = UNSET
    type_: str | Unset = UNSET
    start: float | Unset = UNSET
    period: float | Unset = UNSET
    attributes: MaintenanceAttributes | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        type_ = self.type_

        start = self.start

        period = self.period

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
        if type_ is not UNSET:
            field_dict["type"] = type_
        if start is not UNSET:
            field_dict["start"] = start
        if period is not UNSET:
            field_dict["period"] = period
        if attributes is not UNSET:
            field_dict["attributes"] = attributes

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.maintenance_attributes import MaintenanceAttributes

        d = dict(src_dict)
        id = d.pop("id", UNSET)

        name = d.pop("name", UNSET)

        type_ = d.pop("type", UNSET)

        start = d.pop("start", UNSET)

        period = d.pop("period", UNSET)

        _attributes = d.pop("attributes", UNSET)
        attributes: MaintenanceAttributes | Unset
        if isinstance(_attributes, Unset):
            attributes = UNSET
        else:
            attributes = MaintenanceAttributes.from_dict(_attributes)

        maintenance = cls(
            id=id,
            name=name,
            type_=type_,
            start=start,
            period=period,
            attributes=attributes,
        )

        maintenance.additional_properties = d
        return maintenance

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
