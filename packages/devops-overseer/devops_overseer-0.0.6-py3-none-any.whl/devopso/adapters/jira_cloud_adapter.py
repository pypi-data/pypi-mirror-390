from pprint import pformat

import devopso.clients.jira_cloud
from devopso.core.rest_adapter import RestAdapter


class JiraCloud(RestAdapter):
    """Adapter class for interacting with the Jira Cloud REST API.

    This class wraps the generated `devopso.clients.jira_cloud` client,
    automatically configuring authentication and providing simplified
    static methods for common operations such as retrieving user information
    and groups.

    Attributes:
        _DEFAULT_PATH_CONFIGURATION (str): Default configuration file path for Jira Cloud client setup.
        client (devopso.clients.jira_cloud.ApiClient): Configured API client instance used for API calls.
    """

    _DEFAULT_PATH_CONFIGURATION = "resources/configs/clients/jira-cloud.yml"

    def __init__(self) -> None:
        """Initializes the JiraCloud adapter.

        Loads the REST adapter configuration, initializes the Jira Cloud
        API client using the configured base URL and authentication headers.
        """
        super().__init__(JiraCloud._DEFAULT_PATH_CONFIGURATION)

        configuration = devopso.clients.jira_cloud.Configuration(host=self.base_url)
        self.client = devopso.clients.jira_cloud.ApiClient(configuration)
        self.client.default_headers = self.client.default_headers | self._auth_header

    @staticmethod
    def get_myself():
        """Retrieve information about the currently authenticated Jira user.

        Returns:
            devopso.clients.jira_cloud.models.UserDetails | None:
                The user details object returned by the API, or ``None`` if an exception occurred.

        Logs:
            - Debug information with the formatted API response on success.
            - Error message if the API call fails.
        """
        api_response = None
        a = JiraCloud()
        try:
            api_response = devopso.clients.jira_cloud.MyselfApi(a.client).get_current_user(expand="groups,applicationRoles")
            a.debug("The response of JiraCloud->get_myself:")
            a.debug(pformat(api_response))
        except Exception as e:
            a.error("Exception when calling JiraCloud->get_myself: %s" % e)
        return api_response

    @staticmethod
    def get_user_by_account_id(account_id: str):
        """Retrieve user information by Jira account ID.

        Args:
            account_id (str): The unique account ID of the user to retrieve.

        Returns:
            devopso.clients.jira_cloud.models.User | None:
                The user object corresponding to the given account ID, or ``None`` if an error occurred.

        Logs:
            - Debug information with the formatted API response on success.
            - Error message if the API call fails.
        """
        api_response = None
        a = JiraCloud()
        try:
            api_response = devopso.clients.jira_cloud.UsersApi(a.client).get_user(account_id=account_id, expand="groups")
            a.debug("The response of JiraCloud->get_user_by_account_id:")
            a.debug(pformat(api_response))
        except Exception as e:
            a.error("Exception when calling JiraCloud->get_user_by_account_id: %s" % e)
        return api_response

    @staticmethod
    def get_users_from_group_id(group_id: str):
        """Retrieve all users belonging to a specific Jira group.

        Args:
            group_id (str): The unique identifier of the Jira group.

        Returns:
            devopso.clients.jira_cloud.models.PageBeanUserDetails | None:
                A paginated response containing user details, or ``None`` if an error occurred.

        Logs:
            - Debug information with the formatted API response on success.
            - Error message if the API call fails.
        """
        api_response = None
        a = JiraCloud()
        try:
            api_response = devopso.clients.jira_cloud.GroupsApi(a.client).get_users_from_group(group_id=group_id)
            a.debug("The response of JiraCloud->get_users_from_group_id:")
            a.debug(pformat(api_response))
        except Exception as e:
            a.error("Exception when calling JiraCloud->get_users_from_group_id: %s" % e)
        return api_response

    @staticmethod
    def add_user_to_group(group_id: str, account_id: str):
        """Add a Jira user to a specified group.

        This method wraps the Jira Cloud REST API operation to add a user
        to a group using the Groups API. It logs the API response and any
        encountered errors.

        Args:
            group_id (str): The identifier of the target Jira group.
            account_id (str): The account ID of the user to add.

        Returns:
            Any: The raw API response object returned by Jira Cloud, or None
                if an error occurred.
        """
        api_response = None
        a = JiraCloud()
        try:
            update_user_to_group_bean = {"accountId": account_id}
            api_response = devopso.clients.jira_cloud.GroupsApi(a.client).add_user_to_group(update_user_to_group_bean, group_id=group_id)
            a.debug("The response of JiraCloud->add_user_to_group:")
            a.debug(pformat(api_response))
        except Exception as e:
            a.error("Exception when calling JiraCloud->add_user_to_group: %s" % e)
        return api_response

    @staticmethod
    def remove_user_to_group(group_id: str, account_id: str):
        """Remove a Jira user from a specified group.

        This method wraps the Jira Cloud REST API operation to remove a user
        from a group using the Groups API. It logs the API response and any
        encountered errors.

        Args:
            group_id (str): The identifier of the target Jira group.
            account_id (str): The account ID of the user to remove.

        Returns:
            Any: The raw API response object returned by Jira Cloud, or None
                if an error occurred.
        """
        api_response = None
        a = JiraCloud()
        try:
            api_response = devopso.clients.jira_cloud.GroupsApi(a.client).remove_user_from_group(account_id, group_id=group_id)
            a.debug("The response of JiraCloud->remove_user_from_group:")
            a.debug(pformat(api_response))
        except Exception as e:
            a.error("Exception when calling JiraCloud->remove_user_from_group: %s" % e)
        return api_response
