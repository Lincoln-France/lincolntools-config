# lincolntools-config

> lincolntools : Python toolbox made in [Lincoln France](http://www.lincoln.fr)

* Author: Lincoln Innovation
* Creation date: 2020-10-01
* see [AUTHORS.md](./AUTHORS.md)

This package belongs to the `lincolntools` namespace <br>
The goal of this package is to provide the necessary tools to create a unique and global configuration object that can be queried anywhere in a Python project.


## Table of content

1. [Documentation](#documentation)
2. [Tests](#tests)
3. [Contribute](#contribute)
4. [History](#historique)
5. [Credits](#credits)

## Installation

```bash
    pip install lincolntools-config
```

## How to use
There are several possibilities to load a YAML configuration file :
* Provide the path to **a file** which will be processed and transformed into a Python `dict`
* Provide the path to **a folder** that contains one or more YAML files that will be concatenated into a single object.



### Example
In the following examples we suppose our config folder has the given structure :

```bash
└── config
    ├── config_foo
        ├── foo.yaml               
        └── foo.template 
    └── config_bar
        ├── bar.yaml               
        └── bar.template 
```
*foo.yaml*
```yaml
foo:
    foo_key : foo_value
```

*bar.yaml*
```yaml
bar:
    bar_key : bar_value
```

Code :

```python
from lincolntools.config import Config
my_config = Config('/path/to/config')
print(my_config.conf)
# {'foo': {'foo_key': 'foo_value'}, 'bar': {'bar_key': 'bar_value'}, '_version': 1}
print(my_config.get('foo'))
# {'foo_key': 'foo_value'}

print(my_config.get('foo').get('foo_key'))
# foo_value

print(my_config.get('foo')['foo_key']) # same as above but with another syntax
# foo_value

print(my_config.flatten())
# {'foo-foo_key': 'foo_value', 'bar-bar_key': 'bar_value'}

print(my_config.dump())
# _version: 2
# bar:
#   bar_key: bar_value
# foo:
#   foo_key: foo_value
```

### Important
The `Config` class is based on the Single design pattern ([official documentation](https://python-3-patterns-idioms-test.readthedocs.io/en/latest/Singleton.html)). <br>
**TLDR** : Only one instance of `Config` can be initialized during the whole program lifetime.
 
```python
from lincolntools.config import Config
my_first_config = Config('/path/to/config') # ok, no other instance exists
my_other_config = Config('/path/to/config') # nok
# Exception: This is a singleton
```

## Tests
Launch tests with the default Python version :
```bash
# in the project folder
pytest
````
Launch tests on multiple Python versions (see [`tox.ini`](./tox.ini)) :

```bash
# in the project folder
tox
```

## History

Voir [HISTORY.md](./HISTORY.md)


## Credits

This package was inspired by Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

*  _Cookiecutter: https://github.com/audreyr/cookiecutter
*  _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage

