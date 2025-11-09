"""MkDocs DSFRLink Styling Utility."""

from bs4 import BeautifulSoup


class DSFRLink:
    """
    MkDocs DSFR Link Styling Utility.

    This class provides utility methods for updating HTML content by enhancing the styling of links.

    Methods:
        update: Updates HTML content by adding a specific class to links with a "download" attribute.

    """

    def update(self, html: str) -> str:
        """
        Update HTML content by enhancing the styling of links.

        This method finds all the <a> tags in the input HTML content and adds a specific class
        to those links that have a "download" attribute.

        Args:
            html: The input HTML content.

        Returns:
            str: The modified HTML content with enhanced link styling.

        """
        soup = BeautifulSoup(html, "html.parser")
        a_tags = soup.find_all("a")
        for a_tag in a_tags:
            if "download" in a_tag.attrs:
                a_tag["class"] = "fr-link--download fr-link"
        return soup.prettify()
