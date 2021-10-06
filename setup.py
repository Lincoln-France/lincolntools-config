#!/usr/bin/env python 
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_namespace_packages

with open('README.md') as readme_file:
    readme = readme_file.read()

with open('HISTORY.md') as history_file:
    history = history_file.read()

with open('requirements/prod.txt') as prod_requirements_file:
    prod_requirements = prod_requirements_file.read().splitlines()
    if len(prod_requirements) and prod_requirements[0].startswith('-r'):
        prod_requirements = prod_requirements[1:]

setup_requirements = ['pytest-runner', ]

test_requirements = ['pytest>=3', ]

setup(
    author="Lincoln Innovation",
    author_email='labinnovation@mel.lincoln.fr',
    python_requires='>=3.5',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="Boîte à outils Python made in Lincoln",
    download_url="https://github.com/Lincoln-France/lincolntools-config/archive/refs/tags/v1.0.3.tar.gz",
    install_requires=prod_requirements,
    long_description=readme + '\n\n' + history,
    long_description_content_type="text/markdown",
    include_package_data=True,
    keywords=['configuration', 'yaml', 'lincoln', 'lincolntools', 'lincolntools-config'],
    name='lincolntools-config',
    # packages=find_packages(include=['lincolntools-config', 'lincolntools-config.*']),
    packages=find_namespace_packages(include=['lincolntools.*']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='http://factory.lincoln.cloud/git/Innovation/lincolntools-config',
    version='1.0.3',
    zip_safe=False,
)
