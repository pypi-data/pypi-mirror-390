from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.notification_attributes import NotificationAttributes


T = TypeVar("T", bound="Notification")


@_attrs_define
class Notification:
    """
    Attributes:
        id (int | Unset):
        type_ (str | Unset):
        description (None | str | Unset):
        always (bool | Unset):
        command_id (int | Unset):
        notificators (str | Unset):
        calendar_id (int | Unset):
        attributes (NotificationAttributes | Unset):
    """

    id: int | Unset = UNSET
    type_: str | Unset = UNSET
    description: None | str | Unset = UNSET
    always: bool | Unset = UNSET
    command_id: int | Unset = UNSET
    notificators: str | Unset = UNSET
    calendar_id: int | Unset = UNSET
    attributes: NotificationAttributes | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        type_ = self.type_

        description: None | str | Unset
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        always = self.always

        command_id = self.command_id

        notificators = self.notificators

        calendar_id = self.calendar_id

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
        if description is not UNSET:
            field_dict["description"] = description
        if always is not UNSET:
            field_dict["always"] = always
        if command_id is not UNSET:
            field_dict["commandId"] = command_id
        if notificators is not UNSET:
            field_dict["notificators"] = notificators
        if calendar_id is not UNSET:
            field_dict["calendarId"] = calendar_id
        if attributes is not UNSET:
            field_dict["attributes"] = attributes

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.notification_attributes import NotificationAttributes

        d = dict(src_dict)
        id = d.pop("id", UNSET)

        type_ = d.pop("type", UNSET)

        def _parse_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        description = _parse_description(d.pop("description", UNSET))

        always = d.pop("always", UNSET)

        command_id = d.pop("commandId", UNSET)

        notificators = d.pop("notificators", UNSET)

        calendar_id = d.pop("calendarId", UNSET)

        _attributes = d.pop("attributes", UNSET)
        attributes: NotificationAttributes | Unset
        if isinstance(_attributes, Unset):
            attributes = UNSET
        else:
            attributes = NotificationAttributes.from_dict(_attributes)

        notification = cls(
            id=id,
            type_=type_,
            description=description,
            always=always,
            command_id=command_id,
            notificators=notificators,
            calendar_id=calendar_id,
            attributes=attributes,
        )

        notification.additional_properties = d
        return notification

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
