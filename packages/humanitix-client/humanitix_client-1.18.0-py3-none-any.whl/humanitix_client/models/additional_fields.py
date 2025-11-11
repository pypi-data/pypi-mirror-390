from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.additional_fields_details import AdditionalFieldsDetails


T = TypeVar("T", bound="AdditionalFields")


@_attrs_define
class AdditionalFields:
    """
    Attributes:
        question_id (str):  Example: 5ac5c5e85aec29000ff064f4.
        value (str):  Example: Gluten Free.
        details (AdditionalFieldsDetails | Unset):
    """

    question_id: str
    value: str
    details: AdditionalFieldsDetails | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        question_id = self.question_id

        value = self.value

        details: dict[str, Any] | Unset = UNSET
        if not isinstance(self.details, Unset):
            details = self.details.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "questionId": question_id,
                "value": value,
            }
        )
        if details is not UNSET:
            field_dict["details"] = details

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.additional_fields_details import AdditionalFieldsDetails

        d = dict(src_dict)
        question_id = d.pop("questionId")

        value = d.pop("value")

        _details = d.pop("details", UNSET)
        details: AdditionalFieldsDetails | Unset
        if isinstance(_details, Unset):
            details = UNSET
        else:
            details = AdditionalFieldsDetails.from_dict(_details)

        additional_fields = cls(
            question_id=question_id,
            value=value,
            details=details,
        )

        additional_fields.additional_properties = d
        return additional_fields

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
