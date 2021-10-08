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
    """Utility class that contains the functions to search yaml files and create the configuration object ."""
    #: re.Pattern[]: Regex which matches the environment variables format in configuration file (ex. ${VAR_ENV})
    env_path_matcher = re.compile(r'\$\{([^}^{]+)\}')

    @staticmethod
    def load(file_path: str) -> EasyDict:
        """ Launch the process of configuration file(s) loading.
        Depending on whether it is a path to a file or a folder, 2 different actions are launched.

        Args:
            file_path (str): Path to configuration file/folder.

        Returns:
            EasyDict: The python dict which contains the whole configuration.
        """
        if os.path.isfile(file_path):
            return EasyDict(ConfigLoader.load_from_file(file_path))
        else:
            return EasyDict(ConfigLoader.load_from_folder(file_path))

    @staticmethod
    def load_from_file(file_path: str) -> dict:
        """Creates a Config object from a YAML file.

            Args:
                file_path (str): Absolute path to file.
            Returns:
                dict: Python dict which contains the configuration.
        """
        return ConfigLoader.read_yaml_file(file_path)

    @staticmethod
    def load_from_folder(folder_path: str, concatenate: bool = True) -> dict:
        """Creates a Config object from a folder. The folder and its subfolder are searched recursively to get the YAML files it contains.
        These files are then read and concatenated.

        Args:
            folder_path (str): Absolute path to config folder.
            concatenate (bool): If True, files are concatenated into a single file before it is parsed. Default value is True.
        Returns:
            dict: Python dict which contains the concatenated configs.
        """
        # Recursively read YAML files
        yaml_files = glob.glob(os.path.join(folder_path, '**/*.yaml'), recursive=True)
        yaml_files += glob.glob(os.path.join(folder_path, '**/*.yml'), recursive=True)

        conf = {}
        if concatenate:
            LOGGER.info("Files loading and concatenation.")
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
            LOGGER.info("Configuration files loading")
            for yaml_file in yaml_files:
                new_conf = ConfigLoader.read_yaml_file(yaml_file)
                conf.update(new_conf)
        return conf

    @staticmethod
    def read_yaml_file(filename: str) -> dict:
        """ Create a Config object from a file.

        Args:
            filename (str): Absolute path to file.
        Returns:
            dict: Python dict which contains the key/value from the YAML file.
        """
        with open(filename, 'r') as stream:
            LOGGER.info('Chargement du fichier de configuration %s', filename)
            return ConfigLoader.read_yaml_stream(stream)

    @staticmethod
    def read_yaml_stream(filestream: io.BufferedIOBase) -> dict:
        """ Creates a Config object from a stream.

        Args:
            filestream (io.BufferedIOBase): stream
        Returns:
            dict: Python dict which contains the key/value from the YAML file.
        """
        # Constructor which finds the "custom tags" (!join) in YAML file
        # It enables the program to start a function which will concatenate 2 strings (a bit like os.path.join(...))
        yaml.add_constructor('!join', ConfigLoader.join, yaml.SafeLoader)
        # Resolver which tries to match the regex for environment variables
        yaml.add_implicit_resolver('!env_var', ConfigLoader.env_path_matcher, None, yaml.SafeLoader)
        # Constructeur binded to the previous resolver for environment varaibles
        yaml.add_constructor('!env_var', ConfigLoader.env_path_constructor, yaml.SafeLoader)
        try:
            return yaml.safe_load(filestream)
        except yaml.YAMLError as exc:
            LOGGER.error('Configuration file contains format error.')
            raise exc

    @staticmethod
    def env_path_constructor(loader: yaml.loader.SafeLoader, node: yaml.ScalarNode) -> str:
        """ Extracts the value of a node that matches the regex to read the associated environment variable then replace it with its value. """
        value = node.value
        match = ConfigLoader.env_path_matcher.match(value)
        env_var = match.group(1)

        try:
            env_var_value = os.environ[env_var]
        except KeyError:
            LOGGER.warning("No value for the following environment variable : [%s]. Initializing it as empty string.", str(env_var))
            return ''

        return env_var_value + value[match.end():]

    @staticmethod
    def check_template_match(config_path: str, template_path: str = None) -> bool:
        """ Takes the path to a configuration file as a parameter and returns True if the keys of its template match
        the concerned config file. If not, returns False.

        Args:
            loader (yaml.loader.SafeLoader): pyaml loader (SafeLoader there).
            node (yaml.ScalarNode): The node which contains the tag in YAML file.
        Returns:
            bool: True if everything matches, False if not.
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
            raise ValueError('{config_name} - The following keys were not found in template file: {err}'.format(config_name=config_filename, err=diff['dictionary_item_removed']))

        return match

    # define custom tag handler
    @staticmethod
    def join(loader: yaml.loader.SafeLoader, node: yaml.ScalarNode) -> str:
        """ Custom tags handler. Function launched when reading a configuration file and a \"custom tag\" !path is found.
        It allows to concatenate the string parameters of the field. (ex: data_dir: !join [\*project_dir, /data])

        Args:
            loader (yaml.loader.SafeLoader): pyaml loader (SafeLoader there).
            node (yaml.ScalarNode): The node which contains the tag in YAML file.
        Returns:
            str: Concatenated value of both strings.
        """ 
        seq = loader.construct_sequence(node)
        return ''.join([str(i) for i in seq])
