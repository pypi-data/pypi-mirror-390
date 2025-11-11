from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="AdditionalFieldsDetails")


@_attrs_define
class AdditionalFieldsDetails:
    """
    Attributes:
        street (str | Unset):  Example: 501 Buckland Road.
        suburb (str | Unset):  Example: Hinuera.
        postal_code (str | Unset):  Example: 3472.
        city (str | Unset):  Example: Matamata.
        state (str | Unset):  Example: Waikato.
        country (str | Unset):  Example: New Zealand.
    """

    street: str | Unset = UNSET
    suburb: str | Unset = UNSET
    postal_code: str | Unset = UNSET
    city: str | Unset = UNSET
    state: str | Unset = UNSET
    country: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        street = self.street

        suburb = self.suburb

        postal_code = self.postal_code

        city = self.city

        state = self.state

        country = self.country

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if street is not UNSET:
            field_dict["street"] = street
        if suburb is not UNSET:
            field_dict["suburb"] = suburb
        if postal_code is not UNSET:
            field_dict["postalCode"] = postal_code
        if city is not UNSET:
            field_dict["city"] = city
        if state is not UNSET:
            field_dict["state"] = state
        if country is not UNSET:
            field_dict["country"] = country

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        street = d.pop("street", UNSET)

        suburb = d.pop("suburb", UNSET)

        postal_code = d.pop("postalCode", UNSET)

        city = d.pop("city", UNSET)

        state = d.pop("state", UNSET)

        country = d.pop("country", UNSET)

        additional_fields_details = cls(
            street=street,
            suburb=suburb,
            postal_code=postal_code,
            city=city,
            state=state,
            country=country,
        )

        additional_fields_details.additional_properties = d
        return additional_fields_details

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
