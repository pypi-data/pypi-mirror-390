from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="Artist")


@_attrs_define
class Artist:
    """
    Attributes:
        origin (str): External system from which the artist information originates. Example: spotify.
        name (str): Name of the artist. Example: Gandalf.
        external_id (str | Unset): Identifier used to reference the artist in the external system. Example:
            4ZNG0WQPQ10ehIVkCnM5ku.
    """

    origin: str
    name: str
    external_id: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        origin = self.origin

        name = self.name

        external_id = self.external_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "origin": origin,
                "name": name,
            }
        )
        if external_id is not UNSET:
            field_dict["externalId"] = external_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        origin = d.pop("origin")

        name = d.pop("name")

        external_id = d.pop("externalId", UNSET)

        artist = cls(
            origin=origin,
            name=name,
            external_id=external_id,
        )

        artist.additional_properties = d
        return artist

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
