# -*- coding: utf-8 -*-
# #!/usr/bin/env python

# """Tests for `lincolntools-config` package."""

import os
import pytest

from lincolntools.config import Config

FIXTURE_DIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    'data',
)


def test_singletone():
    conf1 = Config.get_instance()
    conf2 = Config.get_instance()
    conf3 = Config.get()  # noqa: F841
    assert conf1 == conf2
    Config.clear()


@pytest.mark.filterwarnings("ignore:MarkInfo")
@pytest.mark.datafiles(
    os.path.join(FIXTURE_DIR, 'configs', 'basic.yaml')
)
def test_singletone2(datafiles):
    filenames = [str(f) for f in datafiles.listdir()]
    _ = Config(filenames[0])
    with pytest.raises(Exception) as _:
        _ = Config(filenames[0])
    Config.clear()


@pytest.mark.filterwarnings("ignore:MarkInfo")
@pytest.mark.datafiles(
    os.path.join(FIXTURE_DIR, 'configs', 'basic.yaml')
)
def test_update_and_dump(datafiles):
    filenames = [str(f) for f in datafiles.listdir()]
    config = Config(filenames[0])

    assert config['_version'] == 1

    assert config['foo']['bar'] == 1
    assert config['foo']['baz'] == 2

    config['foo']['bar'] = {'test': 10}
    config['foo']['baz'] = 3
    assert config['foo']['bar']['test'] == 10
    assert config['foo']['baz'] == 3

    yaml_string = config.dump()
    assert yaml_string == '_version: 2\nfoo:\n  bar:\n    test: 10\n  baz: 3\n'

    yaml_string = config.dump()
    assert yaml_string == '_version: 3\nfoo:\n  bar:\n    test: 10\n  baz: 3\n'

    config.dump(filenames[0])

    Config.clear()

    config = Config(filenames[0])
    assert config['foo']['bar']['test'] == 10
    assert config['foo']['baz'] == 3
    Config.clear()


@pytest.mark.filterwarnings("ignore:MarkInfo")
@pytest.mark.datafiles(
    os.path.join(FIXTURE_DIR, 'configs', 'basic.yaml')
)
def test_flatten(datafiles):
    filenames = [str(f) for f in datafiles.listdir()]
    config = Config(filenames[0])

    config['tar'] = 'test'
    config['var'] = 'variation'

    p = config._flatten([], config.conf)
    assert len(p) == 4
    assert p[0] == ('foo-bar', 1)
    assert p[1] == ('foo-baz', 2)
    assert p[2] == ('tar', 'test')
    assert p[3] == ('var', 'variation')

    p = config.flatten()
    assert len(p) == 4
    assert p['foo-bar'] == 1
    assert p['foo-baz'] == 2
    assert p['tar'] == 'test'
    assert p['var'] == 'variation'

    Config.clear()


def test_contains():
    config = Config()
    config['key'] = 1

    assert ('key' in config) is True
    assert ('not_exists' in config) is False

    Config.clear()


def test_get_default():
    config = Config()
    config['key'] = 1

    assert config.get('key', 0) == 1
    assert config.get('not_exists', 0) == 0

    Config.clear()
