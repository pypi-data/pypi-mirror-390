from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.payment_options_refund_settings import PaymentOptionsRefundSettings


T = TypeVar("T", bound="PaymentOptions")


@_attrs_define
class PaymentOptions:
    """
    Attributes:
        refund_settings (PaymentOptionsRefundSettings | Unset):
    """

    refund_settings: PaymentOptionsRefundSettings | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        refund_settings: dict[str, Any] | Unset = UNSET
        if not isinstance(self.refund_settings, Unset):
            refund_settings = self.refund_settings.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if refund_settings is not UNSET:
            field_dict["refundSettings"] = refund_settings

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.payment_options_refund_settings import PaymentOptionsRefundSettings

        d = dict(src_dict)
        _refund_settings = d.pop("refundSettings", UNSET)
        refund_settings: PaymentOptionsRefundSettings | Unset
        if isinstance(_refund_settings, Unset):
            refund_settings = UNSET
        else:
            refund_settings = PaymentOptionsRefundSettings.from_dict(_refund_settings)

        payment_options = cls(
            refund_settings=refund_settings,
        )

        payment_options.additional_properties = d
        return payment_options

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
