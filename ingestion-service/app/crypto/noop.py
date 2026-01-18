import json
from typing import Dict, Any

from app.crypto.decryptor import PayloadDecryptor
from app.utils.json import safe_json_loads


class NoopDecryptor(PayloadDecryptor):
    """
    No-op decryptor: assumes payload is plain JSON.
    """

    def decrypt(self, payload: str, asset_id: str) -> Dict[str, Any]:
        return safe_json_loads(payload)
