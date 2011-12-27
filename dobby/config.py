# Copyright 2011 Antoine Bertin <diaoulael@gmail.com>
#
# This file is part of Dobby.

# Dobby is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Dobby is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Dobby.  If not, see <http://www.gnu.org/licenses/>.

from configobj import ConfigObj, flatten_errors
from validate import Validator
import sys

def initConfig(path='config.ini'):
    config = ConfigObj(path, configspec='config.spec', encoding='utf-8')
    results = config.validate(Validator(), copy=True)
    if results != True:
        for (section_list, key, _) in flatten_errors(config, results):
            if key is not None:
                sys.stderr.write('The "%s" key in the section "%s" failed validation\n' % (key, ', '.join(section_list)))
            else:
                sys.stderr.write('The following section was missing: %s\n' % ', '.join(section_list))
            return False
    return config