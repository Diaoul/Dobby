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
from . import Trigger, TriggerEvent, TriggerActionEvent
from .. import pyjulius
import logging


logger = logging.getLogger(__name__)


class Julius(Trigger):
    """Analyze an audio source and put an event in the queue if sentence is spoken"""
    def __init__(self, event_queue, sentence, min_score, host, port, encoding, action):
        super(Julius, self).__init__(event_queue)
        self.sentence = sentence
        self.encoding = encoding
        self.min_score = min_score
        self.action = action
        self.client = pyjulius.Client(host, port, encoding)

    def run(self):
        self.client.connect()
        while not self._stop:
            recog = self.client.sentence()
            if unicode(recog) == self.sentence and abs(recog.score) > self.min_score:
                logger.debug(u'Julius sentence "%s" matched with score %f' % (recog, abs(recog.score)))
                self.event_queue.put(JuliusEvent)
            elif self.action and unicode(recog).startswith(self.sentence) and abs(recog.score) > self.min_score:
                action_sentence = unicode(recog)[len(self.sentence) + 1:]
                logger.debug(u'Julius sentence "%s" is in action "%s" !' % (recog, action_sentence))
                self.event_queue.put(TriggerActionEvent(action_sentence))
        self.client.disconnect()


class JuliusEvent(TriggerEvent):
    pass