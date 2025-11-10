from dataclasses import dataclass
from datetime import timedelta, datetime
from typing import Callable, List, Optional

from pyspark import SparkContext

from pymlga.chromosome import ChromosomeFactory
from pymlga.evolution import breed_next_generation
from pymlga.generation import Generation
from pymlga.individual import Individual
from pymlga.reproduction import ReproductionRules


@dataclass
class Experiment:
    chromosome_factories: List[ChromosomeFactory]
    fitness_evaluator: Callable[[Individual], float]
    reproduction_rules: ReproductionRules
    max_generations: Optional[int] = None
    time_limit: Optional[timedelta] = None
    target_fitness: Optional[float] = None

    def __post_init__(self):
        assert not (self.max_generations is None and self.target_fitness is None and self.time_limit is None)


def run(experiment: Experiment, spark_context: SparkContext) -> Generation:
    start_time = datetime.now()
    print('Breeding initial generation...')
    generation = breed_next_generation(
        spark_context=spark_context,
        chromosome_factories=experiment.chromosome_factories,
        fitness_evaluator=experiment.fitness_evaluator,
        reproduction_rules=experiment.reproduction_rules
    )
    while not _is_final_generation(
        generation=generation,
        elapsed_time=datetime.now() - start_time,
        max_generations=experiment.max_generations,
        time_limit=experiment.time_limit,
        target_fitness=experiment.target_fitness
    ):
        print(f'Generation #{generation.generation_number} '
              f'fitness={"{:0,.2f}".format(generation.fitness.fittest.fitness)} '
              'is not final, experiment continues...')
        generation = breed_next_generation(
            spark_context=spark_context,
            chromosome_factories=experiment.chromosome_factories,
            fitness_evaluator=experiment.fitness_evaluator,
            reproduction_rules=experiment.reproduction_rules,
            previous_generation=generation
        )
    print(f'Experiment completed at generation #{generation.generation_number}!')
    print()
    print(generation)
    print()
    return generation


def _is_final_generation(
        generation: Generation,
        elapsed_time: timedelta,
        max_generations: Optional[int],
        time_limit: Optional[timedelta],
        target_fitness: Optional[float]
) -> bool:
    if max_generations is not None and generation.generation_number == max_generations:
        print('Max generations reached!')
        return True
    if time_limit is not None and elapsed_time >= time_limit:
        print('Time limit reached!')
        return True
    if target_fitness is not None and generation.fitness.top_fitness >= target_fitness:
        print('Target fitness readyed! reached!')
        return True
    return False
