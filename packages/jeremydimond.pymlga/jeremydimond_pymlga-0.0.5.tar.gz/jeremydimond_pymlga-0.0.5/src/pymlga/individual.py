from dataclasses import dataclass
from typing import List

from pymlga.chromosome import Chromosome, ChromosomeFactory


@dataclass
class Individual:
    chromosomes: List[Chromosome]

    def __lt__(self, other: 'Individual'):
        return self.get_alleles() < other.get_alleles()

    def __iter__(self):
        return iter(self.chromosomes)

    def get_alleles(self) -> List[List[str]]:
        return [[gene.allele for gene in chromosome.genes] for chromosome in self.chromosomes]

    def mutate(self, mutation_rate: float, chromosome_factories: List[ChromosomeFactory]) -> 'Individual':
        return Individual(
            chromosomes=[
                chromosome.mutate(mutation_rate=mutation_rate, chromosome_factory=chromosome_factory)
                for chromosome, chromosome_factory in zip(self.chromosomes, chromosome_factories)
            ]
        )

    def crossover(
            self, other: 'Individual',
            mutation_rate: float,
            chromosome_factories: List[ChromosomeFactory]
    ) -> 'Individual':
        chromosomes = [
            chromosome_pair[0].crossover(
                other=chromosome_pair[1],
                mutation_rate=mutation_rate,
                chromosome_factory=chromosome_factory
            )
            for chromosome_pair, chromosome_factory in zip(
                zip(self.chromosomes, other.chromosomes),
                chromosome_factories
            )
        ]
        return Individual(chromosomes=chromosomes)


@dataclass
class EvaluatedIndividual:
    individual: Individual
    fitness: float = 0.0

    def __lt__(self, other: 'EvaluatedIndividual'):
        return self.fitness < other.fitness
