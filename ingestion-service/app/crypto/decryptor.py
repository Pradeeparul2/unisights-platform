from abc import ABC, abstractmethod
from typing import Dict, Any


class PayloadDecryptor(ABC):
    """
    Abstract base class for payload decryption.
    """

    @abstractmethod
    def decrypt(self, payload: str, asset_id: str) -> Dict[str, Any]:
        """
        Decrypt and return analytics payload.

        Raises:
            Exception if decryption fails.
        """
        pass
