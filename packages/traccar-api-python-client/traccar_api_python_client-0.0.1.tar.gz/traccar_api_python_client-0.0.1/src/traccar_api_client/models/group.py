from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.group_attributes import GroupAttributes


T = TypeVar("T", bound="Group")


@_attrs_define
class Group:
    """
    Attributes:
        id (int | Unset):
        name (str | Unset):
        group_id (int | Unset):
        attributes (GroupAttributes | Unset):
    """

    id: int | Unset = UNSET
    name: str | Unset = UNSET
    group_id: int | Unset = UNSET
    attributes: GroupAttributes | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        group_id = self.group_id

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
        if group_id is not UNSET:
            field_dict["groupId"] = group_id
        if attributes is not UNSET:
            field_dict["attributes"] = attributes

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.group_attributes import GroupAttributes

        d = dict(src_dict)
        id = d.pop("id", UNSET)

        name = d.pop("name", UNSET)

        group_id = d.pop("groupId", UNSET)

        _attributes = d.pop("attributes", UNSET)
        attributes: GroupAttributes | Unset
        if isinstance(_attributes, Unset):
            attributes = UNSET
        else:
            attributes = GroupAttributes.from_dict(_attributes)

        group = cls(
            id=id,
            name=name,
            group_id=group_id,
            attributes=attributes,
        )

        group.additional_properties = d
        return group

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
