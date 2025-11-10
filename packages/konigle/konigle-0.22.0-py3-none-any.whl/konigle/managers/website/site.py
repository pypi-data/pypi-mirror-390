from typing import TYPE_CHECKING, Literal, cast

from konigle.managers.base import BaseAsyncManager, BaseSyncManager
from konigle.models.base import BaseResource
from konigle.models.core.site import Site, SiteUpdate

if TYPE_CHECKING:
    from konigle.session import AsyncSession, SyncSession


class BaseSiteManager:
    """Base configuration for Site resource managers."""

    resource_class = Site
    """The resource model class this manager handles."""

    resource_update_class = SiteUpdate
    """The model class used for updating resources."""

    base_path = "/admin/api/shops"
    """The API base path for this resource type."""

    site_documents_base_path = "/admin/api/site-documents"
    """The API base path for site documents."""

    northstar_doc_type = "northstar"
    """Document type for business northstar."""

    business_info_doc_type = "biz_info"
    """Document type for business information."""

    website_info_doc_type = "website_info"
    """Document type for website information."""

    design_system_doc_type = "design_system"
    """Document type for design system."""

    pages_base_path = "/admin/api/pages"
    """The API base path for pages."""


class WebsiteManager(BaseSiteManager, BaseSyncManager):
    """Manager for managing website related information and settings"""

    def __init__(self, session: "SyncSession"):
        super().__init__(session)
        self._site_doc_ids: dict[str, str] = {}

    def list(self, *args, **kwargs):
        raise NotImplementedError(
            "Listing multiple sites is not supported. Use get() to "
            "retrieve the current site."
        )

    def create(self, *args, **kwargs) -> BaseResource:
        raise NotImplementedError(
            "Creating a new site is not supported via SDK. Login to Konigle"
            "admin to create a new site."
        )

    def delete(self, *args, **kwargs) -> bool:
        raise NotImplementedError(
            "Deleting a site is not supported via SDK. Login to Konigle"
            "admin to delete a site."
        )

    def get(self) -> Site:
        """Get a specific for the current site."""
        url = f"{self.base_path}/info"
        response = self._session.get(url)
        return cast(
            Site, self.create_resource(response.json(), is_partial=False)
        )

    def update(self, data: SiteUpdate) -> Site:
        """Update an existing site."""
        # first get the current site info to obtain the site ID
        site = self.get()
        return cast(Site, super().update(site.id, data))

    def get_northstar(self) -> str:
        """
        Get the business northstar content.

        The northstar includes business information, branding, tone, goals,
        target audience etc.

        Returns:
            str: The business northstar content as markdown.
        """
        doc_id = self._get_site_doc_id(self.northstar_doc_type)
        url = f"{self.site_documents_base_path}/{doc_id}"
        response = self._session.get(url)
        response.raise_for_status()
        doc = response.json()
        return doc.get("content", "")

    def set_northstar(self, content: str) -> None:
        """
        Set the business northstar content.

        The northstar includes business information, branding, tone, goals,
        target audience etc.


        Args:
            content (str): The business northstar content as markdown.
        """
        doc_id = self._get_site_doc_id(self.northstar_doc_type)
        url = f"{self.site_documents_base_path}/{doc_id}"
        params = {"content": content}
        response = self._session.patch(url, data=params)
        response.raise_for_status()

    def get_business_info(self) -> str:
        """
        Get the business information content.

        Returns:
            str: The business information content as markdown.
        """
        doc_id = self._get_site_doc_id(self.business_info_doc_type)
        url = f"{self.site_documents_base_path}/{doc_id}"
        response = self._session.get(url)
        response.raise_for_status()
        doc = response.json()
        return doc.get("content", "")

    def set_business_info(self, info: str) -> None:
        """
        Set the business information content.

        Args:
            info (str): The business information content as markdown.
        """
        doc_id = self._get_site_doc_id(self.business_info_doc_type)
        url = f"{self.site_documents_base_path}/{doc_id}"
        params = {"content": info}
        response = self._session.patch(url, data=params)
        response.raise_for_status()

    def get_website_info(self) -> str:
        """
        Get the website information content.

        Returns:
            str: The website information content as markdown.
        """
        doc_id = self._get_site_doc_id(self.website_info_doc_type)
        url = f"{self.site_documents_base_path}/{doc_id}"
        response = self._session.get(url)
        response.raise_for_status()
        doc = response.json()
        return doc.get("content", "")

    def set_website_info(self, info: str) -> None:
        """
        Set the website information content.

        Args:
            info (str): The website information content as markdown.
        """
        doc_id = self._get_site_doc_id(self.website_info_doc_type)

        url = f"{self.site_documents_base_path}/{doc_id}"
        params = {"content": info}
        response = self._session.patch(url, data=params)
        response.raise_for_status()

    def get_design_system(self) -> str:
        """
        Get the design system content.

        Returns:
            str: The design system content as markdown.
        """
        doc_id = self._get_site_doc_id(self.design_system_doc_type)
        url = f"{self.site_documents_base_path}/{doc_id}"
        response = self._session.get(url)
        response.raise_for_status()
        doc = response.json()
        return doc.get("content", "")

    def set_design_system(self, info: str) -> None:
        """
        Set the design system content.

        Args:
            info (str): The design system content as markdown.
        """
        doc_id = self._get_site_doc_id(self.design_system_doc_type)

        url = f"{self.site_documents_base_path}/{doc_id}"
        params = {"content": info}
        response = self._session.patch(url, data=params)
        response.raise_for_status()

    def add_url(
        self, pathname: str, url_type: Literal["page", "folder"] = "page"
    ) -> dict:
        """Add URL to the website.
        This creates nested folders as needed.
        Args:
            pathname (str): The pathname to add.
        Returns:
            dict: Containing type of page and the ID.
        """
        path = f"{self.pages_base_path}/add-url"
        response = self._session.post(
            path, json={"pathname": pathname, "url_type": url_type}
        )
        return response.json()

    def get_url(self, pathname: str, version: str | None = None) -> dict:
        """Get URL details from the website.
        Args:
            pathname (str): The pathname to get.
            version: Page version
        Returns:
            dict: Containing type of page and the ID.
        """
        path = f"{self.pages_base_path}/get-url"
        params = {"pathname": pathname}
        if version:
            params["version"] = version
        response = self._session.get(path, params=params)
        return response.json()

    def _get_site_doc_id(self, type_: str) -> str:
        if type_ in self._site_doc_ids:
            return self._site_doc_ids[type_]

        url = f"{self.site_documents_base_path}/bootstrap"
        response = self._session.post(url, data={"type": type_})
        response.raise_for_status()
        doc = response.json()
        site_doc_id = doc.get("id")
        if site_doc_id:
            self._site_doc_ids[type_] = site_doc_id
        else:
            raise ValueError(f"Site document of type '{type_}' not found")
        return site_doc_id


class AsyncWebsiteManager(BaseSiteManager, BaseAsyncManager):
    """Async Manager for managing website related information and settings"""

    def __init__(self, session: "AsyncSession"):
        super().__init__(session)
        self._site_doc_ids: dict[str, str] = {}

    async def get(
        self,
    ) -> Site:
        """Get a specific for the current site."""
        url = f"{self.base_path}/info"
        response = await self._session.get(url)
        return cast(
            Site, self.create_resource(response.json(), is_partial=False)
        )

    async def update(self, data: SiteUpdate) -> Site:
        """Update an existing site."""
        # first get the current site info to obtain the site ID
        site = await self.get()
        return cast(Site, await super().update(site.id, data))

    async def list(self, *args, **kwargs):
        raise NotImplementedError(
            "Listing multiple sites is not supported. Use get() to "
            "retrieve the current site."
        )

    async def create(self, *args, **kwargs) -> BaseResource:
        raise NotImplementedError(
            "Creating a new site is not supported via SDK. Login to Konigle"
            "admin to create a new site."
        )

    async def delete(self, *args, **kwargs) -> bool:
        raise NotImplementedError(
            "Deleting a site is not supported via SDK. Login to Konigle"
            "admin to delete a site."
        )

    async def get_northstar(self) -> str:
        """
        Get the business northstar content.

        The northstar includes business information, branding, tone, goals,
        target audience etc.

        Returns:
            str: The business northstar content as markdown.
        """
        doc_id = await self._get_site_doc_id(self.northstar_doc_type)
        url = f"{self.site_documents_base_path}/{doc_id}"
        response = await self._session.get(url)
        response.raise_for_status()
        doc = response.json()
        return doc.get("content", "")

    async def set_northstar(self, content: str) -> None:
        """
        Set the business northstar content.

        The northstar includes business information, branding, tone, goals,
        target audience etc.

        Args:
            content (str): The business northstar content as markdown.
        """
        doc_id = await self._get_site_doc_id(self.northstar_doc_type)
        url = f"{self.site_documents_base_path}/{doc_id}"
        params = {"content": content}
        response = await self._session.patch(url, data=params)
        response.raise_for_status()

    async def get_business_info(self) -> str:
        """
        Get the business information content.

        Returns:
            str: The business information content as markdown.
        """
        doc_id = await self._get_site_doc_id(self.business_info_doc_type)
        url = f"{self.site_documents_base_path}/{doc_id}"
        response = await self._session.get(url)
        response.raise_for_status()
        doc = response.json()
        return doc.get("content", "")

    async def set_business_info(self, info: str) -> None:
        """
        Set the business information content.

        Args:
            info (str): The business information content as markdown.
        """
        doc_id = await self._get_site_doc_id(self.business_info_doc_type)
        url = f"{self.site_documents_base_path}/{doc_id}"
        params = {"content": info}
        response = await self._session.patch(url, data=params)
        response.raise_for_status()

    async def get_website_info(self) -> str:
        """
        Get the website information content.

        Returns:
            str: The website information content as markdown.
        """
        doc_id = await self._get_site_doc_id(self.website_info_doc_type)
        url = f"{self.site_documents_base_path}/{doc_id}"
        response = await self._session.get(url)
        response.raise_for_status()
        doc = response.json()
        return doc.get("content", "")

    async def set_website_info(self, info: str) -> None:
        """
        Set the website information content.

        Args:
            info (str): The website information content as markdown.
        """
        doc_id = await self._get_site_doc_id(self.website_info_doc_type)

        url = f"{self.site_documents_base_path}/{doc_id}"
        params = {"content": info}
        response = await self._session.patch(url, data=params)
        response.raise_for_status()

    async def get_design_system(self) -> str:
        """
        Get the design system content.

        Returns:
            str: The design system content as markdown.
        """
        doc_id = await self._get_site_doc_id(self.design_system_doc_type)
        url = f"{self.site_documents_base_path}/{doc_id}"
        response = await self._session.get(url)
        response.raise_for_status()
        doc = response.json()
        return doc.get("content", "")

    async def set_design_system(self, info: str) -> None:
        """
        Set the design system content.

        Args:
            info (str): The design system content as markdown.
        """
        doc_id = await self._get_site_doc_id(self.design_system_doc_type)

        url = f"{self.site_documents_base_path}/{doc_id}"
        params = {"content": info}
        response = await self._session.patch(url, data=params)
        response.raise_for_status()

    async def add_url(
        self, pathname: str, url_type: Literal["page", "folder"] = "page"
    ) -> dict:
        """Add URL to the website.
        This creates nested folders as needed.
        Args:
            pathname (str): The pathname to add.
        Returns:
            dict: Containing type of page and the ID.
        """
        path = f"{self.pages_base_path}/add-url"
        response = await self._session.post(
            path, json={"pathname": pathname, "url_type": url_type}
        )
        return response.json()

    async def get_url(self, pathname: str, version: str | None = None) -> dict:
        """Get URL details from the website.
        Args:
            pathname (str): The pathname to get.
            version: Page version
        Returns:
            dict: Containing type of page and the ID.
        """
        path = f"{self.pages_base_path}/get-url"
        params = {"pathname": pathname}
        if version:
            params["version"] = version
        response = await self._session.get(path, params=params)
        return response.json()

    async def _get_site_doc_id(self, type_: str) -> str:
        if type_ in self._site_doc_ids:
            return self._site_doc_ids[type_]

        url = f"{self.site_documents_base_path}/bootstrap"
        response = await self._session.post(url, data={"type": type_})
        response.raise_for_status()
        doc = response.json()
        site_doc_id = doc.get("id")
        if site_doc_id:
            self._site_doc_ids[type_] = site_doc_id
        else:
            raise ValueError(f"Site document of type '{type_}' not found")
        return site_doc_id
