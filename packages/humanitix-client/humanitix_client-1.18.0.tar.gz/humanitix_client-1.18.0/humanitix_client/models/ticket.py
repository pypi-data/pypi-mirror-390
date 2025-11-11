from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.currency import Currency
from ..models.location import Location
from ..models.sales_channel import SalesChannel
from ..models.ticket_status import TicketStatus
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.additional_fields import AdditionalFields
    from ..models.check_in import CheckIn
    from ..models.discounts import Discounts
    from ..models.qr_code_data import QrCodeData
    from ..models.ticket_seating_location import TicketSeatingLocation
    from ..models.ticket_swap import TicketSwap


T = TypeVar("T", bound="Ticket")


@_attrs_define
class Ticket:
    """
    Attributes:
        field_id (str):  Example: 5da50970ec90824b5ca3608f.
        event_id (str):  Example: 5ac598ccd8fe7c0c0f212e2a.
        order_id (str):  Example: 5ac599d1a488620e6cd01d87.
        order_name (str):  Example: 0064YQ47.
        currency (Currency):
        event_date_id (str):  Example: 5ac598ccd8fe7c0c0f212e2f.
        ticket_type_name (str):  Example: General Admission.
        ticket_type_id (str):  Example: 5da50970ec90824b5ca3608f.
        discount (float):
        net_price (float):  Example: 37.5.
        taxes (float):  Example: 3.41.
        fee (float):  Example: 2.49.
        status (TicketStatus):
        sales_channel (SalesChannel): The channel through which the order or ticket was created, via an online sale or
            manual order.
        qr_code_data (QrCodeData):
        location (Location): The location of where the object is stored. Format is that of ISO 3166-1 alpha-2 country
            codes. Example: AU.
        created_at (datetime.datetime):  Example: 2021-02-01T23:26:13.485Z.
        updated_at (datetime.datetime):  Example: 2021-02-01T23:26:13.485Z.
        number (int | Unset):  Example: 1.
        first_name (str | Unset):  Example: Bilbo.
        last_name (str | Unset):  Example: Baggins.
        organisation (str | Unset):  Example: Free Peoples.
        access_code (str | Unset): The access code used on the order to reveal hidden tickets. If returned on the ticket
            object, this ticket was revealed by that access code. Example: EARLYACCESS.
        price (float | Unset):  Example: 37.5.
        passed_on_fee (float | Unset):
        absorbed_fee (float | Unset):
        dgr_donation (float | Unset):
        total (float | Unset):  Example: 39.99.
        custom_scanning_code (str | Unset):  Example: 29002208237292.
        seating_location (TicketSeatingLocation | Unset):
        additional_fields (list[AdditionalFields] | Unset):
        check_in (CheckIn | Unset):
        check_in_history (list[CheckIn] | Unset):
        cancelled_at (datetime.datetime | Unset):  Example: 2021-02-01T23:26:13.485Z.
        is_donation (bool | Unset):
        package_id (str | Unset):  Example: 5b7364d43bed06000f634bf9.
        package_name (str | Unset):  Example: Family.
        package_group_id (str | Unset):  Example: 5b73675b55aa47000fbdc354.
        package_price (float | Unset):  Example: 120.
        attendee_profile_id (str | Unset):  Example: 5d8d5dbfe40885ede10922d4.
        swapped_from (TicketSwap | Unset):
        swapped_to (TicketSwap | Unset):
        discounts (Discounts | Unset):
    """

    field_id: str
    event_id: str
    order_id: str
    order_name: str
    currency: Currency
    event_date_id: str
    ticket_type_name: str
    ticket_type_id: str
    discount: float
    net_price: float
    taxes: float
    fee: float
    status: TicketStatus
    sales_channel: SalesChannel
    qr_code_data: QrCodeData
    location: Location
    created_at: datetime.datetime
    updated_at: datetime.datetime
    number: int | Unset = UNSET
    first_name: str | Unset = UNSET
    last_name: str | Unset = UNSET
    organisation: str | Unset = UNSET
    access_code: str | Unset = UNSET
    price: float | Unset = UNSET
    passed_on_fee: float | Unset = UNSET
    absorbed_fee: float | Unset = UNSET
    dgr_donation: float | Unset = UNSET
    total: float | Unset = UNSET
    custom_scanning_code: str | Unset = UNSET
    seating_location: TicketSeatingLocation | Unset = UNSET
    additional_fields: list[AdditionalFields] | Unset = UNSET
    check_in: CheckIn | Unset = UNSET
    check_in_history: list[CheckIn] | Unset = UNSET
    cancelled_at: datetime.datetime | Unset = UNSET
    is_donation: bool | Unset = UNSET
    package_id: str | Unset = UNSET
    package_name: str | Unset = UNSET
    package_group_id: str | Unset = UNSET
    package_price: float | Unset = UNSET
    attendee_profile_id: str | Unset = UNSET
    swapped_from: TicketSwap | Unset = UNSET
    swapped_to: TicketSwap | Unset = UNSET
    discounts: Discounts | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        field_id = self.field_id

        event_id = self.event_id

        order_id = self.order_id

        order_name = self.order_name

        currency = self.currency.value

        event_date_id = self.event_date_id

        ticket_type_name = self.ticket_type_name

        ticket_type_id = self.ticket_type_id

        discount = self.discount

        net_price = self.net_price

        taxes = self.taxes

        fee = self.fee

        status = self.status.value

        sales_channel = self.sales_channel.value

        qr_code_data = self.qr_code_data.to_dict()

        location = self.location.value

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        number = self.number

        first_name = self.first_name

        last_name = self.last_name

        organisation = self.organisation

        access_code = self.access_code

        price = self.price

        passed_on_fee = self.passed_on_fee

        absorbed_fee = self.absorbed_fee

        dgr_donation = self.dgr_donation

        total = self.total

        custom_scanning_code = self.custom_scanning_code

        seating_location: dict[str, Any] | Unset = UNSET
        if not isinstance(self.seating_location, Unset):
            seating_location = self.seating_location.to_dict()

        additional_fields: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.additional_fields, Unset):
            additional_fields = []
            for additional_fields_item_data in self.additional_fields:
                additional_fields_item = additional_fields_item_data.to_dict()
                additional_fields.append(additional_fields_item)

        check_in: dict[str, Any] | Unset = UNSET
        if not isinstance(self.check_in, Unset):
            check_in = self.check_in.to_dict()

        check_in_history: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.check_in_history, Unset):
            check_in_history = []
            for check_in_history_item_data in self.check_in_history:
                check_in_history_item = check_in_history_item_data.to_dict()
                check_in_history.append(check_in_history_item)

        cancelled_at: str | Unset = UNSET
        if not isinstance(self.cancelled_at, Unset):
            cancelled_at = self.cancelled_at.isoformat()

        is_donation = self.is_donation

        package_id = self.package_id

        package_name = self.package_name

        package_group_id = self.package_group_id

        package_price = self.package_price

        attendee_profile_id = self.attendee_profile_id

        swapped_from: dict[str, Any] | Unset = UNSET
        if not isinstance(self.swapped_from, Unset):
            swapped_from = self.swapped_from.to_dict()

        swapped_to: dict[str, Any] | Unset = UNSET
        if not isinstance(self.swapped_to, Unset):
            swapped_to = self.swapped_to.to_dict()

        discounts: dict[str, Any] | Unset = UNSET
        if not isinstance(self.discounts, Unset):
            discounts = self.discounts.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "_id": field_id,
                "eventId": event_id,
                "orderId": order_id,
                "orderName": order_name,
                "currency": currency,
                "eventDateId": event_date_id,
                "ticketTypeName": ticket_type_name,
                "ticketTypeId": ticket_type_id,
                "discount": discount,
                "netPrice": net_price,
                "taxes": taxes,
                "fee": fee,
                "status": status,
                "salesChannel": sales_channel,
                "qrCodeData": qr_code_data,
                "location": location,
                "createdAt": created_at,
                "updatedAt": updated_at,
            }
        )
        if number is not UNSET:
            field_dict["number"] = number
        if first_name is not UNSET:
            field_dict["firstName"] = first_name
        if last_name is not UNSET:
            field_dict["lastName"] = last_name
        if organisation is not UNSET:
            field_dict["organisation"] = organisation
        if access_code is not UNSET:
            field_dict["accessCode"] = access_code
        if price is not UNSET:
            field_dict["price"] = price
        if passed_on_fee is not UNSET:
            field_dict["passedOnFee"] = passed_on_fee
        if absorbed_fee is not UNSET:
            field_dict["absorbedFee"] = absorbed_fee
        if dgr_donation is not UNSET:
            field_dict["dgrDonation"] = dgr_donation
        if total is not UNSET:
            field_dict["total"] = total
        if custom_scanning_code is not UNSET:
            field_dict["customScanningCode"] = custom_scanning_code
        if seating_location is not UNSET:
            field_dict["seatingLocation"] = seating_location
        if additional_fields is not UNSET:
            field_dict["additionalFields"] = additional_fields
        if check_in is not UNSET:
            field_dict["checkIn"] = check_in
        if check_in_history is not UNSET:
            field_dict["checkInHistory"] = check_in_history
        if cancelled_at is not UNSET:
            field_dict["cancelledAt"] = cancelled_at
        if is_donation is not UNSET:
            field_dict["isDonation"] = is_donation
        if package_id is not UNSET:
            field_dict["packageId"] = package_id
        if package_name is not UNSET:
            field_dict["packageName"] = package_name
        if package_group_id is not UNSET:
            field_dict["packageGroupId"] = package_group_id
        if package_price is not UNSET:
            field_dict["packagePrice"] = package_price
        if attendee_profile_id is not UNSET:
            field_dict["attendeeProfileId"] = attendee_profile_id
        if swapped_from is not UNSET:
            field_dict["swappedFrom"] = swapped_from
        if swapped_to is not UNSET:
            field_dict["swappedTo"] = swapped_to
        if discounts is not UNSET:
            field_dict["discounts"] = discounts

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.additional_fields import AdditionalFields
        from ..models.check_in import CheckIn
        from ..models.discounts import Discounts
        from ..models.qr_code_data import QrCodeData
        from ..models.ticket_seating_location import TicketSeatingLocation
        from ..models.ticket_swap import TicketSwap

        d = dict(src_dict)
        field_id = d.pop("_id")

        event_id = d.pop("eventId")

        order_id = d.pop("orderId")

        order_name = d.pop("orderName")

        currency = Currency(d.pop("currency"))

        event_date_id = d.pop("eventDateId")

        ticket_type_name = d.pop("ticketTypeName")

        ticket_type_id = d.pop("ticketTypeId")

        discount = d.pop("discount")

        net_price = d.pop("netPrice")

        taxes = d.pop("taxes")

        fee = d.pop("fee")

        status = TicketStatus(d.pop("status"))

        sales_channel = SalesChannel(d.pop("salesChannel"))

        qr_code_data = QrCodeData.from_dict(d.pop("qrCodeData"))

        location = Location(d.pop("location"))

        created_at = isoparse(d.pop("createdAt"))

        updated_at = isoparse(d.pop("updatedAt"))

        number = d.pop("number", UNSET)

        first_name = d.pop("firstName", UNSET)

        last_name = d.pop("lastName", UNSET)

        organisation = d.pop("organisation", UNSET)

        access_code = d.pop("accessCode", UNSET)

        price = d.pop("price", UNSET)

        passed_on_fee = d.pop("passedOnFee", UNSET)

        absorbed_fee = d.pop("absorbedFee", UNSET)

        dgr_donation = d.pop("dgrDonation", UNSET)

        total = d.pop("total", UNSET)

        custom_scanning_code = d.pop("customScanningCode", UNSET)

        _seating_location = d.pop("seatingLocation", UNSET)
        seating_location: TicketSeatingLocation | Unset
        if isinstance(_seating_location, Unset):
            seating_location = UNSET
        else:
            seating_location = TicketSeatingLocation.from_dict(_seating_location)

        _additional_fields = d.pop("additionalFields", UNSET)
        additional_fields: list[AdditionalFields] | Unset = UNSET
        if _additional_fields is not UNSET:
            additional_fields = []
            for additional_fields_item_data in _additional_fields:
                additional_fields_item = AdditionalFields.from_dict(additional_fields_item_data)

                additional_fields.append(additional_fields_item)

        _check_in = d.pop("checkIn", UNSET)
        check_in: CheckIn | Unset
        if isinstance(_check_in, Unset):
            check_in = UNSET
        else:
            check_in = CheckIn.from_dict(_check_in)

        _check_in_history = d.pop("checkInHistory", UNSET)
        check_in_history: list[CheckIn] | Unset = UNSET
        if _check_in_history is not UNSET:
            check_in_history = []
            for check_in_history_item_data in _check_in_history:
                check_in_history_item = CheckIn.from_dict(check_in_history_item_data)

                check_in_history.append(check_in_history_item)

        _cancelled_at = d.pop("cancelledAt", UNSET)
        cancelled_at: datetime.datetime | Unset
        if isinstance(_cancelled_at, Unset):
            cancelled_at = UNSET
        else:
            cancelled_at = isoparse(_cancelled_at)

        is_donation = d.pop("isDonation", UNSET)

        package_id = d.pop("packageId", UNSET)

        package_name = d.pop("packageName", UNSET)

        package_group_id = d.pop("packageGroupId", UNSET)

        package_price = d.pop("packagePrice", UNSET)

        attendee_profile_id = d.pop("attendeeProfileId", UNSET)

        _swapped_from = d.pop("swappedFrom", UNSET)
        swapped_from: TicketSwap | Unset
        if isinstance(_swapped_from, Unset):
            swapped_from = UNSET
        else:
            swapped_from = TicketSwap.from_dict(_swapped_from)

        _swapped_to = d.pop("swappedTo", UNSET)
        swapped_to: TicketSwap | Unset
        if isinstance(_swapped_to, Unset):
            swapped_to = UNSET
        else:
            swapped_to = TicketSwap.from_dict(_swapped_to)

        _discounts = d.pop("discounts", UNSET)
        discounts: Discounts | Unset
        if isinstance(_discounts, Unset):
            discounts = UNSET
        else:
            discounts = Discounts.from_dict(_discounts)

        ticket = cls(
            field_id=field_id,
            event_id=event_id,
            order_id=order_id,
            order_name=order_name,
            currency=currency,
            event_date_id=event_date_id,
            ticket_type_name=ticket_type_name,
            ticket_type_id=ticket_type_id,
            discount=discount,
            net_price=net_price,
            taxes=taxes,
            fee=fee,
            status=status,
            sales_channel=sales_channel,
            qr_code_data=qr_code_data,
            location=location,
            created_at=created_at,
            updated_at=updated_at,
            number=number,
            first_name=first_name,
            last_name=last_name,
            organisation=organisation,
            access_code=access_code,
            price=price,
            passed_on_fee=passed_on_fee,
            absorbed_fee=absorbed_fee,
            dgr_donation=dgr_donation,
            total=total,
            custom_scanning_code=custom_scanning_code,
            seating_location=seating_location,
            additional_fields=additional_fields,
            check_in=check_in,
            check_in_history=check_in_history,
            cancelled_at=cancelled_at,
            is_donation=is_donation,
            package_id=package_id,
            package_name=package_name,
            package_group_id=package_group_id,
            package_price=package_price,
            attendee_profile_id=attendee_profile_id,
            swapped_from=swapped_from,
            swapped_to=swapped_to,
            discounts=discounts,
        )

        ticket.additional_properties = d
        return ticket

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
