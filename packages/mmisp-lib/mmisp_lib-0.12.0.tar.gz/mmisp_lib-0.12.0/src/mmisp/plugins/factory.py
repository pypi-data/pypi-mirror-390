from collections.abc import Sequence
from typing import Literal, TypedDict, overload

from mmisp.plugins.exceptions import NoValidPlugin, PluginNotFound, PluginRegistrationError
from mmisp.plugins.protocols import CorrelationPlugin, EnrichmentPlugin, plugintype_plugin_mapper
from mmisp.plugins.types import PluginType


class PluginDict(TypedDict):
    correlation: dict[str, CorrelationPlugin]
    enrichment: dict[str, EnrichmentPlugin]


_plugins: PluginDict = {"correlation": {}, "enrichment": {}}


def register(plugin: EnrichmentPlugin | CorrelationPlugin) -> None:
    """
    Registers a new plugin.

    Args:
        plugin: The class of the plugin to register.
    Raises:
        PluginRegistrationError: If there is already a plugin registered with the same name.
    """
    try:
        if not isinstance(plugin, plugintype_plugin_mapper[plugin.PLUGIN_TYPE]):
            raise NoValidPlugin("Plugin does not fulfil plugin protocol")
    except AttributeError:
        raise NoValidPlugin("Plugin does not specify PLUGIN_TYPE")

    if plugin.NAME not in _plugins[plugin.PLUGIN_TYPE.value]:
        # unfortunately mypy does not infer correct type
        _plugins[plugin.PLUGIN_TYPE.value][plugin.NAME] = plugin  # type: ignore
    elif plugin != _plugins[plugin.PLUGIN_TYPE.value][plugin.NAME]:
        raise PluginRegistrationError(
            f"Registration not possible. The are at least two plugins with the same name '{plugin.NAME}'."
        )
    else:
        # If plugin is already registered, do nothing.
        pass


def unregister(plugin_type: PluginType, plugin_name: str) -> None:
    """
    Unregisters a plugin.

    The plugin can be registered again later.

    Args:
        plugin_name: The name of the plugin to remove from the factory.
    Raises:
        PluginNotFound: If there is no plugin with the specified name.
    """

    if not is_plugin_registered(plugin_type, plugin_name):
        raise PluginNotFound(message=f"Unknown plugin '{plugin_name}'. Cannot be removed.")

    _plugins[plugin_type.value].pop(plugin_name)


@overload
def get_plugin(plugin_type: Literal[PluginType.ENRICHMENT], plugin_name: str) -> EnrichmentPlugin: ...
@overload
def get_plugin(plugin_type: Literal[PluginType.CORRELATION], plugin_name: str) -> CorrelationPlugin: ...


def get_plugin(plugin_type: PluginType, plugin_name: str) -> EnrichmentPlugin | CorrelationPlugin:
    """
    Returns information about a registered plugin.

    Args:
        plugin_type: The type of the plugin
        plugin_name: The name of the plugin.
    Returns:
        The Plugin
    Raises:
        PluginNotFound: If there is no plugin with the specified name and type.
    """
    try:
        return _plugins[plugin_type.value][plugin_name]
    except KeyError as e:
        raise PluginNotFound from e


@overload
def get_plugins(plugin_type: Literal[PluginType.ENRICHMENT]) -> Sequence[EnrichmentPlugin]: ...
@overload
def get_plugins(plugin_type: Literal[PluginType.CORRELATION]) -> Sequence[CorrelationPlugin]: ...


def get_plugins(plugin_type: PluginType) -> Sequence[EnrichmentPlugin | CorrelationPlugin]:
    """
    Returns a list of registered Plugins.

    :return: The list of plugins.
    :rtype: list[PluginInfo]
    """
    return list(_plugins[plugin_type.value].values())


def is_plugin_registered(plugin_type: PluginType, plugin_name: str) -> bool:
    """
    Checks if the given plugin is registered in the factory.

    :param plugin_name: The name of the plugin to check.
    :type plugin_name: str
    :return: True if the plugin is registered
    """
    return plugin_name in _plugins[plugin_type.value]
