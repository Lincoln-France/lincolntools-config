# lincolntools-config

> lincolntools : Boîte à outils Python made in Lincoln

* Auteur: Lincoln Innovation
* Date de création: 2020-10-01
* voir [AUTHORS.md](./AUTHORS.md)

## Objectif

Ce package fait parti du namespace `lincolntools`.<br>
L'objectif de ce package est de fournir les outils nécessaire à la création d'un objet de configuration global pour un projet Python.


## Table des matières

1. [Les répertoires](#les-répertoires)
2. [Les fichiers importants](#les-fichiers-importants)
3. [Documentation](#documentation)
3. [Tester](#tester)
4. [Contribuer](#contribuer)
5. [Historique](#historique)

## Les répertoires

```bash
.
├── lincolntools        # namespace contenant le module
    └── config/         # le module config
├── requirements/       # dossier contenant les requirements python
├── tests/              # dossier contenant les tests du package
├── logs/               # dossier contenant les logs : dev specific
└── docs/               # documentations générées par sphinx
```

## Les fichiers importants

```bash
.
├── lincolntools
    └── config
        ├── __init__.py
        ├── config.py               # 
        └── config_loader.py        #      
├── README.md                       # this file
├── HISTORY.md                      # historique des version et les modifications
├── CONTRIBUTING.md                 # comment contribuer au projet
├── LICENSE                         # license si besoin
├── Makefile                        # Makefile: aide à la compilation
├── .gitignore                      # Liste des éléments que git doit ignorer lors du commit
├── requirements.txt                # Contient les dépendances (=packages) pyhton du projet
├── setup.cfg                       # aide au setup.py
├── setup.py                        # setup.py pour créer un package python
└── tox.ini                         # aide pour les tests
```

## Installation

    To-Do.......


## Comment l'utiliser
On a la possibilité de charger une configuration au format YAML de plusieurs manière :
* Fournir le chemin vers un fichier qui sera traité et transformé en `dict` Python.
* Fournir le chemin vers un dossier qui contient un ou plusieurs fichier YAML qui seront concatenés en un seul objet.

### Exemple
Dans cet exemple on part du principe qu'on dispose de l'arborescence suivante: 

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

print(my_config.get('foo')['foo_key']) # pareil qu'au dessus avec une autre syntaxe
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
La classe `Config` est basé sur le design pattern Singleton ([explications ici](https://python-3-patterns-idioms-test.readthedocs.io/en/latest/Singleton.html)). Celà signifie qu'une seule et unique instance de ̀`Config` peut être créée pendant la vie d'un programme. 
```python
from lincolntools.config import Config
my_first_config = Config('/path/to/config') # ok, pas d'autre instance existe
my_other_config = Config('/path/to/config') # nok
# Exception: Cette classe est un singleton!
```

## Tester
Lancer les tests avec le version par défaut de Python :
```bash
# dans le projet
pytest
````
Lancer les tests sur toutes les versions de Python (voir [`tox.ini`](./tox.ini)) :
```bash
# dans le projet:
tox
```

## Contribuer

Voir [CONTRIBUTING.md](./CONTRIBUTING.md)


## Historique

Voir [HISTORY.md](./HISTORY.md)


## Credits

This package was inspired by Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

*  _Cookiecutter: https://github.com/audreyr/cookiecutter
*  _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage

