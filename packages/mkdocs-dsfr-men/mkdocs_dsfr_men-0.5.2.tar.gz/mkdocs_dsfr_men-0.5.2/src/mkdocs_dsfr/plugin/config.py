"""MkDocs DSFRConfig class."""

from mkdocs.config.base import Config
from mkdocs.config.config_options import Type


class DSFRConfig(Config):
    """Configuration class for DSFRPlugin."""

    table_bordered = Type(bool, default=False)
    table_no_scroll = Type(bool, default=False)
    table_layout_fixed = Type(bool, default=False)
    table_color = Type(str, default="")
