# This is purely the result of trial and error.

import sys
import codecs

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

import msl


class PyTest(TestCommand):
	# `$ python setup.py test' simply installs minimal requirements
	# and runs the tests with no fancy stuff like parallel execution.
	def finalize_options(self):
		TestCommand.finalize_options(self)
		self.test_args = [
			'--doctest-modules', '--verbose',
			'./msl', './tests'
		]
		self.test_suite = True

	def run_tests(self):
		import pytest
		sys.exit(pytest.main(self.test_args))


tests_require = [
	'pytest',
	'mock',
]


install_requires = [
]


# Conditional dependencies:

# sdist
if 'bdist_wheel' not in sys.argv:
	try:
		# noinspection PyUnresolvedReferences
		import argparse
	except ImportError:
		install_requires.append('argparse>=1.2.1')

	if 'win32' in str(sys.platform).lower():
		# Terminal colors for Windows
		install_requires.append('colorama>=0.2.4')


# bdist_wheel
extras_require = {
	# http://wheel.readthedocs.io/en/latest/#defining-conditional-dependencies
	':python_version == "2.6"'
	' or python_version == "2.7"'
	' or python_version == "2.5" ': ['argparse>=1.2.1'],
	':sys_platform == "win32"': ['colorama>=0.2.4'],
}


long_description = "MSL is gonna make your life simpler.";


setup(
	name='msl',
	version="1.0.0",
	description="msl",
	long_description=long_description,
	url='http://stillhungry.in/',
	download_url='https://github.com/mohitmv/msl',
	author="Mohit Saini",
	author_email='mohitsaini1196@gmail.com',
	license="",
	packages=find_packages(),
	entry_points={
		# 'console_scripts': [
		# 	'http = msl.__main__:main',
		# ],
	},
	extras_require=extras_require,
	install_requires=install_requires,
	tests_require=tests_require,
	cmdclass={'test': PyTest},
	classifiers=[
		'First Version Released - Production/Stable',
	],
)


