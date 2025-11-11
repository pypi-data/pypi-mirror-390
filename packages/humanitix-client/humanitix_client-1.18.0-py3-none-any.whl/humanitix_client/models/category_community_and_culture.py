from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.category_community_and_culture_category import CategoryCommunityAndCultureCategory
from ..models.category_community_and_culture_subcategory import CategoryCommunityAndCultureSubcategory
from ..types import UNSET, Unset

T = TypeVar("T", bound="CategoryCommunityAndCulture")


@_attrs_define
class CategoryCommunityAndCulture:
    """
    Attributes:
        category (CategoryCommunityAndCultureCategory | Unset):
        subcategory (CategoryCommunityAndCultureSubcategory | Unset):
    """

    category: CategoryCommunityAndCultureCategory | Unset = UNSET
    subcategory: CategoryCommunityAndCultureSubcategory | Unset = UNSET
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
        category: CategoryCommunityAndCultureCategory | Unset
        if isinstance(_category, Unset):
            category = UNSET
        else:
            category = CategoryCommunityAndCultureCategory(_category)

        _subcategory = d.pop("subcategory", UNSET)
        subcategory: CategoryCommunityAndCultureSubcategory | Unset
        if isinstance(_subcategory, Unset):
            subcategory = UNSET
        else:
            subcategory = CategoryCommunityAndCultureSubcategory(_subcategory)

        category_community_and_culture = cls(
            category=category,
            subcategory=subcategory,
        )

        category_community_and_culture.additional_properties = d
        return category_community_and_culture

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
