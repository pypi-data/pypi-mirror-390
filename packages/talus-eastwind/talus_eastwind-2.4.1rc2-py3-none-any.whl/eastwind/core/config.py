# -*- coding: utf-8 -*-
import os
import yaml
from zoneinfo import ZoneInfo
from typing import Type, Any


def extract_setting(*paths, source: dict, expect_type: Type = Any, default_value: Any = None) -> Any:
    """
    Extract a config setting value from the config source dictionary.
    :param paths: The setting directory key path.
    :param source: The loaded config file dictionary.
    :param expect_type: The expected value type to be checked.
    :param default_value: If the key path does not exist, the default value to be set.
    :return: The value stored in the directory. If no default value was set, a ValueError will be raised.
    """
    existed_paths = []
    # Extract the value from the provided path.
    target: dict | Any = source
    for block in paths:
        if block not in target:
            if default_value is None:
                # No default value provided, raise the exception.
                raise ValueError(f"No '{block}' found " + ('in config' if len(existed_paths) == 0 else "under '" + '->'.join(existed_paths) + "'"))
            else:
                # For optional value, just return the default value.
                return default_value
        # Extend the exists block path.
        existed_paths.append(block)
        # Change to the target block
        target = target[block]
    # Check the target value type.
    if not isinstance(target, expect_type):
        raise TypeError(f"Expected type '{expect_type.__name__}' but got '{type(target).__name__}' for config '{paths[-1]}'")
    return target


def load_yaml(filepath: str) -> dict:
    """
    Load a YAML configuration file.
    :param filepath: The path to the YAML configuration file.
    :return: The loaded config dictionary.
    """
    # Check file existence.
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"Config yaml file not found: {filepath}")
    # Safely load the structure.
    with open(filepath, 'r') as config_yaml_file:
        return yaml.safe_load(config_yaml_file)


class SurgeMonitorConfig:
    def __init__(self):
        self.address = "127.0.0.1"
        self.port = 11011
        self.url = "http://127.0.0.1:11011/"

    def load_from_dict(self, config_data: dict) -> None:
        self.address = extract_setting('address', source=config_data, expect_type=str, default_value=self.address)
        self.port = extract_setting('port', source=config_data, expect_type=int, default_value=self.port)
        # Update the URL access.
        self.url = f"http://{self.address}:{self.port}/"


class SurgeWorkerConfig:
    def __init__(self):
        self.heartbeat_interval: int = 10
        self.heartbeat_max_timeout: int = 35

    def load_from_dict(self, config_data: dict) -> None:
        self.heartbeat_interval = extract_setting('heartbeat', 'interval', source=config_data, expect_type=int, default_value=self.heartbeat_interval)
        self.heartbeat_max_timeout = extract_setting('heartbeat', 'max_timeout', source=config_data, expect_type=int, default_value=self.heartbeat_max_timeout)


class Config:
    def __init__(self):
        # TALUS library support from the other configuration.
        self.surge_monitor = SurgeMonitorConfig()
        self.surge_worker = SurgeWorkerConfig()
        # Local timezone
        self.timezone: ZoneInfo = ZoneInfo("UTC")
        # Module list
        self.module_builtin: list[str] = []
        self.module_project: list[str] = []
        # Database setting
        self.db_type: str = ''
        self.db_url: str = ''
        # Other configurations.
        self.__config_value: dict[str, Any] = {}

    def load_from_dict(self, config_data: dict) -> None:
        self.module_builtin = extract_setting('modules', 'eastwind', source=config_data, expect_type=list, default_value=[])
        self.module_project = extract_setting('modules', 'project', source=config_data, expect_type=list, default_value=[])
        self.db_type = extract_setting('database', 'type', source=config_data, expect_type=str)
        self.db_url = extract_setting('database', 'url', source=config_data, expect_type=str)
        self.__config_value = extract_setting('config', source=config_data, expect_type=dict, default_value=self.__config_value)
        surge_config = extract_setting('surge', source=self.__config_value, expect_type=dict, default_value=dict())
        self.surge_monitor.load_from_dict(extract_setting('monitor', source=surge_config, expect_type=dict, default_value=dict()))
        self.surge_worker.load_from_dict(extract_setting('worker', source=surge_config, expect_type=dict, default_value=dict()))
        timezone_info: str = extract_setting('timezone', source=config_data, expect_type=str, default_value='UTC')
        try:
            self.timezone = ZoneInfo(timezone_info)
        except Exception as e:
            print(f"Error happens when processing timezone: {str(e)}")
            self.timezone = ZoneInfo('UTC')

    def load_from_yaml(self, filepath: str) -> None:
        self.load_from_dict(load_yaml(filepath))

    def value(self, key: str, default: Any = None) -> Any:
        # Extract the value from key.
        if key in self.__config_value:
            return self.__config_value[key]
        return default
