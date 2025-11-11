from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..models.create_custom_event_location_type import CreateCustomEventLocationType

T = TypeVar("T", bound="CreateCustomEventLocation")


@_attrs_define
class CreateCustomEventLocation:
    """
    Attributes:
        type_ (CreateCustomEventLocationType):
        address (str):  Example: 501 Buckland Road, Hinuera, Matamata 3472, New Zealand.
        venue_name (str):  Example: Hobbiton Movie Set Tours.
    """

    type_: CreateCustomEventLocationType
    address: str
    venue_name: str

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_.value

        address = self.address

        venue_name = self.venue_name

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "type": type_,
                "address": address,
                "venueName": venue_name,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        type_ = CreateCustomEventLocationType(d.pop("type"))

        address = d.pop("address")

        venue_name = d.pop("venueName")

        create_custom_event_location = cls(
            type_=type_,
            address=address,
            venue_name=venue_name,
        )

        return create_custom_event_location
