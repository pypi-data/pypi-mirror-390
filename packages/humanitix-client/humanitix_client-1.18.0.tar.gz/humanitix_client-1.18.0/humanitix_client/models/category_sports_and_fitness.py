from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.category_sports_and_fitness_category import CategorySportsAndFitnessCategory
from ..models.category_sports_and_fitness_subcategory import CategorySportsAndFitnessSubcategory
from ..types import UNSET, Unset

T = TypeVar("T", bound="CategorySportsAndFitness")


@_attrs_define
class CategorySportsAndFitness:
    """
    Attributes:
        category (CategorySportsAndFitnessCategory | Unset):
        subcategory (CategorySportsAndFitnessSubcategory | Unset):
    """

    category: CategorySportsAndFitnessCategory | Unset = UNSET
    subcategory: CategorySportsAndFitnessSubcategory | Unset = UNSET
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
        category: CategorySportsAndFitnessCategory | Unset
        if isinstance(_category, Unset):
            category = UNSET
        else:
            category = CategorySportsAndFitnessCategory(_category)

        _subcategory = d.pop("subcategory", UNSET)
        subcategory: CategorySportsAndFitnessSubcategory | Unset
        if isinstance(_subcategory, Unset):
            subcategory = UNSET
        else:
            subcategory = CategorySportsAndFitnessSubcategory(_subcategory)

        category_sports_and_fitness = cls(
            category=category,
            subcategory=subcategory,
        )

        category_sports_and_fitness.additional_properties = d
        return category_sports_and_fitness

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
