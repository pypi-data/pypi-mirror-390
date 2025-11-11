from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="DiscountsAutoDiscount")


@_attrs_define
class DiscountsAutoDiscount:
    """The automatic discount applied to an order or ticket.

    Attributes:
        discount_amount (int | Unset): The discount amount applied to an order or ticket Example: 20.
    """

    discount_amount: int | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        discount_amount = self.discount_amount

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if discount_amount is not UNSET:
            field_dict["discountAmount"] = discount_amount

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        discount_amount = d.pop("discountAmount", UNSET)

        discounts_auto_discount = cls(
            discount_amount=discount_amount,
        )

        discounts_auto_discount.additional_properties = d
        return discounts_auto_discount

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
