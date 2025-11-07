from pprint import pformat
from typing import Any

import devopso.clients.jira_teams
from devopso.clients.jira_teams.models.public_api_fetch_response_public_api_membership_account_id import PublicApiFetchResponsePublicApiMembershipAccountId
from devopso.clients.jira_teams.models.public_api_membership_fetch_payload import PublicApiMembershipFetchPayload
from devopso.clients.jira_teams.models.public_api_team_pagination_result import PublicApiTeamPaginationResult
from devopso.core.rest_adapter import RestAdapter


class JiraTeams(RestAdapter):
    """Adapter for interacting with the Jira Teams public API.

    Provides methods to query teams, get a specific team and fetch team members
    using the `devopso.clients.jira_teams` client library.
    """

    _DEFAULT_PATH_CONFIGURATION = "resources/configs/clients/jira-teams.yml"

    def __init__(self) -> None:
        """Initialise the JiraTeams REST adapter.

        Loads configuration via the RestAdapter base class and sets up
        the Jira Teams client with authentication headers.
        """
        super().__init__(JiraTeams._DEFAULT_PATH_CONFIGURATION)
        configuration = devopso.clients.jira_teams.Configuration(host=self.base_url)
        self.client = devopso.clients.jira_teams.ApiClient(configuration)
        self.client.default_headers = self.client.default_headers | self._auth_header

    @staticmethod
    def get_teams(org_id: str, site_id: str | None = None, size: int | None = None, cursor: str | None = None) -> PublicApiTeamPaginationResult:
        """Query all teams in an organisation (with optional pagination).

        Args:
            org_id (str): Identifier of the organisation for which to list teams.
            site_id (str | None): Optional site identifier to filter teams.
            size (int | None): Optional maximum number of results to return.
            cursor (str | None): Optional pagination cursor to fetch the next page.

        Returns:
            PublicApiTeamPaginationResult: The paginated result containing teams.
        """
        api_response = None
        a = JiraTeams()
        try:
            api_response = devopso.clients.jira_teams.TeamsPublicAPIApi(a.client).query_teams(org_id, site_id=site_id, size=size, cursor=cursor)
            a.debug("The response of JiraTeams->get_teams:")
            a.debug(pformat(api_response))
        except Exception as e:
            a.error("Exception when calling JiraTeams->get_teams: %s" % e)
        return api_response

    @staticmethod
    def get_team(org_id: str, team_id: str, site_id: str | None = None) -> Any:
        """Get details of a single team by its ID.

        Args:
            org_id (str): Identifier of the organisation where the team resides.
            team_id (str): Identifier of the team to retrieve.
            site_id (str | None): Optional site identifier if needed.

        Returns:
            Any: The API model representing the team if successful, otherwise None.
        """
        api_response = None
        a = JiraTeams()
        try:
            api_response = devopso.clients.jira_teams.TeamsPublicAPIApi(a.client).get_team(org_id, team_id, site_id=site_id)
            a.debug("The response of JiraTeams->get_team:")
            a.debug(pformat(api_response))
        except Exception as e:
            a.error("Exception when calling JiraTeams->get_team: %s" % e)
        return api_response

    @staticmethod
    def get_team_members(
        org_id: str, team_id: Any, site_id: str | None = None, public_api_membership_fetch_payload: PublicApiMembershipFetchPayload | None = None
    ) -> PublicApiFetchResponsePublicApiMembershipAccountId:
        """Fetch the members of a given team.

        Args:
            org_id (str): Identifier of the organisation.
            team_id (Any): Identifier of the team whose members you want to retrieve.
            site_id (str | None): Optional site identifier to filter the request.
            public_api_membership_fetch_payload (PublicApiMembershipFetchPayload | None): Optional payload
                to modulate membership fetch (for example filter by account id or other criteria).

        Returns:
            PublicApiFetchResponsePublicApiMembershipAccountId:
                The API response containing the membership account IDs of the team, or None if error occurred.
        """
        api_response = None
        a = JiraTeams()
        try:
            api_response = devopso.clients.jira_teams.TeamsMembersPublicAPIApi(a.client).fetch_members(
                org_id, team_id, site_id=site_id, public_api_membership_fetch_payload=public_api_membership_fetch_payload
            )
            a.debug("The response of JiraTeams->get_team_members:")
            a.debug(pformat(api_response))
        except Exception as e:
            a.error("Exception when calling JiraTeams->get_team_members: %s" % e)
        return api_response
