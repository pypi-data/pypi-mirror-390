from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.additional_questions_input_type import AdditionalQuestionsInputType
from ..types import UNSET, Unset

T = TypeVar("T", bound="AdditionalQuestions")


@_attrs_define
class AdditionalQuestions:
    """
    Attributes:
        field_id (str):  Example: 5ac5c5e85aec29000ff064f4.
        question (str):
        required (bool):
        per_order (bool):
        input_type (AdditionalQuestionsInputType | Unset):
        description (str | Unset):
        disabled (bool | Unset):
        created_at (datetime.datetime | Unset):  Example: 2021-02-01T23:26:13.485Z.
        updated_at (datetime.datetime | Unset):  Example: 2021-02-01T23:26:13.485Z.
    """

    field_id: str
    question: str
    required: bool
    per_order: bool
    input_type: AdditionalQuestionsInputType | Unset = UNSET
    description: str | Unset = UNSET
    disabled: bool | Unset = UNSET
    created_at: datetime.datetime | Unset = UNSET
    updated_at: datetime.datetime | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        field_id = self.field_id

        question = self.question

        required = self.required

        per_order = self.per_order

        input_type: str | Unset = UNSET
        if not isinstance(self.input_type, Unset):
            input_type = self.input_type.value

        description = self.description

        disabled = self.disabled

        created_at: str | Unset = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()

        updated_at: str | Unset = UNSET
        if not isinstance(self.updated_at, Unset):
            updated_at = self.updated_at.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "_id": field_id,
                "question": question,
                "required": required,
                "perOrder": per_order,
            }
        )
        if input_type is not UNSET:
            field_dict["inputType"] = input_type
        if description is not UNSET:
            field_dict["description"] = description
        if disabled is not UNSET:
            field_dict["disabled"] = disabled
        if created_at is not UNSET:
            field_dict["createdAt"] = created_at
        if updated_at is not UNSET:
            field_dict["updatedAt"] = updated_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        field_id = d.pop("_id")

        question = d.pop("question")

        required = d.pop("required")

        per_order = d.pop("perOrder")

        _input_type = d.pop("inputType", UNSET)
        input_type: AdditionalQuestionsInputType | Unset
        if isinstance(_input_type, Unset):
            input_type = UNSET
        else:
            input_type = AdditionalQuestionsInputType(_input_type)

        description = d.pop("description", UNSET)

        disabled = d.pop("disabled", UNSET)

        _created_at = d.pop("createdAt", UNSET)
        created_at: datetime.datetime | Unset
        if isinstance(_created_at, Unset):
            created_at = UNSET
        else:
            created_at = isoparse(_created_at)

        _updated_at = d.pop("updatedAt", UNSET)
        updated_at: datetime.datetime | Unset
        if isinstance(_updated_at, Unset):
            updated_at = UNSET
        else:
            updated_at = isoparse(_updated_at)

        additional_questions = cls(
            field_id=field_id,
            question=question,
            required=required,
            per_order=per_order,
            input_type=input_type,
            description=description,
            disabled=disabled,
            created_at=created_at,
            updated_at=updated_at,
        )

        additional_questions.additional_properties = d
        return additional_questions

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
