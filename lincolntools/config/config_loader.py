import glob
import os
import yaml
import logging
import re
import errno
import tempfile
import io
from deepdiff import DeepDiff  # For Deep Difference of 2 objects
from easydict import EasyDict
LOGGER = logging.getLogger(__name__)


class ConfigLoader():
    """Classe utilitaire qui contient les fonctions de recherche et de création de la configuration."""
    #: re.Pattern[]: Regex qui match le format variable d'environnement dans le fichier (ex. ${VAR_ENV})
    env_path_matcher = re.compile(r'\$\{([^}^{]+)\}')

    @staticmethod
    def load(file_path: str):
        """ Lance l'action de charger le(s) fichier(s) de configuration.
        En fonction de si c'est un path vers un fichier ou vers un dossier, on lance 2 actions différentes.

        Args:
            file_path (str): Le chemin vers le fichier/dossier de configuration.

        Returns:
            EasyDict: Le dictionnaire qui contient la totalité de la configuration.
        """
        if os.path.isfile(file_path):
            return EasyDict(ConfigLoader.load_from_file(file_path))
        else:
            return EasyDict(ConfigLoader.load_from_folder(file_path))

    @staticmethod
    def load_from_file(file_path: str):
        """Crée un objet Config à partir d'un fichier yaml.

            Args:
                file_path (str): Le chemin absolu vers le fichier config.
            Returns:
                dict: Un dictionnaire qui contient la configuration.
        """
        return ConfigLoader.read_yaml_file(file_path)

    @staticmethod
    def load_from_folder(folder_path: str, concatenate: bool = True):
        """Crée un objet Config à partir d'un dossier. Le dossier ainsi que ses sous-dossiers sont parcourus de manière récursive pour
            y récupérer les fichiers yaml. Ces fichiers sont ensuite lus et concatenés les uns après les autres.

        Args:
            folder_path (str): Le chemin absolu vers le dossier config.
            concatenate (bool): Si True Les fichiers sont concatener en un fichier avant d'être parser. Par défaut à True.
        Returns:
            dict: Un dictionnaire qui contient les configurations concaténées.
        """
        # On lit tous les fichiers yaml de manière récursive
        yaml_files = glob.glob(os.path.join(folder_path, '**/*.yaml'), recursive=True)
        yaml_files += glob.glob(os.path.join(folder_path, '**/*.yml'), recursive=True)

        conf = {}
        if concatenate:
            LOGGER.info("Chargement des fichiers de configuration par concatenation")
            yaml_files_sorted_infos = sorted([(os.path.basename(v), i) for i, v in enumerate(yaml_files)])
            yaml_files_sorted = [yaml_files[idx] for _, idx in yaml_files_sorted_infos]
            fp = tempfile.TemporaryFile()
            for yaml_file in yaml_files_sorted:
                with open(yaml_file, "rb") as yaml_file_stream:
                    fp.write(yaml_file_stream.read())
            fp.seek(0)
            conf = ConfigLoader.read_yaml_stream(fp)
            fp.close()
        else:
            LOGGER.info("Chargement des fichiers de configuration")
            for yaml_file in yaml_files:
                new_conf = ConfigLoader.read_yaml_file(yaml_file)
                conf.update(new_conf)
        return conf

    @staticmethod
    def read_yaml_file(filename: str):
        """ Crée un objet Config à partir d'un fichier.

        Args:
            filename (str): chemin du fichier
        Returns:
            dict: Le dictionnaire qui contient les clés/valeurs du fichier yaml.
        """

        with open(filename, 'r') as stream:
            LOGGER.info('Chargement du fichier de configuration %s', filename)
            return ConfigLoader.read_yaml_stream(stream)

    @staticmethod
    def read_yaml_stream(filestream: io.BufferedIOBase):
        """ Crée un objet Config à partir d'un stream.

        Args:
            filestream (io.BufferedIOBase): stream
        Returns:
            dict: Le dictionnaire qui contient les clés/valeurs du fichier yaml.
        """
        # Constructeur qui repère les "custom tags" !join dans le fichier YAML
        # Cela permet de lancer une fonction qui aura le rôle de concaténer 2 chaines (un peu à la manière de os.path.join(...))
        yaml.add_constructor('!join', ConfigLoader.join, yaml.SafeLoader)
        # Resolver qui recherche à matcher le regex pour les var env
        yaml.add_implicit_resolver('!env_var', ConfigLoader.env_path_matcher, None, yaml.SafeLoader)
        # Constructeur attaché au détecteur précédent pour les var env
        yaml.add_constructor('!env_var', ConfigLoader.env_path_constructor, yaml.SafeLoader)
        try:
            return yaml.safe_load(filestream)
        except yaml.YAMLError as exc:
            LOGGER.error('Il y a une erreur de format dans le fichier de configuration')
            raise exc

    @staticmethod
    def env_path_constructor(loader: yaml.loader.SafeLoader, node: yaml.ScalarNode) -> str:
        """ Extrait la valeur d'un noeud qui match le regex pour lire la variable d'environnement associée puis la remplacer par sa valeur. """
        value = node.value
        match = ConfigLoader.env_path_matcher.match(value)
        env_var = match.group(1)

        try:
            env_var_value = os.environ[env_var]
        except KeyError:
            LOGGER.warning("Aucune valeur pour la variable d'environnement [%s]. Initialisation à vide.", str(env_var))
            return ''

        return env_var_value + value[match.end():]

    @staticmethod
    def check_template_match(config_path: str, template_path: str = None):
        """ Prend le path vers un fichier de configuration en paramètre et retourne True si les clés de son template correspondent
        au fichier de config concerné. False sinon.

        Args:
            loader (yaml.loader.SafeLoader): Le loader pyaml (SafeLoader dans notre cas).
            node (yaml.ScalarNode): Le noeud qui contient le tag dans le fichier yaml.
        Returns:
            bool: True si tout correspond, False sinon.
        """
        match = False
        config_dict = ConfigLoader.read_yaml_file(config_path)
        config_filename = os.path.basename(config_path)
         
        if not template_path:
            template_path = '{path}.template'.format(path=os.path.splitext(config_path)[0])

        if not os.path.isfile(template_path):
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), template_path)

        template_dict = ConfigLoader.read_yaml_file(template_path)
        diff = DeepDiff(config_dict, template_dict, ignore_order=True)
        if('dictionary_item_removed' not in diff.keys()):
            match = True
        else:
            raise ValueError('{config_name} - Les clés suivantes ne sont pas dans le template: {err}'.format(config_name=config_filename, err=diff['dictionary_item_removed']))

        return match

    # define custom tag handler
    @staticmethod
    def join(loader: yaml.loader.SafeLoader, node: yaml.ScalarNode):
        """ Handler pour custom tags. Fonction lancée à la lecture d'un fichier de configuration lorsqu'un custom tag !path est trouvé.
        Elle permet de concaténer les chaîne en paramètre du champ. (ex: data_dir: !join [*project_dir, /data])

        Args:
            loader (yaml.loader.SafeLoader): Le loader pyaml (SafeLoader dans notre cas).
            node (yaml.ScalarNode): Le noeud qui contient le tag dans le fichier yaml.
        Returns:
            str: La valeur des 2 chaînes concaténées.

        """
        seq = loader.construct_sequence(node)
        return ''.join([str(i) for i in seq])
