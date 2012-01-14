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
from . import Action
from sqlalchemy.orm.mapper import reconstructor
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String
import feedparser
import logging


logger = logging.getLogger(__name__)


class Feed(Action):
    """Feed Action fetch feeds using feedparser"""
    __tablename__ = 'feed_actions'
    __mapper_args__ = {'polymorphic_identity': 'feed'}
    id = Column(Integer, ForeignKey('actions.id'), primary_key=True)
    url = Column(String(200))

    def __init__(self, **kwargs):
        super(Feed, self).__init__(**kwargs)
        self.feed = {}

    @reconstructor
    def onload(self):
        self.feed = {}

    def format_tts(self):
        if not self.feed:
            logger.debug(u'Fetching feed from %s' % self.url)
            self.feed = feedparser.parse(self.url)
        return self.tts.format(feed=self.feed)
