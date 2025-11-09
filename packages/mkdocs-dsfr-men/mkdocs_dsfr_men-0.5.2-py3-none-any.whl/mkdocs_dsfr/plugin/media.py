"""MkDocs DSFRMedia Styling Utility."""

from bs4 import BeautifulSoup


class DSFRMedia:
    """
    MkDocs DSFR Media Styling Utility.

    This class provides utility methods for updating HTML content by enhancing the styling of media elements.

    Methods:
        update: Updates HTML content by adding a specific class to image tags, except those with certain existing classes.

    """

    def update(self, html: str) -> str:
        """
        Update HTML content by enhancing the styling of media elements.

        This method finds all the <img> tags in the input HTML content and adds a specific class
        to those images that do not have 'class_to_skip' or 'src_to_skip'.

        Args:
            html: The input HTML content.

        Returns:
            str: The modified HTML content with enhanced media styling.

        """
        soup = BeautifulSoup(html, "html.parser")
        img_tags = soup.find_all("img")

        class_to_skip = [
            "emojione",
            "twemoji",
            "gemoji",
        ]
        src_to_skip = [
            "img.shields.io",
        ]

        for img_tag in img_tags:
            if "class" in img_tag.attrs:
                if any(cls in img_tag["class"] for cls in class_to_skip):
                    continue
            if "src" in img_tag.attrs:
                if any(cls in img_tag["src"] for cls in src_to_skip):
                    continue

            img_tag["class"] = img_tag.get("class", []) + ["fr-responsive-img"]

        return soup.prettify()
