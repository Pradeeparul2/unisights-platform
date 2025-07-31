import base64
import json
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Cipher import AES
from Crypto.Hash import SHA256

def derive_key(passphrase: str, salt: str, iterations: int = 100_000) -> bytes:
    return PBKDF2(passphrase.encode(), salt.encode(), dkLen=32, count=iterations, hmac_hash_module=SHA256)

def decrypt_payload(ciphertext_b64: str, nonce_b64: str, passphrase: str, salt: str) -> dict:
    # Decode base64
    ciphertext = base64.b64decode(ciphertext_b64)
    nonce = base64.b64decode(nonce_b64)

    # Derive the key
    key = derive_key(passphrase, salt)

    # Decrypt using AES-256-GCM
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    plaintext = cipher.decrypt_and_verify(ciphertext[:-16], ciphertext[-16:])  # split into data + tag

    return json.loads(plaintext)

# Example usage
# encrypted_payload = {
#     "data": "<base64 encrypted data>",
#     "id": "<base64 nonce>"
# }

# passphrase = "your-secret-passphrase"
# salt = "your-salt"

# try:
#     decrypted = decrypt_payload(encrypted_payload["data"], encrypted_payload["id"], passphrase, salt)
#     print("Decrypted payload:", json.dumps(decrypted, indent=2))
# except Exception as e:
#     print("Decryption failed:", str(e))
