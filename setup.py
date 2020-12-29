# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open('requirements.txt') as f:
	install_requires = f.read().strip().split('\n')

# get version from __version__ variable in firstu_rewards/__init__.py
from firstu_rewards import __version__ as version

setup(
	name='firstu_rewards',
	version=version,
	description='FirstU Rewards Program',
	author='Tridz',
	author_email='info@tridz.com',
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
