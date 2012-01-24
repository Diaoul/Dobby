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
from models import Base
from models.actions import Action
from models.actions.datetime import Datetime
from models.actions.feed import Feed
from models.actions.weather import Weather
from models.association import Association
from models.command import Command
from models.scenario import Scenario
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm.session import sessionmaker
import logging
import os


logger = logging.getLogger(__name__)


def initDb(path):
    """Initialize database (create/update) and returns a sessionmaker to it

    :return: a session maker object
    :rtype: SessionMaker

    """
    logger.info(u'Initializing database')
    engine = create_engine('sqlite:///' + path)
    if not os.path.exists(path):
        logger.debug(u'Database does not exist, creating...')
        Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)
