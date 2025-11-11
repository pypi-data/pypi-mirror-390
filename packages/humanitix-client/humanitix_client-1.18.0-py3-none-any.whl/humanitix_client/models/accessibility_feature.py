from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="AccessibilityFeature")


@_attrs_define
class AccessibilityFeature:
    """
    Attributes:
        access (bool | Unset):
        wheelchair_accessibility (bool | Unset):
        audio_description (bool | Unset):
        telephone_typewriter (bool | Unset):
        volume_control_telephone (bool | Unset):
        assistive_listening_systems (bool | Unset):
        sign_language_interpretation (bool | Unset):
        accessible_print (bool | Unset):
        closed_captioning (bool | Unset):
        opened_captioning (bool | Unset):
        braille_symbol (bool | Unset):
    """

    access: bool | Unset = UNSET
    wheelchair_accessibility: bool | Unset = UNSET
    audio_description: bool | Unset = UNSET
    telephone_typewriter: bool | Unset = UNSET
    volume_control_telephone: bool | Unset = UNSET
    assistive_listening_systems: bool | Unset = UNSET
    sign_language_interpretation: bool | Unset = UNSET
    accessible_print: bool | Unset = UNSET
    closed_captioning: bool | Unset = UNSET
    opened_captioning: bool | Unset = UNSET
    braille_symbol: bool | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        access = self.access

        wheelchair_accessibility = self.wheelchair_accessibility

        audio_description = self.audio_description

        telephone_typewriter = self.telephone_typewriter

        volume_control_telephone = self.volume_control_telephone

        assistive_listening_systems = self.assistive_listening_systems

        sign_language_interpretation = self.sign_language_interpretation

        accessible_print = self.accessible_print

        closed_captioning = self.closed_captioning

        opened_captioning = self.opened_captioning

        braille_symbol = self.braille_symbol

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if access is not UNSET:
            field_dict["access"] = access
        if wheelchair_accessibility is not UNSET:
            field_dict["wheelchairAccessibility"] = wheelchair_accessibility
        if audio_description is not UNSET:
            field_dict["audioDescription"] = audio_description
        if telephone_typewriter is not UNSET:
            field_dict["telephoneTypewriter"] = telephone_typewriter
        if volume_control_telephone is not UNSET:
            field_dict["volumeControlTelephone"] = volume_control_telephone
        if assistive_listening_systems is not UNSET:
            field_dict["assistiveListeningSystems"] = assistive_listening_systems
        if sign_language_interpretation is not UNSET:
            field_dict["signLanguageInterpretation"] = sign_language_interpretation
        if accessible_print is not UNSET:
            field_dict["accessiblePrint"] = accessible_print
        if closed_captioning is not UNSET:
            field_dict["closedCaptioning"] = closed_captioning
        if opened_captioning is not UNSET:
            field_dict["openedCaptioning"] = opened_captioning
        if braille_symbol is not UNSET:
            field_dict["brailleSymbol"] = braille_symbol

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        access = d.pop("access", UNSET)

        wheelchair_accessibility = d.pop("wheelchairAccessibility", UNSET)

        audio_description = d.pop("audioDescription", UNSET)

        telephone_typewriter = d.pop("telephoneTypewriter", UNSET)

        volume_control_telephone = d.pop("volumeControlTelephone", UNSET)

        assistive_listening_systems = d.pop("assistiveListeningSystems", UNSET)

        sign_language_interpretation = d.pop("signLanguageInterpretation", UNSET)

        accessible_print = d.pop("accessiblePrint", UNSET)

        closed_captioning = d.pop("closedCaptioning", UNSET)

        opened_captioning = d.pop("openedCaptioning", UNSET)

        braille_symbol = d.pop("brailleSymbol", UNSET)

        accessibility_feature = cls(
            access=access,
            wheelchair_accessibility=wheelchair_accessibility,
            audio_description=audio_description,
            telephone_typewriter=telephone_typewriter,
            volume_control_telephone=volume_control_telephone,
            assistive_listening_systems=assistive_listening_systems,
            sign_language_interpretation=sign_language_interpretation,
            accessible_print=accessible_print,
            closed_captioning=closed_captioning,
            opened_captioning=opened_captioning,
            braille_symbol=braille_symbol,
        )

        accessibility_feature.additional_properties = d
        return accessibility_feature

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
