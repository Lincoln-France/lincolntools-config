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
    def get_instance(cfg_path: str = None):
        """Méthode qui permet de récupérer l'instance existante. 
        Si elle n'existe pas, une nouvelle instance est créée en utilisant les valeurs par défaut.

        Returns:
            Config: Le singleton Config.
        """
        if Config._instance is None:
            Config(cfg_path)
        return Config._instance

    @staticmethod
    def get(cfg_path: str = None):
        """Alias de la fonction `get_instance()`

        Returns:
            Config: Le singleton Config.
        """
        return Config.get_instance(cfg_path)

    @staticmethod
    def clear():
        """Réinitialise l'instance de Config."""
        Config._instance = None

    def dump(self, filename: str = None):
        """ Permet de dump la configuration actuellement chargé. 
        Le résultat produit est un fichier YAML qui contient la totalité de la configuration.


        Args:
            filename (str) : Le path vers le fichier de destination. 
        Returns:
            str: Le résultat du dump sous forme d'une chaîne de caractère.

        """
        self.conf['_version'] += 1
        dump_string = yaml.dump(json.loads(json.dumps(self.conf)), default_flow_style=False)
        if filename is not None:
            with open(filename, 'w') as f:
                f.write(dump_string)
        return dump_string

    def __init__(self, cfg_path: str = None):
        """Constructeur de l'objet Configuration.

        Args:
            cfg_path (str, optional): Le chemin vers le fichier/dossier de configuration. Defaults to None.

        Raises:
            Exception: Lancée si on essai de recréer une instance de Config si une instance existe déjà.
        """
        # Si une instance de la classe existe déjà => erreur.
        if Config._instance is not None:
            raise Exception('Cette classe est un singleton!')
        #: str: contient le path vers le fichier/dossier de configuration
        self.config_path = None
        #: dict: le `dict` qui correspond à l'objet configuration
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
        Fonction qui retourne l'objet Config sous forme de dict(). Les clés sont toute "aplaties" en une seule et même chaîne (ex: key1-subkey1: value).

        Returns:
            dict: Dictionnaire de clé/valeur correspondant à la hierarchie du fichier de config.

        """
        if key is not None:
            return dict(self._flatten([], self.conf[key]))
        return dict(self._flatten([], self.conf))

    def __str__(self):
        return 'conf:%s' % (self.conf)

    def __contains__(self, item):
        return item in self.conf

    def __getitem__(self, key: str, default_value=''):
        return self.conf[key]

    def __setitem__(self, key: str, value: object):
        self.conf[key] = value
