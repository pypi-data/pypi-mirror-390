from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.device_attributes import DeviceAttributes


T = TypeVar("T", bound="Device")


@_attrs_define
class Device:
    """
    Attributes:
        id (int | Unset):
        name (str | Unset):
        unique_id (str | Unset):
        status (str | Unset):
        disabled (bool | Unset):
        last_update (datetime.datetime | None | Unset): in ISO 8601 format. eg. `1963-11-22T18:30:00Z`
        position_id (int | None | Unset):
        group_id (int | None | Unset):
        phone (None | str | Unset):
        model (None | str | Unset):
        contact (None | str | Unset):
        category (None | str | Unset):
        attributes (DeviceAttributes | Unset):
    """

    id: int | Unset = UNSET
    name: str | Unset = UNSET
    unique_id: str | Unset = UNSET
    status: str | Unset = UNSET
    disabled: bool | Unset = UNSET
    last_update: datetime.datetime | None | Unset = UNSET
    position_id: int | None | Unset = UNSET
    group_id: int | None | Unset = UNSET
    phone: None | str | Unset = UNSET
    model: None | str | Unset = UNSET
    contact: None | str | Unset = UNSET
    category: None | str | Unset = UNSET
    attributes: DeviceAttributes | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        unique_id = self.unique_id

        status = self.status

        disabled = self.disabled

        last_update: None | str | Unset
        if isinstance(self.last_update, Unset):
            last_update = UNSET
        elif isinstance(self.last_update, datetime.datetime):
            last_update = self.last_update.isoformat()
        else:
            last_update = self.last_update

        position_id: int | None | Unset
        if isinstance(self.position_id, Unset):
            position_id = UNSET
        else:
            position_id = self.position_id

        group_id: int | None | Unset
        if isinstance(self.group_id, Unset):
            group_id = UNSET
        else:
            group_id = self.group_id

        phone: None | str | Unset
        if isinstance(self.phone, Unset):
            phone = UNSET
        else:
            phone = self.phone

        model: None | str | Unset
        if isinstance(self.model, Unset):
            model = UNSET
        else:
            model = self.model

        contact: None | str | Unset
        if isinstance(self.contact, Unset):
            contact = UNSET
        else:
            contact = self.contact

        category: None | str | Unset
        if isinstance(self.category, Unset):
            category = UNSET
        else:
            category = self.category

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
        if status is not UNSET:
            field_dict["status"] = status
        if disabled is not UNSET:
            field_dict["disabled"] = disabled
        if last_update is not UNSET:
            field_dict["lastUpdate"] = last_update
        if position_id is not UNSET:
            field_dict["positionId"] = position_id
        if group_id is not UNSET:
            field_dict["groupId"] = group_id
        if phone is not UNSET:
            field_dict["phone"] = phone
        if model is not UNSET:
            field_dict["model"] = model
        if contact is not UNSET:
            field_dict["contact"] = contact
        if category is not UNSET:
            field_dict["category"] = category
        if attributes is not UNSET:
            field_dict["attributes"] = attributes

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.device_attributes import DeviceAttributes

        d = dict(src_dict)
        id = d.pop("id", UNSET)

        name = d.pop("name", UNSET)

        unique_id = d.pop("uniqueId", UNSET)

        status = d.pop("status", UNSET)

        disabled = d.pop("disabled", UNSET)

        def _parse_last_update(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                last_update_type_0 = isoparse(data)

                return last_update_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        last_update = _parse_last_update(d.pop("lastUpdate", UNSET))

        def _parse_position_id(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        position_id = _parse_position_id(d.pop("positionId", UNSET))

        def _parse_group_id(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        group_id = _parse_group_id(d.pop("groupId", UNSET))

        def _parse_phone(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        phone = _parse_phone(d.pop("phone", UNSET))

        def _parse_model(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        model = _parse_model(d.pop("model", UNSET))

        def _parse_contact(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        contact = _parse_contact(d.pop("contact", UNSET))

        def _parse_category(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        category = _parse_category(d.pop("category", UNSET))

        _attributes = d.pop("attributes", UNSET)
        attributes: DeviceAttributes | Unset
        if isinstance(_attributes, Unset):
            attributes = UNSET
        else:
            attributes = DeviceAttributes.from_dict(_attributes)

        device = cls(
            id=id,
            name=name,
            unique_id=unique_id,
            status=status,
            disabled=disabled,
            last_update=last_update,
            position_id=position_id,
            group_id=group_id,
            phone=phone,
            model=model,
            contact=contact,
            category=category,
            attributes=attributes,
        )

        device.additional_properties = d
        return device

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
