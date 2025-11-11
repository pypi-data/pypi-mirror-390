from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="OrderTotals")


@_attrs_define
class OrderTotals:
    """
    Attributes:
        subtotal (float):  Example: 50.
        client_donation (float):
        net_client_donation (float):
        donation (float):  Example: 1.19.
        fees_included (bool):
        booking_taxes (float):  Example: 0.36.
        taxes (float):
        total_taxes (float):  Example: 0.36.
        discounts (float):
        refunds (float):
        net_sales (float):  Example: 50.
        gross_sales (float):  Example: 53.98.
        total (float):  Example: 53.98.
        amex_fee (float | Unset):
        zip_fee (float | Unset):
        humanitix_fee (float | Unset):  Example: 3.98.
        booking_fee (float | Unset):  Example: 3.98.
        passed_on_fee (float | Unset):
        dgr_donation (float | Unset):
        gift_card_credit (float | Unset):
        credit (float | Unset):
        outstanding_amount (float | Unset):
        passed_on_taxes (float | Unset):
        referral_amount (float | Unset):
    """

    subtotal: float
    client_donation: float
    net_client_donation: float
    donation: float
    fees_included: bool
    booking_taxes: float
    taxes: float
    total_taxes: float
    discounts: float
    refunds: float
    net_sales: float
    gross_sales: float
    total: float
    amex_fee: float | Unset = UNSET
    zip_fee: float | Unset = UNSET
    humanitix_fee: float | Unset = UNSET
    booking_fee: float | Unset = UNSET
    passed_on_fee: float | Unset = UNSET
    dgr_donation: float | Unset = UNSET
    gift_card_credit: float | Unset = UNSET
    credit: float | Unset = UNSET
    outstanding_amount: float | Unset = UNSET
    passed_on_taxes: float | Unset = UNSET
    referral_amount: float | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        subtotal = self.subtotal

        client_donation = self.client_donation

        net_client_donation = self.net_client_donation

        donation = self.donation

        fees_included = self.fees_included

        booking_taxes = self.booking_taxes

        taxes = self.taxes

        total_taxes = self.total_taxes

        discounts = self.discounts

        refunds = self.refunds

        net_sales = self.net_sales

        gross_sales = self.gross_sales

        total = self.total

        amex_fee = self.amex_fee

        zip_fee = self.zip_fee

        humanitix_fee = self.humanitix_fee

        booking_fee = self.booking_fee

        passed_on_fee = self.passed_on_fee

        dgr_donation = self.dgr_donation

        gift_card_credit = self.gift_card_credit

        credit = self.credit

        outstanding_amount = self.outstanding_amount

        passed_on_taxes = self.passed_on_taxes

        referral_amount = self.referral_amount

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "subtotal": subtotal,
                "clientDonation": client_donation,
                "netClientDonation": net_client_donation,
                "donation": donation,
                "feesIncluded": fees_included,
                "bookingTaxes": booking_taxes,
                "taxes": taxes,
                "totalTaxes": total_taxes,
                "discounts": discounts,
                "refunds": refunds,
                "netSales": net_sales,
                "grossSales": gross_sales,
                "total": total,
            }
        )
        if amex_fee is not UNSET:
            field_dict["amexFee"] = amex_fee
        if zip_fee is not UNSET:
            field_dict["zipFee"] = zip_fee
        if humanitix_fee is not UNSET:
            field_dict["humanitixFee"] = humanitix_fee
        if booking_fee is not UNSET:
            field_dict["bookingFee"] = booking_fee
        if passed_on_fee is not UNSET:
            field_dict["passedOnFee"] = passed_on_fee
        if dgr_donation is not UNSET:
            field_dict["dgrDonation"] = dgr_donation
        if gift_card_credit is not UNSET:
            field_dict["giftCardCredit"] = gift_card_credit
        if credit is not UNSET:
            field_dict["credit"] = credit
        if outstanding_amount is not UNSET:
            field_dict["outstandingAmount"] = outstanding_amount
        if passed_on_taxes is not UNSET:
            field_dict["passedOnTaxes"] = passed_on_taxes
        if referral_amount is not UNSET:
            field_dict["referralAmount"] = referral_amount

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        subtotal = d.pop("subtotal")

        client_donation = d.pop("clientDonation")

        net_client_donation = d.pop("netClientDonation")

        donation = d.pop("donation")

        fees_included = d.pop("feesIncluded")

        booking_taxes = d.pop("bookingTaxes")

        taxes = d.pop("taxes")

        total_taxes = d.pop("totalTaxes")

        discounts = d.pop("discounts")

        refunds = d.pop("refunds")

        net_sales = d.pop("netSales")

        gross_sales = d.pop("grossSales")

        total = d.pop("total")

        amex_fee = d.pop("amexFee", UNSET)

        zip_fee = d.pop("zipFee", UNSET)

        humanitix_fee = d.pop("humanitixFee", UNSET)

        booking_fee = d.pop("bookingFee", UNSET)

        passed_on_fee = d.pop("passedOnFee", UNSET)

        dgr_donation = d.pop("dgrDonation", UNSET)

        gift_card_credit = d.pop("giftCardCredit", UNSET)

        credit = d.pop("credit", UNSET)

        outstanding_amount = d.pop("outstandingAmount", UNSET)

        passed_on_taxes = d.pop("passedOnTaxes", UNSET)

        referral_amount = d.pop("referralAmount", UNSET)

        order_totals = cls(
            subtotal=subtotal,
            client_donation=client_donation,
            net_client_donation=net_client_donation,
            donation=donation,
            fees_included=fees_included,
            booking_taxes=booking_taxes,
            taxes=taxes,
            total_taxes=total_taxes,
            discounts=discounts,
            refunds=refunds,
            net_sales=net_sales,
            gross_sales=gross_sales,
            total=total,
            amex_fee=amex_fee,
            zip_fee=zip_fee,
            humanitix_fee=humanitix_fee,
            booking_fee=booking_fee,
            passed_on_fee=passed_on_fee,
            dgr_donation=dgr_donation,
            gift_card_credit=gift_card_credit,
            credit=credit,
            outstanding_amount=outstanding_amount,
            passed_on_taxes=passed_on_taxes,
            referral_amount=referral_amount,
        )

        order_totals.additional_properties = d
        return order_totals

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
