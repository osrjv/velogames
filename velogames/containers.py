from dataclasses import dataclass
from typing import Optional


def optional_int(val):
    return int(val) if val is not None else val


@dataclass
class Stage:
    name: str
    gid: Optional[str]  # Game id
    sid: Optional[str]  # Stage id

    def __post_init__(self):
        self.gid = optional_int(self.gid)
        self.sid = optional_int(self.sid)

    def __lt__(self, other):
        return self.sid < other.sid


@dataclass
class Standing:
    name: str
    user: str
    score: int
    tid: str  # Team id

    def __post_init__(self):
        self.score = int(self.score)

    def __lt__(self, other):
        return self.score < other.score


@dataclass
class Team:
    name: str
    user: str
    country: str
    cost: int
    score: int
    rank: int
    tid: str  # Team id

    def __post_init__(self):
        self.cost = int(self.cost)
        self.score = int(self.score)
        self.rank = int(self.rank)

    def __lt__(self, other):
        return self.score < other.score
