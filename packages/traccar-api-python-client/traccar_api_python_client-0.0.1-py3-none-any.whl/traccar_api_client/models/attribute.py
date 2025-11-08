from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="Attribute")


@_attrs_define
class Attribute:
    """
    Attributes:
        id (int | Unset):
        description (str | Unset):
        attribute (str | Unset):
        expression (str | Unset):
        type_ (str | Unset): String|Number|Boolean
    """

    id: int | Unset = UNSET
    description: str | Unset = UNSET
    attribute: str | Unset = UNSET
    expression: str | Unset = UNSET
    type_: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        description = self.description

        attribute = self.attribute

        expression = self.expression

        type_ = self.type_

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if description is not UNSET:
            field_dict["description"] = description
        if attribute is not UNSET:
            field_dict["attribute"] = attribute
        if expression is not UNSET:
            field_dict["expression"] = expression
        if type_ is not UNSET:
            field_dict["type"] = type_

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id", UNSET)

        description = d.pop("description", UNSET)

        attribute = d.pop("attribute", UNSET)

        expression = d.pop("expression", UNSET)

        type_ = d.pop("type", UNSET)

        attribute = cls(
            id=id,
            description=description,
            attribute=attribute,
            expression=expression,
            type_=type_,
        )

        attribute.additional_properties = d
        return attribute

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
