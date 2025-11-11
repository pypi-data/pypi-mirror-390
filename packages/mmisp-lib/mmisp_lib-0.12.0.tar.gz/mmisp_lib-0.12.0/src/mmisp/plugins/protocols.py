from collections.abc import Iterable
from typing import Any, Protocol, runtime_checkable

from sqlalchemy.ext.asyncio import AsyncSession

from mmisp.db.models.attribute import Attribute
from mmisp.lib.attributes import literal_valid_attribute_types
from mmisp.plugins.enrichment.data import EnrichAttributeResult
from mmisp.plugins.types import CorrelationPluginType, EnrichmentPluginType, PluginType


class Plugin(Protocol):
    """
    Interface providing all attributes and methods a plugin must implement.
    """

    NAME: str
    """Name of the plugin"""
    PLUGIN_TYPE: PluginType
    """Type of the plugin"""
    DESCRIPTION: str
    """Description of the plugin"""
    AUTHOR: str
    """Author who wrote the plugin"""
    VERSION: str
    """Version of the plugin"""


@runtime_checkable
class CorrelationPlugin(Plugin, Protocol):
    """
    Class to hold information about a correlation plugin.
    """

    CORRELATION_TYPE: CorrelationPluginType

    async def run(self: Any, db: AsyncSession, attribute: Attribute, correlation_threshold: int) -> Any:
        """
        Entry point of the plugin. Runs the plugin and returns any existing result.

        :return: The result the plugin returns
        :rtype Any
        """
        ...


@runtime_checkable
class EnrichmentPlugin(Plugin, Protocol):
    ENRICHMENT_TYPE: Iterable[EnrichmentPluginType]
    """The type of the enrichment plugin."""
    ATTRIBUTE_TYPES_INPUT: list[literal_valid_attribute_types]
    """The accepted attribute types of the enrichment plugin."""
    ATTRIBUTE_TYPES_OUTPUT: list[literal_valid_attribute_types]
    """The returned types of attributes of the enrichment plugin."""

    async def run(self: Any, db: AsyncSession, attribute: Attribute) -> EnrichAttributeResult:
        """
        Entry point of the plugin. Runs the plugin and returns any existing result.

        :return: The result the plugin returns
        :rtype Any
        """
        ...


plugintype_plugin_mapper = {PluginType.ENRICHMENT: EnrichmentPlugin, PluginType.CORRELATION: CorrelationPlugin}
