from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..models.create_online_event_location_type import CreateOnlineEventLocationType
from ..types import UNSET, Unset

T = TypeVar("T", bound="CreateOnlineEventLocation")


@_attrs_define
class CreateOnlineEventLocation:
    """
    Attributes:
        type_ (CreateOnlineEventLocationType):
        online_url (str | Unset):  Example: www.zoom.com/hobbit-dance-off.
        instructions (str | Unset):  Example: Take the guided tour departing from The Shires rest, 15 minutes from
            Matamata town centre by car..
    """

    type_: CreateOnlineEventLocationType
    online_url: str | Unset = UNSET
    instructions: str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_.value

        online_url = self.online_url

        instructions = self.instructions

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "type": type_,
            }
        )
        if online_url is not UNSET:
            field_dict["onlineUrl"] = online_url
        if instructions is not UNSET:
            field_dict["instructions"] = instructions

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        type_ = CreateOnlineEventLocationType(d.pop("type"))

        online_url = d.pop("onlineUrl", UNSET)

        instructions = d.pop("instructions", UNSET)

        create_online_event_location = cls(
            type_=type_,
            online_url=online_url,
            instructions=instructions,
        )

        return create_online_event_location
