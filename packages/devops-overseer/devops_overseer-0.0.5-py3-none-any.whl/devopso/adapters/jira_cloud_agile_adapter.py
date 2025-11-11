import devopso.clients.jira_cloud_agile
from devopso.core.rest_adapter import RestAdapter


class JiraAgileCloud(RestAdapter):
    """
    Adapter for the Jira Cloud Agile REST API.

    Provides a simplified interface for accessing Jira Agile resources such as
    boards and board configurations. The adapter extends `RestAdapter` to
    automatically handle base URL configuration and authentication headers.
    """

    _DEFAULT_PATH_CONFIGURATION = "resources/configs/clients/jira-cloud-agile.yml"

    def __init__(self) -> None:
        """
        Initialize the Jira Agile Cloud client adapter.

        This sets up the Jira Agile API client using the base URL and
        authentication header defined in the inherited RestAdapter
        configuration.
        """
        super().__init__(JiraAgileCloud._DEFAULT_PATH_CONFIGURATION)
        configuration = devopso.clients.jira_cloud_agile.Configuration(host=self.base_url)
        self.client = devopso.clients.jira_cloud_agile.ApiClient(configuration)
        self.client.default_headers = self.client.default_headers | self._auth_header

    @staticmethod
    def get_kanban_board(board_id: int):
        """
        Retrieve information about a specific Kanban board.

        Args:
            board_id (int): The unique identifier of the Jira Agile board.

        Returns:
            Any | None: The board information returned by the Jira Agile API
            if successful, otherwise None.

        Raises:
            Exception: If the API request fails or cannot be completed.
        """
        api_response = None
        try:
            api_response = devopso.clients.jira_cloud_agile.BoardApi(JiraAgileCloud().client).get_board(board_id)
        except Exception as e:
            print("Exception when calling BoardApi->get_board: %s\n" % e)
        return api_response

    @staticmethod
    def get_kanban_board_configuration(board_id: int):
        """
        Retrieve configuration details for a specific Kanban board.

        Includes information such as columns, estimation settings, and ranking
        configuration defined for the board.

        Args:
            board_id (int): The unique identifier of the Jira Agile board.

        Returns:
            Any | None: The board configuration returned by the Jira Agile API
            if successful, otherwise None.

        Raises:
            Exception: If the API request fails or cannot be completed.
        """
        api_response = None
        try:
            api_response = devopso.clients.jira_cloud_agile.BoardApi(JiraAgileCloud().client).get_configuration(board_id)
        except Exception as e:
            print("Exception when calling BoardApi->get_board: %s\n" % e)
        return api_response
