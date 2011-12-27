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

__all__ = ['Sentence', 'Action', 'Weather', 'Say']


from elixir.entity import Entity
from elixir.fields import Field
from elixir.options import using_options
from sqlalchemy.types import UnicodeText


class Sentence(Entity):
    text = Field(UnicodeText)
    
    def __repr__(self):
        return '<Sentence "%s">' % self.text


class Action(Entity):
    using_options(inheritance='multi')
    tts = Field(UnicodeText)


class Weather(Action):
    using_options(inheritance='multi')


class Say(Action):
    using_options(inheritance='multi')

