import os

from azure.core.credentials import AccessToken
from azure.identity import DefaultAzureCredential

# Taken from https://github.com/Azure/azure-sdk-for-python/blob/bb35e8719972a81a07c7359e729f17e2cc0dae40/sdk/identity/azure-identity/samples/custom_credentials.py#L15
class StaticTokenCredential(object):
    """Authenticates with a previously-acquired access token

    Note that an access token is valid only for certain resources and eventually expires. This credential is therefore
    quite limited. An application using it must ensure the token is valid and contains all claims required by any
    service client given an instance of this credential.
    """

    def __init__(self, access_token):
        if isinstance(access_token, AccessToken):
            self._token = access_token
        else:
            # setting expires_on in the past causes Azure SDK clients to call get_token every time they need a token
            self._token = AccessToken(token=access_token, expires_on=0)

    def get_token(self, *scopes, claims = None, tenant_id= None, **kwargs):
        """get_token is the only method a credential must implement"""
        return self._token


def get_credentials():
    """
    Gets a credential to use with Azure services.

    It will first try to read an existing access token from the ACCESS_TOKEN env variable.
    If no existing token is found it will fall back to standard DefaultAzureCredential workflow.

    Returns:
        A credential to use with Azure services.
    """
    if "ACCESS_TOKEN" in os.environ:
        return StaticTokenCredential(os.environ["ACCESS_TOKEN"])
    else:
        return DefaultAzureCredential()