from typing import Optional, Union
from urllib.parse import urljoin

import requests
from cachetools import cached, LRUCache, keys
from frogml.core.exceptions import FrogmlLoginException
from frogml.core.exceptions.frogml_token_exception import FrogMLTokenException
from frogml.storage.authentication.models import AuthConfig, BearerAuth, EmptyAuth
from frogml.storage.authentication.utils import get_credentials
from requests import Response
from requests.exceptions import RequestException
from typing_extensions import Self


class FrogMLAuthClient:
    __MIN_TOKEN_LENGTH: int = 64

    def __init__(self: Self, auth_config: Optional[AuthConfig] = None):
        self.__auth_config: Optional[AuthConfig] = auth_config
        self.__token: Optional[str] = None
        self.__tenant_id: Optional[str] = None

    def get_token(self: Self) -> str:
        auth: Union[EmptyAuth, BearerAuth] = self.get_auth()

        if isinstance(auth, BearerAuth):
            self.validate_token(auth.token)
            self.__token = auth.token

        else:
            raise FrogMLTokenException(
                message="Token not found in the authentication configurations."
            )

        return self.__token

    @cached(cache=LRUCache(maxsize=1), key=keys.methodkey)
    def get_tenant_id(self: Self) -> str:
        base_url: str = self.get_base_url()
        url: str = urljoin(base_url, "/ui/api/v1/system/auth/screen/footer")

        try:
            response: Response = requests.get(url, timeout=15, auth=self.get_auth())
            response.raise_for_status()  # Raises an HTTPError for bad responses
            response_data: dict = response.json()

            if "serverId" in response_data:
                self.__tenant_id = response_data["serverId"]
            else:
                self.__tenant_id = self.__get_jpd_id(base_url)

            return self.__tenant_id

        except (RequestException, ValueError) as exc:
            raise FrogmlLoginException(
                "Failed to authenticate with JFrog. Please check your credentials"
            ) from exc

    def get_base_url(self: Self) -> str:
        artifactory_url, _ = get_credentials(self.__auth_config)
        return self.__remove_artifactory_path_from_url(artifactory_url)

    def get_auth(self: Self) -> Union[EmptyAuth, BearerAuth]:
        return get_credentials(self.__auth_config)[1]

    def validate_token(self: Self, token: Optional[str]):
        if token is None or len(token) <= self.__MIN_TOKEN_LENGTH or token.isspace():
            raise FrogmlLoginException(
                "Authentication with JFrog failed: Only JWT Access Tokens are supported. "
                "Please ensure you are using a valid JWT Access Token."
            )

    @cached(cache=LRUCache(maxsize=10), key=keys.methodkey)
    def __get_jpd_id(self: Self, base_url: str) -> str:
        url: str = urljoin(base_url, "/jfconnect/api/v1/system/jpd_id")
        response: Response = requests.get(url=url, timeout=15, auth=self.get_auth())

        if response.status_code == 200:
            return response.text

        if response.status_code == 401:
            raise FrogmlLoginException(
                "Failed to authenticate with JFrog. Please check your credentials"
            )
        else:
            raise FrogmlLoginException(
                "Failed to authenticate with JFrog. Please check your artifactory configuration"
            )

    @staticmethod
    def __remove_artifactory_path_from_url(artifactory_url: str) -> str:
        # Remove '/artifactory' from the URL
        base_url: str = artifactory_url.replace("/artifactory", "", 1)
        # Remove trailing slash if exists
        return base_url.rstrip("/")
