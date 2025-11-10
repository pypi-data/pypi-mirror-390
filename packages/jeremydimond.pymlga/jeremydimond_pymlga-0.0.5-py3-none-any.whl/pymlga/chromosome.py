import random
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List

from pymlga.gene import GeneFactory, Gene, SimpleGeneFactory


@dataclass
class Chromosome:
    genes: List[Gene]

    def __iter__(self):
        return iter(self.genes)

    def mutate(self, mutation_rate: float, chromosome_factory: 'ChromosomeFactory') -> 'Chromosome':
        mutated_genes = _mutate_genes(
            genes=self.genes,
            mutation_rate=mutation_rate,
            chromosome_factory=chromosome_factory
        )
        return Chromosome(genes=mutated_genes)

    def crossover(
            self, other: 'Chromosome', mutation_rate: float, chromosome_factory: 'ChromosomeFactory'
    ) -> 'Chromosome':
        crossover_genes = [random.choice(pair) for pair in zip(self.genes, other.genes)]
        mutated_genes = _mutate_genes(
            genes=crossover_genes,
            mutation_rate=mutation_rate,
            chromosome_factory=chromosome_factory
        )
        return Chromosome(genes=mutated_genes)


def _mutate_genes(genes: List[Gene], mutation_rate: float, chromosome_factory: 'ChromosomeFactory') -> List[Gene]:
    mutated_genes = [
        gene.mutate(mutation_rate=mutation_rate, gene_factory=chromosome_factory.gene_factory())
        for gene in genes if random.random() >= mutation_rate
    ]
    while len(mutated_genes) < chromosome_factory.min_length():
        mutated_genes.append(chromosome_factory.gene_factory().random())
    for _ in range(chromosome_factory.max_length() - len(mutated_genes)):
        if random.random() < mutation_rate:
            mutated_genes.append(chromosome_factory.gene_factory().random())
    return mutated_genes


class ChromosomeFactory(ABC):
    @abstractmethod
    def min_length(self) -> int:  # pragma: no cover
        pass

    @abstractmethod
    def max_length(self) -> int:  # pragma: no cover
        pass

    @abstractmethod
    def gene_factory(self) -> GeneFactory:  # pragma: no cover
        pass


class SimpleChromosomeFactory(ChromosomeFactory):
    def __init__(self, alleles: List[str], min_length: int, max_length: int):
        self._min_length = min_length
        self._max_length = max_length
        self._gene_factory = SimpleGeneFactory(genes=[Gene(allele=allele) for allele in alleles])

    def min_length(self) -> int:
        return self._min_length

    def max_length(self) -> int:
        return self._max_length

    def gene_factory(self) -> GeneFactory:
        return self._gene_factory
