"""MkDocs DSFR Plugin Utils."""

from typing import Any

import markdown
import yaml
from jinja2 import Environment, PackageLoader, TemplateNotFound, select_autoescape
from yaml.parser import ParserError


class DSFRUtils:
    """
    Utility class for working with DSFR-related operations.

    Methods:
        convert_content_to_html: Convert 'content' markdown to html.
        parse_yaml: Parse a YAML-formatted string and returns the corresponding Python object.
        render_template: Renders a Jinja2 template with the provided data.

    """

    def convert_content_to_html(self, data: Any) -> Any:
        """
        Convert 'content' markdown to html.

        Args:
            data: The data dict or list

        Returns:
            Any: The modified data object.

        """
        if isinstance(data, dict):
            for key in list(data.keys()):
                if key == "content" and isinstance(data[key], str):
                    data[key] = markdown.markdown(data[key])
                elif isinstance(data[key], (dict, list)):
                    data[key] = self.convert_content_to_html(data[key])

        elif isinstance(data, list):
            for i in range(len(data)):
                if isinstance(data[i], (dict, list)):
                    data[i] = self.convert_content_to_html(data[i])

        return data

    def parse_yaml(self, content_block: str) -> Any:
        """
        Parse a YAML-formatted string and returns the corresponding Python object.

        Args:
            content_block: A string containing YAML-formatted data.

        Returns:
            Any: The Python object representing the parsed YAML data.

        """
        try:
            parsed_yaml = yaml.safe_load(content_block)
        except ParserError as e:
            print(f"ParserError: {e}")
            return ""
        parsed_yaml = self.convert_content_to_html(parsed_yaml)
        return parsed_yaml

    def render_template(self, template_name: str, data: dict[Any, Any]) -> str:
        """
        Render a Jinja2 template with the provided data.

        Args:
            template_name: The name of the Jinja2 template to render.
            data: A dictionary containing data to be used in template rendering.

        Returns:
            str: The rendered content as a string.

        """
        env = Environment(
            loader=PackageLoader("mkdocs_dsfr.plugin", "templates"),
            lstrip_blocks=True,
            trim_blocks=True,
            autoescape=select_autoescape(
                default=False, default_for_string=False, enabled_extensions=()
            ),
        )
        try:
            template = env.get_template(f"{template_name}.html")
        except TemplateNotFound as e:
            print(f"TemplateNotFound: {e}")
            return ""
        return template.render(data)
