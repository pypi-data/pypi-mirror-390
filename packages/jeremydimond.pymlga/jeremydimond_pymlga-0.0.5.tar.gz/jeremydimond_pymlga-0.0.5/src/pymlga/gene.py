import random
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List


@dataclass
class Gene:
    allele: str

    def mutate(self, mutation_rate: float, gene_factory: 'GeneFactory') -> 'Gene':
        if random.random() < mutation_rate:
            return gene_factory.random()
        return Gene(allele=self.allele)


class GeneFactory(ABC):
    @abstractmethod
    def random(self) -> Gene:  # pragma: no cover
        pass


@dataclass
class SimpleGeneFactory(GeneFactory):
    genes: List[Gene]

    def random(self) -> Gene:
        return self.genes.pop(0)
