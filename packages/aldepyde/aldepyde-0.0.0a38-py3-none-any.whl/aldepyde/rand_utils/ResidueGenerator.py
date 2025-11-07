from abc import ABC, abstractmethod
from .PolymerClassifier import PolymerClassifier

class ResidueGenerator(ABC):
    def __init__(self, classifier:PolymerClassifier):
        self.classifier = classifier

    def _generate(self):
        pass