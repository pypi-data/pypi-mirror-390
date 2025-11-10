import random
from dataclasses import dataclass
from operator import attrgetter
from typing import List, Optional, Tuple

from pyspark import RDD, SparkContext

from pymlga.chromosome import ChromosomeFactory
from pymlga.individual import Individual, EvaluatedIndividual
from pymlga.spawn import spawn_new_individuals


@dataclass
class ReproductionRules:
    population_size: int
    clone_fittest_survival_rate: float = 0.1
    mutate_fittest_survival_rate: float = 0.1
    crossover_fittest_survival_rate: float = 0.6
    crossover_random_survival_rate: float = 0.05
    clone_mutation_rate: float = 0.1
    crossover_mutation_rate: float = 0.05

    def __post_init__(self):
        assert sum([
            self.clone_fittest_survival_rate,
            self.mutate_fittest_survival_rate,
            self.crossover_fittest_survival_rate,
            self.crossover_random_survival_rate
        ]) <= 1.0, "survival rates must not exceed 1.0"
        # noinspection PyUnresolvedReferences
        for field in self.__dataclass_fields__:
            if field.endswith('_rate'):
                assert self.__getattribute__(field) >= 0
                assert self.__getattribute__(field) <= 1


def reproduce(
        spark_context: SparkContext,
        evaluated_individuals: Optional[RDD[EvaluatedIndividual]],
        chromosome_factories: List[ChromosomeFactory],
        reproduction_rules: ReproductionRules
) -> RDD[Individual]:
    reproduced_individuals = clone_fittest(
        spark_context=spark_context,
        chromosome_factories=chromosome_factories,
        evaluated_individuals=evaluated_individuals,
        survival_rate=reproduction_rules.clone_fittest_survival_rate
    ).union(
        mutate_fittest(
            spark_context=spark_context,
            evaluated_individuals=evaluated_individuals,
            chromosome_factories=chromosome_factories,
            survival_rate=reproduction_rules.mutate_fittest_survival_rate,
            mutation_rate=reproduction_rules.clone_mutation_rate
        )
    ).union(
        crossover_fittest(
            spark_context=spark_context,
            evaluated_individuals=evaluated_individuals,
            chromosome_factories=chromosome_factories,
            survival_rate=reproduction_rules.crossover_fittest_survival_rate,
            mutation_rate=reproduction_rules.crossover_mutation_rate
        )
    ).union(
        crossover_random(
            spark_context=spark_context,
            evaluated_individuals=evaluated_individuals,
            chromosome_factories=chromosome_factories,
            survival_rate=reproduction_rules.crossover_random_survival_rate,
            mutation_rate=reproduction_rules.crossover_mutation_rate
        )
    ) if evaluated_individuals else spark_context.parallelize([])

    number_to_spawn = reproduction_rules.population_size - reproduced_individuals.count()
    return reproduced_individuals.union(
        spawn_new_individuals(
            spark_context=spark_context,
            number_to_spawn=number_to_spawn,
            chromosome_factories=chromosome_factories
        )
    )


def clone_fittest(
        spark_context: SparkContext,
        evaluated_individuals: RDD[EvaluatedIndividual],
        chromosome_factories: List[ChromosomeFactory],
        survival_rate: float
) -> RDD[Individual]:
    return mutate_fittest(
        spark_context=spark_context,
        evaluated_individuals=evaluated_individuals,
        chromosome_factories=chromosome_factories,
        survival_rate=survival_rate,
        mutation_rate=0.0
    )


def mutate_fittest(
        spark_context: SparkContext,
        evaluated_individuals: RDD[EvaluatedIndividual],
        chromosome_factories: List[ChromosomeFactory],
        survival_rate: float,
        mutation_rate: float
) -> RDD[Individual]:
    return spark_context.parallelize([
        evaluated_individual.individual.mutate(
            mutation_rate=mutation_rate,
            chromosome_factories=chromosome_factories
        )
        for evaluated_individual in _get_fittest(
            number_to_keep=int(float(survival_rate) * float(evaluated_individuals.count())),
            evaluated_individuals=evaluated_individuals
        )
    ])


def crossover_fittest(
        spark_context: SparkContext,
        evaluated_individuals: RDD[EvaluatedIndividual],
        chromosome_factories: List[ChromosomeFactory],
        survival_rate: float,
        mutation_rate: float
) -> RDD[Individual]:
    number_to_keep = int(float(survival_rate) * float(evaluated_individuals.count()))
    fittest = _get_fittest(
        number_to_keep=number_to_keep,
        evaluated_individuals=evaluated_individuals
    )
    return spark_context.parallelize(
        [
            male.crossover(female, mutation_rate=mutation_rate, chromosome_factories=chromosome_factories)
            for male, female in _select_individuals_for_mating(count=number_to_keep, evaluated_individuals=fittest)
        ]
    )


def crossover_random(
        spark_context: SparkContext,
        evaluated_individuals: RDD[EvaluatedIndividual],
        chromosome_factories: List[ChromosomeFactory],
        survival_rate: float,
        mutation_rate: float,
) -> RDD[Individual]:
    starting_population_count = evaluated_individuals.count()
    number_to_keep = int(float(survival_rate) * float(starting_population_count))
    return spark_context.parallelize(
        [
            male.crossover(female, mutation_rate=mutation_rate, chromosome_factories=chromosome_factories)
            for male, female in _select_individuals_for_mating(
                count=number_to_keep,
                evaluated_individuals=_get_fittest(
                    number_to_keep=starting_population_count,
                    evaluated_individuals=evaluated_individuals
                )
            )
        ]
    )


def _get_fittest(number_to_keep: int, evaluated_individuals: RDD[EvaluatedIndividual]) -> List[EvaluatedIndividual]:
    return sorted(evaluated_individuals.collect(), key=attrgetter('fitness'), reverse=True)[:number_to_keep]


def _select_individuals_for_mating(
        count: int,
        evaluated_individuals: List[EvaluatedIndividual]
) -> List[Tuple[Individual, Individual]]:
    return [_select_mating_pair(evaluated_individuals=evaluated_individuals) for _ in range(count)]


def _select_mating_pair(evaluated_individuals: List[EvaluatedIndividual]) -> Tuple[Individual, Individual]:
    male_index = random.randint(0, len(evaluated_individuals) - 1)
    female_index = male_index
    while female_index == male_index:
        female_index = random.randint(0, len(evaluated_individuals) - 1)
    return evaluated_individuals[male_index].individual, evaluated_individuals[female_index].individual
