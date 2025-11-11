from enum import Enum


class CategorySportsAndFitnessCategory(str, Enum):
    SPORTSANDFITNESS = "sportsAndFitness"

    def __str__(self) -> str:
        return str(self.value)
