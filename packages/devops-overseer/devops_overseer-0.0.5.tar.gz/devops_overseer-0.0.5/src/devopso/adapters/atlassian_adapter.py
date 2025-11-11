from datetime import datetime

from devopso.adapters.confluence_cloud_adapter import ConfluenceCloud
from devopso.adapters.jira_cloud_adapter import JiraCloud
from devopso.adapters.jira_teams_adapter import JiraTeams
from devopso.clients.confluence_cloud.models.create_page200_response import CreatePage200Response
from devopso.clients.jira_cloud.models.user import User
from devopso.core.logging import ConfiguredLogger


class Atlassian(ConfiguredLogger):
    """
    High-level aggregator adapter providing convenience helper functions
    over Jira Cloud, Jira Teams, and Confluence Cloud APIs.

    This class centralizes common operations such as:
      • retrieving teammates by group
      • fetching group accounts
      • creating or updating Confluence pages
      • generating snapshots of existing Confluence pages
      • resolving all members of a Jira team

    Logging is inherited from `ConfiguredLogger` and uses the adapter-specific
    configuration file defined in `_DEFAULT_PATH_CONFIGURATION`.
    """

    _DEFAULT_PATH_CONFIGURATION = "resources/configs/adapters/atlassian.yml"

    def __init__(self) -> None:
        """Initialize the Atlassian helper adapter.

        Loads logging configuration and prepares structured logger.
        """
        super().__init__(Atlassian._DEFAULT_PATH_CONFIGURATION)

    @staticmethod
    def get_current_user_teammates(ignore_groups: list[str]) -> dict[str, User]:
        """Return teammates of the currently authenticated Jira user.

        Teammates are defined as users sharing at least one group with
        the current user, except for groups listed in `ignore_groups`.

        Args:
            ignore_groups (list[str]): Group names to exclude from search.

        Returns:
            dict[str, User]: Mapping of display name → User object.
        """
        return Atlassian.get_user_teammates(JiraCloud.get_myself().account_id, ignore_groups)

    @staticmethod
    def get_user_teammates(user_id: str, ignore_groups: list[str]) -> dict[str, User]:
        """Retrieve all teammates of a user based on shared Jira Cloud groups.

        Args:
            user_id (str): The Jira account ID to search teammates for.
            ignore_groups (list[str]): List of group names to skip.

        Returns:
            dict[str, User]: Mapping of display name → User objects for teammates.
        """
        users = {}
        user_account = JiraCloud.get_user_by_account_id(user_id)
        for group in user_account.groups.items:
            if group.name not in ignore_groups:
                users = users | Atlassian.get_group_accounts(group.group_id)
        return users

    @staticmethod
    def get_group_accounts(group_id: str) -> dict[str, User]:
        """Retrieve all users belonging to a specific Jira group.

        Args:
            group_id (str): Unique group identifier.

        Returns:
            dict[str, User]: Mapping of display name → User objects.
        """
        users = {}
        group_members = JiraCloud.get_users_from_group_id(group_id)
        for account_x in group_members.values:
            users[account_x.display_name] = account_x
        return users

    @staticmethod
    def update_or_create_confluence_page(space_key: str, parent_title: str, title: str, body: str, representation: str) -> CreatePage200Response:
        """Create or update a page in a Confluence space.

        If a page with the given title does not exist, it is created under
        the specified parent page. If it exists, the method updates its
        title, body and version.

        Args:
            space_key (str): Confluence space key (e.g., "ENG").
            parent_title (str): Title of the parent page if creation is needed.
            title (str): Title of the page to update or create.
            body (str): Page body content (storage or wiki format).
            representation (str): Content representation type (e.g., "storage").

        Returns:
            CreatePage200Response | None: Response of page update/creation,
            or None if an error occurred.
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
        return ConfluenceCloud.update_page(pages_found.results[0].id, title, representation, body, int(pages_found.results[0].version.number) + 1)

    @staticmethod
    def snapshot_date_confluence_page(space_key: str, page_title: str, add_time: bool = False) -> CreatePage200Response:
        """Create a date-based snapshot of an existing Confluence page.

        The snapshot title will be:
            "<page_title> YYYY-MM-DD"
        and optionally:
            "<page_title> YYYY-MM-DD-HH-MM"

        Args:
            space_key (str): Confluence space key.
            page_title (str): Title of the page to snapshot.
            add_time (bool): Whether to append hour/minute to the snapshot name.

        Returns:
            CreatePage200Response | None: Snapshot creation response, or None.
        """
        today = datetime.today()
        snap_title = f"{page_title} {today.year:04d}-{today.month:02d}-{today.day:02d}"
        if add_time is True:
            snap_title = f"{snap_title}-{today.hour:02d}-{today.minute:02d}"
        return Atlassian.snapshot_confluence_page(space_key, page_title, snap_title)

    @staticmethod
    def snapshot_confluence_page(space_key: str, page_title: str, snapshot_name) -> CreatePage200Response:
        """Create a snapshot of a Confluence page using a provided snapshot title.

        Args:
            space_key (str): Confluence space key.
            page_title (str): Title of the source page to snapshot.
            snapshot_name (str): New title assigned to the snapshot page.

        Returns:
            CreatePage200Response | None: Response from snapshot creation,
            or None on failure.
        """
        a = Atlassian()

        spaces_found = ConfluenceCloud.get_spaces([space_key])
        if spaces_found.results is None or len(spaces_found.results) == 0:
            a.error("No space matches the specs for updating.")
            return None

        a.info("fetching page")
        pages_found = ConfluenceCloud.get_pages_in_space(int(spaces_found.results[0].id), page_title)
        if pages_found.results is None or len(pages_found.results) == 0:
            a.error("No page or parent page matches the specs for updating.")
            return None

        page_with_body = ConfluenceCloud.get_page_by_id(pages_found.results[0].id)
        return Atlassian.update_or_create_confluence_page(
            space_key, page_title, snapshot_name, page_with_body.body.storage.value, page_with_body.body.storage.representation
        )

    @staticmethod
    def get_team_members(org_id: str, team_name: str) -> dict[str, User]:
        """Retrieve all members belonging to a Jira Team inside an organization.

        Args:
            org_id (str): Organization identifier.
            team_name (str): Display name of the team.

        Returns:
            dict[str, User]: Mapping of display name → User objects for team members.
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
