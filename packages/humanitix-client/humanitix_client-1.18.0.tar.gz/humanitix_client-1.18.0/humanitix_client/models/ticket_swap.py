from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

T = TypeVar("T", bound="TicketSwap")


@_attrs_define
class TicketSwap:
    """
    Attributes:
        id (str):  Example: 5ac599d1a488620e6cd01d88.
        swapped_at (datetime.datetime):  Example: 2021-02-01T23:26:13.485Z.
        user_id (str):  Example: nEOqx8s9UueyRu48789C0sY9set1.
    """

    id: str
    swapped_at: datetime.datetime
    user_id: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        swapped_at = self.swapped_at.isoformat()

        user_id = self.user_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "swappedAt": swapped_at,
                "userId": user_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        swapped_at = isoparse(d.pop("swappedAt"))

        user_id = d.pop("userId")

        ticket_swap = cls(
            id=id,
            swapped_at=swapped_at,
            user_id=user_id,
        )

        ticket_swap.additional_properties = d
        return ticket_swap

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
