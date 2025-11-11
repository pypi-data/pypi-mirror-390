from enum import Enum


class Category(str, Enum):
    AUTOBOATANDAIR = "autoBoatAndAir"
    BUSINESSANDPROFESSIONAL = "businessAndProfessional"
    CHARITYANDCAUSES = "charityAndCauses"
    COMMUNITYANDCULTURE = "communityAndCulture"
    FAMILYANDEDUCATION = "familyAndEducation"
    FASHIONANDBEAUTY = "fashionAndBeauty"
    FILMMEDIAANDENTERTAINMENT = "filmMediaAndEntertainment"
    FOODANDDRINK = "foodAndDrink"
    GOVERNMENTANDPOLITICS = "governmentAndPolitics"
    HEALTHANDWELLNESS = "healthAndWellness"
    HOBBIESANDSPECIALINTEREST = "hobbiesAndSpecialInterest"
    HOMEANDLIFESTYLE = "homeAndLifestyle"
    MUSIC = "music"
    OTHER = "other"
    PERFORMINGANDVISUALARTS = "performingAndVisualArts"
    RELIGIONANDSPIRITUALITY = "religionAndSpirituality"
    SCHOOLACTIVITIES = "schoolActivities"
    SCIENCEANDTECHNOLOGY = "scienceAndTechnology"
    SEASONALANDHOLIDAY = "seasonalAndHoliday"
    SPORTSANDFITNESS = "sportsAndFitness"
    TRAVELANDOUTDOOR = "travelAndOutdoor"

    def __str__(self) -> str:
        return str(self.value)
