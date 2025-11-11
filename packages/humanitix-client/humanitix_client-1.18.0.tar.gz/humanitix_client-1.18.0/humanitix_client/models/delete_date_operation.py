from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.delete_date_operation_operation import DeleteDateOperationOperation

T = TypeVar("T", bound="DeleteDateOperation")


@_attrs_define
class DeleteDateOperation:
    """
    Attributes:
        field_id (str):  Example: 5c9c25e08965939104239aab.
        operation (DeleteDateOperationOperation):
    """

    field_id: str
    operation: DeleteDateOperationOperation
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        field_id = self.field_id

        operation = self.operation.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "_id": field_id,
                "operation": operation,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        field_id = d.pop("_id")

        operation = DeleteDateOperationOperation(d.pop("operation"))

        delete_date_operation = cls(
            field_id=field_id,
            operation=operation,
        )

        delete_date_operation.additional_properties = d
        return delete_date_operation

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
