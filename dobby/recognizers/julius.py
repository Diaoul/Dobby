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
from . import Recognizer
import logging


logger = logging.getLogger(__name__)


class Julius(Recognizer):
    def __init__(self, client, min_score):
        super(Julius, self).__init__()
        self.client = client
        self.min_score = min_score

    def run(self):
        self.client.connect()
        while not self._stop:
            recognition = self.client.recognize()
            sentence = unicode(recognition)
            score = abs(recognition.score)
            if self.min_score and score < self.min_score:
                logger.debug(u'Rejected sentence "%s" with score %f < %f' % (sentence, score, self.min_score))
                continue
            logger.debug(u'Firing recognition "%s" with score %f' % (sentence, score))
            for q in self.queues:
                q.put(recognition)
        self.client.disconnect()
