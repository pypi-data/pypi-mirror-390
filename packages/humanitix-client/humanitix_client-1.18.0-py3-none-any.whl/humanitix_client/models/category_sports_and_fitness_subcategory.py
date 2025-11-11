from enum import Enum


class CategorySportsAndFitnessSubcategory(str, Enum):
    AMERICANFOOTBALL = "americanFootball"
    BASEBALL = "baseball"
    BASKETBALL = "basketball"
    CAMPS = "camps"
    CHEER = "cheer"
    CYCLING = "cycling"
    EXERCISE = "exercise"
    FIGHTINGMARTIALARTS = "fightingMartialArts"
    FOOTBALL = "football"
    GOLF = "golf"
    HOCKEY = "hockey"
    LACROSSE = "lacrosse"
    MOTORSPORTS = "motorsports"
    MOUNTAINBIKING = "mountainBiking"
    OBSTACLES = "obstacles"
    OTHER = "other"
    RUGBY = "rugby"
    RUNNING = "running"
    SNOWSPORTS = "snowSports"
    SOFTBALL = "softball"
    SWIMMINGWATERSPORTS = "swimmingWaterSports"
    TENNIS = "tennis"
    TRACKFIELD = "trackField"
    VOLLEYBALL = "volleyball"
    WALKING = "walking"
    WEIGHTLIFTING = "weightlifting"
    WRESTLING = "wrestling"
    YOGA = "yoga"

    def __str__(self) -> str:
        return str(self.value)
