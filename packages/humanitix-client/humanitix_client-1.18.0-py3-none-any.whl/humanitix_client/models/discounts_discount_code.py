from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="DiscountsDiscountCode")


@_attrs_define
class DiscountsDiscountCode:
    """The object for the discount code applied onto an order or ticket to apply a discount.

    Attributes:
        code (str | Unset): The discount code applied onto an order or ticket to apply a discount. Example: FIFTYOFF.
        discount_amount (int | Unset): The discount amount applied to an order or ticket Example: 20.
    """

    code: str | Unset = UNSET
    discount_amount: int | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        code = self.code

        discount_amount = self.discount_amount

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if code is not UNSET:
            field_dict["code"] = code
        if discount_amount is not UNSET:
            field_dict["discountAmount"] = discount_amount

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        code = d.pop("code", UNSET)

        discount_amount = d.pop("discountAmount", UNSET)

        discounts_discount_code = cls(
            code=code,
            discount_amount=discount_amount,
        )

        discounts_discount_code.additional_properties = d
        return discounts_discount_code

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
