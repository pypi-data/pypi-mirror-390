from pprint import pformat

from devopso.core.rest_adapter import RestAdapter
import devopso.clients.confluence_cloud
from devopso.clients.confluence_cloud.models import CreatePageRequest, PageBodyWrite, UpdatePageRequestVersion


class ConfluenceCloud(RestAdapter):
    """Wrapper class around the Confluence Cloud REST API client.

    This class provides simplified static helper methods to interact with
    Confluence Cloud REST APIs through the generated OpenAPI client. It also
    integrates with the `RestAdapter` base class for unified logging,
    authentication, and configuration handling.

    The configuration file path used by default is:
    `resources/configs/clients/confluence-cloud.yml`.
    """

    _DEFAULT_PATH_CONFIGURATION = "resources/configs/clients/confluence-cloud.yml"

    def __init__(self) -> None:
        """Initialize the Confluence Cloud API client."""
        super().__init__(ConfluenceCloud._DEFAULT_PATH_CONFIGURATION)

        configuration = devopso.clients.confluence_cloud.Configuration(host=self.base_url)
        self.client = devopso.clients.confluence_cloud.ApiClient(configuration)
        self.client.default_headers = self.client.default_headers | self._auth_header

    @staticmethod
    def get_pages_in_space(space_id: int, page_title: str):
        """Retrieve a list of pages within a Confluence space filtered by title.

        Args:
            space_id (int): The unique identifier of the Confluence space.
            page_title (str): The page title to filter results by.

        Returns:
            MultiEntityResultPage | None: The API response containing pages
            matching the title, or None if an exception occurred.
        """
        api_response = None
        a = ConfluenceCloud()
        try:
            api_response = devopso.clients.confluence_cloud.PageApi(a.client).get_pages_in_space(space_id, title=page_title)
            a.debug("The response of ConfluenceCloud->get_pages_in_space:")
            a.debug(pformat(api_response))
        except Exception as e:
            a.error(f"Exception when calling ConfluenceCloud->get_pages_in_space: {e}")
        return api_response

    @staticmethod
    def get_spaces(space_keys: list[str]):
        """Retrieve information about one or more Confluence spaces.

        Args:
            space_keys (list[str]): A list of space keys identifying the spaces to fetch.

        Returns:
            MultiEntityResultPage | None: The API response containing the requested
            spaces, or None if an exception occurred.
        """
        api_response = None
        a = ConfluenceCloud()
        try:
            api_response = devopso.clients.confluence_cloud.SpaceApi(a.client).get_spaces(keys=space_keys)
            a.debug("The response of ConfluenceCloud->get_spaces:")
            a.debug(pformat(api_response))
        except Exception as e:
            a.error(f"Exception when calling ConfluenceCloud->get_spaces: {e}")
        return api_response

    @staticmethod
    def get_page_by_id(page_id):
        """Retrieve a Confluence page by its numeric identifier.

        Args:
            page_id (int | str): The unique page identifier.

        Returns:
            dict | None: The page data as returned by the API, or None if an error occurred.
        """
        api_response = None
        a = ConfluenceCloud()
        try:
            api_response = devopso.clients.confluence_cloud.PageApi(a.client).get_page_by_id(int(page_id), body_format="storage")
            a.debug("The response of ConfluenceCloud->get_page_by_id:")
            a.debug(pformat(api_response))
        except Exception as e:
            a.error(f"Exception when calling ConfluenceCloud->get_page_by_id: {e}")
        return api_response

    @staticmethod
    def create_page(space_id: str, title: str, representation: str, wiki_body: str, parent_id: str):
        """Create a new Confluence page.

        Args:
            space_id (str): The space ID where the page should be created.
            title (str): The title of the new page.
            representation (str): The content representation format (e.g. 'storage' or 'wiki').
            wiki_body (str): The body content of the page in the given representation.
            parent_id (str): The ID of the parent page (for hierarchy).

        Returns:
            CreatePage200Response | None: The created page response object, or None if an error occurred.
        """
        api_response = None
        a = ConfluenceCloud()
        try:
            create_page_request = CreatePageRequest(
                title=title,
                space_id=space_id,
                parent_id=parent_id,
                body=PageBodyWrite(representation=representation, value=wiki_body),
            )

            embedded = False
            private = False
            root_level = False

            api_response = devopso.clients.confluence_cloud.PageApi(a.client).create_page(
                create_page_request, embedded=embedded, private=private, root_level=root_level
            )
            a.debug("The response of ConfluenceCloud->create_page:")
            a.debug(pformat(api_response))
        except Exception as e:
            a.error(f"Exception when calling ConfluenceCloud->create_page: {e}")
        return api_response

    @staticmethod
    def update_page(page_id: str, new_title: str, representation: str, new_body: str, new_version: int):
        """Update an existing Confluence page.

        Args:
            page_id (str): The ID of the page to update.
            new_title (str): The updated page title.
            representation (str): The content representation format (e.g. 'storage' or 'wiki').
            new_body (str): The updated body content of the page.
            new_version (int): The new version number for the update.

        Returns:
            dict | None: The updated page response from the API, or None if an error occurred.
        """
        api_response = None
        a = ConfluenceCloud()
        try:
            update_page_request = devopso.clients.confluence_cloud.UpdatePageRequest(
                id=page_id,
                body=PageBodyWrite(representation=representation, value=new_body),
                title=new_title,
                status="current",
                version=UpdatePageRequestVersion(
                    number=new_version,
                    message="automatic update",
                ),
            )

            api_response = devopso.clients.confluence_cloud.PageApi(a.client).update_page(int(page_id), update_page_request)
            a.debug("The response of ConfluenceCloud->update_page:")
            a.debug(pformat(api_response))
        except Exception as e:
            a.error(f"Exception when calling ConfluenceCloud->update_page: {e}")
        return api_response
