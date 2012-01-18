#!/usr/bin/env python
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
import glob
import os.path
import subprocess


uidir = os.path.abspath(os.path.dirname(__file__))


def generate():
    """Generate PySide UI Python files using a subprocess call"""
    for py in glob.glob(os.path.join(uidir, '*ui.py')):
        os.remove(py)
    for ui in glob.glob(os.path.join(uidir, '*.ui')):
        with open(os.path.splitext(ui)[0] + 'ui.py', 'w') as py:
            subprocess.call(['pyside-uic', ui], stdout=py)

if __name__ == '__main__':
    generate()
