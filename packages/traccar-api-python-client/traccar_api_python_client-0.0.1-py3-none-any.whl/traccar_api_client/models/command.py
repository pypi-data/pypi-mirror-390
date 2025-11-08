from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.command_attributes import CommandAttributes


T = TypeVar("T", bound="Command")


@_attrs_define
class Command:
    """
    Attributes:
        id (int | Unset):
        device_id (int | Unset):
        description (str | Unset):
        type_ (str | Unset):
        attributes (CommandAttributes | Unset):
    """

    id: int | Unset = UNSET
    device_id: int | Unset = UNSET
    description: str | Unset = UNSET
    type_: str | Unset = UNSET
    attributes: CommandAttributes | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        device_id = self.device_id

        description = self.description

        type_ = self.type_

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
        if description is not UNSET:
            field_dict["description"] = description
        if type_ is not UNSET:
            field_dict["type"] = type_
        if attributes is not UNSET:
            field_dict["attributes"] = attributes

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.command_attributes import CommandAttributes

        d = dict(src_dict)
        id = d.pop("id", UNSET)

        device_id = d.pop("deviceId", UNSET)

        description = d.pop("description", UNSET)

        type_ = d.pop("type", UNSET)

        _attributes = d.pop("attributes", UNSET)
        attributes: CommandAttributes | Unset
        if isinstance(_attributes, Unset):
            attributes = UNSET
        else:
            attributes = CommandAttributes.from_dict(_attributes)

        command = cls(
            id=id,
            device_id=device_id,
            description=description,
            type_=type_,
            attributes=attributes,
        )

        command.additional_properties = d
        return command

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
