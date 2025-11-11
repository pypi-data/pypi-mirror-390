from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define

from ..models.create_address_event_location_type import CreateAddressEventLocationType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.create_google_address_components import CreateGoogleAddressComponents


T = TypeVar("T", bound="CreateAddressEventLocation")


@_attrs_define
class CreateAddressEventLocation:
    """
    Attributes:
        type_ (CreateAddressEventLocationType):
        address (str):  Example: 501 Buckland Road, Hinuera, Matamata 3472, New Zealand.
        venue_name (str):
        lat_lng (list[float]):  Example: [-37.8691623, 175.6802895].
        place_id (str | Unset): See https://developers.google.com/maps/documentation/places/web-service/details#Place-
            place_id Example: ChIJP0sTGs-uMioR7xB_WgdR9Bo.
        address_components (list[CreateGoogleAddressComponents] | Unset):
    """

    type_: CreateAddressEventLocationType
    address: str
    venue_name: str
    lat_lng: list[float]
    place_id: str | Unset = UNSET
    address_components: list[CreateGoogleAddressComponents] | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_.value

        address = self.address

        venue_name = self.venue_name

        lat_lng = self.lat_lng

        place_id = self.place_id

        address_components: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.address_components, Unset):
            address_components = []
            for address_components_item_data in self.address_components:
                address_components_item = address_components_item_data.to_dict()
                address_components.append(address_components_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "type": type_,
                "address": address,
                "venueName": venue_name,
                "latLng": lat_lng,
            }
        )
        if place_id is not UNSET:
            field_dict["placeId"] = place_id
        if address_components is not UNSET:
            field_dict["addressComponents"] = address_components

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.create_google_address_components import CreateGoogleAddressComponents

        d = dict(src_dict)
        type_ = CreateAddressEventLocationType(d.pop("type"))

        address = d.pop("address")

        venue_name = d.pop("venueName")

        lat_lng = cast(list[float], d.pop("latLng"))

        place_id = d.pop("placeId", UNSET)

        _address_components = d.pop("addressComponents", UNSET)
        address_components: list[CreateGoogleAddressComponents] | Unset = UNSET
        if _address_components is not UNSET:
            address_components = []
            for address_components_item_data in _address_components:
                address_components_item = CreateGoogleAddressComponents.from_dict(address_components_item_data)

                address_components.append(address_components_item)

        create_address_event_location = cls(
            type_=type_,
            address=address,
            venue_name=venue_name,
            lat_lng=lat_lng,
            place_id=place_id,
            address_components=address_components,
        )

        return create_address_event_location
