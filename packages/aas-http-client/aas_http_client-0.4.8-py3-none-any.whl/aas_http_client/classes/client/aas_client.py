"""Client for HTTP API communication with AAS server."""

import json
import logging
import time
from pathlib import Path

import basyx.aas.adapter.json
import requests
from basyx.aas.model import Reference, Submodel
from pydantic import BaseModel, Field, PrivateAttr, ValidationError
from requests import Session
from requests.auth import HTTPBasicAuth

from aas_http_client.classes.client.implementations.authentication import AuthMethod, get_token
from aas_http_client.classes.Configuration.config_classes import AuthenticationConfig
from aas_http_client.core.encoder import decode_base_64
from aas_http_client.utilities.http_helper import log_response_errors

logger = logging.getLogger(__name__)

STATUS_CODE_200 = 200
STATUS_CODE_201 = 201
STATUS_CODE_202 = 202
STATUS_CODE_204 = 204
STATUS_CODE_404 = 404

# region AasHttpClient


class AasHttpClient(BaseModel):
    """Represents a AasHttpClient to communicate with a REST API."""

    base_url: str = Field(..., alias="BaseUrl", description="Base URL of the AAS server.")
    auth_settings: AuthenticationConfig = Field(
        default_factory=AuthenticationConfig, alias="AuthenticationSettings", description="Authentication settings for the AAS server."
    )
    https_proxy: str | None = Field(default=None, alias="HttpsProxy", description="HTTPS proxy URL.")
    http_proxy: str | None = Field(default=None, alias="HttpProxy", description="HTTP proxy URL.")
    time_out: int = Field(default=200, alias="TimeOut", description="Timeout for HTTP requests.")
    connection_time_out: int = Field(default=100, alias="ConnectionTimeOut", description="Connection timeout for HTTP requests.")
    ssl_verify: bool = Field(default=True, alias="SslVerify", description="Enable SSL verification.")
    trust_env: bool = Field(default=True, alias="TrustEnv", description="Trust environment variables.")
    _session: Session = PrivateAttr(default=None)
    _auth_method: AuthMethod = PrivateAttr(default=AuthMethod.basic_auth)

    def initialize(self):
        """Initialize the AasHttpClient with the given URL, username and password."""
        if self.base_url.endswith("/"):
            self.base_url = self.base_url[:-1]

        self._session = requests.Session()

        self._handle_auth_method()

        self._session.verify = self.ssl_verify
        self._session.trust_env = self.trust_env

        if self.https_proxy:
            self._session.proxies.update({"https": self.https_proxy})
        if self.http_proxy:
            self._session.proxies.update({"http": self.http_proxy})

        self._session.headers.update(
            {
                "Content-Type": "application/json",
                "Accept": "*/*",
                "User-Agent": "python-requests/2.32.5",
                "Connection": "close",
            }
        )

    def _handle_auth_method(self):
        """Handles the authentication method based on the provided settings."""
        if self.auth_settings.bearer_auth.is_active():
            self._auth_method = AuthMethod.bearer
            logger.info("Authentication method: Bearer Token")
            self._session.headers.update({"Authorization": f"Bearer {self.auth_settings.bearer_auth.get_token()}"})
        elif self.auth_settings.o_auth.is_active():
            self._auth_method = AuthMethod.o_auth
            logger.info(
                f"Authentication method: OAuth | '{self.auth_settings.o_auth.client_id}' | '{self.auth_settings.o_auth.token_url}' | '{self.auth_settings.o_auth.grant_type}'"
            )
        elif self.auth_settings.basic_auth.is_active():
            self._auth_method = AuthMethod.basic_auth
            logger.info(f"Authentication method: Basic Auth | '{self.auth_settings.basic_auth.username}'")
            self._session.auth = HTTPBasicAuth(self.auth_settings.basic_auth.username, self.auth_settings.basic_auth.get_password())
        else:
            self._auth_method = AuthMethod.No
            logger.info("Authentication method: No Authentication")

    def get_root(self) -> dict | None:
        """Get the root endpoint of the AAS server API to test connectivity.

        This method calls the '/shells' endpoint to verify that the AAS server is accessible
        and responding. It automatically handles authentication token setup if service
        provider authentication is configured.

        :return: Response data as a dictionary containing shell information, or None if an error occurred
        """
        url = f"{self.base_url}/shells"

        self._set_token()

        try:
            response = self._session.get(url, timeout=10)
            logger.debug(f"Call REST API url '{response.url}'")

            if response.status_code != STATUS_CODE_200:
                log_response_errors(response)
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Error call REST API: {e}")
            return None

        content = response.content.decode("utf-8")
        return json.loads(content)

    def _set_token(self) -> str | None:
        """Set authentication token in session headers based on configured authentication method.

        :raises requests.exceptions.RequestException: If token retrieval fails
        """
        if self._auth_method != AuthMethod.o_auth:
            return None

        token = get_token(self.auth_settings.o_auth).strip()

        if token:
            self._session.headers.update({"Authorization": f"Bearer {token}"})
            return token

        return None

    # endregion

    # region shells

    def post_asset_administration_shell(self, aas_data: dict) -> dict | None:
        """Creates a new Asset Administration Shell.

        :param aas_data: Json data of the Asset Administration Shell to post
        :return: Response data as a dictionary or None if an error occurred
        """
        url = f"{self.base_url}/shells"
        logger.debug(f"Call REST API url '{url}'")

        self._set_token()

        try:
            response = self._session.post(url, json=aas_data, timeout=self.time_out)
            logger.debug(f"Call REST API url '{response.url}'")

            if response.status_code not in (STATUS_CODE_201, STATUS_CODE_202):
                log_response_errors(response)
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Error call REST API: {e}")
            return None

        content = response.content.decode("utf-8")
        return json.loads(content)

    def put_asset_administration_shell_by_id(self, identifier: str, aas_data: dict) -> bool:
        """Creates or replaces an existing Asset Administration Shell.

        :param identifier: Identifier of the AAS to update
        :param aas_data: Json data of the Asset Administration Shell data to update
        :return: True if the update was successful, False otherwise
        """
        decoded_identifier: str = decode_base_64(identifier)
        url = f"{self.base_url}/shells/{decoded_identifier}"

        self._set_token()

        try:
            response = self._session.put(url, json=aas_data, timeout=self.time_out)
            logger.debug(f"Call REST API url '{response.url}'")

            if response.status_code is not STATUS_CODE_204:
                log_response_errors(response)
                return False

        except requests.exceptions.RequestException as e:
            logger.error(f"Error call REST API: {e}")
            return False

        return True

    def put_submodel_by_id_aas_repository(self, aas_id: str, submodel_id: str, submodel_data: dict) -> bool:
        """Updates the Submodel.

        :param aas_id: ID of the AAS to update the submodel for
        :param submodel_data: Json data to the Submodel to update
        :return: True if the update was successful, False otherwise
        """
        decoded_aas_id: str = decode_base_64(aas_id)
        decoded_submodel_id: str = decode_base_64(submodel_id)
        url = f"{self.base_url}/shells/{decoded_aas_id}/submodels/{decoded_submodel_id}"

        self._set_token()

        try:
            response = self._session.put(url, json=submodel_data, timeout=self.time_out)
            logger.debug(f"Call REST API url '{response.url}'")

            if response.status_code != STATUS_CODE_204:
                log_response_errors(response)
                return False

        except requests.exceptions.RequestException as e:
            logger.error(f"Error call REST API: {e}")
            return False

        return True

    def get_all_asset_administration_shells(self) -> list[dict] | None:
        """Returns all Asset Administration Shells.

        :return: List of paginated Asset Administration Shells data or None if an error occurred
        """
        url = f"{self.base_url}/shells"

        self._set_token()

        try:
            response = self._session.get(url, timeout=self.time_out)
            logger.debug(f"Call REST API url '{response.url}'")

            if response.status_code != STATUS_CODE_200:
                log_response_errors(response)
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Error call REST API: {e}")
            return None

        content = response.content.decode("utf-8")
        return json.loads(content)

    def get_asset_administration_shell_by_id(self, aas_id: str) -> dict | None:
        """Returns a specific Asset Administration Shell.

        :param aas_id: ID of the AAS to retrieve
        :return: Asset Administration Shells data or None if an error occurred
        """
        decoded_aas_id: str = decode_base_64(aas_id)
        url = f"{self.base_url}/shells/{decoded_aas_id}"

        self._set_token()

        try:
            response = self._session.get(url, timeout=self.time_out)
            logger.debug(f"Call REST API url '{response.url}'")

            if response.status_code != STATUS_CODE_200:
                log_response_errors(response)
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Error call REST API: {e}")
            return None

        content = response.content.decode("utf-8")
        return json.loads(content)

    def get_asset_administration_shell_by_id_reference_aas_repository(self, aas_id: str) -> Reference | None:
        """Returns a specific Asset Administration Shell as a Reference.

        :param aas_id: ID of the AAS reference to retrieve
        :return: Asset Administration Shells reference data or None if an error occurred
        """
        decoded_aas_id: str = decode_base_64(aas_id)
        url = f"{self.base_url}/shells/{decoded_aas_id}/$reference"

        self._set_token()

        try:
            response = self._session.get(url, timeout=self.time_out)
            logger.debug(f"Call REST API url '{response.url}'")

            if response.status_code != STATUS_CODE_200:
                log_response_errors(response)
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Error call REST API: {e}")
            return None

        ref_dict_string = response.content.decode("utf-8")
        return json.loads(ref_dict_string, cls=basyx.aas.adapter.json.AASFromJsonDecoder)

    def get_submodel_by_id_aas_repository(self, aas_id: str, submodel_id: str) -> Submodel | None:
        """Returns the Submodel.

        :param aas_id: ID of the AAS to retrieve the submodel from
        :param submodel_id: ID of the submodel to retrieve
        :return: Submodel object or None if an error occurred
        """
        decoded_aas_id: str = decode_base_64(aas_id)
        decoded_submodel_id: str = decode_base_64(submodel_id)

        url = f"{self.base_url}/shells/{decoded_aas_id}/submodels/{decoded_submodel_id}"

        self._set_token()

        try:
            response = self._session.get(url, timeout=self.time_out)
            logger.debug(f"Call REST API url '{response.url}'")

            if response.status_code != STATUS_CODE_200:
                log_response_errors(response)
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Error call REST API: {e}")
            return None

        content = response.content.decode("utf-8")
        return json.loads(content)

    def delete_asset_administration_shell_by_id(self, aas_id: str) -> bool:
        """Deletes an Asset Administration Shell.

        :param aas_id: ID of the AAS to retrieve
        :return: True if the deletion was successful, False otherwise
        """
        decoded_aas_id: str = decode_base_64(aas_id)
        url = f"{self.base_url}/shells/{decoded_aas_id}"

        self._set_token()

        try:
            response = self._session.delete(url, timeout=self.time_out)
            logger.debug(f"Call REST API url '{response.url}'")

            if response.status_code != STATUS_CODE_204:
                log_response_errors(response)
                return False

        except requests.exceptions.RequestException as e:
            logger.error(f"Error call REST API: {e}")
            return False

        return True

    # endregion

    # region submodels

    def post_submodel(self, submodel_data: dict) -> dict | None:
        """Creates a new Submodel.

        :param Submodel_data: Json data of the Submodel to post
        :return: Submodel data or None if an error occurred
        """
        url = f"{self.base_url}/submodels"

        self._set_token()

        try:
            response = self._session.post(url, json=submodel_data, timeout=self.time_out)
            logger.debug(f"Call REST API url '{response.url}'")

            if response.status_code not in (STATUS_CODE_201, STATUS_CODE_202):
                log_response_errors(response)
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Error call REST API: {e}")
            return None

        content = response.content.decode("utf-8")
        return json.loads(content)

    def put_submodels_by_id(self, identifier: str, submodel_data: dict) -> bool:
        """Updates a existing Submodel.

        :param identifier: Encoded ID of the Submodel to update
        :param submodel_data: Json data of the Submodel to update
        :return: True if the update was successful, False otherwise
        """
        decoded_identifier: str = decode_base_64(identifier)
        url = f"{self.base_url}/submodels/{decoded_identifier}"

        self._set_token()

        try:
            response = self._session.put(url, json=submodel_data, timeout=self.time_out)
            logger.debug(f"Call REST API url '{response.url}'")

            if response.status_code != STATUS_CODE_204:
                log_response_errors(response)
                return False

        except requests.exceptions.RequestException as e:
            logger.error(f"Error call REST API: {e}")
            return False

        return True

    def get_all_submodels(self) -> list[dict] | None:
        """Returns all Submodels.

        :return: List of Submodel data or None if an error occurred
        """
        url = f"{self.base_url}/submodels"

        self._set_token()

        try:
            response = self._session.get(url, timeout=self.time_out)
            logger.debug(f"Call REST API url '{response.url}'")

            if response.status_code != STATUS_CODE_200:
                log_response_errors(response)
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Error call REST API: {e}")
            return None

        content = response.content.decode("utf-8")
        return json.loads(content)

    def get_submodel_by_id(self, submodel_id: str) -> dict | None:
        """Returns a specific Submodel.

        :param submodel_id: Encoded ID of the Submodel to retrieve
        :return: Submodel data or None if an error occurred
        """
        decoded_submodel_id: str = decode_base_64(submodel_id)
        url = f"{self.base_url}/submodels/{decoded_submodel_id}"

        self._set_token()

        try:
            response = self._session.get(url, timeout=self.time_out)
            logger.debug(f"Call REST API url '{response.url}'")

            if response.status_code != STATUS_CODE_200:
                log_response_errors(response)
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Error call REST API: {e}")
            return None

        content = response.content.decode("utf-8")
        return json.loads(content)

    def patch_submodel_by_id(self, submodel_id: str, submodel_data: dict) -> bool:
        """Updates an existing Submodel.

        :param submodel_id: Encoded ID of the Submodel to delete
        :return: True if the patch was successful, False otherwise
        """
        decoded_submodel_id: str = decode_base_64(submodel_id)
        url = f"{self.base_url}/submodels/{decoded_submodel_id}"

        self._set_token()

        try:
            response = self._session.patch(url, json=submodel_data, timeout=self.time_out)
            logger.debug(f"Call REST API url '{response.url}'")

            if response.status_code != STATUS_CODE_204:
                log_response_errors(response)
                return False

        except requests.exceptions.RequestException as e:
            logger.error(f"Error call REST API: {e}")
            return False

        return True

    def delete_submodel_by_id(self, submodel_id: str) -> bool:
        """Deletes a Submodel.

        :param submodel_id: Encoded ID of the Submodel to delete
        :return: True if the deletion was successful, False otherwise
        """
        decoded_submodel_id: str = decode_base_64(submodel_id)
        url = f"{self.base_url}/submodels/{decoded_submodel_id}"

        self._set_token()

        try:
            response = self._session.delete(url, timeout=self.time_out)
            logger.debug(f"Call REST API url '{response.url}'")

            if response.status_code != STATUS_CODE_204:
                log_response_errors(response)
                return False

        except requests.exceptions.RequestException as e:
            logger.error(f"Error call REST API: {e}")
            return False

        return True

    def get_all_submodel_elements_submodel_repository(self, submodel_id: str) -> list[dict] | None:
        """Returns all submodel elements including their hierarchy.

        :param submodel_id: Encoded ID of the Submodel to retrieve elements from
        :return: List of Submodel element data or None if an error occurred
        """
        decoded_submodel_id: str = decode_base_64(submodel_id)
        url = f"{self.base_url}/submodels/{decoded_submodel_id}/submodel-elements"

        self._set_token()

        try:
            response = self._session.get(url, timeout=self.time_out)
            logger.debug(f"Call REST API url '{response.url}'")

            if response.status_code != STATUS_CODE_200:
                log_response_errors(response)
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Error call REST API: {e}")
            return None

        content = response.content.decode("utf-8")
        return json.loads(content)

    def post_submodel_element_submodel_repo(self, submodel_id: str, submodel_element_data: dict) -> dict | None:
        """Creates a new submodel element.

        :param submodel_id: Encoded ID of the Submodel to create elements for
        :return: Submodel element data or None if an error occurred
        """
        decoded_submodel_id: str = decode_base_64(submodel_id)
        url = f"{self.base_url}/submodels/{decoded_submodel_id}/submodel-elements"

        self._set_token()

        try:
            response = self._session.post(url, json=submodel_element_data, timeout=self.time_out)
            logger.debug(f"Call REST API url '{response.url}'")

            if response.status_code != STATUS_CODE_201:
                log_response_errors(response)
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Error call REST API: {e}")
            return None

        content = response.content.decode("utf-8")
        return json.loads(content)

    def post_submodel_element_by_path_submodel_repo(self, submodel_id: str, submodel_element_path: str, submodel_element_data: dict) -> dict | None:
        """Creates a new submodel element at a specified path within submodel elements hierarchy.

        :param submodel_id: Encoded ID of the Submodel to create elements for
        :param submodel_element_path: Path within the Submodel elements hierarchy
        :param submodel_element_data: Data for the new Submodel element
        :return: Submodel element data or None if an error occurred
        """
        decoded_submodel_id: str = decode_base_64(submodel_id)
        url = f"{self.base_url}/submodels/{decoded_submodel_id}/submodel-elements/{submodel_element_path}"

        self._set_token()

        try:
            response = self._session.post(url, json=submodel_element_data, timeout=self.time_out)
            logger.debug(f"Call REST API url '{response.url}'")

            if response.status_code != STATUS_CODE_201:
                log_response_errors(response)
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Error call REST API: {e}")
            return None

        content = response.content.decode("utf-8")
        return json.loads(content)

    def get_submodel_element_by_path_submodel_repo(self, submodel_id: str, submodel_element_path: str) -> dict | None:
        """Returns a specific submodel element from the Submodel at a specified path.

        :param submodel_id: Encoded ID of the Submodel to retrieve element from
        :param submodel_element_path: Path of the Submodel element to retrieve
        :return: Submodel element data or None if an error occurred
        """
        decoded_submodel_id: str = decode_base_64(submodel_id)

        url = f"{self.base_url}/submodels/{decoded_submodel_id}/submodel-elements/{submodel_element_path}"

        self._set_token()

        try:
            response = self._session.get(url, timeout=self.time_out)
            logger.debug(f"Call REST API url '{response.url}'")

            if response.status_code != STATUS_CODE_200:
                log_response_errors(response)
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Error call REST API: {e}")
            return None

        content = response.content.decode("utf-8")
        return json.loads(content)

    def delete_submodel_element_by_path_submodel_repo(self, submodel_id: str, submodel_element_path: str):
        """Deletes a submodel element at a specified path within the submodel elements hierarchy.

        :param submodel_id: Encoded ID of the Submodel to delete submodel element from
        :param submodel_element_path: Path of the Submodel element to delete
        :return: True if the deletion was successful, False otherwise
        """
        decoded_submodel_id: str = decode_base_64(submodel_id)

        url = f"{self.base_url}/submodels/{decoded_submodel_id}/submodel-elements/{submodel_element_path}"

        self._set_token()

        try:
            response = self._session.delete(url, timeout=self.time_out)
            logger.debug(f"Call REST API url '{response.url}'")

            if response.status_code != STATUS_CODE_204:
                log_response_errors(response)
                return False

        except requests.exceptions.RequestException as e:
            logger.error(f"Error call REST API: {e}")
            return False

        return True

    def patch_submodel_element_by_path_value_only_submodel_repo(self, submodel_id: str, submodel_element_path: str, value: str) -> bool:
        """Updates the value of an existing SubmodelElement.

        :param submodel_id: Encoded ID of the Submodel to update submodel element for
        :param submodel_element_path: Path of the Submodel element to update
        :param value: Submodel element value to update as string
        :return: True if the patch was successful, False otherwise
        """
        decoded_submodel_id: str = decode_base_64(submodel_id)

        url = f"{self.base_url}/submodels/{decoded_submodel_id}/submodel-elements/{submodel_element_path}/$value"

        self._set_token()

        try:
            response = self._session.patch(url, json=value, timeout=self.time_out)
            logger.debug(f"Call REST API url '{response.url}'")

            if response.status_code != STATUS_CODE_204:
                log_response_errors(response)
                return False

        except requests.exceptions.RequestException as e:
            logger.error(f"Error call REST API: {e}")
            return False

        return True


# endregion

# region client


def create_client_by_url(
    base_url: str,
    basic_auth_username: str = "",
    basic_auth_password: str = "",
    o_auth_client_id: str = "",
    o_auth_client_secret: str = "",
    o_auth_token_url: str = "",
    bearer_auth_token: str = "",
    http_proxy: str = "",
    https_proxy: str = "",
    time_out: int = 200,
    connection_time_out: int = 60,
    ssl_verify: str = True,  # noqa: FBT002
    trust_env: bool = True,  # noqa: FBT001, FBT002
) -> AasHttpClient | None:
    """Create a HTTP client for a AAS server connection from the given parameters.

    :param base_url: Base URL of the AAS server, e.g. "http://basyx_python_server:80/"
    :param basic_auth_username: Username for the AAS server basic authentication, defaults to ""
    :param basic_auth_password: Password for the AAS server basic authentication, defaults to ""
    :param o_auth_client_id: Client ID for OAuth authentication, defaults to ""
    :param o_auth_client_secret: Client secret for OAuth authentication, defaults to ""
    :param o_auth_token_url: Token URL for OAuth authentication, defaults to ""
    :param bearer_auth_token: Bearer token for authentication, defaults to ""
    :param http_proxy: HTTP proxy URL, defaults to ""
    :param https_proxy: HTTPS proxy URL, defaults to ""
    :param time_out: Timeout for the API calls, defaults to 200
    :param connection_time_out: Timeout for the connection to the API, defaults to 60
    :param ssl_verify: Whether to verify SSL certificates, defaults to True
    :param trust_env: Whether to trust environment variables for proxy settings, defaults to True
    :return: An instance of AasHttpClient initialized with the provided parameters or None if connection fails
    """
    logger.info(f"Create AAS server http client from URL '{base_url}'.")
    config_dict: dict[str, str] = {}
    config_dict["BaseUrl"] = base_url
    config_dict["HttpProxy"] = http_proxy
    config_dict["HttpsProxy"] = https_proxy
    config_dict["TimeOut"] = time_out
    config_dict["ConnectionTimeOut"] = connection_time_out
    config_dict["SslVerify"] = ssl_verify
    config_dict["TrustEnv"] = trust_env

    config_dict["AuthenticationSettings"] = {
        "BasicAuth": {"Username": basic_auth_username},
        "OAuth": {
            "ClientId": o_auth_client_id,
            "TokenUrl": o_auth_token_url,
        },
    }

    return create_client_by_dict(config_dict, basic_auth_password, o_auth_client_secret, bearer_auth_token)


def create_client_by_dict(
    configuration: dict, basic_auth_password: str = "", o_auth_client_secret: str = "", bearer_auth_token: str = ""
) -> AasHttpClient | None:
    """Create a HTTP client for a AAS server connection from the given configuration.

    :param configuration: Dictionary containing the AAS server connection settings
    :param basic_auth_password: Password for the AAS server basic authentication, defaults to ""
    :param o_auth_client_secret: Client secret for OAuth authentication, defaults to ""
    :param bearer_auth_token: Bearer token for authentication, defaults to ""
    :return: An instance of AasHttpClient initialized with the provided parameters or None if validation fails
    """
    logger.info("Create AAS server http client from dictionary.")
    config_string = json.dumps(configuration, indent=4)

    return _create_client(config_string, basic_auth_password, o_auth_client_secret, bearer_auth_token)


def create_client_by_config(
    config_file: Path, basic_auth_password: str = "", o_auth_client_secret: str = "", bearer_auth_token: str = ""
) -> AasHttpClient | None:
    """Create a HTTP client for a AAS server connection from a given configuration file.

    :param config_file: Path to the configuration file containing the AAS server connection settings
    :param basic_auth_password: Password for the AAS server basic authentication, defaults to ""
    :param o_auth_client_secret: Client secret for OAuth authentication, defaults to ""
    :param bearer_auth_token: Bearer token for authentication, defaults to ""
    :return: An instance of AasHttpClient initialized with the provided parameters or None if validation fails
    """
    config_file = config_file.resolve()
    logger.info(f"Create AAS server http client from configuration file '{config_file}'.")
    if not config_file.exists():
        config_string = "{}"
        logger.warning(f"Configuration file '{config_file}' not found. Using default configuration.")
    else:
        config_string = config_file.read_text(encoding="utf-8")
        logger.debug(f"Configuration  file '{config_file}' found.")

    return _create_client(config_string, basic_auth_password, o_auth_client_secret, bearer_auth_token)


def _create_client(config_string: str, basic_auth_password: str, o_auth_client_secret: str, bearer_auth_token: str) -> AasHttpClient | None:
    """Create and initialize an AAS HTTP client from configuration string.

    This internal method validates the configuration, sets authentication credentials,
    initializes the client, and tests the connection to the AAS server.

    :param config_string: JSON configuration string containing AAS server settings
    :param basic_auth_password: Password for basic authentication, defaults to ""
    :param o_auth_client_secret: Client secret for OAuth authentication, defaults to ""
    :param bearer_auth_token: Bearer token for authentication, defaults to ""
    :return: An initialized and connected AasHttpClient instance or None if connection fails
    :raises ValidationError: If the configuration string is invalid
    :raises TimeoutError: If connection to the server times out
    """
    try:
        client = AasHttpClient.model_validate_json(config_string)
    except ValidationError as ve:
        raise ValidationError(f"Invalid BaSyx server configuration file: {ve}") from ve

    client.auth_settings.basic_auth.set_password(basic_auth_password)
    client.auth_settings.o_auth.set_client_secret(o_auth_client_secret)
    client.auth_settings.bearer_auth.set_token(bearer_auth_token)

    logger.info("Using server configuration:")
    logger.info(f"BaseUrl: '{client.base_url}'")
    logger.info(f"TimeOut: '{client.time_out}'")
    logger.info(f"HttpsProxy: '{client.https_proxy}'")
    logger.info(f"HttpProxy: '{client.http_proxy}'")
    logger.info(f"ConnectionTimeOut: '{client.connection_time_out}'.")
    logger.info(f"SSLVerify: '{client.ssl_verify}'.")
    logger.info(f"TrustEnv: '{client.trust_env}'.")

    client.initialize()

    # test the connection to the REST API
    connected = _connect_to_api(client)

    if not connected:
        return None

    return client


def _connect_to_api(client: AasHttpClient) -> bool:
    """Test the connection to the AAS server API with retry logic.

    This internal method attempts to establish a connection to the AAS server by calling
    the get_root() method. It retries the connection for the duration specified in the
    client's connection_time_out setting, sleeping 1 second between attempts.

    :param client: The AasHttpClient instance to test the connection for
    :return: True if connection is successful, False otherwise
    :raises TimeoutError: If connection attempts fail for the entire timeout duration
    """
    start_time = time.time()
    logger.debug(f"Try to connect to REST API '{client.base_url}' for {client.connection_time_out} seconds.")
    counter: int = 0
    while True:
        try:
            root = client.get_root()
            if root:
                logger.info(f"Connected to server API at '{client.base_url}' successfully.")
                return True
        except requests.exceptions.ConnectionError:
            pass
        if time.time() - start_time > client.connection_time_out:
            raise TimeoutError(f"Connection to server API timed out after {client.connection_time_out} seconds.")

        counter += 1
        logger.warning(f"Retrying connection (attempt: {counter}).")
        time.sleep(1)


# endregion
