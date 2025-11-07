from datetime import datetime

from devopso.adapters.confluence_cloud_adapter import ConfluenceCloud
from devopso.adapters.jira_cloud_adapter import JiraCloud
from devopso.adapters.jira_teams_adapter import JiraTeams
from devopso.clients.jira_cloud.models.user import User
from devopso.core.logging import ConfiguredLogger


class Atlassian(ConfiguredLogger):
    """High-level adapter providing convenience methods for retrieving
    user and group data from Atlassian (Jira Cloud) APIs.

    This class leverages the `JiraCloud` adapter to aggregate user
    and teammate information across groups, while inheriting structured
    logging capabilities from `ConfiguredLogger`.

    Attributes:
        _DEFAULT_PATH_CONFIGURATION (str): Default path to the adapter's configuration file.
    """

    _DEFAULT_PATH_CONFIGURATION = "resources/configs/adapters/atlassian.yml"

    def __init__(self) -> None:
        """Initialize the Atlassian adapter.

        Loads the logger configuration defined in the adapter's configuration file.
        """
        super().__init__(Atlassian._DEFAULT_PATH_CONFIGURATION)

    @staticmethod
    def get_current_user_teammates(ignore_groups: list[str]) -> dict[str, User]:
        """Retrieve all teammates of the currently authenticated Jira user.

        Args:
            ignore_groups (list[str]): List of group names to exclude from the search.

        Returns:
            dict[str, User]: A dictionary mapping display names to `User` objects
                representing the teammates of the current user, excluding those
                in ignored groups.
        """
        return Atlassian.get_user_teammates(JiraCloud.get_myself().account_id, ignore_groups)

    @staticmethod
    def get_user_teammates(user_id: str, ignore_groups: list[str]) -> dict[str, User]:
        """Retrieve all teammates of a given Jira user by their account ID.

        This method gathers all users who share at least one group
        with the specified user, excluding groups listed in `ignore_groups`.

        Args:
            user_id (str): The Jira account ID of the user whose teammates should be retrieved.
            ignore_groups (list[str]): List of group names to exclude from the search.

        Returns:
            dict[str, User]: A dictionary mapping display names to `User` objects
                representing the teammates of the given user.
        """
        users = {}
        user_account = JiraCloud.get_user_by_account_id(user_id)
        for group in user_account.groups.items:
            if group.name not in ignore_groups:
                users = users | Atlassian.get_group_accounts(group.group_id)
        return users

    @staticmethod
    def get_group_accounts(group_id: str) -> dict[str, User]:
        """Retrieve all user accounts belonging to a specific Jira group.

        Args:
            group_id (str): The unique identifier of the Jira group.

        Returns:
            dict[str, User]: A dictionary mapping display names to `User` objects
                representing all members of the specified group.
        """
        users = {}
        group_members = JiraCloud.get_users_from_group_id(group_id)
        for account_x in group_members.values:
            users[account_x.display_name] = account_x
        return users

    @staticmethod
    def update_or_create_confluence_page(space_key: str, parent_title: str, title: str, body: str, representation: str) -> None:
        """Create or update a Confluence page in the specified space.

        If the page does not exist, it is created under the provided parent page.
        If the page already exists, its content is updated to the new body and title.

        Args:
            space_key (str): The key of the Confluence space where the page resides.
            parent_title (str): The title of the parent page to attach a new page under if creation is needed.
            title (str): The title of the page to update or create.
            body (str): The Confluence Wiki or Storage formatted content of the page.
            representation (str): The content representation format (e.g., 'storage' or 'wiki').

        Returns:
            None: The function logs progress and errors internally via `ConfiguredLogger`.
        """
        a = Atlassian()

        spaces_found = ConfluenceCloud.get_spaces([space_key])
        if spaces_found.results is None or len(spaces_found.results) == 0:
            a.error("No space matches the specs for updating.")
            return

        a.info("fetching page")
        pages_found = ConfluenceCloud.get_pages_in_space(int(spaces_found.results[0].id), title)
        if pages_found.results is None or len(pages_found.results) == 0:
            parent_found = ConfluenceCloud.get_pages_in_space(int(spaces_found.results[0].id), parent_title)
            if parent_found.results is None or len(parent_found.results) == 0:
                a.error("No page or parent page matches the specs for updating.")
                return
            a.info("creating page")
            ConfluenceCloud.create_page(spaces_found.results[0].id, title, representation, " ", parent_found.results[0].id)

            a.info("fetching page again")
            pages_found = ConfluenceCloud.get_pages_in_space(int(spaces_found.results[0].id), title)
            if pages_found.results is None or len(pages_found.results) == 0:
                a.error("creation failed")
                return

        a.info("updating page")
        ConfluenceCloud.update_page(pages_found.results[0].id, title, representation, body, int(pages_found.results[0].version.number) + 1)

    @staticmethod
    def snapshot_confluence_page(space_key: str, page_title: str, add_time: bool = False) -> None:
        """Create a snapshot (version copy) of an existing Confluence page.

        This method duplicates a given Confluence page under the same parent,
        using the current date (and optionally time) in the title to distinguish it.
        Useful for versioned backups of periodic reports or dashboards.

        Args:
            space_key (str): The key of the Confluence space containing the page.
            page_title (str): The title of the page to snapshot.
            add_time (bool, optional): Whether to append the current time (HH-MM)
                to the snapshot title. Defaults to False.

        Returns:
            None: The function logs progress and errors internally via `ConfiguredLogger`.
        """
        a = Atlassian()

        spaces_found = ConfluenceCloud.get_spaces([space_key])
        if spaces_found.results is None or len(spaces_found.results) == 0:
            a.error("No space matches the specs for updating.")
            return

        a.info("fetching page")
        pages_found = ConfluenceCloud.get_pages_in_space(int(spaces_found.results[0].id), page_title)
        if pages_found.results is None or len(pages_found.results) == 0:
            a.error("No page or parent page matches the specs for updating.")
            return

        today = datetime.today()
        snap_title = f"{page_title} {today.year:04d}-{today.month:02d}-{today.day:02d}"
        if add_time is True:
            snap_title = f"{snap_title}-{today.hour:02d}-{today.minute:02d}"

        page_with_body = ConfluenceCloud.get_page_by_id(pages_found.results[0].id)
        Atlassian.update_or_create_confluence_page(
            space_key, page_title, snap_title, page_with_body.body.storage.value, page_with_body.body.storage.representation
        )

    @staticmethod
    def get_team_members(org_id: str, team_name: str) -> dict[str, User]:
        """Retrieve all members of a specific team in Jira.

        Given an organization ID and a team name, this method finds the
        matching team and returns a dictionary mapping display names to
        `User` objects for all its members.

        Args:
            org_id (str): The organization identifier under which the team is defined.
            team_name (str): The display name of the team for which members are requested.

        Returns:
            dict[str, User]: A dictionary mapping display names to `User` objects
                representing all members of the specified team.
        """
        all_teams = JiraTeams.get_teams(org_id)

        users: dict[str, User] = {}
        for raw_team in all_teams.entities:
            if raw_team.display_name == team_name:
                team_members = JiraTeams.get_team_members(org_id, raw_team.team_id)
                for team_member_id in team_members.results:
                    team_member_account = JiraCloud.get_user_by_account_id(team_member_id.account_id)
                    users[team_member_account.display_name] = team_member_account
        return users
