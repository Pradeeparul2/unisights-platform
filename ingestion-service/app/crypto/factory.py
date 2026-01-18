from app.core.settings import Settings
from app.crypto.decryptor import PayloadDecryptor
from app.crypto.wasm_aes import WasmAESDecryptor
from app.crypto.noop import NoopDecryptor


def create_decryptor(settings: Settings) -> PayloadDecryptor:
    """
    Create and return the configured payload decryptor.
    """

    if settings.encryption_enabled:
        return WasmAESDecryptor(settings)

    return NoopDecryptor()
