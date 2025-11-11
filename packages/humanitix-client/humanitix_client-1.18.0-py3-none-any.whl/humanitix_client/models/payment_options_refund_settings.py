from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PaymentOptionsRefundSettings")


@_attrs_define
class PaymentOptionsRefundSettings:
    """
    Attributes:
        refund_policy (str | Unset):  Example: Refunds are available 1 month prior to the event.
        custom_refund_policy (str | Unset):  Example: In the event you are not able to attend the hobbit dance off due
            to unforeseen circumstances, The Shire Council needs to be advised in writing no later than 14 days prior to the
            event in order to receive a full refund.  If your cancellation is less than 14 days prior to the event you will
            be refunded the cost of the dance off less fireworks charges and a $25 administration fee. By booking you
            confirm that you are aware of our cancellation policy..
    """

    refund_policy: str | Unset = UNSET
    custom_refund_policy: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        refund_policy = self.refund_policy

        custom_refund_policy = self.custom_refund_policy

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if refund_policy is not UNSET:
            field_dict["refundPolicy"] = refund_policy
        if custom_refund_policy is not UNSET:
            field_dict["customRefundPolicy"] = custom_refund_policy

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        refund_policy = d.pop("refundPolicy", UNSET)

        custom_refund_policy = d.pop("customRefundPolicy", UNSET)

        payment_options_refund_settings = cls(
            refund_policy=refund_policy,
            custom_refund_policy=custom_refund_policy,
        )

        payment_options_refund_settings.additional_properties = d
        return payment_options_refund_settings

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
