from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.category_business_and_professional_category import CategoryBusinessAndProfessionalCategory
from ..models.category_business_and_professional_subcategory import CategoryBusinessAndProfessionalSubcategory
from ..types import UNSET, Unset

T = TypeVar("T", bound="CategoryBusinessAndProfessional")


@_attrs_define
class CategoryBusinessAndProfessional:
    """
    Attributes:
        category (CategoryBusinessAndProfessionalCategory | Unset):
        subcategory (CategoryBusinessAndProfessionalSubcategory | Unset):
    """

    category: CategoryBusinessAndProfessionalCategory | Unset = UNSET
    subcategory: CategoryBusinessAndProfessionalSubcategory | Unset = UNSET
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
        category: CategoryBusinessAndProfessionalCategory | Unset
        if isinstance(_category, Unset):
            category = UNSET
        else:
            category = CategoryBusinessAndProfessionalCategory(_category)

        _subcategory = d.pop("subcategory", UNSET)
        subcategory: CategoryBusinessAndProfessionalSubcategory | Unset
        if isinstance(_subcategory, Unset):
            subcategory = UNSET
        else:
            subcategory = CategoryBusinessAndProfessionalSubcategory(_subcategory)

        category_business_and_professional = cls(
            category=category,
            subcategory=subcategory,
        )

        category_business_and_professional.additional_properties = d
        return category_business_and_professional

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
