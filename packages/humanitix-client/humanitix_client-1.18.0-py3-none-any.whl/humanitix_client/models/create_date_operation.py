from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.create_date_operation_operation import CreateDateOperationOperation

T = TypeVar("T", bound="CreateDateOperation")


@_attrs_define
class CreateDateOperation:
    """
    Attributes:
        start_date (datetime.datetime):  Example: 2021-02-01T23:26:13.485Z.
        end_date (datetime.datetime):  Example: 2021-02-01T23:26:13.485Z.
        operation (CreateDateOperationOperation):
    """

    start_date: datetime.datetime
    end_date: datetime.datetime
    operation: CreateDateOperationOperation
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        start_date = self.start_date.isoformat()

        end_date = self.end_date.isoformat()

        operation = self.operation.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "startDate": start_date,
                "endDate": end_date,
                "operation": operation,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        start_date = isoparse(d.pop("startDate"))

        end_date = isoparse(d.pop("endDate"))

        operation = CreateDateOperationOperation(d.pop("operation"))

        create_date_operation = cls(
            start_date=start_date,
            end_date=end_date,
            operation=operation,
        )

        create_date_operation.additional_properties = d
        return create_date_operation

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
