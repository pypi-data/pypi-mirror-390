from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="Pricing")


@_attrs_define
class Pricing:
    """
    Attributes:
        minimum_price (float): Minimum ticket price on an event. If the event has free tickets, this will be 0.
        maximum_price (float): Maximum ticket price on an event. If the event only has free tickets, this will be 0.
            Example: 123.45.
    """

    minimum_price: float
    maximum_price: float
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        minimum_price = self.minimum_price

        maximum_price = self.maximum_price

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "minimumPrice": minimum_price,
                "maximumPrice": maximum_price,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        minimum_price = d.pop("minimumPrice")

        maximum_price = d.pop("maximumPrice")

        pricing = cls(
            minimum_price=minimum_price,
            maximum_price=maximum_price,
        )

        pricing.additional_properties = d
        return pricing

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
