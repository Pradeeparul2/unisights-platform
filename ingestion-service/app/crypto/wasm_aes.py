import logging
from typing import Dict, Any

from app.crypto.decryptor import PayloadDecryptor
from app.core.settings import Settings
from cipher import decrypt_payload

logger = logging.getLogger(__name__)


class WasmAESDecryptor(PayloadDecryptor):
    """
    AES decryptor compatible with the WASM SDK encryption.
    """

    def __init__(self, settings: Settings):
        self.passphrase = settings.encryption_passphrase
        self.salt = settings.encryption_salt

        if not self.passphrase or not self.salt:
            raise RuntimeError("Encryption enabled but secrets are missing")

    def decrypt(self, payload: str, asset_id: str) -> Dict[str, Any]:
        try:
            return decrypt_payload(
                payload,
                asset_id,
                self.passphrase,
                self.salt,
            )
        except Exception as e:
            logger.warning("Payload decryption failed")
            raise
