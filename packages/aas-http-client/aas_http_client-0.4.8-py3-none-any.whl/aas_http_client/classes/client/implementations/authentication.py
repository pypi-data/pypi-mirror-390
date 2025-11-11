import json
import logging
from enum import Enum

import requests
from requests.auth import HTTPBasicAuth

from aas_http_client.classes.Configuration.config_classes import OAuth
from aas_http_client.utilities.http_helper import log_response_errors

logger = logging.getLogger(__name__)


class AuthMethod(Enum):
    """Defines authentication methods.

    :param Enum: Base class for enumerations
    """

    No = 1
    basic_auth = 2
    o_auth = 3
    bearer = 4


def get_token(o_auth_configuration: OAuth) -> str | None:
    """Get token based on the provided OAuth configuration.

    :param auth_configuration: Authentication configuration
    :return: Access token or None if an error occurred
    """
    if o_auth_configuration.grant_type == "password":
        token = get_token_by_password(
            o_auth_configuration.token_url,
            o_auth_configuration.client_id,
            o_auth_configuration.get_client_secret(),
        )

    elif o_auth_configuration.is_active() and o_auth_configuration.grant_type == "client_credentials":
        token = get_token_by_basic_auth(
            o_auth_configuration.token_url,
            o_auth_configuration.client_id,
            o_auth_configuration.get_client_secret(),
        )

    return token


def get_token_by_basic_auth(endpoint: str, username: str, password: str, timeout=200) -> dict | None:
    """Get token from a specific authentication service provider by basic authentication.

    :param endpoint: Get token endpoint for the authentication service provider
    :param username: Username for the authentication service provider
    :param password: Password for the authentication service provider
    :param timeout: Timeout for the API calls, defaults to 200
    :return: Access token or None if an error occurred
    """
    data = {"grant_type": "client_credentials"}

    auth = HTTPBasicAuth(username, password)

    return _get_token_from_endpoint(endpoint, data, auth, timeout)


def get_token_by_password(endpoint: str, username: str, password: str, timeout=200) -> dict | None:
    """Get token from a specific authentication service provider by username and password.

    :param endpoint: Get token endpoint for the authentication service provider
    :param username: Username for the authentication service provider
    :param password: Password for the authentication service provider
    :param timeout: Timeout for the API calls, defaults to 200
    :return: Access token or None if an error occurred
    """
    data = {"grant_type": "password", "username": username, "password": password}

    return _get_token_from_endpoint(endpoint, data, None, timeout)


def _get_token_from_endpoint(endpoint: str, data: dict[str, str], auth: HTTPBasicAuth | None = None, timeout: int = 200) -> dict | None:
    """Get token from a specific authentication service provider.

    :param endpoint: Get token endpoint for the authentication service provider
    :param data: Data for the authentication service provider
    :param timeout: Timeout for the API calls, defaults to 200
    :return: Access token or None if an error occurred
    """
    try:
        response = requests.post(endpoint, auth=auth, data=data, timeout=timeout)
        logger.debug(f"Call REST API url '{response.url}'")

        if response.status_code != 200:
            log_response_errors(response)
            return None

    except requests.exceptions.RequestException as e:
        logger.error(f"Error call REST API: {e}")
        return False

    content = response.content.decode("utf-8")
    data = json.loads(content)
    return data.get("access_token", None)
