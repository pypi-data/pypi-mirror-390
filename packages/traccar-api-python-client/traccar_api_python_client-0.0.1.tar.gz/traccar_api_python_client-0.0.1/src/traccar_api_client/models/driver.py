from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.driver_attributes import DriverAttributes


T = TypeVar("T", bound="Driver")


@_attrs_define
class Driver:
    """
    Attributes:
        id (int | Unset):
        name (str | Unset):
        unique_id (str | Unset):
        attributes (DriverAttributes | Unset):
    """

    id: int | Unset = UNSET
    name: str | Unset = UNSET
    unique_id: str | Unset = UNSET
    attributes: DriverAttributes | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        unique_id = self.unique_id

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
        if unique_id is not UNSET:
            field_dict["uniqueId"] = unique_id
        if attributes is not UNSET:
            field_dict["attributes"] = attributes

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.driver_attributes import DriverAttributes

        d = dict(src_dict)
        id = d.pop("id", UNSET)

        name = d.pop("name", UNSET)

        unique_id = d.pop("uniqueId", UNSET)

        _attributes = d.pop("attributes", UNSET)
        attributes: DriverAttributes | Unset
        if isinstance(_attributes, Unset):
            attributes = UNSET
        else:
            attributes = DriverAttributes.from_dict(_attributes)

        driver = cls(
            id=id,
            name=name,
            unique_id=unique_id,
            attributes=attributes,
        )

        driver.additional_properties = d
        return driver

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
