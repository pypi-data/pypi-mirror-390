"""tsp.py"""

from math import acos, cos, radians, sin
from typing import overload

from pyvrp import Client, Depot, Model
from pyvrp.stop import MaxIterations

type Location = Client | Depot
type Key = int | str
type DistanceDict = dict[tuple[int, int], int] | dict[tuple[str, str], int] | list[list[int]]

DEFAULT_MAX_ITERATIONS = 100


def distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great circle distance (km) between two points"""
    r = 6371
    ry1, rx1, ry2, rx2 = radians(lat1), radians(lon1), radians(lat2), radians(lon2)
    return r * acos(min(1.0, sin(ry1) * sin(ry2) + cos(ry1) * cos(ry2) * cos(rx1 - rx2)))


def _get_location_or_create(m: Model, locations: dict[Key, Location], key: Key) -> Location:
    """If not, create it and return location"""
    if location := locations.get(key):
        return location
    locations[key] = location = m.add_client(x=0, y=0, name=str(key))
    return location


@overload
def tsp(
    distances: dict[tuple[int, int], int], depot: int = 0, max_iterations: int = DEFAULT_MAX_ITERATIONS
) -> list[int]: ...


@overload
def tsp(
    distances: dict[tuple[str, str], int], depot: str, max_iterations: int = DEFAULT_MAX_ITERATIONS
) -> list[str]: ...


@overload
def tsp(distances: list[list[int]], depot: int = 0, max_iterations: int = DEFAULT_MAX_ITERATIONS) -> list[str]: ...


def tsp(
    distances: DistanceDict,
    depot: Key = 0,
    max_iterations: int = DEFAULT_MAX_ITERATIONS,
) -> list[int] | list[str]:
    """Solve a traveling salesman problem and return a list of cities

    :param distances: Dictionary or list of distances
    :param depot: First city, defaults to 0
    :param max_iterations: Number of iterations to use in PyVRP, defaults to DEFAULT_MAX_ITERATIONS
    :return: A list of cities
    """
    m = Model()
    m.add_vehicle_type(1)
    locations: dict[Key, Location] = {depot: m.add_depot(x=0, y=0, name=str(depot))}
    if isinstance(distances, dict):
        for (i, j), distance in distances.items():
            location_i = _get_location_or_create(m, locations, i)
            location_j = _get_location_or_create(m, locations, j)
            m.add_edge(location_i, location_j, distance=distance)
    else:
        assert isinstance(distances, list)  # noqa: S101
        n = len(distances)
        for i in range(1, n):
            m.add_client(x=0, y=0, name=str(i))
        for i in range(n):
            for j in range(n):
                if i != j:
                    m.add_edge(m.locations[i], m.locations[j], distance=distances[i][j])

    result = m.solve(MaxIterations(max_iterations), display=False)
    if result.best.distance() >= 2**52:
        return []
    route = result.best.routes()[0]
    key_type = type(depot)
    cities_ = (key_type(m.locations[i].name) for i in route.visits())
    return [depot, *(cities_)]  # type: ignore[bad-assignment]
