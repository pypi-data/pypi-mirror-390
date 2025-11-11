from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.event_location_type import EventLocationType
from ..types import UNSET, Unset

T = TypeVar("T", bound="EventLocation")


@_attrs_define
class EventLocation:
    """
    Attributes:
        type_ (EventLocationType):
        venue_name (str | Unset):
        address (str | Unset):  Example: 501 Buckland Road, Hinuera, Matamata 3472, New Zealand.
        lat_lng (list[float] | Unset):  Example: [-37.8691623, 175.6802895].
        instructions (str | Unset):  Example: Take the guided tour departing from The Shires rest, 15 minutes from
            Matamata town centre by car..
        place_id (str | Unset):  Example: ChIJP0sTGs-uMioR7xB_WgdR9Bo.
        online_url (str | Unset):  Example: www.zoom.com/hobbit-dance-off.
        map_url (str | Unset):  Example: https://cdn.filestackcontent.com/o5uJJsdJS8uH4PGcyBXx.
        city (str | Unset): The 'locality' from the Google geocoding api Example: Sydney.
        region (str | Unset): The 'administrative_area_level_1' from the Google geocoding api Example: NSW.
        country (str | Unset): The 'country' from the Google geocoding api. Format is that of ISO 3166-1 alpha-2 country
            codes. Example: AU.
    """

    type_: EventLocationType
    venue_name: str | Unset = UNSET
    address: str | Unset = UNSET
    lat_lng: list[float] | Unset = UNSET
    instructions: str | Unset = UNSET
    place_id: str | Unset = UNSET
    online_url: str | Unset = UNSET
    map_url: str | Unset = UNSET
    city: str | Unset = UNSET
    region: str | Unset = UNSET
    country: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_.value

        venue_name = self.venue_name

        address = self.address

        lat_lng: list[float] | Unset = UNSET
        if not isinstance(self.lat_lng, Unset):
            lat_lng = self.lat_lng

        instructions = self.instructions

        place_id = self.place_id

        online_url = self.online_url

        map_url = self.map_url

        city = self.city

        region = self.region

        country = self.country

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type_,
            }
        )
        if venue_name is not UNSET:
            field_dict["venueName"] = venue_name
        if address is not UNSET:
            field_dict["address"] = address
        if lat_lng is not UNSET:
            field_dict["latLng"] = lat_lng
        if instructions is not UNSET:
            field_dict["instructions"] = instructions
        if place_id is not UNSET:
            field_dict["placeId"] = place_id
        if online_url is not UNSET:
            field_dict["onlineUrl"] = online_url
        if map_url is not UNSET:
            field_dict["mapUrl"] = map_url
        if city is not UNSET:
            field_dict["city"] = city
        if region is not UNSET:
            field_dict["region"] = region
        if country is not UNSET:
            field_dict["country"] = country

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        type_ = EventLocationType(d.pop("type"))

        venue_name = d.pop("venueName", UNSET)

        address = d.pop("address", UNSET)

        lat_lng = cast(list[float], d.pop("latLng", UNSET))

        instructions = d.pop("instructions", UNSET)

        place_id = d.pop("placeId", UNSET)

        online_url = d.pop("onlineUrl", UNSET)

        map_url = d.pop("mapUrl", UNSET)

        city = d.pop("city", UNSET)

        region = d.pop("region", UNSET)

        country = d.pop("country", UNSET)

        event_location = cls(
            type_=type_,
            venue_name=venue_name,
            address=address,
            lat_lng=lat_lng,
            instructions=instructions,
            place_id=place_id,
            online_url=online_url,
            map_url=map_url,
            city=city,
            region=region,
            country=country,
        )

        event_location.additional_properties = d
        return event_location

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
