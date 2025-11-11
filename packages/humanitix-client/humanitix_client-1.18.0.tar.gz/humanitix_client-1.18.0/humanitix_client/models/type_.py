from enum import Enum


class Type(str, Enum):
    APPEARANCEORSIGNING = "appearanceOrSigning"
    ATTRACTION = "attraction"
    CAMPTRIPORRETREAT = "campTripOrRetreat"
    CLASSTRAININGORWORKSHOP = "classTrainingOrWorkshop"
    CONCERTORPERFORMANCE = "concertOrPerformance"
    CONFERENCE = "conference"
    CONVENTION = "convention"
    DINNERORGALA = "dinnerOrGala"
    FESTIVALORFAIR = "festivalOrFair"
    GAMEORCOMPETITION = "gameOrCompetition"
    MEETINGORNETWORKINGEVENT = "meetingOrNetworkingEvent"
    OTHER = "other"
    PARTYORSOCIALGATHERING = "partyOrSocialGathering"
    RACEORENDURANCEEVENT = "raceOrEnduranceEvent"
    RALLY = "rally"
    SCREENING = "screening"
    SEMINARORTALK = "seminarOrTalk"
    TOUR = "tour"
    TOURNAMENT = "tournament"
    TRADESHOWCONSUMERSHOWOREXPO = "tradeShowConsumerShowOrExpo"

    def __str__(self) -> str:
        return str(self.value)
