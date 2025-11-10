from dataclasses import dataclass
from operator import attrgetter
from typing import List, Callable

from pyspark import RDD

from pymlga.individual import EvaluatedIndividual


@dataclass
class GenerationFitness:
    population_size: int
    top_fitness: float
    average_fitness: float
    bottom_fitness: float
    sum_fitness: float
    fittest: EvaluatedIndividual


@dataclass
class Generation:
    generation_number: int
    evaluated_individuals: RDD[EvaluatedIndividual]
    fitness: GenerationFitness


def get_top(count: int, evaluated_individuals: RDD[EvaluatedIndividual]) -> List[EvaluatedIndividual]:

    return evaluated_individuals.map(_to_singleton_list).reduce(_keep_fittest(count))


def _to_singleton_list(evaluated_individual: EvaluatedIndividual) -> List[EvaluatedIndividual]:
    return [evaluated_individual]


def _keep_fittest(count: int) -> Callable[
    [List[EvaluatedIndividual], List[EvaluatedIndividual]],
    List[EvaluatedIndividual]
]:
    return lambda list1, list2: sorted(list1 + list2, key=attrgetter('fitness'), reverse=True)[:count]
