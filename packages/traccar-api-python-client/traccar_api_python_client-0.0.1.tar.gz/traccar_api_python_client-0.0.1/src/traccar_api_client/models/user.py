from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.user_attributes import UserAttributes


T = TypeVar("T", bound="User")


@_attrs_define
class User:
    """
    Attributes:
        id (int | Unset):
        name (str | Unset):
        email (str | Unset):
        phone (None | str | Unset):
        readonly (bool | Unset):
        administrator (bool | Unset):
        map_ (None | str | Unset):
        latitude (float | Unset):
        longitude (float | Unset):
        zoom (int | Unset):
        password (str | Unset):
        coordinate_format (None | str | Unset):
        disabled (bool | Unset):
        expiration_time (datetime.datetime | None | Unset): in ISO 8601 format. eg. `1963-11-22T18:30:00Z`
        device_limit (int | Unset):
        user_limit (int | Unset):
        device_readonly (bool | Unset):
        limit_commands (bool | Unset):
        fixed_email (bool | Unset):
        poi_layer (None | str | Unset):
        attributes (UserAttributes | Unset):
    """

    id: int | Unset = UNSET
    name: str | Unset = UNSET
    email: str | Unset = UNSET
    phone: None | str | Unset = UNSET
    readonly: bool | Unset = UNSET
    administrator: bool | Unset = UNSET
    map_: None | str | Unset = UNSET
    latitude: float | Unset = UNSET
    longitude: float | Unset = UNSET
    zoom: int | Unset = UNSET
    password: str | Unset = UNSET
    coordinate_format: None | str | Unset = UNSET
    disabled: bool | Unset = UNSET
    expiration_time: datetime.datetime | None | Unset = UNSET
    device_limit: int | Unset = UNSET
    user_limit: int | Unset = UNSET
    device_readonly: bool | Unset = UNSET
    limit_commands: bool | Unset = UNSET
    fixed_email: bool | Unset = UNSET
    poi_layer: None | str | Unset = UNSET
    attributes: UserAttributes | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        email = self.email

        phone: None | str | Unset
        if isinstance(self.phone, Unset):
            phone = UNSET
        else:
            phone = self.phone

        readonly = self.readonly

        administrator = self.administrator

        map_: None | str | Unset
        if isinstance(self.map_, Unset):
            map_ = UNSET
        else:
            map_ = self.map_

        latitude = self.latitude

        longitude = self.longitude

        zoom = self.zoom

        password = self.password

        coordinate_format: None | str | Unset
        if isinstance(self.coordinate_format, Unset):
            coordinate_format = UNSET
        else:
            coordinate_format = self.coordinate_format

        disabled = self.disabled

        expiration_time: None | str | Unset
        if isinstance(self.expiration_time, Unset):
            expiration_time = UNSET
        elif isinstance(self.expiration_time, datetime.datetime):
            expiration_time = self.expiration_time.isoformat()
        else:
            expiration_time = self.expiration_time

        device_limit = self.device_limit

        user_limit = self.user_limit

        device_readonly = self.device_readonly

        limit_commands = self.limit_commands

        fixed_email = self.fixed_email

        poi_layer: None | str | Unset
        if isinstance(self.poi_layer, Unset):
            poi_layer = UNSET
        else:
            poi_layer = self.poi_layer

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
        if email is not UNSET:
            field_dict["email"] = email
        if phone is not UNSET:
            field_dict["phone"] = phone
        if readonly is not UNSET:
            field_dict["readonly"] = readonly
        if administrator is not UNSET:
            field_dict["administrator"] = administrator
        if map_ is not UNSET:
            field_dict["map"] = map_
        if latitude is not UNSET:
            field_dict["latitude"] = latitude
        if longitude is not UNSET:
            field_dict["longitude"] = longitude
        if zoom is not UNSET:
            field_dict["zoom"] = zoom
        if password is not UNSET:
            field_dict["password"] = password
        if coordinate_format is not UNSET:
            field_dict["coordinateFormat"] = coordinate_format
        if disabled is not UNSET:
            field_dict["disabled"] = disabled
        if expiration_time is not UNSET:
            field_dict["expirationTime"] = expiration_time
        if device_limit is not UNSET:
            field_dict["deviceLimit"] = device_limit
        if user_limit is not UNSET:
            field_dict["userLimit"] = user_limit
        if device_readonly is not UNSET:
            field_dict["deviceReadonly"] = device_readonly
        if limit_commands is not UNSET:
            field_dict["limitCommands"] = limit_commands
        if fixed_email is not UNSET:
            field_dict["fixedEmail"] = fixed_email
        if poi_layer is not UNSET:
            field_dict["poiLayer"] = poi_layer
        if attributes is not UNSET:
            field_dict["attributes"] = attributes

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.user_attributes import UserAttributes

        d = dict(src_dict)
        id = d.pop("id", UNSET)

        name = d.pop("name", UNSET)

        email = d.pop("email", UNSET)

        def _parse_phone(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        phone = _parse_phone(d.pop("phone", UNSET))

        readonly = d.pop("readonly", UNSET)

        administrator = d.pop("administrator", UNSET)

        def _parse_map_(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        map_ = _parse_map_(d.pop("map", UNSET))

        latitude = d.pop("latitude", UNSET)

        longitude = d.pop("longitude", UNSET)

        zoom = d.pop("zoom", UNSET)

        password = d.pop("password", UNSET)

        def _parse_coordinate_format(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        coordinate_format = _parse_coordinate_format(d.pop("coordinateFormat", UNSET))

        disabled = d.pop("disabled", UNSET)

        def _parse_expiration_time(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                expiration_time_type_0 = isoparse(data)

                return expiration_time_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        expiration_time = _parse_expiration_time(d.pop("expirationTime", UNSET))

        device_limit = d.pop("deviceLimit", UNSET)

        user_limit = d.pop("userLimit", UNSET)

        device_readonly = d.pop("deviceReadonly", UNSET)

        limit_commands = d.pop("limitCommands", UNSET)

        fixed_email = d.pop("fixedEmail", UNSET)

        def _parse_poi_layer(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        poi_layer = _parse_poi_layer(d.pop("poiLayer", UNSET))

        _attributes = d.pop("attributes", UNSET)
        attributes: UserAttributes | Unset
        if isinstance(_attributes, Unset):
            attributes = UNSET
        else:
            attributes = UserAttributes.from_dict(_attributes)

        user = cls(
            id=id,
            name=name,
            email=email,
            phone=phone,
            readonly=readonly,
            administrator=administrator,
            map_=map_,
            latitude=latitude,
            longitude=longitude,
            zoom=zoom,
            password=password,
            coordinate_format=coordinate_format,
            disabled=disabled,
            expiration_time=expiration_time,
            device_limit=device_limit,
            user_limit=user_limit,
            device_readonly=device_readonly,
            limit_commands=limit_commands,
            fixed_email=fixed_email,
            poi_layer=poi_layer,
            attributes=attributes,
        )

        user.additional_properties = d
        return user

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
