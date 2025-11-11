from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.packaged_tickets_tickets_item import PackagedTicketsTicketsItem


T = TypeVar("T", bound="PackagedTickets")


@_attrs_define
class PackagedTickets:
    """
    Attributes:
        field_id (str | Unset):  Example: 5da50970ec90824b5ca3608f.
        name (str | Unset):  Example: Family ticket.
        price (float | Unset):  Example: 120.
        quantity (int | Unset):  Example: 125.
        description (str | Unset):  Example: Includes 2x Adult ticket and 2x Child ticket.
        disabled (bool | Unset):
        deleted (bool | Unset):
        tickets (list[PackagedTicketsTicketsItem] | Unset):
    """

    field_id: str | Unset = UNSET
    name: str | Unset = UNSET
    price: float | Unset = UNSET
    quantity: int | Unset = UNSET
    description: str | Unset = UNSET
    disabled: bool | Unset = UNSET
    deleted: bool | Unset = UNSET
    tickets: list[PackagedTicketsTicketsItem] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        field_id = self.field_id

        name = self.name

        price = self.price

        quantity = self.quantity

        description = self.description

        disabled = self.disabled

        deleted = self.deleted

        tickets: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.tickets, Unset):
            tickets = []
            for tickets_item_data in self.tickets:
                tickets_item = tickets_item_data.to_dict()
                tickets.append(tickets_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if field_id is not UNSET:
            field_dict["_id"] = field_id
        if name is not UNSET:
            field_dict["name"] = name
        if price is not UNSET:
            field_dict["price"] = price
        if quantity is not UNSET:
            field_dict["quantity"] = quantity
        if description is not UNSET:
            field_dict["description"] = description
        if disabled is not UNSET:
            field_dict["disabled"] = disabled
        if deleted is not UNSET:
            field_dict["deleted"] = deleted
        if tickets is not UNSET:
            field_dict["tickets"] = tickets

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.packaged_tickets_tickets_item import PackagedTicketsTicketsItem

        d = dict(src_dict)
        field_id = d.pop("_id", UNSET)

        name = d.pop("name", UNSET)

        price = d.pop("price", UNSET)

        quantity = d.pop("quantity", UNSET)

        description = d.pop("description", UNSET)

        disabled = d.pop("disabled", UNSET)

        deleted = d.pop("deleted", UNSET)

        _tickets = d.pop("tickets", UNSET)
        tickets: list[PackagedTicketsTicketsItem] | Unset = UNSET
        if _tickets is not UNSET:
            tickets = []
            for tickets_item_data in _tickets:
                tickets_item = PackagedTicketsTicketsItem.from_dict(tickets_item_data)

                tickets.append(tickets_item)

        packaged_tickets = cls(
            field_id=field_id,
            name=name,
            price=price,
            quantity=quantity,
            description=description,
            disabled=disabled,
            deleted=deleted,
            tickets=tickets,
        )

        packaged_tickets.additional_properties = d
        return packaged_tickets

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
