import dotenv
from azure.core.exceptions import HttpResponseError
from azure.keyvault.secrets import SecretClient

from az_container_helper.utils import get_credentials


class Secret:
    """Class to store secret values
    It will prevent the secret value from being printed or logged accidentally.
    """

    def __init__(self, secret_value):
        self._secret_value = secret_value

    def __str__(self):
        return "********" if self._secret_value else "None"

    def get_secret_value(self):
        return self._secret_value


class KeyVault:
    """KeyVault wrapper class to conveniently access Azure KeyVault secrets.
    If the KeyVault cannot be accessed, it will try to read secrets from a
    .secrets file instead. This can be useful for testing or inside restricted
    environments like containers.

    Args:
        url (str): URL of the Azure KeyVault
        secrets_path (str, optional): Path to the .secrets file. Defaults to None.
    """
    def __init__(self, url, secrets_path=None):
        self.url = url
        self.secrets = dotenv.dotenv_values(dotenv_path=secrets_path)
        self.credential = get_credentials()
        self.client = SecretClient(vault_url=self.url, credential=self.credential)

    def get_secret(self, secret_name):
        secret_value = None
        try:
            secret = self.client.get_secret(secret_name)
            secret_value = secret.value
        except HttpResponseError:
            secret_value = self.secrets[secret_name]
        return Secret(secret_value)
