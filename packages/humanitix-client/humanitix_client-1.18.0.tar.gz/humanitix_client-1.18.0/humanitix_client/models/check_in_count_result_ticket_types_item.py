from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="CheckInCountResultTicketTypesItem")


@_attrs_define
class CheckInCountResultTicketTypesItem:
    """
    Attributes:
        ticket_type_id (str):  Example: 5da50970ec90824b5ca3608f.
        ticket_type_name (str):  Example: General Admission.
        checked_in (int):  Example: 732.
    """

    ticket_type_id: str
    ticket_type_name: str
    checked_in: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        ticket_type_id = self.ticket_type_id

        ticket_type_name = self.ticket_type_name

        checked_in = self.checked_in

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "ticketTypeId": ticket_type_id,
                "ticketTypeName": ticket_type_name,
                "checkedIn": checked_in,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        ticket_type_id = d.pop("ticketTypeId")

        ticket_type_name = d.pop("ticketTypeName")

        checked_in = d.pop("checkedIn")

        check_in_count_result_ticket_types_item = cls(
            ticket_type_id=ticket_type_id,
            ticket_type_name=ticket_type_name,
            checked_in=checked_in,
        )

        check_in_count_result_ticket_types_item.additional_properties = d
        return check_in_count_result_ticket_types_item

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
