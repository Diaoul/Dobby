# Copyright 2011 Antoine Bertin <diaoulael@gmail.com>
#
# This file is part of Dobby.
#
# Dobby is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Dobby is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Dobby.  If not, see <http://www.gnu.org/licenses/>.
from setuptools import setup, find_packages
import os.path
import dobby.infos


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(name='Dobby',
    version=dobby.infos.__version__,
    license='GPLv3',
    description='Python implementation of Ext Direct',
    long_description=read('README.rst') + '\n\n' +
                     read('NEWS.rst'),
    keywords='speech recognition voice synthesis',
    author='Antoine Bertin',
    author_email='diaoulael@gmail.com',
    url='https://github.com/Diaoul/Dobby',
    packages=find_packages(),
    include_package_data=True,
    setup_requires=['setuptools_git'],
    exclude_package_data={'': ['.gitignore']},
    scripts=['Dobby.py', 'DobbyQt.py'],
    install_requires=['pyaudio', 'pyjulius', 'pywunderground', 'SQLAlchemy'])
