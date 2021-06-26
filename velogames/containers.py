# pylint: disable=too-few-public-methods
from typing import Optional
from pydantic import BaseModel


class Stage(BaseModel):
    name: str
    game_id: Optional[int]
    stage_id: Optional[int]

    def __lt__(self, other: "Stage") -> bool:
        this = self.stage_id
        that = other.stage_id

        if this is None:
            return True
        if that is None:
            return False

        return this < that


class Standing(BaseModel):
    team_id: str

    name: str
    user: str
    score: int

    def __lt__(self, other: "Standing") -> bool:
        return self.score < other.score


class Team(BaseModel):
    team_id: str

    name: str
    user: str
    country: str
    cost: int
    score: int
    rank: int

    def __lt__(self, other: "Team") -> bool:
        return self.score < other.score


class Rider(BaseModel):
    rider_id: str

    name: str
    team: str
    cost: int
    points: int

    # Points breakdown
    stage: int
    general: int
    daily: int
    kom: int
    sprint: int
    summit: int
    breakaway: int
    assist: int

    def __lt__(self, other: "Rider") -> bool:
        return self.points < other.points and self.name > other.name
