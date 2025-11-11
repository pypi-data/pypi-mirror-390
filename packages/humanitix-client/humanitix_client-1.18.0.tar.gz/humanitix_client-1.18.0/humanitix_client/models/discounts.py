from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.discounts_auto_discount import DiscountsAutoDiscount
    from ..models.discounts_discount_code import DiscountsDiscountCode


T = TypeVar("T", bound="Discounts")


@_attrs_define
class Discounts:
    """
    Attributes:
        auto_discount (DiscountsAutoDiscount | Unset): The automatic discount applied to an order or ticket.
        discount_code (DiscountsDiscountCode | Unset): The object for the discount code applied onto an order or ticket
            to apply a discount.
    """

    auto_discount: DiscountsAutoDiscount | Unset = UNSET
    discount_code: DiscountsDiscountCode | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        auto_discount: dict[str, Any] | Unset = UNSET
        if not isinstance(self.auto_discount, Unset):
            auto_discount = self.auto_discount.to_dict()

        discount_code: dict[str, Any] | Unset = UNSET
        if not isinstance(self.discount_code, Unset):
            discount_code = self.discount_code.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if auto_discount is not UNSET:
            field_dict["autoDiscount"] = auto_discount
        if discount_code is not UNSET:
            field_dict["discountCode"] = discount_code

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.discounts_auto_discount import DiscountsAutoDiscount
        from ..models.discounts_discount_code import DiscountsDiscountCode

        d = dict(src_dict)
        _auto_discount = d.pop("autoDiscount", UNSET)
        auto_discount: DiscountsAutoDiscount | Unset
        if isinstance(_auto_discount, Unset):
            auto_discount = UNSET
        else:
            auto_discount = DiscountsAutoDiscount.from_dict(_auto_discount)

        _discount_code = d.pop("discountCode", UNSET)
        discount_code: DiscountsDiscountCode | Unset
        if isinstance(_discount_code, Unset):
            discount_code = UNSET
        else:
            discount_code = DiscountsDiscountCode.from_dict(_discount_code)

        discounts = cls(
            auto_discount=auto_discount,
            discount_code=discount_code,
        )

        discounts.additional_properties = d
        return discounts

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
