from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.ticket_type_price_options import TicketTypePriceOptions
    from ..models.ticket_type_price_range import TicketTypePriceRange


T = TypeVar("T", bound="TicketType")


@_attrs_define
class TicketType:
    """
    Attributes:
        name (str):  Example: Adult.
        field_id (str | Unset):  Example: 5da50970ec90824b5ca3608f.
        price (float | Unset):  Example: 100.
        price_range (TicketTypePriceRange | Unset):
        price_options (TicketTypePriceOptions | Unset):
        quantity (int | Unset):  Example: 500.
        description (str | Unset):  Example: Admits one hobbit..
        disabled (bool | Unset):
        deleted (bool | Unset):
        is_donation (bool | Unset):
    """

    name: str
    field_id: str | Unset = UNSET
    price: float | Unset = UNSET
    price_range: TicketTypePriceRange | Unset = UNSET
    price_options: TicketTypePriceOptions | Unset = UNSET
    quantity: int | Unset = UNSET
    description: str | Unset = UNSET
    disabled: bool | Unset = UNSET
    deleted: bool | Unset = UNSET
    is_donation: bool | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        field_id = self.field_id

        price = self.price

        price_range: dict[str, Any] | Unset = UNSET
        if not isinstance(self.price_range, Unset):
            price_range = self.price_range.to_dict()

        price_options: dict[str, Any] | Unset = UNSET
        if not isinstance(self.price_options, Unset):
            price_options = self.price_options.to_dict()

        quantity = self.quantity

        description = self.description

        disabled = self.disabled

        deleted = self.deleted

        is_donation = self.is_donation

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
            }
        )
        if field_id is not UNSET:
            field_dict["_id"] = field_id
        if price is not UNSET:
            field_dict["price"] = price
        if price_range is not UNSET:
            field_dict["priceRange"] = price_range
        if price_options is not UNSET:
            field_dict["priceOptions"] = price_options
        if quantity is not UNSET:
            field_dict["quantity"] = quantity
        if description is not UNSET:
            field_dict["description"] = description
        if disabled is not UNSET:
            field_dict["disabled"] = disabled
        if deleted is not UNSET:
            field_dict["deleted"] = deleted
        if is_donation is not UNSET:
            field_dict["isDonation"] = is_donation

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.ticket_type_price_options import TicketTypePriceOptions
        from ..models.ticket_type_price_range import TicketTypePriceRange

        d = dict(src_dict)
        name = d.pop("name")

        field_id = d.pop("_id", UNSET)

        price = d.pop("price", UNSET)

        _price_range = d.pop("priceRange", UNSET)
        price_range: TicketTypePriceRange | Unset
        if isinstance(_price_range, Unset):
            price_range = UNSET
        else:
            price_range = TicketTypePriceRange.from_dict(_price_range)

        _price_options = d.pop("priceOptions", UNSET)
        price_options: TicketTypePriceOptions | Unset
        if isinstance(_price_options, Unset):
            price_options = UNSET
        else:
            price_options = TicketTypePriceOptions.from_dict(_price_options)

        quantity = d.pop("quantity", UNSET)

        description = d.pop("description", UNSET)

        disabled = d.pop("disabled", UNSET)

        deleted = d.pop("deleted", UNSET)

        is_donation = d.pop("isDonation", UNSET)

        ticket_type = cls(
            name=name,
            field_id=field_id,
            price=price,
            price_range=price_range,
            price_options=price_options,
            quantity=quantity,
            description=description,
            disabled=disabled,
            deleted=deleted,
            is_donation=is_donation,
        )

        ticket_type.additional_properties = d
        return ticket_type

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
