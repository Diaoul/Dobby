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
import pyjulius


logger = logging.getLogger(__name__)


class Julius(Recognizer):
    """Julius Recognizer is based on `Julius speech recognition engine <http://julius.sourceforge.jp/en/>`_.
    It uses :mod:`pyjulius` to connect to julius instance running in module mode
    
    :param string host: host of the server
    :param integer port: port of the server
    :param string encoding: encoding used to decode server's output
    :param float min_score: minimum score under which the recognition result will be ignored

    """
    def __init__(self, host, port, encoding, min_score):
        super(Julius, self).__init__()
        self.client = pyjulius.Client(host, port, encoding)
        self.min_score = min_score
        self.client.connect()

    def run(self):
        """Run the recognition and :meth:`~dobby.recognizers.Recognizer.publish` the recognized :class:`pyjulius.Sentence` objects"""
        while not self._stop:
            recognition = self.client.recognize()
            sentence = unicode(recognition)
            score = abs(recognition.score)
            if self.min_score and score < self.min_score:
                logger.debug(u'Rejected sentence "%s" with score %f < %f' % (sentence, score, self.min_score))
                continue
            logger.debug(u'Firing recognition "%s" with score %f' % (sentence, score))
            self.publish(recognition)
        self.client.disconnect()
