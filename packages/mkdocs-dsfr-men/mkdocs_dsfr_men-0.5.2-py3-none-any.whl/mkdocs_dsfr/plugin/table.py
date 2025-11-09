"""MkDocs DSFR Table Styling Utility."""

from bs4 import BeautifulSoup
from mkdocs_dsfr.plugin.config import DSFRConfig


class DSFRTable:
    """
    DSFRTable class for enhancing the styling of tables in HTML content.

    Methods:
        update: Updates HTML content by wrapping each table with a `div` element
                and adding the class "fr-table."

    """

    def __init__(self, config: DSFRConfig) -> None:
        """Init DSFRTable config."""
        self.table_bordered = config.table_bordered
        self.table_no_scroll = config.table_no_scroll
        self.table_layout_fixed = config.table_layout_fixed
        self.table_color = config.table_color

    def _build_table_div(self) -> str:
        div = "fr-table"
        div += " fr-table--bordered" if self.table_bordered else ""
        div += " fr-table--no-scroll" if self.table_no_scroll else ""
        div += " fr-table--layout-fixed" if self.table_layout_fixed else ""
        div += f" fr-table--{self.table_color}" if self.table_color else ""
        return div

    def update(self, html: str) -> str:
        """
        Update HTML content by enhancing the styling of tables.

        This method finds all the tables in the input HTML content and wraps each of them
        with a `div` element and adding the "fr-table" class.

        Args:
            html: The input HTML content.

        Returns:
            str: The modified HTML content with enhanced table styling.

        """
        soup = BeautifulSoup(html, "html.parser")
        tables = soup.find_all("table")
        for table in tables:
            new_div = soup.new_tag("div")
            new_div["class"] = self._build_table_div()
            table.wrap(new_div)
        return soup.prettify()
