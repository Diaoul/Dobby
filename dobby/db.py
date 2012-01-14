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
from models.sentence import Sentence
from models.association import Association
from models.actions import Action
from models.actions.weather import Weather
from models.actions.datetime import Datetime
from sqlalchemy.engine import create_engine
from sqlalchemy.orm.session import sessionmaker
import logging


logger = logging.getLogger(__name__)
Session = sessionmaker()


def initDb(path):
    logger.info(u'Initializing database')
    engine = create_engine('sqlite:///' + path)
    Session.configure(bind=engine)
    Base.metadata.create_all(engine)
