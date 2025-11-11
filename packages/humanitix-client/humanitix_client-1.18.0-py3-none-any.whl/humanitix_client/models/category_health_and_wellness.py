from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.category_health_and_wellness_category import CategoryHealthAndWellnessCategory
from ..models.category_health_and_wellness_subcategory import CategoryHealthAndWellnessSubcategory
from ..types import UNSET, Unset

T = TypeVar("T", bound="CategoryHealthAndWellness")


@_attrs_define
class CategoryHealthAndWellness:
    """
    Attributes:
        category (CategoryHealthAndWellnessCategory | Unset):
        subcategory (CategoryHealthAndWellnessSubcategory | Unset):
    """

    category: CategoryHealthAndWellnessCategory | Unset = UNSET
    subcategory: CategoryHealthAndWellnessSubcategory | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        category: str | Unset = UNSET
        if not isinstance(self.category, Unset):
            category = self.category.value

        subcategory: str | Unset = UNSET
        if not isinstance(self.subcategory, Unset):
            subcategory = self.subcategory.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if category is not UNSET:
            field_dict["category"] = category
        if subcategory is not UNSET:
            field_dict["subcategory"] = subcategory

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        _category = d.pop("category", UNSET)
        category: CategoryHealthAndWellnessCategory | Unset
        if isinstance(_category, Unset):
            category = UNSET
        else:
            category = CategoryHealthAndWellnessCategory(_category)

        _subcategory = d.pop("subcategory", UNSET)
        subcategory: CategoryHealthAndWellnessSubcategory | Unset
        if isinstance(_subcategory, Unset):
            subcategory = UNSET
        else:
            subcategory = CategoryHealthAndWellnessSubcategory(_subcategory)

        category_health_and_wellness = cls(
            category=category,
            subcategory=subcategory,
        )

        category_health_and_wellness.additional_properties = d
        return category_health_and_wellness

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
