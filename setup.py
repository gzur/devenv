#!/usr/bin/env python
import os
from setuptools import setup, find_packages
# https://stackoverflow.com/questions/49837301/pip-10-no-module-named-pip-req
try:  # for pip >= 10
    from pip._internal.req import parse_requirements
except ImportError:  # for pip <= 9.0.3
    from pip.req import parse_requirements

root_dir = 'devenv'


def get_version():
    with open(os.path.join(root_dir, 'VERSION')) as version_file:
        return version_file.readlines()[0].strip()


version = get_version()
if 'SETUP_BRANCH' in os.environ:
    version += "-%s" % os.environ['SETUP_BRANCH']


setup(
    name='devenv',
    version=version,
    description='Development environment isolation suite (',
    author='gzur',
    author_email='gzur@gzur.net',
    url='http://gzur/net',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    package_data={'devenv': ['VERSION', 'PUBLIC_KEY']},
    install_requires=[
        str(i.req)
        for i in parse_requirements('requirements.txt', session=False)
        if i.req
    ],
    entry_points={
        'console_scripts': [
            'devenv = devenv.cli:cli',
        ]
    },
)
