import itertools
import random
from collections import defaultdict
from functools import lru_cache


def flatten(team):
    return [rider for slot in team for rider in slot]


@lru_cache(maxsize=None)
def score(team):
    riders = flatten(team)
    if len(set(riders)) != len(riders):
        return -1
    if sum(rider.cost for rider in riders) > 100:
        return -1
    return sum(rider.points for rider in riders)


def to_slots(riders):
    roles = defaultdict(list)
    for rider in riders:
        roles[rider.role].append(rider)

    def combinations(iterable, count):
        return [tuple(i) for i in itertools.combinations(iterable, count)]

    return [
        combinations(roles["All Rounder"], 2),
        combinations(roles["Climber"], 2),
        combinations(roles["Sprinter"], 1),
        combinations(roles["Unclassed"], 3),
        combinations(riders, 1),
    ]


class Solver:
    # pylint: disable=too-few-public-methods

    def __init__(
        self,
        riders,
        generations: int = 10000,
        population: int = 100,
        p_crossover: float = 0.8,
        p_mutation: float = 0.2,
        n_tournament: int = 3,
    ):
        # pylint: disable=too-many-arguments
        assert not population % 2, "Invalid population size (n % 2)"
        assert 0 <= p_crossover <= 1, "Invalid crossover probability"
        assert 0 <= p_mutation <= 1, "Invalid mutation probability"

        self.slots = to_slots(riders)
        self.generations = generations
        self.population = population

        self.p_crossover = p_crossover
        self.p_mutation = p_mutation
        self.n_tournament = n_tournament

    def _generate(self):
        return tuple(random.choice(slot) for slot in self.slots)

    def _tournament(self, teams):
        sample = random.sample(teams, self.n_tournament)
        return max(sample, key=score)

    def _crossover(self, lhs, rhs):
        if random.random() >= self.p_crossover:
            idx = random.randint(1, len(lhs) - 1)
            return lhs[:idx] + rhs[idx:], rhs[:idx] + lhs[idx:]

        return lhs, rhs

    def _mutate(self, team):
        return tuple(
            random.choice(self.slots[idx])
            if random.random() < self.p_mutation
            else slot
            for idx, slot in enumerate(team)
        )

    def iter(self, interval=100):
        gen = 0
        teams = [self._generate() for _ in range(self.population)]
        best = teams[0]

        for gen in range(self.generations + 1):
            is_changed = False
            for team in teams:
                if score(team) > score(best):
                    is_changed = True
                    best = team

            if is_changed or not gen % interval:
                yield gen, flatten(best)

            parents = [self._tournament(teams) for _ in range(self.population)]

            children = []
            for idx in range(0, self.population, 2):
                lhs, rhs = parents[idx : idx + 2]
                for child in self._crossover(lhs, rhs):
                    child = self._mutate(child)
                    children.append(child)

            teams = children

        yield gen, flatten(best)
