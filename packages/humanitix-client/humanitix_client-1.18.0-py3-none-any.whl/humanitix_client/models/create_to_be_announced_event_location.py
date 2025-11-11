from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..models.create_to_be_announced_event_location_type import CreateToBeAnnouncedEventLocationType

T = TypeVar("T", bound="CreateToBeAnnouncedEventLocation")


@_attrs_define
class CreateToBeAnnouncedEventLocation:
    """
    Attributes:
        type_ (CreateToBeAnnouncedEventLocationType):
    """

    type_: CreateToBeAnnouncedEventLocationType

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_.value

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "type": type_,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        type_ = CreateToBeAnnouncedEventLocationType(d.pop("type"))

        create_to_be_announced_event_location = cls(
            type_=type_,
        )

        return create_to_be_announced_event_location
