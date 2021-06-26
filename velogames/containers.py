# pylint: disable=too-few-public-methods
from typing import Optional
from pydantic import BaseModel


class Stage(BaseModel):
    name: str
    game_id: Optional[int]
    stage_id: Optional[int]

    def __lt__(self, other):
        return self.stage_id < other.stage_id


class Standing(BaseModel):
    team_id: str

    name: str
    user: str
    score: int

    def __lt__(self, other):
        return self.score < other.score


class Team(BaseModel):
    team_id: str

    name: str
    user: str
    country: str
    cost: int
    score: int
    rank: int

    def __lt__(self, other):
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

    def __lt__(self, other):
        return self.points < other.points and self.name > other.name
