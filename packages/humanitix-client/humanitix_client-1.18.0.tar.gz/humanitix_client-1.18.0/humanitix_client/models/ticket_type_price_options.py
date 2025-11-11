from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.ticket_type_price_options_options_item import TicketTypePriceOptionsOptionsItem


T = TypeVar("T", bound="TicketTypePriceOptions")


@_attrs_define
class TicketTypePriceOptions:
    """
    Attributes:
        enabled (bool | Unset):
        options (list[TicketTypePriceOptionsOptionsItem] | Unset):
    """

    enabled: bool | Unset = UNSET
    options: list[TicketTypePriceOptionsOptionsItem] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        enabled = self.enabled

        options: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.options, Unset):
            options = []
            for options_item_data in self.options:
                options_item = options_item_data.to_dict()
                options.append(options_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if enabled is not UNSET:
            field_dict["enabled"] = enabled
        if options is not UNSET:
            field_dict["options"] = options

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.ticket_type_price_options_options_item import TicketTypePriceOptionsOptionsItem

        d = dict(src_dict)
        enabled = d.pop("enabled", UNSET)

        _options = d.pop("options", UNSET)
        options: list[TicketTypePriceOptionsOptionsItem] | Unset = UNSET
        if _options is not UNSET:
            options = []
            for options_item_data in _options:
                options_item = TicketTypePriceOptionsOptionsItem.from_dict(options_item_data)

                options.append(options_item)

        ticket_type_price_options = cls(
            enabled=enabled,
            options=options,
        )

        ticket_type_price_options.additional_properties = d
        return ticket_type_price_options

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
