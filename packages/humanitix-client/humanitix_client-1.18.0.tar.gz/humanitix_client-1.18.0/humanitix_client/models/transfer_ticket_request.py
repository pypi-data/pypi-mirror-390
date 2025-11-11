from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="TransferTicketRequest")


@_attrs_define
class TransferTicketRequest:
    """
    Attributes:
        first_name (str):  Example: Bilbo.
        last_name (str):  Example: Baggins.
        email (str):  Example: bilbo.baggins@middleearth.com.
        mobile (str):  Example: 0412345678.
    """

    first_name: str
    last_name: str
    email: str
    mobile: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        first_name = self.first_name

        last_name = self.last_name

        email = self.email

        mobile = self.mobile

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "firstName": first_name,
                "lastName": last_name,
                "email": email,
                "mobile": mobile,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        first_name = d.pop("firstName")

        last_name = d.pop("lastName")

        email = d.pop("email")

        mobile = d.pop("mobile")

        transfer_ticket_request = cls(
            first_name=first_name,
            last_name=last_name,
            email=email,
            mobile=mobile,
        )

        transfer_ticket_request.additional_properties = d
        return transfer_ticket_request

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
