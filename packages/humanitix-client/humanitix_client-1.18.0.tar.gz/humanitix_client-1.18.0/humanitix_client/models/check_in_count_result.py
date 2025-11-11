from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.check_in_count_result_ticket_types_item import CheckInCountResultTicketTypesItem


T = TypeVar("T", bound="CheckInCountResult")


@_attrs_define
class CheckInCountResult:
    """
    Attributes:
        event_id (str):  Example: 5ac598ccd8fe7c0c0f212e2a.
        event_date_id (str):  Example: 5ac598ccd8fe7c0c0f212e2f.
        checked_in (int): The number of check ins across all ticket types. Example: 732.
        ticket_types (list[CheckInCountResultTicketTypesItem]):
    """

    event_id: str
    event_date_id: str
    checked_in: int
    ticket_types: list[CheckInCountResultTicketTypesItem]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        event_id = self.event_id

        event_date_id = self.event_date_id

        checked_in = self.checked_in

        ticket_types = []
        for ticket_types_item_data in self.ticket_types:
            ticket_types_item = ticket_types_item_data.to_dict()
            ticket_types.append(ticket_types_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "eventId": event_id,
                "eventDateId": event_date_id,
                "checkedIn": checked_in,
                "ticketTypes": ticket_types,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.check_in_count_result_ticket_types_item import CheckInCountResultTicketTypesItem

        d = dict(src_dict)
        event_id = d.pop("eventId")

        event_date_id = d.pop("eventDateId")

        checked_in = d.pop("checkedIn")

        ticket_types = []
        _ticket_types = d.pop("ticketTypes")
        for ticket_types_item_data in _ticket_types:
            ticket_types_item = CheckInCountResultTicketTypesItem.from_dict(ticket_types_item_data)

            ticket_types.append(ticket_types_item)

        check_in_count_result = cls(
            event_id=event_id,
            event_date_id=event_date_id,
            checked_in=checked_in,
            ticket_types=ticket_types,
        )

        check_in_count_result.additional_properties = d
        return check_in_count_result

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
