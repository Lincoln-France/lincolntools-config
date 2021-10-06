# -*- coding: utf-8 -*-
# #!/usr/bin/env python

# """Tests for `lincolntools-config` package."""

import os
import pytest
import yaml
from lincolntools.config import ConfigLoader

FIXTURE_DIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    'data',
)


@pytest.mark.filterwarnings("ignore:MarkInfo")
@pytest.mark.datafiles(
    os.path.join(FIXTURE_DIR, 'configs', 'configs_sample', 'config.yaml')
)
def test_read_single_file(datafiles):
    filenames = [str(f) for f in datafiles.listdir()]
    os.environ['ENV_VALUE_TEST'] = 'test'
    config = ConfigLoader.load_from_file(filenames[0])
    assert config['mode'] == 'dev'
    assert config['foo']['test_env'] == 'test'
    assert type(config['data']['float']) == float
    assert config['data']['float'] == 0.1
    assert config['data']['bool'] is False
    assert len(config['data']['list']) == 3


@pytest.mark.filterwarnings("ignore:MarkInfo")
@pytest.mark.datafiles(
    os.path.join(FIXTURE_DIR, 'configs', 'configs_sample')
)
def test_read_folder(datafiles):
    os.environ['ENV_VALUE_TEST'] = 'test'
    config = ConfigLoader.load_from_folder(datafiles.strpath)

    assert config['mode'] == 'dev'
    assert type(config['data']) == dict
    assert type(config['part1']) == dict
    assert config['part1']['port'] == 12345
    assert type(config['part2']) == dict
    assert config['part2']['classic']['project_dir'] == '/path/to/project'
    assert type(config['foo']) == dict
    assert config['foo']['test_env'] == 'test'
    assert type(config['data']['float']) == float
    assert config['data']['float'] == 0.1
    assert config['data']['bool'] is False
    assert len(config['data']['list']) == 3


@pytest.mark.filterwarnings("ignore:MarkInfo")
@pytest.mark.datafiles(
    os.path.join(FIXTURE_DIR, 'configs', 'configs_sample')
)
def test_anchor_references(datafiles):
    config = ConfigLoader.load_from_folder(datafiles.strpath)
    assert config['mode'] == 'dev'  # simple test
    assert config['part2']['classic']['project_dir'] == '/path/to/project'
    # testing complex part
    assert config['part2']['complex']['data_dir'] == '/path/to/project/data'
    assert config['part2']['complex']['tests_dir'] == '/path/to/project/tests'
    assert config['part2']['complex']['subproject_dir'] == '/path/to/project/subproject'
    assert config['part2']['complex']['subproject_data_dir'] == '/path/to/project/subproject/data'
    assert config['part2']['complex']['subproject_tests_dir'] == '/path/to/project/subproject/tests'


@pytest.mark.filterwarnings("ignore:MarkInfo")
@pytest.mark.datafiles(
    os.path.join(FIXTURE_DIR, 'configs', 'configs_sample', 'with_difference')
)
def test_template_not_match(datafiles):
    config_path = os.path.join(datafiles.strpath, 'diff.yaml')
    with pytest.raises(ValueError):
        ConfigLoader.check_template_match(config_path)


@pytest.mark.filterwarnings("ignore:MarkInfo")
@pytest.mark.datafiles(
    os.path.join(FIXTURE_DIR, 'configs', 'configs_sample', 'with_difference')
)
def test_template_not_exists(datafiles):
    config_path = os.path.join(datafiles.strpath, 'anything.yaml')
    with pytest.raises(FileNotFoundError):
        ConfigLoader.check_template_match(config_path)


@pytest.mark.filterwarnings("ignore:MarkInfo")
@pytest.mark.datafiles(
    os.path.join(FIXTURE_DIR, 'configs', 'configs_sample', 'concat')
)
def test_concatenate_multiple_files(datafiles):
    os.environ['ENV_VALUE_TEST'] = 'test'
    config = ConfigLoader.load_from_folder(datafiles.strpath, concatenate=True)

    assert config['concat2']['other_dir'] == "/path/to/project/other"
    assert config['concat2']['subdir_concat'] == "/path/to/project/subproject/subdir"

    with pytest.raises(yaml.composer.ComposerError):
        config = ConfigLoader.load_from_folder(datafiles.strpath, concatenate=False)
