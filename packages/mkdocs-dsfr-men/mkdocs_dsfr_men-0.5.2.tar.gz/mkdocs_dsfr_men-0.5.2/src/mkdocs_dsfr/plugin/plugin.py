"""MkDocs DSFRPlugin."""

import re
from typing import Match, Optional
from urllib.parse import urlparse

from mkdocs.config.defaults import MkDocsConfig
from mkdocs.plugins import BasePlugin
from mkdocs.structure.files import Files
from mkdocs.structure.pages import Page
from mkdocs_dsfr.plugin.config import DSFRConfig
from mkdocs_dsfr.plugin.link import DSFRLink
from mkdocs_dsfr.plugin.media import DSFRMedia
from mkdocs_dsfr.plugin.table import DSFRTable
from mkdocs_dsfr.plugin.utils import DSFRUtils


class DSFRPlugin(BasePlugin[DSFRConfig]):
    """
    MkDocs plugin for DSFR integration.

    Methods:
        replace_component: Replaces DSFR content blocks with rendered HTML.
        on_page_markdown: Hook called when processing Markdown content.
        on_page_content: Hook called when processing HTML content.

    """

    def __init__(self) -> None:
        """Init DSFRPlugin config."""
        self.mkdocs_config = MkDocsConfig()
        self.match_id = 0

    def replace_component(self, match: Match[str]) -> str:
        """
        Replace DSFR content blocks with rendered HTML.

        Args:
            match: A regex match object representing a DSFR content block.

        Returns:
            str: The rendered HTML content.

        """
        dsfr_utils = DSFRUtils()
        base_type = match.group(1)
        content_yaml = match.group(2)
        parsed_yaml = dsfr_utils.parse_yaml(content_yaml)
        if parsed_yaml is None or base_type is None or type(parsed_yaml) is not dict:
            return ""
        parsed_yaml["match_id"] = self.match_id
        template_data = {
            "data": parsed_yaml,
            "base_url": urlparse(self.mkdocs_config["site_url"]).path,
        }
        self.match_id += 1
        return dsfr_utils.render_template(base_type, template_data)

    # pylint: disable-next=unused-argument
    def on_page_markdown(
        self, markdown: str, page: Page, config: MkDocsConfig, files: Files
    ) -> Optional[str]:
        """
        MkDocs hook called when processing Markdown content.

        This method is called during the Markdown rendering process and replaces DSFR content
        blocks with rendered HTML.

        Args:
            markdown (str): The input Markdown content.
            page (Page): The MkDocs Page object.
            config (MkDocsConfig): The MkDocs configuration object.
            files (Files): The MkDocs Files object.

        Returns:
            Optional[str]: The modified Markdown content.

        """
        self.mkdocs_config = config

        dsfr_utils = DSFRUtils()
        components_replaced_md = re.sub(
            re.compile(r"```dsfr-plugin(?:-(\w+))?\n(.*?)\n```", re.DOTALL),
            self.replace_component,
            markdown,
        )

        icons_replaced_md = re.sub(
            re.compile(r":dsfr-icon-(.*?)(?:\|(.*?))?:", re.DOTALL),
            lambda match: dsfr_utils.render_template(
                "icon",
                {
                    "icon_name": match.group(1),
                    "icon_color": match.group(2) if match.group(2) else None,
                },
            ),
            components_replaced_md,
        )

        pictograms_replaced_md = re.sub(
            re.compile(r":dsfr-picto-(.*?)-(.*?):", re.DOTALL),
            lambda match: dsfr_utils.render_template(
                "pictogram",
                {
                    "pictogram_category": match.group(1),
                    "pictogram_name": match.group(2),
                    "base_url": urlparse(self.mkdocs_config["site_url"]).path,
                },
            ),
            icons_replaced_md,
        )

        return pictograms_replaced_md

    # pylint: disable-next=unused-argument
    def on_page_content(
        self, html: str, page: Page, config: MkDocsConfig, files: Files
    ) -> Optional[str]:
        """
        MkDocs hook called when processing HTML content.

        This method is called during the HTML rendering process and enhances the styling
        of tables and links in the content.

        Args:
            html: The input HTML content.
            page: The MkDocs Page object.
            config: The MkDocs configuration object.
            files: The MkDocs Files object.

        Returns:
            Optional[str]: The modified HTML content with enhanced table and link styling.

        """
        dsfr_table = DSFRTable(self.config)
        dsfr_link = DSFRLink()
        dsfr_media = DSFRMedia()

        updated_tables = dsfr_table.update(html)
        updated_links = dsfr_link.update(updated_tables)
        updated_medias = dsfr_media.update(updated_links)

        return updated_medias
