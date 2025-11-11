from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.currency import Currency
from ..models.location import Location
from ..models.order_financial_status import OrderFinancialStatus
from ..models.order_payment_gateway import OrderPaymentGateway
from ..models.order_payment_type import OrderPaymentType
from ..models.order_status import OrderStatus
from ..models.sales_channel import SalesChannel
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.additional_fields import AdditionalFields
    from ..models.discounts import Discounts
    from ..models.order_totals import OrderTotals


T = TypeVar("T", bound="Order")


@_attrs_define
class Order:
    """
    Attributes:
        field_id (str):  Example: 5ac599d1a488620e6cd01d87.
        currency (Currency):
        status (OrderStatus):
        financial_status (OrderFinancialStatus):
        manual_order (bool):
        sales_channel (SalesChannel): The channel through which the order or ticket was created, via an online sale or
            manual order.
        location (Location): The location of where the object is stored. Format is that of ISO 3166-1 alpha-2 country
            codes. Example: AU.
        created_at (datetime.datetime):  Example: 2021-02-01T23:26:13.485Z.
        updated_at (datetime.datetime):  Example: 2021-02-01T23:26:13.485Z.
        event_id (str | Unset):  Example: 5ac598ccd8fe7c0c0f212e2a.
        user_id (str | Unset):  Example: nEOqx8s9UueyRu48789C0sY9set1.
        event_date_id (str | Unset):  Example: 5ac598ccd8fe7c0c0f212e2f.
        first_name (str | Unset):  Example: Bilbo.
        last_name (str | Unset):  Example: Baggins.
        organisation (str | Unset):  Example: ABC School.
        mobile (str | Unset):  Example: 0412345678.
        email (str | Unset):  Example: bilbo.baggins@middleearth.com.
        access_code (str | Unset): The access code used on the order to reveal hidden tickets. If returned on the ticket
            object, this ticket was revealed by that access code. Example: EARLYACCESS.
        discounts (Discounts | Unset):
        business_purpose (bool | Unset):
        business_tax_id (str | Unset):  Example: 12345678901.
        business_name (str | Unset):  Example: ABC School.
        payment_type (OrderPaymentType | Unset):
        payment_gateway (OrderPaymentGateway | Unset):
        tip_fees (bool | Unset):
        client_donation (float | Unset):  Example: 5.
        notes (str | Unset):  Example: Example note.
        organiser_mail_list_opt_in (bool | Unset):
        incomplete_at (datetime.datetime | Unset):  Example: 2021-02-01T23:26:13.485Z.
        completed_at (datetime.datetime | Unset):  Example: 2021-02-01T23:26:13.485Z.
        waitlist_offer_id (str | Unset):  Example: 5d0ae7ef9d3e67012780u70d.
        is_international_transaction (bool | Unset):
        totals (OrderTotals | Unset):
        purchase_totals (OrderTotals | Unset):
        additional_fields (list[AdditionalFields] | Unset):
    """

    field_id: str
    currency: Currency
    status: OrderStatus
    financial_status: OrderFinancialStatus
    manual_order: bool
    sales_channel: SalesChannel
    location: Location
    created_at: datetime.datetime
    updated_at: datetime.datetime
    event_id: str | Unset = UNSET
    user_id: str | Unset = UNSET
    event_date_id: str | Unset = UNSET
    first_name: str | Unset = UNSET
    last_name: str | Unset = UNSET
    organisation: str | Unset = UNSET
    mobile: str | Unset = UNSET
    email: str | Unset = UNSET
    access_code: str | Unset = UNSET
    discounts: Discounts | Unset = UNSET
    business_purpose: bool | Unset = UNSET
    business_tax_id: str | Unset = UNSET
    business_name: str | Unset = UNSET
    payment_type: OrderPaymentType | Unset = UNSET
    payment_gateway: OrderPaymentGateway | Unset = UNSET
    tip_fees: bool | Unset = UNSET
    client_donation: float | Unset = UNSET
    notes: str | Unset = UNSET
    organiser_mail_list_opt_in: bool | Unset = UNSET
    incomplete_at: datetime.datetime | Unset = UNSET
    completed_at: datetime.datetime | Unset = UNSET
    waitlist_offer_id: str | Unset = UNSET
    is_international_transaction: bool | Unset = UNSET
    totals: OrderTotals | Unset = UNSET
    purchase_totals: OrderTotals | Unset = UNSET
    additional_fields: list[AdditionalFields] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        field_id = self.field_id

        currency = self.currency.value

        status = self.status.value

        financial_status = self.financial_status.value

        manual_order = self.manual_order

        sales_channel = self.sales_channel.value

        location = self.location.value

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        event_id = self.event_id

        user_id = self.user_id

        event_date_id = self.event_date_id

        first_name = self.first_name

        last_name = self.last_name

        organisation = self.organisation

        mobile = self.mobile

        email = self.email

        access_code = self.access_code

        discounts: dict[str, Any] | Unset = UNSET
        if not isinstance(self.discounts, Unset):
            discounts = self.discounts.to_dict()

        business_purpose = self.business_purpose

        business_tax_id = self.business_tax_id

        business_name = self.business_name

        payment_type: str | Unset = UNSET
        if not isinstance(self.payment_type, Unset):
            payment_type = self.payment_type.value

        payment_gateway: str | Unset = UNSET
        if not isinstance(self.payment_gateway, Unset):
            payment_gateway = self.payment_gateway.value

        tip_fees = self.tip_fees

        client_donation = self.client_donation

        notes = self.notes

        organiser_mail_list_opt_in = self.organiser_mail_list_opt_in

        incomplete_at: str | Unset = UNSET
        if not isinstance(self.incomplete_at, Unset):
            incomplete_at = self.incomplete_at.isoformat()

        completed_at: str | Unset = UNSET
        if not isinstance(self.completed_at, Unset):
            completed_at = self.completed_at.isoformat()

        waitlist_offer_id = self.waitlist_offer_id

        is_international_transaction = self.is_international_transaction

        totals: dict[str, Any] | Unset = UNSET
        if not isinstance(self.totals, Unset):
            totals = self.totals.to_dict()

        purchase_totals: dict[str, Any] | Unset = UNSET
        if not isinstance(self.purchase_totals, Unset):
            purchase_totals = self.purchase_totals.to_dict()

        additional_fields: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.additional_fields, Unset):
            additional_fields = []
            for additional_fields_item_data in self.additional_fields:
                additional_fields_item = additional_fields_item_data.to_dict()
                additional_fields.append(additional_fields_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "_id": field_id,
                "currency": currency,
                "status": status,
                "financialStatus": financial_status,
                "manualOrder": manual_order,
                "salesChannel": sales_channel,
                "location": location,
                "createdAt": created_at,
                "updatedAt": updated_at,
            }
        )
        if event_id is not UNSET:
            field_dict["eventId"] = event_id
        if user_id is not UNSET:
            field_dict["userId"] = user_id
        if event_date_id is not UNSET:
            field_dict["eventDateId"] = event_date_id
        if first_name is not UNSET:
            field_dict["firstName"] = first_name
        if last_name is not UNSET:
            field_dict["lastName"] = last_name
        if organisation is not UNSET:
            field_dict["organisation"] = organisation
        if mobile is not UNSET:
            field_dict["mobile"] = mobile
        if email is not UNSET:
            field_dict["email"] = email
        if access_code is not UNSET:
            field_dict["accessCode"] = access_code
        if discounts is not UNSET:
            field_dict["discounts"] = discounts
        if business_purpose is not UNSET:
            field_dict["businessPurpose"] = business_purpose
        if business_tax_id is not UNSET:
            field_dict["businessTaxId"] = business_tax_id
        if business_name is not UNSET:
            field_dict["businessName"] = business_name
        if payment_type is not UNSET:
            field_dict["paymentType"] = payment_type
        if payment_gateway is not UNSET:
            field_dict["paymentGateway"] = payment_gateway
        if tip_fees is not UNSET:
            field_dict["tipFees"] = tip_fees
        if client_donation is not UNSET:
            field_dict["clientDonation"] = client_donation
        if notes is not UNSET:
            field_dict["notes"] = notes
        if organiser_mail_list_opt_in is not UNSET:
            field_dict["organiserMailListOptIn"] = organiser_mail_list_opt_in
        if incomplete_at is not UNSET:
            field_dict["incompleteAt"] = incomplete_at
        if completed_at is not UNSET:
            field_dict["completedAt"] = completed_at
        if waitlist_offer_id is not UNSET:
            field_dict["waitlistOfferId"] = waitlist_offer_id
        if is_international_transaction is not UNSET:
            field_dict["isInternationalTransaction"] = is_international_transaction
        if totals is not UNSET:
            field_dict["totals"] = totals
        if purchase_totals is not UNSET:
            field_dict["purchaseTotals"] = purchase_totals
        if additional_fields is not UNSET:
            field_dict["additionalFields"] = additional_fields

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.additional_fields import AdditionalFields
        from ..models.discounts import Discounts
        from ..models.order_totals import OrderTotals

        d = dict(src_dict)
        field_id = d.pop("_id")

        currency = Currency(d.pop("currency"))

        status = OrderStatus(d.pop("status"))

        financial_status = OrderFinancialStatus(d.pop("financialStatus"))

        manual_order = d.pop("manualOrder")

        sales_channel = SalesChannel(d.pop("salesChannel"))

        location = Location(d.pop("location"))

        created_at = isoparse(d.pop("createdAt"))

        updated_at = isoparse(d.pop("updatedAt"))

        event_id = d.pop("eventId", UNSET)

        user_id = d.pop("userId", UNSET)

        event_date_id = d.pop("eventDateId", UNSET)

        first_name = d.pop("firstName", UNSET)

        last_name = d.pop("lastName", UNSET)

        organisation = d.pop("organisation", UNSET)

        mobile = d.pop("mobile", UNSET)

        email = d.pop("email", UNSET)

        access_code = d.pop("accessCode", UNSET)

        _discounts = d.pop("discounts", UNSET)
        discounts: Discounts | Unset
        if isinstance(_discounts, Unset):
            discounts = UNSET
        else:
            discounts = Discounts.from_dict(_discounts)

        business_purpose = d.pop("businessPurpose", UNSET)

        business_tax_id = d.pop("businessTaxId", UNSET)

        business_name = d.pop("businessName", UNSET)

        _payment_type = d.pop("paymentType", UNSET)
        payment_type: OrderPaymentType | Unset
        if isinstance(_payment_type, Unset):
            payment_type = UNSET
        else:
            payment_type = OrderPaymentType(_payment_type)

        _payment_gateway = d.pop("paymentGateway", UNSET)
        payment_gateway: OrderPaymentGateway | Unset
        if isinstance(_payment_gateway, Unset):
            payment_gateway = UNSET
        else:
            payment_gateway = OrderPaymentGateway(_payment_gateway)

        tip_fees = d.pop("tipFees", UNSET)

        client_donation = d.pop("clientDonation", UNSET)

        notes = d.pop("notes", UNSET)

        organiser_mail_list_opt_in = d.pop("organiserMailListOptIn", UNSET)

        _incomplete_at = d.pop("incompleteAt", UNSET)
        incomplete_at: datetime.datetime | Unset
        if isinstance(_incomplete_at, Unset):
            incomplete_at = UNSET
        else:
            incomplete_at = isoparse(_incomplete_at)

        _completed_at = d.pop("completedAt", UNSET)
        completed_at: datetime.datetime | Unset
        if isinstance(_completed_at, Unset):
            completed_at = UNSET
        else:
            completed_at = isoparse(_completed_at)

        waitlist_offer_id = d.pop("waitlistOfferId", UNSET)

        is_international_transaction = d.pop("isInternationalTransaction", UNSET)

        _totals = d.pop("totals", UNSET)
        totals: OrderTotals | Unset
        if isinstance(_totals, Unset):
            totals = UNSET
        else:
            totals = OrderTotals.from_dict(_totals)

        _purchase_totals = d.pop("purchaseTotals", UNSET)
        purchase_totals: OrderTotals | Unset
        if isinstance(_purchase_totals, Unset):
            purchase_totals = UNSET
        else:
            purchase_totals = OrderTotals.from_dict(_purchase_totals)

        _additional_fields = d.pop("additionalFields", UNSET)
        additional_fields: list[AdditionalFields] | Unset = UNSET
        if _additional_fields is not UNSET:
            additional_fields = []
            for additional_fields_item_data in _additional_fields:
                additional_fields_item = AdditionalFields.from_dict(additional_fields_item_data)

                additional_fields.append(additional_fields_item)

        order = cls(
            field_id=field_id,
            currency=currency,
            status=status,
            financial_status=financial_status,
            manual_order=manual_order,
            sales_channel=sales_channel,
            location=location,
            created_at=created_at,
            updated_at=updated_at,
            event_id=event_id,
            user_id=user_id,
            event_date_id=event_date_id,
            first_name=first_name,
            last_name=last_name,
            organisation=organisation,
            mobile=mobile,
            email=email,
            access_code=access_code,
            discounts=discounts,
            business_purpose=business_purpose,
            business_tax_id=business_tax_id,
            business_name=business_name,
            payment_type=payment_type,
            payment_gateway=payment_gateway,
            tip_fees=tip_fees,
            client_donation=client_donation,
            notes=notes,
            organiser_mail_list_opt_in=organiser_mail_list_opt_in,
            incomplete_at=incomplete_at,
            completed_at=completed_at,
            waitlist_offer_id=waitlist_offer_id,
            is_international_transaction=is_international_transaction,
            totals=totals,
            purchase_totals=purchase_totals,
            additional_fields=additional_fields,
        )

        order.additional_properties = d
        return order

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
