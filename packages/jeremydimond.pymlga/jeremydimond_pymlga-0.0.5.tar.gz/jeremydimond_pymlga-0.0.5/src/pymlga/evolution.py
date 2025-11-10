from typing import List, Callable, Optional

from pyspark import SparkContext, RDD

from pymlga.chromosome import ChromosomeFactory
from pymlga.generation import Generation, GenerationFitness
from pymlga.individual import Individual, EvaluatedIndividual
from pymlga.reproduction import ReproductionRules, reproduce


def breed_next_generation(
        spark_context: SparkContext,
        chromosome_factories: List[ChromosomeFactory],
        fitness_evaluator: Callable[[Individual], float],
        reproduction_rules: ReproductionRules,
        previous_generation: Optional[Generation] = None
) -> Generation:
    individuals = reproduce(
        spark_context=spark_context,
        reproduction_rules=reproduction_rules,
        chromosome_factories=chromosome_factories,
        evaluated_individuals=previous_generation.evaluated_individuals if previous_generation else None
    )

    evaluated_individuals = _evaluate(
        individuals=individuals,
        fitness_evaluator=fitness_evaluator
    ).persist()

    if previous_generation:
        previous_generation.evaluated_individuals.unpersist()

    return Generation(
        generation_number=previous_generation.generation_number + 1 if previous_generation else 1,
        evaluated_individuals=evaluated_individuals,
        fitness=_calculate_generation_fitness_for(evaluated_individuals=evaluated_individuals)
    )


def _evaluate(
        individuals: RDD[Individual],
        fitness_evaluator: Callable[[Individual], float]
) -> RDD[EvaluatedIndividual]:
    return individuals.map(_to_individual_evaluated_with(fitness_evaluator))


def _to_individual_evaluated_with(
        fitness_evaluator: Callable[[Individual], float]
) -> Callable[[Individual], EvaluatedIndividual]:
    return lambda individual: EvaluatedIndividual(
        individual=individual,
        fitness=fitness_evaluator(individual)
    )


def _calculate_generation_fitness_for(evaluated_individuals: RDD[EvaluatedIndividual]) -> GenerationFitness:
    return evaluated_individuals.map(_individual_to_generation_fitness).reduce(_to_generation_fitness)


def _to_generation_fitness(f1: GenerationFitness, f2: GenerationFitness) -> GenerationFitness:
    population_size = f1.population_size + f2.population_size
    sum_fitness = f1.sum_fitness + f2.sum_fitness
    return GenerationFitness(
        population_size=population_size,
        top_fitness=max(f1.top_fitness, f2.top_fitness),
        average_fitness=sum_fitness / population_size,
        bottom_fitness=min(f1.bottom_fitness, f2.bottom_fitness),
        sum_fitness=sum_fitness,
        fittest=f1.fittest if f1.fittest.fitness >= f2.fittest.fitness else f2.fittest
    )


def _individual_to_generation_fitness(evaluated_individual: EvaluatedIndividual) -> GenerationFitness:
    return GenerationFitness(
        population_size=1,
        top_fitness=evaluated_individual.fitness,
        average_fitness=evaluated_individual.fitness,
        bottom_fitness=evaluated_individual.fitness,
        sum_fitness=evaluated_individual.fitness,
        fittest=evaluated_individual
    )
