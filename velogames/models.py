# pylint: disable=too-few-public-methods
import enum
import math
import re
from typing import Optional
from pydantic import BaseModel, validator


def field_enum(model):
    schema = model.schema()
    fields = {prop["title"]: field for field, prop in schema["properties"].items()}
    return enum.Enum("Fields", fields)


class Model(BaseModel):
    def __hash__(self):
        return hash((type(self),) + tuple(self.__dict__.values()))


class Percentage(float):
    PATTERN = re.compile(r"(\d+\.\d+)%")

    @classmethod
    def __get_validators__(cls):
        yield cls.from_string
        yield cls.from_number

    @classmethod
    def from_string(cls, value):
        if isinstance(value, (int, float)):
            return value

        if not isinstance(value, str):
            raise TypeError("Value should be number or string")

        match = cls.PATTERN.fullmatch(value)
        if not match:
            raise ValueError("Invalid percentage format")

        return float(match.group(1))

    @classmethod
    def from_number(cls, value):
        if not 0 <= value <= 100:
            raise ValueError("Value out of bounds")

        return value


class Stage(Model):
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


class Standing(Model):
    team_id: str

    name: str
    user: str
    score: int

    def __lt__(self, other: "Standing") -> bool:
        return self.score < other.score


class Team(Model):
    team_id: str

    name: str
    user: str
    country: str
    cost: int
    score: int
    rank: int

    def __lt__(self, other: "Team") -> bool:
        return self.score < other.score


class RiderBase(Model):
    rider_id: int

    name: str
    team: str

    cost: int
    points: int
    value: int = 0

    def __lt__(self, other: "RiderBase") -> bool:
        return (-self.points, self.name) > (-other.points, other.name)

    @validator("value", pre=True, always=True)
    def set_value(cls, value, values, config, field) -> int:
        # pylint: disable=unused-argument,no-self-use,no-self-argument
        return value or math.ceil(values["points"] / values["cost"])
