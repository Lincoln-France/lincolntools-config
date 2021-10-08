# -*- coding: utf-8 -*-
from .config_loader import ConfigLoader
import logging
import yaml
import json
import os
# import glob

LOGGER = logging.getLogger(__name__)


class Config():
    _instance = None

    @staticmethod
    def get_instance(cfg_path: str = None) -> 'Config':
        """Function which return the current instance. 
        If it doesn't exists, a new instance is initialized using the default values.

        Returns:
            Config: Config singleton.
        """
        if Config._instance is None:
            Config(cfg_path)
        return Config._instance

    @staticmethod
    def get(cfg_path: str = None) -> 'Config':
        """Alias of `get_instance()`

        Returns:
            Config: Config singleton.
        """
        return Config.get_instance(cfg_path)

    @staticmethod
    def clear():
        """Config instance reinitialization."""
        Config._instance = None

    def dump(self, filename: str = None) -> str:
        """ Creates a string dump of the current configuration. 
        It can produce a YAML file which contains the dumped whole configuration.


        Args:
            filename (str) : Absolute path to destination file. 
        Returns:
            str: String value which is the dump of the Config object.

        """
        self.conf['_version'] += 1
        dump_string = yaml.dump(json.loads(json.dumps(self.conf)), default_flow_style=False)
        if filename is not None:
            with open(filename, 'w') as f:
                f.write(dump_string)
        return dump_string

    def __init__(self, cfg_path: str = None):
        """Constructor of the Config object.

        Args:
            cfg_path (str, optional): The path to configuration file/folder. Defaults to None.

        Raises:
            Exception: Raised if you try to create an instance if there is already one which exists.
        """
        # If an instance already exists => Exception.
        if Config._instance is not None:
            raise Exception('Sorry but it is a singleton class!')
        #: str: contains the path to a configuration file/folder
        self.config_path = None
        #: dict: Python `dict` which is the configuration object
        self.conf = {}
        if cfg_path is not None:
            LOGGER.info('load config at: %s', cfg_path)
            self.config_path = cfg_path
            self.conf = ConfigLoader.load(cfg_path)

        if '_version' not in self.conf:
            self.conf['_version'] = 1

        Config._instance = self
        self.get = self._instance_get

    def _instance_get(self, key, default_value=''):
        return self.conf.get(key, default_value)

    def _flatten(self, keys, values):
        """
        Flattens the config object as a list of string representation.

        Returns:
            list: A list of Key-value dicts that matches the config file hierarchy.

        """
        flatten_list = []
        if isinstance(values, dict):
            for key, value in values.items():
                if key.startswith('_'):
                    continue
                v = self._flatten(keys + [key], value)
                flatten_list += v
        elif isinstance(values, list):
            for key, value in enumerate(values):
                v = self._flatten(keys + [str(key)], value)
                flatten_list += v
        else:
            v = [('-'.join(keys), values)]
            flatten_list += v
        return flatten_list

    def flatten(self, key: str = None):
        """
        Function which returns the Config object as a Python dict. Every keys are flattened into a single string (ex: key1-subkey1: value).

        Returns:
            dict: Key-value dict which matches the config file hierarchy.

        """
        if key is not None:
            return dict(self._flatten([], self.conf[key]))
        return dict(self._flatten([], self.conf))

    def __str__(self):
        """
        Equivalent of toString for the configuration object.

        Returns:
            str: String representation of the Config object.

        """
        return 'conf:%s' % (self.conf)

    def __contains__(self, item):
        """
        Check if an element is in the Config.

        Returns:
            dict: Python dict with the desired item.

        """
        return item in self.conf

    def __getitem__(self, key: str, default_value=''):
        """
        Returns an element that is in the Config.

        Returns:
            dict: Python dict with the desired item.

        """
        return self.conf[key]

    def __setitem__(self, key: str, value: object):
        """ Updates an element that is in the Config. """
        self.conf[key] = value
