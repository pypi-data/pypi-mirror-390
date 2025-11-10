import random
from typing import List

from pyspark import SparkContext, RDD

from pymlga.chromosome import Chromosome
from pymlga.chromosome import ChromosomeFactory
from pymlga.individual import Individual


def spawn_new_individuals(
        spark_context: SparkContext,
        number_to_spawn: int,
        chromosome_factories: List[ChromosomeFactory]
) -> RDD[Individual]:
    return _create_rdd(
        spark_context=spark_context,
        number_to_spawn=number_to_spawn,
        chromosome_factories=chromosome_factories
    ).map(_to_individual)


def _create_rdd(
        spark_context: SparkContext,
        number_to_spawn: int,
        chromosome_factories: List[ChromosomeFactory]
) -> RDD[List[ChromosomeFactory]]:
    return spark_context.parallelize([chromosome_factories for _ in range(number_to_spawn)])


def _to_individual(chromosome_factories: List[ChromosomeFactory]) -> Individual:
    return Individual(chromosomes=[
        _spawn_chromosome(chromosome_factory=chromosome_factory)
        for chromosome_factory in chromosome_factories
    ])


def _spawn_chromosome(chromosome_factory: ChromosomeFactory) -> Chromosome:
    return Chromosome(genes=[
        chromosome_factory.gene_factory().random()
        for _ in range(random.randint(chromosome_factory.min_length(), chromosome_factory.max_length()))
    ])
