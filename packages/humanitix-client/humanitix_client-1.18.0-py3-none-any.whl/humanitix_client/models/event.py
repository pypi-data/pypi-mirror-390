from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.currency import Currency
from ..models.location import Location
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.accessibility import Accessibility
    from ..models.additional_questions import AdditionalQuestions
    from ..models.artist import Artist
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
    from ..models.date_range import DateRange
    from ..models.event_affiliate_code import EventAffiliateCode
    from ..models.event_location import EventLocation
    from ..models.image import Image
    from ..models.packaged_tickets import PackagedTickets
    from ..models.payment_options import PaymentOptions
    from ..models.pricing import Pricing
    from ..models.ticket_type import TicketType


T = TypeVar("T", bound="Event")


@_attrs_define
class Event:
    """
    Attributes:
        field_id (str):  Example: 5ac598ccd8fe7c0c0f212e2a.
        user_id (str):  Example: nEOqx8s9UueyRu48789C0sY9set1.
        currency (Currency):
        name (str):  Example: Hobbit Dance Off.
        description (str):  Example: Where hobbits from all across the shire come to show off their movies!.
        slug (str):  Example: hobbit-dance-off.
        public (bool):
        published (bool):
        timezone (str):  Example: Pacific/Auckland.
        total_capacity (float):  Example: 1000.
        location (Location): The location of where the object is stored. Format is that of ISO 3166-1 alpha-2 country
            codes. Example: AU.
        created_at (datetime.datetime):  Example: 2021-02-01T23:26:13.485Z.
        updated_at (datetime.datetime):  Example: 2021-02-01T23:26:13.485Z.
        organiser_id (str | Unset):  Example: 5ac597aed8fe7c0c0f212e27.
        url (str | Unset):  Example: https://events.humanitix.com/hobbit-dance-off.
        tag_ids (list[str] | Unset):
        category (str | Unset):  Example: community.
        classification (CategoryAutoBoatAndAir | CategoryBusinessAndProfessional | CategoryCharityAndCauses |
            CategoryCommunityAndCulture | CategoryFamilyAndEducation | CategoryFashionAndBeauty |
            CategoryFilmMediaAndEntertainment | CategoryFoodAndDrink | CategoryGovernmentAndPolitics |
            CategoryHealthAndWellness | CategoryHobbiesAndSpecialInterest | CategoryHomeAndLifestyle | CategoryMusic |
            CategoryOther | CategoryPerformingAndVisualArts | CategoryReligionAndSpirituality | CategorySchoolActivities |
            CategoryScienceAndTechnology | CategorySeasonalAndHoliday | CategorySportsAndFitness | CategoryTravelAndOutdoor
            | Unset):
        artists (list[Artist] | Unset):
        suspend_sales (bool | Unset):
        marked_as_sold_out (bool | Unset):
        start_date (datetime.datetime | Unset):  Example: 2021-02-01T23:26:13.485Z.
        end_date (datetime.datetime | Unset):  Example: 2021-02-01T23:26:13.485Z.
        ticket_types (list[TicketType] | Unset):
        pricing (Pricing | Unset):
        payment_options (PaymentOptions | Unset):
        published_at (datetime.datetime | Unset):  Example: 2021-02-01T23:26:13.485Z.
        additional_questions (list[AdditionalQuestions] | Unset):
        banner_image (Image | Unset):
        feature_image (Image | Unset):
        social_image (Image | Unset):
        event_location (EventLocation | Unset):
        dates (list[DateRange] | Unset):
        packaged_tickets (list[PackagedTickets] | Unset):
        accessibility (Accessibility | Unset):
        affiliate_code (EventAffiliateCode | Unset):
        keywords (list[str] | Unset):
    """

    field_id: str
    user_id: str
    currency: Currency
    name: str
    description: str
    slug: str
    public: bool
    published: bool
    timezone: str
    total_capacity: float
    location: Location
    created_at: datetime.datetime
    updated_at: datetime.datetime
    organiser_id: str | Unset = UNSET
    url: str | Unset = UNSET
    tag_ids: list[str] | Unset = UNSET
    category: str | Unset = UNSET
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
    artists: list[Artist] | Unset = UNSET
    suspend_sales: bool | Unset = UNSET
    marked_as_sold_out: bool | Unset = UNSET
    start_date: datetime.datetime | Unset = UNSET
    end_date: datetime.datetime | Unset = UNSET
    ticket_types: list[TicketType] | Unset = UNSET
    pricing: Pricing | Unset = UNSET
    payment_options: PaymentOptions | Unset = UNSET
    published_at: datetime.datetime | Unset = UNSET
    additional_questions: list[AdditionalQuestions] | Unset = UNSET
    banner_image: Image | Unset = UNSET
    feature_image: Image | Unset = UNSET
    social_image: Image | Unset = UNSET
    event_location: EventLocation | Unset = UNSET
    dates: list[DateRange] | Unset = UNSET
    packaged_tickets: list[PackagedTickets] | Unset = UNSET
    accessibility: Accessibility | Unset = UNSET
    affiliate_code: EventAffiliateCode | Unset = UNSET
    keywords: list[str] | Unset = UNSET
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

        field_id = self.field_id

        user_id = self.user_id

        currency = self.currency.value

        name = self.name

        description = self.description

        slug = self.slug

        public = self.public

        published = self.published

        timezone = self.timezone

        total_capacity = self.total_capacity

        location = self.location.value

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        organiser_id = self.organiser_id

        url = self.url

        tag_ids: list[str] | Unset = UNSET
        if not isinstance(self.tag_ids, Unset):
            tag_ids = self.tag_ids

        category = self.category

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

        artists: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.artists, Unset):
            artists = []
            for artists_item_data in self.artists:
                artists_item = artists_item_data.to_dict()
                artists.append(artists_item)

        suspend_sales = self.suspend_sales

        marked_as_sold_out = self.marked_as_sold_out

        start_date: str | Unset = UNSET
        if not isinstance(self.start_date, Unset):
            start_date = self.start_date.isoformat()

        end_date: str | Unset = UNSET
        if not isinstance(self.end_date, Unset):
            end_date = self.end_date.isoformat()

        ticket_types: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.ticket_types, Unset):
            ticket_types = []
            for ticket_types_item_data in self.ticket_types:
                ticket_types_item = ticket_types_item_data.to_dict()
                ticket_types.append(ticket_types_item)

        pricing: dict[str, Any] | Unset = UNSET
        if not isinstance(self.pricing, Unset):
            pricing = self.pricing.to_dict()

        payment_options: dict[str, Any] | Unset = UNSET
        if not isinstance(self.payment_options, Unset):
            payment_options = self.payment_options.to_dict()

        published_at: str | Unset = UNSET
        if not isinstance(self.published_at, Unset):
            published_at = self.published_at.isoformat()

        additional_questions: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.additional_questions, Unset):
            additional_questions = []
            for additional_questions_item_data in self.additional_questions:
                additional_questions_item = additional_questions_item_data.to_dict()
                additional_questions.append(additional_questions_item)

        banner_image: dict[str, Any] | Unset = UNSET
        if not isinstance(self.banner_image, Unset):
            banner_image = self.banner_image.to_dict()

        feature_image: dict[str, Any] | Unset = UNSET
        if not isinstance(self.feature_image, Unset):
            feature_image = self.feature_image.to_dict()

        social_image: dict[str, Any] | Unset = UNSET
        if not isinstance(self.social_image, Unset):
            social_image = self.social_image.to_dict()

        event_location: dict[str, Any] | Unset = UNSET
        if not isinstance(self.event_location, Unset):
            event_location = self.event_location.to_dict()

        dates: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.dates, Unset):
            dates = []
            for dates_item_data in self.dates:
                dates_item = dates_item_data.to_dict()
                dates.append(dates_item)

        packaged_tickets: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.packaged_tickets, Unset):
            packaged_tickets = []
            for packaged_tickets_item_data in self.packaged_tickets:
                packaged_tickets_item = packaged_tickets_item_data.to_dict()
                packaged_tickets.append(packaged_tickets_item)

        accessibility: dict[str, Any] | Unset = UNSET
        if not isinstance(self.accessibility, Unset):
            accessibility = self.accessibility.to_dict()

        affiliate_code: dict[str, Any] | Unset = UNSET
        if not isinstance(self.affiliate_code, Unset):
            affiliate_code = self.affiliate_code.to_dict()

        keywords: list[str] | Unset = UNSET
        if not isinstance(self.keywords, Unset):
            keywords = self.keywords

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "_id": field_id,
                "userId": user_id,
                "currency": currency,
                "name": name,
                "description": description,
                "slug": slug,
                "public": public,
                "published": published,
                "timezone": timezone,
                "totalCapacity": total_capacity,
                "location": location,
                "createdAt": created_at,
                "updatedAt": updated_at,
            }
        )
        if organiser_id is not UNSET:
            field_dict["organiserId"] = organiser_id
        if url is not UNSET:
            field_dict["url"] = url
        if tag_ids is not UNSET:
            field_dict["tagIds"] = tag_ids
        if category is not UNSET:
            field_dict["category"] = category
        if classification is not UNSET:
            field_dict["classification"] = classification
        if artists is not UNSET:
            field_dict["artists"] = artists
        if suspend_sales is not UNSET:
            field_dict["suspendSales"] = suspend_sales
        if marked_as_sold_out is not UNSET:
            field_dict["markedAsSoldOut"] = marked_as_sold_out
        if start_date is not UNSET:
            field_dict["startDate"] = start_date
        if end_date is not UNSET:
            field_dict["endDate"] = end_date
        if ticket_types is not UNSET:
            field_dict["ticketTypes"] = ticket_types
        if pricing is not UNSET:
            field_dict["pricing"] = pricing
        if payment_options is not UNSET:
            field_dict["paymentOptions"] = payment_options
        if published_at is not UNSET:
            field_dict["publishedAt"] = published_at
        if additional_questions is not UNSET:
            field_dict["additionalQuestions"] = additional_questions
        if banner_image is not UNSET:
            field_dict["bannerImage"] = banner_image
        if feature_image is not UNSET:
            field_dict["featureImage"] = feature_image
        if social_image is not UNSET:
            field_dict["socialImage"] = social_image
        if event_location is not UNSET:
            field_dict["eventLocation"] = event_location
        if dates is not UNSET:
            field_dict["dates"] = dates
        if packaged_tickets is not UNSET:
            field_dict["packagedTickets"] = packaged_tickets
        if accessibility is not UNSET:
            field_dict["accessibility"] = accessibility
        if affiliate_code is not UNSET:
            field_dict["affiliateCode"] = affiliate_code
        if keywords is not UNSET:
            field_dict["keywords"] = keywords

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.accessibility import Accessibility
        from ..models.additional_questions import AdditionalQuestions
        from ..models.artist import Artist
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
        from ..models.date_range import DateRange
        from ..models.event_affiliate_code import EventAffiliateCode
        from ..models.event_location import EventLocation
        from ..models.image import Image
        from ..models.packaged_tickets import PackagedTickets
        from ..models.payment_options import PaymentOptions
        from ..models.pricing import Pricing
        from ..models.ticket_type import TicketType

        d = dict(src_dict)
        field_id = d.pop("_id")

        user_id = d.pop("userId")

        currency = Currency(d.pop("currency"))

        name = d.pop("name")

        description = d.pop("description")

        slug = d.pop("slug")

        public = d.pop("public")

        published = d.pop("published")

        timezone = d.pop("timezone")

        total_capacity = d.pop("totalCapacity")

        location = Location(d.pop("location"))

        created_at = isoparse(d.pop("createdAt"))

        updated_at = isoparse(d.pop("updatedAt"))

        organiser_id = d.pop("organiserId", UNSET)

        url = d.pop("url", UNSET)

        tag_ids = cast(list[str], d.pop("tagIds", UNSET))

        category = d.pop("category", UNSET)

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

        _artists = d.pop("artists", UNSET)
        artists: list[Artist] | Unset = UNSET
        if _artists is not UNSET:
            artists = []
            for artists_item_data in _artists:
                artists_item = Artist.from_dict(artists_item_data)

                artists.append(artists_item)

        suspend_sales = d.pop("suspendSales", UNSET)

        marked_as_sold_out = d.pop("markedAsSoldOut", UNSET)

        _start_date = d.pop("startDate", UNSET)
        start_date: datetime.datetime | Unset
        if isinstance(_start_date, Unset):
            start_date = UNSET
        else:
            start_date = isoparse(_start_date)

        _end_date = d.pop("endDate", UNSET)
        end_date: datetime.datetime | Unset
        if isinstance(_end_date, Unset):
            end_date = UNSET
        else:
            end_date = isoparse(_end_date)

        _ticket_types = d.pop("ticketTypes", UNSET)
        ticket_types: list[TicketType] | Unset = UNSET
        if _ticket_types is not UNSET:
            ticket_types = []
            for ticket_types_item_data in _ticket_types:
                ticket_types_item = TicketType.from_dict(ticket_types_item_data)

                ticket_types.append(ticket_types_item)

        _pricing = d.pop("pricing", UNSET)
        pricing: Pricing | Unset
        if isinstance(_pricing, Unset):
            pricing = UNSET
        else:
            pricing = Pricing.from_dict(_pricing)

        _payment_options = d.pop("paymentOptions", UNSET)
        payment_options: PaymentOptions | Unset
        if isinstance(_payment_options, Unset):
            payment_options = UNSET
        else:
            payment_options = PaymentOptions.from_dict(_payment_options)

        _published_at = d.pop("publishedAt", UNSET)
        published_at: datetime.datetime | Unset
        if isinstance(_published_at, Unset):
            published_at = UNSET
        else:
            published_at = isoparse(_published_at)

        _additional_questions = d.pop("additionalQuestions", UNSET)
        additional_questions: list[AdditionalQuestions] | Unset = UNSET
        if _additional_questions is not UNSET:
            additional_questions = []
            for additional_questions_item_data in _additional_questions:
                additional_questions_item = AdditionalQuestions.from_dict(additional_questions_item_data)

                additional_questions.append(additional_questions_item)

        _banner_image = d.pop("bannerImage", UNSET)
        banner_image: Image | Unset
        if isinstance(_banner_image, Unset):
            banner_image = UNSET
        else:
            banner_image = Image.from_dict(_banner_image)

        _feature_image = d.pop("featureImage", UNSET)
        feature_image: Image | Unset
        if isinstance(_feature_image, Unset):
            feature_image = UNSET
        else:
            feature_image = Image.from_dict(_feature_image)

        _social_image = d.pop("socialImage", UNSET)
        social_image: Image | Unset
        if isinstance(_social_image, Unset):
            social_image = UNSET
        else:
            social_image = Image.from_dict(_social_image)

        _event_location = d.pop("eventLocation", UNSET)
        event_location: EventLocation | Unset
        if isinstance(_event_location, Unset):
            event_location = UNSET
        else:
            event_location = EventLocation.from_dict(_event_location)

        _dates = d.pop("dates", UNSET)
        dates: list[DateRange] | Unset = UNSET
        if _dates is not UNSET:
            dates = []
            for dates_item_data in _dates:
                dates_item = DateRange.from_dict(dates_item_data)

                dates.append(dates_item)

        _packaged_tickets = d.pop("packagedTickets", UNSET)
        packaged_tickets: list[PackagedTickets] | Unset = UNSET
        if _packaged_tickets is not UNSET:
            packaged_tickets = []
            for packaged_tickets_item_data in _packaged_tickets:
                packaged_tickets_item = PackagedTickets.from_dict(packaged_tickets_item_data)

                packaged_tickets.append(packaged_tickets_item)

        _accessibility = d.pop("accessibility", UNSET)
        accessibility: Accessibility | Unset
        if isinstance(_accessibility, Unset):
            accessibility = UNSET
        else:
            accessibility = Accessibility.from_dict(_accessibility)

        _affiliate_code = d.pop("affiliateCode", UNSET)
        affiliate_code: EventAffiliateCode | Unset
        if isinstance(_affiliate_code, Unset):
            affiliate_code = UNSET
        else:
            affiliate_code = EventAffiliateCode.from_dict(_affiliate_code)

        keywords = cast(list[str], d.pop("keywords", UNSET))

        event = cls(
            field_id=field_id,
            user_id=user_id,
            currency=currency,
            name=name,
            description=description,
            slug=slug,
            public=public,
            published=published,
            timezone=timezone,
            total_capacity=total_capacity,
            location=location,
            created_at=created_at,
            updated_at=updated_at,
            organiser_id=organiser_id,
            url=url,
            tag_ids=tag_ids,
            category=category,
            classification=classification,
            artists=artists,
            suspend_sales=suspend_sales,
            marked_as_sold_out=marked_as_sold_out,
            start_date=start_date,
            end_date=end_date,
            ticket_types=ticket_types,
            pricing=pricing,
            payment_options=payment_options,
            published_at=published_at,
            additional_questions=additional_questions,
            banner_image=banner_image,
            feature_image=feature_image,
            social_image=social_image,
            event_location=event_location,
            dates=dates,
            packaged_tickets=packaged_tickets,
            accessibility=accessibility,
            affiliate_code=affiliate_code,
            keywords=keywords,
        )

        event.additional_properties = d
        return event

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
