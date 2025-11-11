"""
Implements the loading and registration process of plugins.
"""

import importlib.util
import logging
import os.path
import sys
from importlib.machinery import ModuleSpec
from types import ModuleType

from mmisp.plugins.exceptions import PluginImportError

_log = logging.getLogger(__name__)


PLUGIN_MODULE_NAME_PREFIX: str = "mmisp_plugins"


def _import_module(path: str) -> ModuleType:
    plugin_dir_name: str = os.path.basename(os.path.split(path)[0])
    module_name: str = os.path.splitext(os.path.basename(path))[0]
    extended_module_name: str = f"{PLUGIN_MODULE_NAME_PREFIX}.{plugin_dir_name}.{module_name}"

    module: ModuleType
    if extended_module_name in sys.modules.keys():
        module = sys.modules[extended_module_name]
    else:
        module_spec: ModuleSpec | None
        if os.path.isfile(path):
            module_spec = importlib.util.spec_from_file_location(extended_module_name, path)
        else:
            module_init_path: str = os.path.join(path, "__init__.py")
            module_spec = importlib.util.spec_from_file_location(
                extended_module_name, module_init_path, submodule_search_locations=[]
            )
        if module_spec is None:
            raise ValueError(f"Could not load module: {path}")

        module = importlib.util.module_from_spec(module_spec)
        sys.modules[extended_module_name] = module
        try:
            if module_spec.loader is None:
                raise ValueError()
            module_spec.loader.exec_module(module)
        except FileNotFoundError as file_not_found_error:
            raise file_not_found_error
        except Exception as import_error:
            raise PluginImportError(
                message=f"An error occurred while importing the plugin '{path}'. Error: {import_error}"
            )
    return module


#    return cast(PluginModuleInterface, module)


def load_plugins(plugins: list[str]) -> None:
    """
    Loads the specified plugins and registers them in the given factory.

    :param plugins: A list of paths to plugin modules to load.
    :type plugins: list[str]
    :param factory: The factory in which the plugins are to be registered.
    :type factory: PluginFactory
    """

    for plugin in plugins:
        try:
            _import_module(plugin)
        except FileNotFoundError as file_not_found_error:
            _log.exception(f"Plugin {plugin}: The plugin could not be imported. File not found: {file_not_found_error}")
            continue
        except PluginImportError as import_error:
            _log.exception(f"An error occurred while importing the plugin '̛{plugin}'. Error: {import_error}")
            continue


def load_plugins_from_directory(*directories: str) -> None:
    """
    Loads all plugins that are in the specified directory.

    :param directory: The path to a directory containing plugins to load.
    :type directory: str
    :param factory: The factory in which the plugins are to be registered.
    :type factory: PluginFactory
    """
    for directory in directories:
        if not directory:
            raise ValueError("Path to a directory is required. May not be empty.")
        if not os.path.isdir(directory):
            raise ValueError(f"The directory '{directory}' doesn't exist.")

        path_content: list[str] = os.listdir(directory)
        plugin_modules: list[str] = []
        for element in path_content:
            element_path: str = os.path.join(directory, element)
            if os.path.isdir(element_path):
                if os.path.isfile(os.path.join(element_path, "__init__.py")):
                    plugin_modules.append(element_path)
            else:
                file_extension: str = os.path.splitext(element)[1]
                if file_extension == ".py":
                    plugin_modules.append(element_path)

        load_plugins(plugin_modules)
