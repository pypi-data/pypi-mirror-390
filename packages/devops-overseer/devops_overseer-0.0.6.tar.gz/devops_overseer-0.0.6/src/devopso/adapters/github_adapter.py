import devopso.clients.github
from pprint import pformat
from devopso.core.rest_adapter import RestAdapter
from pydantic import StrictInt


class GitHub(RestAdapter):
    """High-level wrapper around the GitHub REST API client.

    This class provides an abstraction on top of the raw OpenAPI-generated
    GitHub client, handling authentication setup and exposing convenience
    methods for interacting with GitHub resources.

    Attributes:
        client (devopso.clients.github.ApiClient): Configured API client
            instance with authentication headers set.
    """

    _DEFAULT_PATH_CONFIGURATION = "resources/configs/clients/github.yml"

    def __init__(self) -> None:
        """Initialize a GitHub REST client instance.

        Loads base configuration from the default config file, initializes
        the underlying OpenAPI GitHub ApiClient and injects authentication
        headers coming from the RestAdapter logic.
        """
        super().__init__(GitHub._DEFAULT_PATH_CONFIGURATION)

        configuration = devopso.clients.github.Configuration(host=self.base_url)
        self.client = devopso.clients.github.ApiClient(configuration)
        self.client.default_headers = self.client.default_headers | self._auth_header

    @staticmethod
    def list_repos(org: str, page: StrictInt, per_page: StrictInt):
        """List repositories for a given GitHub organization.

        This is a convenience wrapper around the GitHub Repos API. It performs
        a paginated request to retrieve repository metadata for a specific org.

        Args:
            org (str): Name of the GitHub organization.
            page (StrictInt): Page index to request (1-based index).
            per_page (StrictInt): Number of repositories per page.

        Returns:
            Any: Parsed API response object returned by the OpenAPI client,
            typically a list of repositories. Returns ``None`` if the
            request fails.

        Logs:
            Debug output of API response on success.
            Error message if the request raises an exception.
        """
        api_response = None
        a = GitHub()
        try:
            api_response = devopso.clients.github.ReposApi(a.client).repos_list_for_org(org, page=page, per_page=per_page)
            a.debug("The response of ReposApi->repos_list_for_org:")
            a.debug(pformat(api_response))
        except Exception as e:
            a.error(f"Exception when calling ReposApi->repos_list_for_org: {e}")
        return api_response
