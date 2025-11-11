from __future__ import annotations

import base64
from dataclasses import dataclass
from pathlib import Path

import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

from devopso.core.configuration import Configuration
from devopso.core.configuration import Error as ConfigurationError
from devopso.core.logging import ConfiguredLogger


@dataclass(frozen=True)
class Auth:
    """Authentication data container.

    Attributes:
        email (str): Email or login for API authentication.
        api_token (str): Raw API token (unencoded). This will be encoded or
            transformed depending on the authentication scheme used by the
            adapter (e.g., Basic or Bearer auth).
    """

    email: str
    api_token: str  # unencoded


class Error(Exception):
    """API-level error raised when a REST request fails.

    Attributes:
        status (int): HTTP status code returned by the API.
        url (str): URL that triggered the error.
        body (str): Server response body, truncated for readability.
    """

    def __init__(self, status: int, url: str, body: str):
        """
        Args:
            status (int): HTTP status code.
            url (str): Request URL.
            body (str): Full response body; only first 500 chars will be shown in the exception.
        """
        super().__init__(f"devopso API error {status} for {url}: {body[:500]}")
        self.status = status
        self.url = url
        self.body = body


class RestAdapter(ConfiguredLogger):
    """Base class for REST API adapters in devopso.

    This class provides:
    - Loading of adapter-specific configuration
    - Credential resolution and authentication header construction
    - An HTTP `requests.Session` with retry logic
    - Standardised logging inherited from `ConfiguredLogger`

    Attributes:
        base_url (str): Base URL of the remote API, normalized without trailing slash.
        timeout_s (float): Default request timeout in seconds.
        session (requests.Session): HTTP session with retry policy configured.
        _auth_header (dict): Authorization headers generated from credentials.
        _base_headers (dict): Base HTTP headers included in every request.
    """

    def __init__(self, config_path: str) -> None:
        """Initialize the REST adapter and prepare authenticated HTTP session.

        Loads configuration (endpoint, headers, credentials path, retry
        settings, etc.) from the provided config path, then configures an
        HTTP session with retry strategy and authentication headers.

        Args:
            config_path (str): Path to YAML configuration file defining API client behavior.
        """
        super().__init__(config_path)

        base_url = self._conf["base-url"]
        user_agent = self._conf["user-agent"]
        timeout_s = self._conf["timeout"]
        max_retries = self._conf["max-retries"]
        backoff_factor = self._conf["backoff-factor"]
        extra_headers = self._conf["extra-headers"]

        if base_url.endswith("/"):
            base_url = base_url[:-1]
        self.base_url = base_url
        self.timeout_s = timeout_s

        self._read_credentials()

        # Configure HTTP session with retry logic
        self.session = requests.Session()
        retry = Retry(
            total=max_retries,
            read=max_retries,
            connect=max_retries,
            backoff_factor=backoff_factor,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=("GET", "POST", "PUT", "DELETE"),
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

        self._base_headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": user_agent,
        }
        if extra_headers:
            self._base_headers.update(extra_headers)

    def _read_credentials(self) -> None:
        """Resolve and load API credentials from the configuration.

        Supports multiple authentication schemes (Basic, Bearer) via YAML config.
        Expected config structure:

        ```yaml
        credentials:
          path: ~/.config/devopso/credentials.yml
          app: github
        ```

        Raises:
            ConfigurationError: If config is missing credentials, authentication
                type, or expected fields like login/api-token.
        """
        if "credentials" in self._conf:
            creds_conf = self._conf["credentials"]
            app_credentials = {}
            credentials = {}

            # Load global credentials file if defined
            if "path" in creds_conf:
                app_credentials = Configuration.read_configuration(Path(creds_conf["path"]).expanduser().resolve(strict=False))

            if not app_credentials:
                raise ConfigurationError(self._conf_path, "missing app credentials configuration")

            # Select app-specific credentials block
            if "app" in creds_conf and creds_conf["app"] in app_credentials["apps"]:
                credentials = app_credentials["apps"][creds_conf["app"]]

            if not credentials:
                raise ConfigurationError(self._conf_path, "missing credentials configuration")

            if "auth-type" not in credentials:
                raise ConfigurationError(self._conf_path, "missing authentication type")

            # Basic Auth
            if credentials["auth-type"] == "Basic":
                raw = f"{credentials['login']}:{credentials['api-token']}".encode("utf-8")
                b64 = base64.b64encode(raw).decode("utf-8")
                self._auth_header = {"Authorization": f"Basic {b64}"}

            # Bearer Token
            if credentials["auth-type"] == "Bearer":
                self._auth_header = {"Authorization": f"Bearer {credentials['api-token']}"}
