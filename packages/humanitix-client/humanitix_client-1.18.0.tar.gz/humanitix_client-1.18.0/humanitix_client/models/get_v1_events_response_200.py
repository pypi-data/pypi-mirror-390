from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.event import Event


T = TypeVar("T", bound="GetV1EventsResponse200")


@_attrs_define
class GetV1EventsResponse200:
    """
    Attributes:
        total (int): The total number of items matching your query. Example: 58.
        page (int): Page number you wish to fetch.
        page_size (int): Page size of the results you wish to fetch.
        events (list[Event]):
    """

    total: int
    page: int
    page_size: int
    events: list[Event]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        total = self.total

        page = self.page

        page_size = self.page_size

        events = []
        for events_item_data in self.events:
            events_item = events_item_data.to_dict()
            events.append(events_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "total": total,
                "page": page,
                "pageSize": page_size,
                "events": events,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.event import Event

        d = dict(src_dict)
        total = d.pop("total")

        page = d.pop("page")

        page_size = d.pop("pageSize")

        events = []
        _events = d.pop("events")
        for events_item_data in _events:
            events_item = Event.from_dict(events_item_data)

            events.append(events_item)

        get_v1_events_response_200 = cls(
            total=total,
            page=page,
            page_size=page_size,
            events=events,
        )

        get_v1_events_response_200.additional_properties = d
        return get_v1_events_response_200

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
