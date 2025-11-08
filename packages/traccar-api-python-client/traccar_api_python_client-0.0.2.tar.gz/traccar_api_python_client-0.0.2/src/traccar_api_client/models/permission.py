from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="Permission")


@_attrs_define
class Permission:
    """This is a permission map that contain two object indexes. It is used to link/unlink objects. Order is important.
    Example: { deviceId:8, geofenceId: 16 }

        Attributes:
            user_id (int | Unset): User id, can be only first parameter
            device_id (int | Unset): Device id, can be first parameter or second only in combination with userId
            group_id (int | Unset): Group id, can be first parameter or second only in combination with userId
            geofence_id (int | Unset): Geofence id, can be second parameter only
            notification_id (int | Unset): Notification id, can be second parameter only
            calendar_id (int | Unset): Calendar id, can be second parameter only and only in combination with userId
            attribute_id (int | Unset): Computed attribute id, can be second parameter only
            driver_id (int | Unset): Driver id, can be second parameter only
            managed_user_id (int | Unset): User id, can be second parameter only and only in combination with userId
            command_id (int | Unset): Saved command id, can be second parameter only
    """

    user_id: int | Unset = UNSET
    device_id: int | Unset = UNSET
    group_id: int | Unset = UNSET
    geofence_id: int | Unset = UNSET
    notification_id: int | Unset = UNSET
    calendar_id: int | Unset = UNSET
    attribute_id: int | Unset = UNSET
    driver_id: int | Unset = UNSET
    managed_user_id: int | Unset = UNSET
    command_id: int | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        user_id = self.user_id

        device_id = self.device_id

        group_id = self.group_id

        geofence_id = self.geofence_id

        notification_id = self.notification_id

        calendar_id = self.calendar_id

        attribute_id = self.attribute_id

        driver_id = self.driver_id

        managed_user_id = self.managed_user_id

        command_id = self.command_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if user_id is not UNSET:
            field_dict["userId"] = user_id
        if device_id is not UNSET:
            field_dict["deviceId"] = device_id
        if group_id is not UNSET:
            field_dict["groupId"] = group_id
        if geofence_id is not UNSET:
            field_dict["geofenceId"] = geofence_id
        if notification_id is not UNSET:
            field_dict["notificationId"] = notification_id
        if calendar_id is not UNSET:
            field_dict["calendarId"] = calendar_id
        if attribute_id is not UNSET:
            field_dict["attributeId"] = attribute_id
        if driver_id is not UNSET:
            field_dict["driverId"] = driver_id
        if managed_user_id is not UNSET:
            field_dict["managedUserId"] = managed_user_id
        if command_id is not UNSET:
            field_dict["commandId"] = command_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        user_id = d.pop("userId", UNSET)

        device_id = d.pop("deviceId", UNSET)

        group_id = d.pop("groupId", UNSET)

        geofence_id = d.pop("geofenceId", UNSET)

        notification_id = d.pop("notificationId", UNSET)

        calendar_id = d.pop("calendarId", UNSET)

        attribute_id = d.pop("attributeId", UNSET)

        driver_id = d.pop("driverId", UNSET)

        managed_user_id = d.pop("managedUserId", UNSET)

        command_id = d.pop("commandId", UNSET)

        permission = cls(
            user_id=user_id,
            device_id=device_id,
            group_id=group_id,
            geofence_id=geofence_id,
            notification_id=notification_id,
            calendar_id=calendar_id,
            attribute_id=attribute_id,
            driver_id=driver_id,
            managed_user_id=managed_user_id,
            command_id=command_id,
        )

        permission.additional_properties = d
        return permission

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
