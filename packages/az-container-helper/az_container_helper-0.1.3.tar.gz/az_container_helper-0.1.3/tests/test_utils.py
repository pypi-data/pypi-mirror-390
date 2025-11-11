import os

from az_container_helper import get_credentials


def test_get_credentials_with_access_token():
    os.environ["ACCESS_TOKEN"] = "test_token" #noqa: S105
    assert get_credentials().get_token().token == "test_token"   #noqa: S105
