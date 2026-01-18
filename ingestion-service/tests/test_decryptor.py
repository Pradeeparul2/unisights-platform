import json
from app.crypto.noop import NoopDecryptor


def test_noop_decryptor():
    decryptor = NoopDecryptor()

    payload = json.dumps({
        "asset_id": "a1",
        "session_id": "s1",
        "events": [],
        "device_info": {},
        "utm_params": {},
    })

    decrypted = decryptor.decrypt(payload, "a1")

    assert decrypted["asset_id"] == "a1"
    assert decrypted["session_id"] == "s1"
