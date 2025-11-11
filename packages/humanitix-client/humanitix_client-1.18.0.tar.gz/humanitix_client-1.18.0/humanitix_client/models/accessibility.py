from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.accessibility_feature import AccessibilityFeature


T = TypeVar("T", bound="Accessibility")


@_attrs_define
class Accessibility:
    """
    Attributes:
        contact_name (str | Unset):  Example: Gandalf The Grey.
        contact_number (str | Unset):  Example: 0412345678.
        travel_instructions (str | Unset):  Example: The closest drop off point is The Shires Rest. The best public
            transport option is....
        entry_instructions (str | Unset):  Example: To enter the building there is....
        after_entry_instructions (str | Unset):  Example: fter entering the building walk 10 meters forward than 3
            meters right where you should introduce yourself to reception....
        hazards (str | Unset):  Example: NA.
        toilet_location (str | Unset):  Example: Disabled toilets are located on ground level of the building only..
        disabled_parking (str | Unset):  Example: 5 spaces available in the Wilsons car park at 151 Example Street..
        features (AccessibilityFeature | Unset):
    """

    contact_name: str | Unset = UNSET
    contact_number: str | Unset = UNSET
    travel_instructions: str | Unset = UNSET
    entry_instructions: str | Unset = UNSET
    after_entry_instructions: str | Unset = UNSET
    hazards: str | Unset = UNSET
    toilet_location: str | Unset = UNSET
    disabled_parking: str | Unset = UNSET
    features: AccessibilityFeature | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        contact_name = self.contact_name

        contact_number = self.contact_number

        travel_instructions = self.travel_instructions

        entry_instructions = self.entry_instructions

        after_entry_instructions = self.after_entry_instructions

        hazards = self.hazards

        toilet_location = self.toilet_location

        disabled_parking = self.disabled_parking

        features: dict[str, Any] | Unset = UNSET
        if not isinstance(self.features, Unset):
            features = self.features.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if contact_name is not UNSET:
            field_dict["contactName"] = contact_name
        if contact_number is not UNSET:
            field_dict["contactNumber"] = contact_number
        if travel_instructions is not UNSET:
            field_dict["travelInstructions"] = travel_instructions
        if entry_instructions is not UNSET:
            field_dict["entryInstructions"] = entry_instructions
        if after_entry_instructions is not UNSET:
            field_dict["afterEntryInstructions"] = after_entry_instructions
        if hazards is not UNSET:
            field_dict["hazards"] = hazards
        if toilet_location is not UNSET:
            field_dict["toiletLocation"] = toilet_location
        if disabled_parking is not UNSET:
            field_dict["disabledParking"] = disabled_parking
        if features is not UNSET:
            field_dict["features"] = features

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.accessibility_feature import AccessibilityFeature

        d = dict(src_dict)
        contact_name = d.pop("contactName", UNSET)

        contact_number = d.pop("contactNumber", UNSET)

        travel_instructions = d.pop("travelInstructions", UNSET)

        entry_instructions = d.pop("entryInstructions", UNSET)

        after_entry_instructions = d.pop("afterEntryInstructions", UNSET)

        hazards = d.pop("hazards", UNSET)

        toilet_location = d.pop("toiletLocation", UNSET)

        disabled_parking = d.pop("disabledParking", UNSET)

        _features = d.pop("features", UNSET)
        features: AccessibilityFeature | Unset
        if isinstance(_features, Unset):
            features = UNSET
        else:
            features = AccessibilityFeature.from_dict(_features)

        accessibility = cls(
            contact_name=contact_name,
            contact_number=contact_number,
            travel_instructions=travel_instructions,
            entry_instructions=entry_instructions,
            after_entry_instructions=after_entry_instructions,
            hazards=hazards,
            toilet_location=toilet_location,
            disabled_parking=disabled_parking,
            features=features,
        )

        accessibility.additional_properties = d
        return accessibility

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
