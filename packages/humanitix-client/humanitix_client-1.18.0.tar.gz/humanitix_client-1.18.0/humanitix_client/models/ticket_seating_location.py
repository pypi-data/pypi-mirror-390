from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.seating_location_id import SeatingLocationId


T = TypeVar("T", bound="TicketSeatingLocation")


@_attrs_define
class TicketSeatingLocation:
    """
    Attributes:
        seating_map_id (str | Unset):  Example: 5b4d44e0d76d957e9c672907.
        name (str | Unset):  Example: Section C Table 49 Seat 10.
        section (SeatingLocationId | Unset):
        table (SeatingLocationId | Unset):
        seat (SeatingLocationId | Unset):
        note (str | Unset):  Example: Door 2.
    """

    seating_map_id: str | Unset = UNSET
    name: str | Unset = UNSET
    section: SeatingLocationId | Unset = UNSET
    table: SeatingLocationId | Unset = UNSET
    seat: SeatingLocationId | Unset = UNSET
    note: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        seating_map_id = self.seating_map_id

        name = self.name

        section: dict[str, Any] | Unset = UNSET
        if not isinstance(self.section, Unset):
            section = self.section.to_dict()

        table: dict[str, Any] | Unset = UNSET
        if not isinstance(self.table, Unset):
            table = self.table.to_dict()

        seat: dict[str, Any] | Unset = UNSET
        if not isinstance(self.seat, Unset):
            seat = self.seat.to_dict()

        note = self.note

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if seating_map_id is not UNSET:
            field_dict["seatingMapId"] = seating_map_id
        if name is not UNSET:
            field_dict["name"] = name
        if section is not UNSET:
            field_dict["section"] = section
        if table is not UNSET:
            field_dict["table"] = table
        if seat is not UNSET:
            field_dict["seat"] = seat
        if note is not UNSET:
            field_dict["note"] = note

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.seating_location_id import SeatingLocationId

        d = dict(src_dict)
        seating_map_id = d.pop("seatingMapId", UNSET)

        name = d.pop("name", UNSET)

        _section = d.pop("section", UNSET)
        section: SeatingLocationId | Unset
        if isinstance(_section, Unset):
            section = UNSET
        else:
            section = SeatingLocationId.from_dict(_section)

        _table = d.pop("table", UNSET)
        table: SeatingLocationId | Unset
        if isinstance(_table, Unset):
            table = UNSET
        else:
            table = SeatingLocationId.from_dict(_table)

        _seat = d.pop("seat", UNSET)
        seat: SeatingLocationId | Unset
        if isinstance(_seat, Unset):
            seat = UNSET
        else:
            seat = SeatingLocationId.from_dict(_seat)

        note = d.pop("note", UNSET)

        ticket_seating_location = cls(
            seating_map_id=seating_map_id,
            name=name,
            section=section,
            table=table,
            seat=seat,
            note=note,
        )

        ticket_seating_location.additional_properties = d
        return ticket_seating_location

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
