from pathlib import Path

import pytest

from az_container_helper.keyvault import KeyVault

test_dir = Path(__file__).parent.absolute()
secrets_path = test_dir / "resources" / ".secrets"

KV_URL = "https://test-keyvault.vault.azure.net"

def test_keyvault_with_secrets():
    kv = KeyVault(KV_URL, secrets_path=secrets_path)

    secret_name = "TEST_SECRET"  #noqa: S105
    secret = kv.get_secret(secret_name)
    assert secret.get_secret_value() == "123456" #noqa: S105

    secret_name = "VERY_SECRET_SECRET" #noqa: S105
    secret = kv.get_secret(secret_name)
    assert secret.get_secret_value() == "abcdefgh" #noqa: S105


def test_keyvault_without_secrets():
    with pytest.raises(KeyError):
        kv = KeyVault(KV_URL)
        secret_name = "TEST_SECRET" #noqa: S105
        secret = kv.get_secret(secret_name)
        assert secret.get_secret_value() == "123456" #noqa: S105