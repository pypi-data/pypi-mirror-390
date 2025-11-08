from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.server_attributes import ServerAttributes


T = TypeVar("T", bound="Server")


@_attrs_define
class Server:
    """
    Attributes:
        id (int | Unset):
        registration (bool | Unset):
        readonly (bool | Unset):
        device_readonly (bool | Unset):
        limit_commands (bool | Unset):
        map_ (str | Unset):
        bing_key (str | Unset):
        map_url (str | Unset):
        poi_layer (str | Unset):
        latitude (float | Unset):
        longitude (float | Unset):
        zoom (int | Unset):
        version (str | Unset):
        force_settings (bool | Unset):
        coordinate_format (str | Unset):
        open_id_enabled (bool | Unset):
        open_id_force (bool | Unset):
        attributes (ServerAttributes | Unset):
    """

    id: int | Unset = UNSET
    registration: bool | Unset = UNSET
    readonly: bool | Unset = UNSET
    device_readonly: bool | Unset = UNSET
    limit_commands: bool | Unset = UNSET
    map_: str | Unset = UNSET
    bing_key: str | Unset = UNSET
    map_url: str | Unset = UNSET
    poi_layer: str | Unset = UNSET
    latitude: float | Unset = UNSET
    longitude: float | Unset = UNSET
    zoom: int | Unset = UNSET
    version: str | Unset = UNSET
    force_settings: bool | Unset = UNSET
    coordinate_format: str | Unset = UNSET
    open_id_enabled: bool | Unset = UNSET
    open_id_force: bool | Unset = UNSET
    attributes: ServerAttributes | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        registration = self.registration

        readonly = self.readonly

        device_readonly = self.device_readonly

        limit_commands = self.limit_commands

        map_ = self.map_

        bing_key = self.bing_key

        map_url = self.map_url

        poi_layer = self.poi_layer

        latitude = self.latitude

        longitude = self.longitude

        zoom = self.zoom

        version = self.version

        force_settings = self.force_settings

        coordinate_format = self.coordinate_format

        open_id_enabled = self.open_id_enabled

        open_id_force = self.open_id_force

        attributes: dict[str, Any] | Unset = UNSET
        if not isinstance(self.attributes, Unset):
            attributes = self.attributes.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if registration is not UNSET:
            field_dict["registration"] = registration
        if readonly is not UNSET:
            field_dict["readonly"] = readonly
        if device_readonly is not UNSET:
            field_dict["deviceReadonly"] = device_readonly
        if limit_commands is not UNSET:
            field_dict["limitCommands"] = limit_commands
        if map_ is not UNSET:
            field_dict["map"] = map_
        if bing_key is not UNSET:
            field_dict["bingKey"] = bing_key
        if map_url is not UNSET:
            field_dict["mapUrl"] = map_url
        if poi_layer is not UNSET:
            field_dict["poiLayer"] = poi_layer
        if latitude is not UNSET:
            field_dict["latitude"] = latitude
        if longitude is not UNSET:
            field_dict["longitude"] = longitude
        if zoom is not UNSET:
            field_dict["zoom"] = zoom
        if version is not UNSET:
            field_dict["version"] = version
        if force_settings is not UNSET:
            field_dict["forceSettings"] = force_settings
        if coordinate_format is not UNSET:
            field_dict["coordinateFormat"] = coordinate_format
        if open_id_enabled is not UNSET:
            field_dict["openIdEnabled"] = open_id_enabled
        if open_id_force is not UNSET:
            field_dict["openIdForce"] = open_id_force
        if attributes is not UNSET:
            field_dict["attributes"] = attributes

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.server_attributes import ServerAttributes

        d = dict(src_dict)
        id = d.pop("id", UNSET)

        registration = d.pop("registration", UNSET)

        readonly = d.pop("readonly", UNSET)

        device_readonly = d.pop("deviceReadonly", UNSET)

        limit_commands = d.pop("limitCommands", UNSET)

        map_ = d.pop("map", UNSET)

        bing_key = d.pop("bingKey", UNSET)

        map_url = d.pop("mapUrl", UNSET)

        poi_layer = d.pop("poiLayer", UNSET)

        latitude = d.pop("latitude", UNSET)

        longitude = d.pop("longitude", UNSET)

        zoom = d.pop("zoom", UNSET)

        version = d.pop("version", UNSET)

        force_settings = d.pop("forceSettings", UNSET)

        coordinate_format = d.pop("coordinateFormat", UNSET)

        open_id_enabled = d.pop("openIdEnabled", UNSET)

        open_id_force = d.pop("openIdForce", UNSET)

        _attributes = d.pop("attributes", UNSET)
        attributes: ServerAttributes | Unset
        if isinstance(_attributes, Unset):
            attributes = UNSET
        else:
            attributes = ServerAttributes.from_dict(_attributes)

        server = cls(
            id=id,
            registration=registration,
            readonly=readonly,
            device_readonly=device_readonly,
            limit_commands=limit_commands,
            map_=map_,
            bing_key=bing_key,
            map_url=map_url,
            poi_layer=poi_layer,
            latitude=latitude,
            longitude=longitude,
            zoom=zoom,
            version=version,
            force_settings=force_settings,
            coordinate_format=coordinate_format,
            open_id_enabled=open_id_enabled,
            open_id_force=open_id_force,
            attributes=attributes,
        )

        server.additional_properties = d
        return server

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
