from abc import ABC, abstractmethod
from typing import List
from loly.violation import Violation


class ViolationPresenter(ABC):
    """Abstract base class for presenting violations."""

    @abstractmethod
    def present(self, violations: List[Violation]) -> str:
        pass
