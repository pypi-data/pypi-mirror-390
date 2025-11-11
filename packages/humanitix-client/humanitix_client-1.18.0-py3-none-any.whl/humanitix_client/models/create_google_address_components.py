from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="CreateGoogleAddressComponents")


@_attrs_define
class CreateGoogleAddressComponents:
    """See https://developers.google.com/maps/documentation/places/web-service/details#AddressComponent

    Attributes:
        long_name (str | Unset):
        short_name (str | Unset):
        types (list[str] | Unset):
    """

    long_name: str | Unset = UNSET
    short_name: str | Unset = UNSET
    types: list[str] | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        long_name = self.long_name

        short_name = self.short_name

        types: list[str] | Unset = UNSET
        if not isinstance(self.types, Unset):
            types = self.types

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if long_name is not UNSET:
            field_dict["long_name"] = long_name
        if short_name is not UNSET:
            field_dict["short_name"] = short_name
        if types is not UNSET:
            field_dict["types"] = types

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        long_name = d.pop("long_name", UNSET)

        short_name = d.pop("short_name", UNSET)

        types = cast(list[str], d.pop("types", UNSET))

        create_google_address_components = cls(
            long_name=long_name,
            short_name=short_name,
            types=types,
        )

        return create_google_address_components
