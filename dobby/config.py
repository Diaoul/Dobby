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
from configobj import ConfigObj
from validate import Validator, VdtTypeError, VdtValueError
import os.path


def is_option_list(value, *args):
    """Validator for a list of options"""
    if not isinstance(value, list):
        raise VdtTypeError(value)
    for v in value:
        if v not in args:
            raise VdtValueError(v)
    return value

validator = Validator({'option_list': is_option_list})

def initConfig(path='config.ini'):
    """Initialize the configuration from the given file

    :param string path: path to the configuration file
    :return: the read configuration
    :rtype: ConfigObj

    """
    return ConfigObj(path, configspec=os.path.join(os.path.abspath(os.path.dirname(__file__)), 'config.spec'), encoding='utf-8')
