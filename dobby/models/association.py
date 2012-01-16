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
from . import Base
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer


class Association(Base):
    """Association model that represents an association between a :class:`~dobby.models.scenario.Scenario`
    and a :class:`~dobby.models.actions.Action` with a special :attr:`order`

    :param \*\*kwargs: can set all attributes

    .. attribute:: scenario_id

        Foreing key to :attr:`Scenario.id <dobby.models.scenario.Scenario.id>`

    .. attribute:: action_id

        Foreing key to :attr:`Action.id <dobby.models.actions.Action.id>`

    .. attribute:: order

        Order in which the :class:`~dobby.models.actions.Action` objects of a :class:`~dobby.models.scenario.Scenario` should be executed

    .. attribute:: scenario

        Direct access to the :class:`~dobby.models.scenario.Scenario` object

    .. attribute:: action

         Direct access to the :class:`~dobby.models.actions.Action` object

    """
    __tablename__ = 'associations'
    scenario_id = Column(Integer, ForeignKey('scenarios.id'), primary_key=True)
    action_id = Column(Integer, ForeignKey('actions.id'), primary_key=True)
    order = Column(Integer)

    scenario = relationship('Scenario', back_populates='associations')
    action = relationship('Action', back_populates='associations')

    def __repr__(self):
        return "<Association('%r', '%r', '%d')>" % (self.scenario, self.action, self.order or 0)
