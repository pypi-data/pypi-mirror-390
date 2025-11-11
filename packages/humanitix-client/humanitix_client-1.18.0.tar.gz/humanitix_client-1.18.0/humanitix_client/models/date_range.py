from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="DateRange")


@_attrs_define
class DateRange:
    """
    Attributes:
        start_date (datetime.datetime):  Example: 2021-02-01T23:26:13.485Z.
        end_date (datetime.datetime):  Example: 2021-02-01T23:26:13.485Z.
        field_id (str | Unset):  Example: 5c9c25e08965939104239aab.
        schedule_id (str | Unset):  Example: 5fb6ceea1b2dec000ab9d367.
        disabled (bool | Unset):
        deleted (bool | Unset):
    """

    start_date: datetime.datetime
    end_date: datetime.datetime
    field_id: str | Unset = UNSET
    schedule_id: str | Unset = UNSET
    disabled: bool | Unset = UNSET
    deleted: bool | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        start_date = self.start_date.isoformat()

        end_date = self.end_date.isoformat()

        field_id = self.field_id

        schedule_id = self.schedule_id

        disabled = self.disabled

        deleted = self.deleted

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "startDate": start_date,
                "endDate": end_date,
            }
        )
        if field_id is not UNSET:
            field_dict["_id"] = field_id
        if schedule_id is not UNSET:
            field_dict["scheduleId"] = schedule_id
        if disabled is not UNSET:
            field_dict["disabled"] = disabled
        if deleted is not UNSET:
            field_dict["deleted"] = deleted

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        start_date = isoparse(d.pop("startDate"))

        end_date = isoparse(d.pop("endDate"))

        field_id = d.pop("_id", UNSET)

        schedule_id = d.pop("scheduleId", UNSET)

        disabled = d.pop("disabled", UNSET)

        deleted = d.pop("deleted", UNSET)

        date_range = cls(
            start_date=start_date,
            end_date=end_date,
            field_id=field_id,
            schedule_id=schedule_id,
            disabled=disabled,
            deleted=deleted,
        )

        date_range.additional_properties = d
        return date_range

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
