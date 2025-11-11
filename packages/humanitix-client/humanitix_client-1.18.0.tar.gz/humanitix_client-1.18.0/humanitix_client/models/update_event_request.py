from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.location import Location
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.category_auto_boat_and_air import CategoryAutoBoatAndAir
    from ..models.category_business_and_professional import CategoryBusinessAndProfessional
    from ..models.category_charity_and_causes import CategoryCharityAndCauses
    from ..models.category_community_and_culture import CategoryCommunityAndCulture
    from ..models.category_family_and_education import CategoryFamilyAndEducation
    from ..models.category_fashion_and_beauty import CategoryFashionAndBeauty
    from ..models.category_film_media_and_entertainment import CategoryFilmMediaAndEntertainment
    from ..models.category_food_and_drink import CategoryFoodAndDrink
    from ..models.category_government_and_politics import CategoryGovernmentAndPolitics
    from ..models.category_health_and_wellness import CategoryHealthAndWellness
    from ..models.category_hobbies_and_special_interest import CategoryHobbiesAndSpecialInterest
    from ..models.category_home_and_lifestyle import CategoryHomeAndLifestyle
    from ..models.category_music import CategoryMusic
    from ..models.category_other import CategoryOther
    from ..models.category_performing_and_visual_arts import CategoryPerformingAndVisualArts
    from ..models.category_religion_and_spirituality import CategoryReligionAndSpirituality
    from ..models.category_school_activities import CategorySchoolActivities
    from ..models.category_science_and_technology import CategoryScienceAndTechnology
    from ..models.category_seasonal_and_holiday import CategorySeasonalAndHoliday
    from ..models.category_sports_and_fitness import CategorySportsAndFitness
    from ..models.category_travel_and_outdoor import CategoryTravelAndOutdoor
    from ..models.create_address_event_location import CreateAddressEventLocation
    from ..models.create_custom_event_location import CreateCustomEventLocation
    from ..models.create_date_operation import CreateDateOperation
    from ..models.create_online_event_location import CreateOnlineEventLocation
    from ..models.create_to_be_announced_event_location import CreateToBeAnnouncedEventLocation
    from ..models.delete_date_operation import DeleteDateOperation
    from ..models.update_date_operation import UpdateDateOperation


T = TypeVar("T", bound="UpdateEventRequest")


@_attrs_define
class UpdateEventRequest:
    """
    Attributes:
        name (str | Unset):  Example: Lord of the Rings.
        description (str | Unset):  Example: A quest to destroy a powerful ring and defeat a dark lord.
        timezone (str | Unset):  Example: Pacific/Auckland.
        event_location (CreateAddressEventLocation | CreateCustomEventLocation | CreateOnlineEventLocation |
            CreateToBeAnnouncedEventLocation | Unset):
        keywords (list[str] | Unset):
        classification (CategoryAutoBoatAndAir | CategoryBusinessAndProfessional | CategoryCharityAndCauses |
            CategoryCommunityAndCulture | CategoryFamilyAndEducation | CategoryFashionAndBeauty |
            CategoryFilmMediaAndEntertainment | CategoryFoodAndDrink | CategoryGovernmentAndPolitics |
            CategoryHealthAndWellness | CategoryHobbiesAndSpecialInterest | CategoryHomeAndLifestyle | CategoryMusic |
            CategoryOther | CategoryPerformingAndVisualArts | CategoryReligionAndSpirituality | CategorySchoolActivities |
            CategoryScienceAndTechnology | CategorySeasonalAndHoliday | CategorySportsAndFitness | CategoryTravelAndOutdoor
            | Unset):
        dates (list[CreateDateOperation | DeleteDateOperation | UpdateDateOperation] | Unset):
        location (Location | Unset): The location of where the object is stored. Format is that of ISO 3166-1 alpha-2
            country codes. Example: AU.
    """

    name: str | Unset = UNSET
    description: str | Unset = UNSET
    timezone: str | Unset = UNSET
    event_location: (
        CreateAddressEventLocation
        | CreateCustomEventLocation
        | CreateOnlineEventLocation
        | CreateToBeAnnouncedEventLocation
        | Unset
    ) = UNSET
    keywords: list[str] | Unset = UNSET
    classification: (
        CategoryAutoBoatAndAir
        | CategoryBusinessAndProfessional
        | CategoryCharityAndCauses
        | CategoryCommunityAndCulture
        | CategoryFamilyAndEducation
        | CategoryFashionAndBeauty
        | CategoryFilmMediaAndEntertainment
        | CategoryFoodAndDrink
        | CategoryGovernmentAndPolitics
        | CategoryHealthAndWellness
        | CategoryHobbiesAndSpecialInterest
        | CategoryHomeAndLifestyle
        | CategoryMusic
        | CategoryOther
        | CategoryPerformingAndVisualArts
        | CategoryReligionAndSpirituality
        | CategorySchoolActivities
        | CategoryScienceAndTechnology
        | CategorySeasonalAndHoliday
        | CategorySportsAndFitness
        | CategoryTravelAndOutdoor
        | Unset
    ) = UNSET
    dates: list[CreateDateOperation | DeleteDateOperation | UpdateDateOperation] | Unset = UNSET
    location: Location | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.category_auto_boat_and_air import CategoryAutoBoatAndAir
        from ..models.category_business_and_professional import CategoryBusinessAndProfessional
        from ..models.category_charity_and_causes import CategoryCharityAndCauses
        from ..models.category_community_and_culture import CategoryCommunityAndCulture
        from ..models.category_family_and_education import CategoryFamilyAndEducation
        from ..models.category_fashion_and_beauty import CategoryFashionAndBeauty
        from ..models.category_film_media_and_entertainment import CategoryFilmMediaAndEntertainment
        from ..models.category_food_and_drink import CategoryFoodAndDrink
        from ..models.category_government_and_politics import CategoryGovernmentAndPolitics
        from ..models.category_health_and_wellness import CategoryHealthAndWellness
        from ..models.category_hobbies_and_special_interest import CategoryHobbiesAndSpecialInterest
        from ..models.category_home_and_lifestyle import CategoryHomeAndLifestyle
        from ..models.category_music import CategoryMusic
        from ..models.category_performing_and_visual_arts import CategoryPerformingAndVisualArts
        from ..models.category_religion_and_spirituality import CategoryReligionAndSpirituality
        from ..models.category_school_activities import CategorySchoolActivities
        from ..models.category_science_and_technology import CategoryScienceAndTechnology
        from ..models.category_seasonal_and_holiday import CategorySeasonalAndHoliday
        from ..models.category_sports_and_fitness import CategorySportsAndFitness
        from ..models.category_travel_and_outdoor import CategoryTravelAndOutdoor
        from ..models.create_address_event_location import CreateAddressEventLocation
        from ..models.create_custom_event_location import CreateCustomEventLocation
        from ..models.create_date_operation import CreateDateOperation
        from ..models.create_online_event_location import CreateOnlineEventLocation
        from ..models.update_date_operation import UpdateDateOperation

        name = self.name

        description = self.description

        timezone = self.timezone

        event_location: dict[str, Any] | Unset
        if isinstance(self.event_location, Unset):
            event_location = UNSET
        elif isinstance(self.event_location, CreateOnlineEventLocation):
            event_location = self.event_location.to_dict()
        elif isinstance(self.event_location, CreateAddressEventLocation):
            event_location = self.event_location.to_dict()
        elif isinstance(self.event_location, CreateCustomEventLocation):
            event_location = self.event_location.to_dict()
        else:
            event_location = self.event_location.to_dict()

        keywords: list[str] | Unset = UNSET
        if not isinstance(self.keywords, Unset):
            keywords = self.keywords

        classification: dict[str, Any] | Unset
        if isinstance(self.classification, Unset):
            classification = UNSET
        elif isinstance(self.classification, CategoryAutoBoatAndAir):
            classification = self.classification.to_dict()
        elif isinstance(self.classification, CategoryBusinessAndProfessional):
            classification = self.classification.to_dict()
        elif isinstance(self.classification, CategoryCharityAndCauses):
            classification = self.classification.to_dict()
        elif isinstance(self.classification, CategoryCommunityAndCulture):
            classification = self.classification.to_dict()
        elif isinstance(self.classification, CategoryFamilyAndEducation):
            classification = self.classification.to_dict()
        elif isinstance(self.classification, CategoryFashionAndBeauty):
            classification = self.classification.to_dict()
        elif isinstance(self.classification, CategoryFilmMediaAndEntertainment):
            classification = self.classification.to_dict()
        elif isinstance(self.classification, CategoryFoodAndDrink):
            classification = self.classification.to_dict()
        elif isinstance(self.classification, CategoryGovernmentAndPolitics):
            classification = self.classification.to_dict()
        elif isinstance(self.classification, CategoryHealthAndWellness):
            classification = self.classification.to_dict()
        elif isinstance(self.classification, CategoryHobbiesAndSpecialInterest):
            classification = self.classification.to_dict()
        elif isinstance(self.classification, CategoryHomeAndLifestyle):
            classification = self.classification.to_dict()
        elif isinstance(self.classification, CategoryMusic):
            classification = self.classification.to_dict()
        elif isinstance(self.classification, CategoryPerformingAndVisualArts):
            classification = self.classification.to_dict()
        elif isinstance(self.classification, CategoryReligionAndSpirituality):
            classification = self.classification.to_dict()
        elif isinstance(self.classification, CategorySchoolActivities):
            classification = self.classification.to_dict()
        elif isinstance(self.classification, CategoryScienceAndTechnology):
            classification = self.classification.to_dict()
        elif isinstance(self.classification, CategorySeasonalAndHoliday):
            classification = self.classification.to_dict()
        elif isinstance(self.classification, CategorySportsAndFitness):
            classification = self.classification.to_dict()
        elif isinstance(self.classification, CategoryTravelAndOutdoor):
            classification = self.classification.to_dict()
        else:
            classification = self.classification.to_dict()

        dates: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.dates, Unset):
            dates = []
            for dates_item_data in self.dates:
                dates_item: dict[str, Any]
                if isinstance(dates_item_data, CreateDateOperation):
                    dates_item = dates_item_data.to_dict()
                elif isinstance(dates_item_data, UpdateDateOperation):
                    dates_item = dates_item_data.to_dict()
                else:
                    dates_item = dates_item_data.to_dict()

                dates.append(dates_item)

        location: str | Unset = UNSET
        if not isinstance(self.location, Unset):
            location = self.location.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if description is not UNSET:
            field_dict["description"] = description
        if timezone is not UNSET:
            field_dict["timezone"] = timezone
        if event_location is not UNSET:
            field_dict["eventLocation"] = event_location
        if keywords is not UNSET:
            field_dict["keywords"] = keywords
        if classification is not UNSET:
            field_dict["classification"] = classification
        if dates is not UNSET:
            field_dict["dates"] = dates
        if location is not UNSET:
            field_dict["location"] = location

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.category_auto_boat_and_air import CategoryAutoBoatAndAir
        from ..models.category_business_and_professional import CategoryBusinessAndProfessional
        from ..models.category_charity_and_causes import CategoryCharityAndCauses
        from ..models.category_community_and_culture import CategoryCommunityAndCulture
        from ..models.category_family_and_education import CategoryFamilyAndEducation
        from ..models.category_fashion_and_beauty import CategoryFashionAndBeauty
        from ..models.category_film_media_and_entertainment import CategoryFilmMediaAndEntertainment
        from ..models.category_food_and_drink import CategoryFoodAndDrink
        from ..models.category_government_and_politics import CategoryGovernmentAndPolitics
        from ..models.category_health_and_wellness import CategoryHealthAndWellness
        from ..models.category_hobbies_and_special_interest import CategoryHobbiesAndSpecialInterest
        from ..models.category_home_and_lifestyle import CategoryHomeAndLifestyle
        from ..models.category_music import CategoryMusic
        from ..models.category_other import CategoryOther
        from ..models.category_performing_and_visual_arts import CategoryPerformingAndVisualArts
        from ..models.category_religion_and_spirituality import CategoryReligionAndSpirituality
        from ..models.category_school_activities import CategorySchoolActivities
        from ..models.category_science_and_technology import CategoryScienceAndTechnology
        from ..models.category_seasonal_and_holiday import CategorySeasonalAndHoliday
        from ..models.category_sports_and_fitness import CategorySportsAndFitness
        from ..models.category_travel_and_outdoor import CategoryTravelAndOutdoor
        from ..models.create_address_event_location import CreateAddressEventLocation
        from ..models.create_custom_event_location import CreateCustomEventLocation
        from ..models.create_date_operation import CreateDateOperation
        from ..models.create_online_event_location import CreateOnlineEventLocation
        from ..models.create_to_be_announced_event_location import CreateToBeAnnouncedEventLocation
        from ..models.delete_date_operation import DeleteDateOperation
        from ..models.update_date_operation import UpdateDateOperation

        d = dict(src_dict)
        name = d.pop("name", UNSET)

        description = d.pop("description", UNSET)

        timezone = d.pop("timezone", UNSET)

        def _parse_event_location(
            data: object,
        ) -> (
            CreateAddressEventLocation
            | CreateCustomEventLocation
            | CreateOnlineEventLocation
            | CreateToBeAnnouncedEventLocation
            | Unset
        ):
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_create_update_event_location_type_0 = CreateOnlineEventLocation.from_dict(data)

                return componentsschemas_create_update_event_location_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_create_update_event_location_type_1 = CreateAddressEventLocation.from_dict(data)

                return componentsschemas_create_update_event_location_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_create_update_event_location_type_2 = CreateCustomEventLocation.from_dict(data)

                return componentsschemas_create_update_event_location_type_2
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            if not isinstance(data, dict):
                raise TypeError()
            componentsschemas_create_update_event_location_type_3 = CreateToBeAnnouncedEventLocation.from_dict(data)

            return componentsschemas_create_update_event_location_type_3

        event_location = _parse_event_location(d.pop("eventLocation", UNSET))

        keywords = cast(list[str], d.pop("keywords", UNSET))

        def _parse_classification(
            data: object,
        ) -> (
            CategoryAutoBoatAndAir
            | CategoryBusinessAndProfessional
            | CategoryCharityAndCauses
            | CategoryCommunityAndCulture
            | CategoryFamilyAndEducation
            | CategoryFashionAndBeauty
            | CategoryFilmMediaAndEntertainment
            | CategoryFoodAndDrink
            | CategoryGovernmentAndPolitics
            | CategoryHealthAndWellness
            | CategoryHobbiesAndSpecialInterest
            | CategoryHomeAndLifestyle
            | CategoryMusic
            | CategoryOther
            | CategoryPerformingAndVisualArts
            | CategoryReligionAndSpirituality
            | CategorySchoolActivities
            | CategoryScienceAndTechnology
            | CategorySeasonalAndHoliday
            | CategorySportsAndFitness
            | CategoryTravelAndOutdoor
            | Unset
        ):
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_event_classification_type_0 = CategoryAutoBoatAndAir.from_dict(data)

                return componentsschemas_event_classification_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_event_classification_type_1 = CategoryBusinessAndProfessional.from_dict(data)

                return componentsschemas_event_classification_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_event_classification_type_2 = CategoryCharityAndCauses.from_dict(data)

                return componentsschemas_event_classification_type_2
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_event_classification_type_3 = CategoryCommunityAndCulture.from_dict(data)

                return componentsschemas_event_classification_type_3
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_event_classification_type_4 = CategoryFamilyAndEducation.from_dict(data)

                return componentsschemas_event_classification_type_4
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_event_classification_type_5 = CategoryFashionAndBeauty.from_dict(data)

                return componentsschemas_event_classification_type_5
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_event_classification_type_6 = CategoryFilmMediaAndEntertainment.from_dict(data)

                return componentsschemas_event_classification_type_6
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_event_classification_type_7 = CategoryFoodAndDrink.from_dict(data)

                return componentsschemas_event_classification_type_7
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_event_classification_type_8 = CategoryGovernmentAndPolitics.from_dict(data)

                return componentsschemas_event_classification_type_8
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_event_classification_type_9 = CategoryHealthAndWellness.from_dict(data)

                return componentsschemas_event_classification_type_9
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_event_classification_type_10 = CategoryHobbiesAndSpecialInterest.from_dict(data)

                return componentsschemas_event_classification_type_10
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_event_classification_type_11 = CategoryHomeAndLifestyle.from_dict(data)

                return componentsschemas_event_classification_type_11
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_event_classification_type_12 = CategoryMusic.from_dict(data)

                return componentsschemas_event_classification_type_12
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_event_classification_type_13 = CategoryPerformingAndVisualArts.from_dict(data)

                return componentsschemas_event_classification_type_13
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_event_classification_type_14 = CategoryReligionAndSpirituality.from_dict(data)

                return componentsschemas_event_classification_type_14
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_event_classification_type_15 = CategorySchoolActivities.from_dict(data)

                return componentsschemas_event_classification_type_15
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_event_classification_type_16 = CategoryScienceAndTechnology.from_dict(data)

                return componentsschemas_event_classification_type_16
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_event_classification_type_17 = CategorySeasonalAndHoliday.from_dict(data)

                return componentsschemas_event_classification_type_17
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_event_classification_type_18 = CategorySportsAndFitness.from_dict(data)

                return componentsschemas_event_classification_type_18
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_event_classification_type_19 = CategoryTravelAndOutdoor.from_dict(data)

                return componentsschemas_event_classification_type_19
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            if not isinstance(data, dict):
                raise TypeError()
            componentsschemas_event_classification_type_20 = CategoryOther.from_dict(data)

            return componentsschemas_event_classification_type_20

        classification = _parse_classification(d.pop("classification", UNSET))

        _dates = d.pop("dates", UNSET)
        dates: list[CreateDateOperation | DeleteDateOperation | UpdateDateOperation] | Unset = UNSET
        if _dates is not UNSET:
            dates = []
            for dates_item_data in _dates:

                def _parse_dates_item(data: object) -> CreateDateOperation | DeleteDateOperation | UpdateDateOperation:
                    try:
                        if not isinstance(data, dict):
                            raise TypeError()
                        componentsschemas_date_operation_type_0 = CreateDateOperation.from_dict(data)

                        return componentsschemas_date_operation_type_0
                    except (TypeError, ValueError, AttributeError, KeyError):
                        pass
                    try:
                        if not isinstance(data, dict):
                            raise TypeError()
                        componentsschemas_date_operation_type_1 = UpdateDateOperation.from_dict(data)

                        return componentsschemas_date_operation_type_1
                    except (TypeError, ValueError, AttributeError, KeyError):
                        pass
                    if not isinstance(data, dict):
                        raise TypeError()
                    componentsschemas_date_operation_type_2 = DeleteDateOperation.from_dict(data)

                    return componentsschemas_date_operation_type_2

                dates_item = _parse_dates_item(dates_item_data)

                dates.append(dates_item)

        _location = d.pop("location", UNSET)
        location: Location | Unset
        if isinstance(_location, Unset):
            location = UNSET
        else:
            location = Location(_location)

        update_event_request = cls(
            name=name,
            description=description,
            timezone=timezone,
            event_location=event_location,
            keywords=keywords,
            classification=classification,
            dates=dates,
            location=location,
        )

        update_event_request.additional_properties = d
        return update_event_request

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
