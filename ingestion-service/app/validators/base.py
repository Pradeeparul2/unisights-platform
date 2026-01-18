from abc import ABC, abstractmethod
from typing import Dict, Any


class Validator(ABC):
    """
    Base class for all validators.
    """

    @abstractmethod
    def validate(self, data: Dict[str, Any]) -> None:
        """
        Validate input data.

        Raises:
            ValueError if validation fails.
        """
        pass
